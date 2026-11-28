"""
Performs top-level control over a Multi-Objective Optimization (MOO) run

The Pareto front between two objective functions (f1, f2) is explored with the augmented
epsilon-constraint method:  f1 is minimized while f2 is bound by a set of evenly spaced caps
between its lowest value and the value it takes when f1 is at its minimum.

The method is described in Finke and Bertsch (2023):
https://doi.org/10.1016/j.apenergy.2022.120521
"""

from __future__ import annotations

import logging
import queue
import sqlite3
import time
from dataclasses import dataclass
from importlib import resources
from logging import getLogger
from typing import TYPE_CHECKING, Any, cast

import pyomo.environ as pyo
from pyomo.opt import check_optimal_termination

from temoa._internal.run_actions import build_instance, solve_instance
from temoa._internal.table_writer import PolledResults, ResultPoller, TableWriter
from temoa.core.solver_spec import (
    mode_solver_options,
    read_options_file,
    redact_solver_options,
    resolve_num_workers,
    resolve_solver_options,
)
from temoa.data_io.hybrid_loader import HybridLoader
from temoa.extensions.modeling_to_generate_alternatives.worker import WORKER_CONTEXT, Worker
from temoa.extensions.multi_objective_optimization.custom_objectives import (
    CustomObjectiveWeights,
    custom_objective_expression,
    load_custom_objective_weights,
)
from temoa.extensions.multi_objective_optimization.moo_constants import MooObjective
from temoa.extensions.multi_objective_optimization.objectives import objective_expression
from temoa.model_checking.pricing_check import price_checker

if TYPE_CHECKING:
    from multiprocessing import Queue
    from multiprocessing.process import BaseProcess

    from pyomo.dataportal import DataPortal

    from temoa.core.config import TemoaConfig
    from temoa.core.model import TemoaModel

logger = getLogger(__name__)


def is_suboptimal(res: Any) -> bool:
    """
    The solver stopped with a feasible but not provably optimal solution, which it loaded: e.g. a
    gurobi barrier solve without crossover that cannot meet the optimality tolerances
    """
    if res.solver.termination_condition == pyo.TerminationCondition.feasible:
        return True
    return (
        res.solver.status == pyo.SolverStatus.warning
        and 'sub-optimal' in str(res.solver.message).lower()
    )


F1_TOLERANCE = 1e-6

solver_options_path = (
    resources.files('temoa.extensions.multi_objective_optimization') / 'MOO_solver_options.toml'
)


def _label_list(raw: object, option: str) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, (list, tuple)) and all(isinstance(item, str) for item in raw):
        return list(raw)
    raise ValueError(f'MOO option {option} must be a list of commodity names')


@dataclass(frozen=True)
class MooResult:
    """What a worker sends back for a solved Pareto point, instead of the model"""

    name: str
    values: list[tuple[str, float]]
    results: PolledResults


@dataclass(frozen=True)
class MooResultExtractor:
    """Takes the objective values and the results out of a solved Pareto point, in the worker"""

    poller: ResultPoller
    labels: tuple[str, ...]

    def __call__(self, model: TemoaModel) -> MooResult:
        moo_values: Any = model.moo_values
        return MooResult(
            name=model.name,
            values=[(label, float(pyo.value(moo_values[label]))) for label in self.labels],
            results=self.poller(model),
        )


class MooSequencer:
    def __init__(self, config: TemoaConfig, inputs: dict[str, Any] | None = None):
        if not config.input_database == config.output_database:
            raise NotImplementedError('MOO assumes input and output databases are same')
        self.con = sqlite3.connect(config.input_database)
        if config.save_lp_file:
            logger.warning('Saving LP file is disabled during MOO runs.')
            config.save_lp_file = False
        if config.save_excel:
            logger.warning('Saving excel is disabled during MOO runs.')
            config.save_excel = False
        self.config = config

        moo_inputs: dict[str, Any] = dict(config.moo_inputs or {}) if inputs is None else inputs
        self.custom_weights: dict[str, CustomObjectiveWeights] = {}
        self.f1 = self._objective_label(moo_inputs.get('f1', 'cost'))
        self.f2 = self._objective_label(moo_inputs.get('f2', 'emission'))
        if self.f1 == self.f2:
            raise ValueError('MOO objectives f1 and f2 must be different')
        self.ncaps = int(moo_inputs.get('ncaps', 11))
        if self.ncaps < 2:
            raise ValueError('MOO option ncaps must be at least 2')
        self.slack_weight = float(moo_inputs.get('c', 1e-4))
        if self.slack_weight < 0:
            raise ValueError('MOO option c must be non-negative')
        self.emission_commodities = _label_list(
            moo_inputs.get('emission_commodities'), 'emission_commodities'
        )
        self.construction_input_commodities = _label_list(
            moo_inputs.get('construction_input_commodities'), 'construction_input_commodities'
        )
        logger.info(
            'Initialized MOO sequencer with f1: %s, f2: %s, ncaps: %d, c: %s',
            self.f1,
            self.f2,
            self.ncaps,
            self.slack_weight,
        )
        logger.info(
            'MOO emission commodities: %s.  MOO construction input commodities: %s',
            self.emission_commodities or 'all',
            self.construction_input_commodities or 'all',
        )

        all_options = read_options_file(solver_options_path)
        self.num_workers = resolve_num_workers(moo_inputs, all_options, 'MOO')
        self.worker_solver_options = resolve_solver_options(
            self.config.solver,
            mode_solver_options(moo_inputs, 'MOO'),
            fallback_options=all_options.get(self.config.solver_name, {}),
        )
        logger.info('MOO workers are set to %d', self.num_workers)
        logger.info(
            'Using worker solver options: %s', redact_solver_options(self.worker_solver_options)
        )

        self.writer = TableWriter(self.config)
        self.writer.clear_scenario()
        self.solve_count = 0

    def _objective_label(self, raw: object) -> str:
        label = str(raw).strip()
        builtin = {objective.value for objective in MooObjective}
        if label.lower() in builtin:
            return label.lower()
        self.custom_weights[label] = load_custom_objective_weights(self.con, label)
        return label

    def start(self) -> None:
        """Run the sequencer"""
        # ==== basic sequence ====
        # 1. Load the model data and build the instance
        # 2. Replace the cost objective with the expressions of the MOO objective functions
        # 3. Determine the Pareto boundaries (lowest f1, lowest f2, f2 at lowest f1)
        # 4. Solve for each cap on f2 and record the results
        instance = self.build_model()
        self.solve_points(instance, dict(enumerate(reversed(self.find_caps(instance)))))

    def build_model(self) -> TemoaModel:
        # 1. Load data
        hybrid_loader = HybridLoader(db_connection=self.con, config=self.config)
        data_portal: DataPortal = hybrid_loader.load_data_portal(myopic_index=None)
        instance: TemoaModel = build_instance(
            loaded_portal=data_portal,
            model_name=self.config.scenario,
            silent=self.config.silent,
            extensions=self.config.extensions,
        )
        if self.config.price_check:
            good_prices = price_checker(instance)
            if not good_prices and not self.config.silent:
                print('Warning:  Cost anomalies discovered.  Check log file for details.')

        # 2. Set up the objective function expressions
        instance.del_component(instance.total_cost)
        expressions = {
            objective.value: objective_expression(
                instance,
                objective,
                emission_commodities=self.emission_commodities,
                construction_input_commodities=self.construction_input_commodities,
            )
            for objective in MooObjective
        }
        for label, weights in self.custom_weights.items():
            expressions[label] = custom_objective_expression(instance, weights)
        for label in (self.f1, self.f2):
            if not hasattr(expressions[label], 'is_expression_type'):
                msg = f'Construction of the MOO objective {label} failed to locate any variables.'
                logger.error(msg)
                raise ValueError(msg)
        self.labels = list(expressions)
        instance.moo_values = pyo.Expression(self.labels, initialize=expressions)
        instance.moo_slack = pyo.Var(domain=pyo.NonNegativeReals, initialize=0)
        return instance

    def find_caps(self, instance: TemoaModel) -> list[float]:
        f1_expr = instance.moo_values[self.f1]
        f2_expr = instance.moo_values[self.f2]

        # 3. Pareto boundaries
        self._report(f'Calculating the minimum {self.f1} value.')
        instance.moo_objective = pyo.Objective(expr=f1_expr, sense=pyo.minimize)
        self._solve(instance)
        f1_lowest = pyo.value(f1_expr)
        instance.del_component(instance.moo_objective)

        self._report(f'Calculating the minimum {self.f2} value.')
        instance.moo_objective = pyo.Objective(expr=f2_expr, sense=pyo.minimize)
        self._solve(instance)
        f2_lowest = pyo.value(f2_expr)

        self._report(f'Calculating the {self.f2} value associated with the minimum {self.f1}.')
        instance.moo_f1_cap = pyo.Constraint(
            expr=f1_expr <= f1_lowest + F1_TOLERANCE * max(1.0, abs(f1_lowest))
        )
        self._solve(instance)
        f2_highest = pyo.value(f2_expr)
        instance.del_component(instance.moo_f1_cap)
        instance.del_component(instance.moo_objective)

        logger.info(
            'MOO boundaries:  lowest %s: %0.6g, lowest %s: %0.6g, highest %s: %0.6g',
            self.f1,
            f1_lowest,
            self.f2,
            f2_lowest,
            self.f2,
            f2_highest,
        )
        if f2_highest <= f2_lowest:
            logger.warning(
                'The MOO objectives %s and %s are not conflicting: all the caps lead to the same '
                'solution.',
                self.f1,
                self.f2,
            )
            f2_highest = f2_lowest

        # 4. Pareto optimal solutions
        step = (f2_highest - f2_lowest) / (self.ncaps - 1)
        caps = [f2_lowest + n * step for n in range(self.ncaps)]
        caps[-1] = f2_highest
        self.f2_range = f2_highest - f2_lowest
        return caps

    def point_instance(self, instance: TemoaModel, iteration: int, cap: float) -> TemoaModel:
        """A copy of the instance that computes the Pareto optimal solution at a cap on f2"""
        model: Any = instance
        slack_coefficient = (
            self.slack_weight / self.f2_range if self.f2_range > 0 else self.slack_weight
        )
        model.moo_objective = pyo.Objective(
            expr=model.moo_values[self.f1] - model.moo_slack * slack_coefficient,
            sense=pyo.minimize,
        )
        model.moo_f2_cap = pyo.Constraint(expr=model.moo_values[self.f2] + model.moo_slack == cap)
        try:
            point = cast('TemoaModel', instance.clone())
        finally:
            instance.del_component(model.moo_f2_cap)
            instance.del_component(model.moo_objective)
        if not self.config.save_duals and point.component('dual') is not None:
            point.del_component('dual')
        point.name = f'{self.config.scenario}-{iteration}'
        return point

    def solve_points(
        self, instance: TemoaModel, caps: dict[int, float]
    ) -> dict[int, tuple[float, float]]:
        """Solve the Pareto optimal solutions at the caps on f2 in parallel and record the results.

        Args:
            instance: The model built by build_model().
            caps: The caps on f2, by iteration.

        Returns:
            The values of f1 and f2 of the solutions found, by iteration.
        """
        work_queue: Queue[Any] = WORKER_CONTEXT.Queue(1)
        result_queue: Queue[Any] = WORKER_CONTEXT.Queue()
        log_queue: Queue[Any] = WORKER_CONTEXT.Queue(50)
        solver_logs = self.config.output_path / 'solver_logs'
        solver_logs.mkdir(exist_ok=True)
        workers: list[BaseProcess] = []
        for _ in range(min(self.num_workers, len(caps))):
            worker = Worker(
                model_queue=work_queue,
                results_queue=result_queue,
                log_root_name=__name__,
                log_queue=log_queue,
                log_level=logging.INFO,
                solver_name=self.config.solver_name,
                solver_options=self.worker_solver_options,
                solver_log_path=solver_logs,
                result_extractor=MooResultExtractor(
                    self.writer.result_poller(check_balance=True), tuple(self.labels)
                ),
            )
            worker.start()
            workers.append(worker)

        pending = list(caps.items())
        shutdown_signals = len(workers)
        stopped = 0
        job: Any = None
        found: dict[int, tuple[float, float]] = {}
        try:
            while stopped < len(workers):
                if job is None and pending:
                    n, cap = pending.pop(0)
                    self._report(
                        f'Calculating Pareto optimal solution {n} ({self.f2} cap: {cap:0.6g}).'
                    )
                    job = self.point_instance(instance, iteration=n, cap=cap)
                elif job is None and shutdown_signals:
                    job = 'ZEBRA'
                    shutdown_signals -= 1
                if job is not None:
                    try:
                        work_queue.put(job, block=False)
                        job = None
                    except queue.Full:
                        pass
                try:
                    result = result_queue.get_nowait()
                except queue.Empty:
                    result = None
                if result is None and not any(process.is_alive() for process in workers):
                    try:
                        result = result_queue.get(timeout=1)
                    except queue.Empty:
                        raise RuntimeError('The MOO workers stopped unexpectedly') from None
                if result == 'COYOTE':
                    stopped += 1
                elif isinstance(result, str):
                    pass
                elif result is not None:
                    n = int(result.name.split('-')[-1])
                    self._record(result, iteration=n, cap=caps[n])
                    found[n] = self.objective_values(result)
                self._handle_logs(log_queue)
                time.sleep(0.05)
        finally:
            work_queue.cancel_join_thread()
            for process in workers:
                process.join(timeout=1 if stopped < len(workers) else None)
                if process.is_alive():
                    process.terminate()
            self._handle_logs(log_queue)
        for n in sorted(set(caps) - set(found)):
            logger.warning('MOO solve of Pareto optimal solution %d failed.  Skipping it.', n)
        return found

    def objective_values(self, result: MooResult) -> tuple[float, float]:
        values = dict(result.values)
        return values[self.f1], values[self.f2]

    @staticmethod
    def _handle_logs(log_queue: Queue[Any]) -> None:
        while True:
            try:
                record = log_queue.get_nowait()
            except queue.Empty:
                break
            getLogger(record.name).handle(record)

    def _report(self, msg: str) -> None:
        logger.info(msg)
        if not self.config.silent:
            print(msg)

    def _solve(self, instance: TemoaModel) -> None:
        self.solve_count += 1
        try:
            _, res = solve_instance(
                instance=instance,
                solver_name=self.config.solver_name,
                silent=self.config.silent,
                solver_options=resolve_solver_options(self.config.solver),
            )
            if check_optimal_termination(res):
                return
            if is_suboptimal(res):
                logger.warning(
                    'MOO solve #%d ended with a sub-optimal solution (%s).  It is used: the '
                    'objective values of this solve may be slightly off.',
                    self.solve_count,
                    res.solver.message,
                )
                return
            status = str(res.solver.termination_condition)
        except RuntimeError:
            status = 'no solution returned'
        msg = (
            f'MOO solve #{self.solve_count} failed with status: {status}.  The objective function '
            'may be unbounded, e.g. because of negative weights in a custom objective.  '
            'Terminating run.'
        )
        logger.error(msg)
        raise RuntimeError(msg)

    def _record(self, result: MooResult, iteration: int, cap: float) -> None:
        values = result.values
        logger.info(
            'MOO solution %d (%s cap: %0.6g):  %s',
            iteration,
            self.f2,
            cap,
            ', '.join(f'{name}: {val:0.6g}' for name, val in values),
        )
        if self.config.save_duals and not result.results.duals:
            logger.warning(
                'The solver returned no duals for MOO solution %d: solvers return none for '
                'mixed-integer models.',
                iteration,
            )
        self.writer.write_polled_results(result.results, iteration=iteration)
        self.writer._insert_objective_results(values, iteration=iteration)

    def __del__(self) -> None:
        if hasattr(self, 'con') and self.con is not None:
            try:
                self.con.close()
            except Exception:
                pass
