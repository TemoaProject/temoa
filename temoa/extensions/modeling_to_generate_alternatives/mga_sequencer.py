"""
Performs top-level control over an MGA model run
"""

import logging
import queue
import sqlite3
import time
import tomllib
from datetime import datetime
from logging import getLogger
from multiprocessing import Queue
from importlib import resources
from pathlib import Path
from queue import Empty

import pyomo.environ as pyo
from pyomo.contrib.solver.common.results import Results
from pyomo.dataportal import DataPortal
from pyomo.opt import check_optimal_termination

from temoa._internal.run_actions import build_instance
from temoa._internal.table_writer import TableWriter
from temoa.components.costs import total_cost_rule
from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel
from temoa.data_io.hybrid_loader import HybridLoader
from temoa.extensions.modeling_to_generate_alternatives.manager_factory import get_manager
from temoa.extensions.modeling_to_generate_alternatives.mga_constants import MgaAxis, MgaWeighting
from temoa.extensions.modeling_to_generate_alternatives.vector_manager import VectorManager
from temoa.extensions.modeling_to_generate_alternatives.worker import Worker
from temoa.model_checking.pricing_check import price_checker

logger = getLogger(__name__)

solver_options_path = (
    resources.files('temoa.extensions.modeling_to_generate_alternatives')
    / 'MGA_solver_options.toml'
)


class MgaSequencer:
    def __init__(self, config: TemoaConfig):
        # PRELIMINARIES...
        # let's start with the assumption that input db = output db...  this may change?
        if not config.input_database == config.output_database:
            raise NotImplementedError('MGA assumes input and output databases are same')
        self.con = sqlite3.connect(config.input_database)
        if not config.source_trace:
            logger.warning(
                'Performing MGA runs without source trace.  '
                'Recommend selecting source trace in config file.'
            )
        if config.save_lp_file:
            logger.warning('Saving LP file is disabled during MGA runs.')
            config.save_lp_file = False
        if config.save_duals:
            logger.warning('Saving duals is disabled during MGA runs.')
            config.save_duals = False
        if config.save_excel:
            logger.warning('Saving excel is disabled during MGA runs.')
            config.save_excel = False
        self.config = config

        # read in the options
        try:
            with resources.as_file(solver_options_path) as path:
                with open(path, 'rb') as f:
                    all_options = tomllib.load(f)
            s_options = all_options.get(self.config.solver_name, {})
            logger.info('Using solver options: %s', s_options)

        except FileNotFoundError:
            logger.warning('Unable to find solver options toml file.  Using default options.')
            s_options = {}
            all_options = {}

        # get handle on solver instance
        self.opt = pyo.SolverFactory(self.config.solver_name)
        self.worker_solver_options = s_options

        # some defaults, etc.
        self.internal_stop = False
        axis_label = config.mga_inputs.get('axis', '').upper()
        try:
            self.mga_axis = MgaAxis[axis_label]
            logger.info('MGA axis is set to %s.', self.mga_axis.name)
        except KeyError:
            logger.warning('No/bad MGA Axis specified.  Using default: Activity by Tech Category')
            self.mga_axis = MgaAxis.TECH_CATEGORY_ACTIVITY
        weighting_label = config.mga_inputs.get('weighting', '').upper()
        try:
            self.mga_weighting = MgaWeighting[weighting_label]
            logger.info('MGA weighting set to %s', self.mga_weighting.name)
        except KeyError:
            logger.warning('No/bad MGA Weighting specified.  Using default: Hull Expansion')
            self.mga_weighting = MgaWeighting.HULL_EXPANSION
        self.num_workers = all_options.get('num_workers', 1)
        logger.info('MGA workers are set to %s', self.num_workers)
        self.iteration_limit = config.mga_inputs.get('iteration_limit', 20)
        logger.info('Set MGA iteration limit to: %d', self.iteration_limit)
        self.time_limit_hrs = config.mga_inputs.get('time_limit_hrs', 12)
        logger.info('Set MGA time limit hours to: %0.1f', self.time_limit_hrs)
        self.cost_epsilon = config.mga_inputs.get('cost_epsilon', 0.05)
        logger.info('Set MGA cost (relaxation) epsilon to: %0.3f', self.cost_epsilon)

        # internal records
        self.solve_count = 0
        self.seen_instance_indices = set()
        self.orig_label = self.config.scenario

        # output handling
        self.writer = TableWriter(self.config)
        self.writer.clear_scenario()
        self.verbose = False  # for troubleshooting

        logger.info(
            'Initialized MGA sequencer with MGA Axis %s and weighting %s',
            self.mga_axis.name,
            self.mga_weighting.name,
        )

    def start(self):
        """Run the sequencer"""
        # ==== basic sequence ====
        # 1. Load the model data, which may involve filtering it down if source tracing
        # 2. Solve the base model (using persistent solver...maybe)
        # 3. Adjust the model
        # 4. Instantiate a Manager to pull in more instances
        # 5. Start the re-solve loop

        start_time = datetime.now()

        # 1. Load data
        hybrid_loader = HybridLoader(db_connection=self.con, config=self.config)
        data_portal: DataPortal = hybrid_loader.load_data_portal(myopic_index=None)
        instance: TemoaModel = build_instance(
            loaded_portal=data_portal, model_name=self.config.scenario, silent=self.config.silent
        )
        if self.config.price_check:
            good_prices = price_checker(instance)
            if not good_prices and not self.config.silent:
                print('Warning:  Cost anomalies discovered.  Check log file for details.')
        # tag the instance by name, so we can sort out the multiple results...
        instance.name = '-'.join((self.config.scenario, '0'))

        # 2. Base solve
        tic = datetime.now()
        #   ============ First Solve ============
        #  Note:  We *exclude* the worker_solver_options here to get a more precise base cost
        res: Results = self.opt.solve(instance)
        toc = datetime.now()
        elapsed = toc - tic
        self.solve_count += 1
        logger.info(f'Initial solve time: {elapsed.total_seconds():.4f}')
        status = res.solver.termination_condition
        logger.debug('Termination condition: %s', status.name)
        if not check_optimal_termination(res):
            logger.error('The baseline MGA solve failed.  Terminating run.')
            raise RuntimeError('Baseline MGA solve failed.  Terminating run.')

        # record the 0-solve in all tables
        self.writer.write_results(instance, iteration=0)
        self.writer.make_summary_flow_table()  # make the flow summary table, if it doesn't exist
        self.writer.write_summary_flow(instance, iteration=0)

        # 3a. Capture cost and make it a constraint
        tot_cost = pyo.value(instance.total_cost)
        logger.info('Completed initial solve with total cost:  %0.2f', tot_cost)
        logger.info('Relaxing cost by fraction:  %0.3f', self.cost_epsilon)
        # get hook on the expression generator for total cost...
        cost_expression = total_cost_rule(instance)
        instance.cost_cap = pyo.Constraint(
            expr=cost_expression <= (1 + self.cost_epsilon) * tot_cost
        )

        # 3b. remove the old objective and prep for iterative solving
        instance.del_component(instance.total_cost)

        # 4.  Instantiate the vector manager
        vector_manager: VectorManager = get_manager(
            axis=self.mga_axis,
            model=instance,
            weighting=self.mga_weighting,
            con=self.con,
            optimal_cost=tot_cost,
            cost_relaxation=self.cost_epsilon,
            config=self.config,
        )

        # 5.  Set up the Workers
        num_workers = self.num_workers
        work_queue = Queue(1)  # restrict the queue to hold just 1 models in it max
        result_queue = Queue(
            num_workers + 1
        )  # must be able to hold a shutdown signal from all workers at once!
        log_queue = Queue(50)
        # make workers
        workers = []
        kwargs = {
            'solver_name': self.config.solver_name,
            'solver_options': self.worker_solver_options,
        }
        # construct path for the solver logs
        s_path = self.config.output_path / 'solver_logs'
        if not s_path.exists():
            s_path.mkdir()
        for _ in range(num_workers):
            w = Worker(
                model_queue=work_queue,
                results_queue=result_queue,
                log_root_name=__name__,
                log_queue=log_queue,
                log_level=logging.INFO,
                solver_log_path=s_path,
                **kwargs,
            )
            w.start()
            workers.append(w)
        # workers now running and waiting for jobs...

        # 6.  Start the iterative solve process and let the manager run the show
        instance_generator = vector_manager.model_generator()
        instance = next(instance_generator)
        while not vector_manager.expired and not self.internal_stop:
            try:
                work_queue.put(instance, block=False)  # put a log on the fire, if room
                logger.info('Putting an instance in the work queue')
                instance = next(instance_generator)
            except queue.Full:
                # print('work queue is full')
                pass
            # see if there is a result ready to pick up, if not, pass
            try:
                next_result = result_queue.get_nowait()
            except Empty:
                next_result = None
                # print('no result')
            if next_result is not None:
                vector_manager.process_results(M=next_result)
                self.process_solve_results(next_result)
                logger.info('Solve count: %d', self.solve_count)
                self.solve_count += 1
                if self.verbose or not self.config.silent:
                    print(f'MGA Solve count: {self.solve_count}')
                if self.solve_count >= self.iteration_limit:
                    logger.info('Starting shutdown process based on MGA iteration limit')
                    self.internal_stop = True
            # pull anything from the logging queue and log it...
            while True:
                try:
                    record = log_queue.get_nowait()
                    process_logger = getLogger(record.name)
                    process_logger.handle(record)
                except Empty:
                    break
            time.sleep(0.1)  # prevent hyperactivity...

            # test for over time limit
            elapsed = datetime.now() - start_time
            if elapsed.total_seconds() / 3600 > self.time_limit_hrs:
                logger.info('Starting shutdown process based on MGA time limit')
                self.internal_stop = True

        # 7. Shut down the workers and then the logging queue
        if self.verbose:
            print('shutting it down')
        for _ in workers:
            if self.verbose:
                print('shutdown sent')
            work_queue.put('ZEBRA')  # shutdown signal

        # 7b.  Keep pulling results from the queue to empty it out
        empty = 0
        while True:
            try:
                next_result = result_queue.get_nowait()
                if next_result == 'COYOTE':  # shutdown signal
                    empty += 1
            except Empty:
                next_result = None
            if next_result is not None and next_result != 'COYOTE':
                logger.debug('bagged a result post-shutdown')
                vector_manager.process_results(M=next_result)
                self.process_solve_results(next_result)
                logger.info('Solve count: %d', self.solve_count)
                self.solve_count += 1
                if self.verbose or not self.config.silent:
                    print(f'MGA Solve count: {self.solve_count}')
            while True:
                try:
                    record = log_queue.get_nowait()
                    process_logger = getLogger(record.name)
                    process_logger.handle(record)
                except Empty:
                    break
            if empty == num_workers:
                break

        for w in workers:
            w.join()
            logger.debug('worker wrapped up...')

        log_queue.close()
        log_queue.join_thread()
        if self.verbose:
            print('log queue closed')
        work_queue.close()
        work_queue.join_thread()
        if self.verbose:
            print('work queue joined')
        result_queue.close()
        result_queue.join_thread()
        if self.verbose:
            print('result queue joined')

        # 8. Wrap it up
        vector_manager.finalize_tracker()

    def solve_instance(self, instance: TemoaModel) -> bool:
        tic = datetime.now()
        res = self.opt.solve(instance)
        toc = datetime.now()
        elapsed = toc - tic
        status = res['Solver'].termination_condition
        logger.info(
            'Solve #%d time: %0.4f.  Status: %s',
            self.solve_count,
            elapsed.total_seconds(),
            status.name,
        )
        return status == pyo.TerminationCondition.convergenceCriteriaSatisfied

    def process_solve_results(self, instance: TemoaModel):
        """write the results as required"""
        # get the instance number from the model name, if provided
        if '-' not in instance.name:
            raise ValueError(
                'Instance name does not appear to contain a -idx value.  The manager should be '
                'tagging/updating this'
            )
        idx = int(instance.name.split('-')[-1])
        if idx in self.seen_instance_indices:
            raise ValueError('Instance index already seen.  Likely coding error')
        self.seen_instance_indices.add(idx)
        self.writer.write_capacity_tables(model=instance, iteration=idx)
        self.writer.write_summary_flow(instance, iteration=idx)

    def __del__(self):
        self.con.close()
