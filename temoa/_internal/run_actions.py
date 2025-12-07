"""
Basic-level atomic functions that can be used by a sequencer, as needed
"""

import sqlite3
from collections.abc import Generator, Iterable
from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from sys import version_info
from time import perf_counter

from pyomo.environ import (
    Constraint,
    DataPortal,
    SolverFactory,
    Suffix,
    UnknownSolver,
    Var,
    check_optimal_termination,
    value,
)
from pyomo.opt import SolverResults

from temoa._internal.table_writer import TableWriter
from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel
from temoa.data_processing.db_to_excel import make_excel

logger = getLogger(__name__)


@contextmanager
def task_timer(action_name: str, *, silent: bool = False) -> Generator[None, None, None]:
    """
    Context manager to time blocks of code using the standard logger.
    """
    if not silent:
        logger.info('Started: %s', action_name)

    start_time = perf_counter()

    try:
        yield
    finally:
        duration = perf_counter() - start_time
        if not silent:
            # sample output: [10:30:35] INFO Finished: Creating model instance (Time taken: 0.07s)
            logger.info('Finished: %s (Time taken: %.2fs)', action_name, duration)


def check_python_version(min_major: int, min_minor: int) -> bool:
    if (min_major, min_minor) >= version_info:
        logger.error(
            'Model is being run with python %d.%d.  Expecting version %d.%d or later.  ',
            version_info.major,
            version_info.minor,
            min_major,
            min_minor,
        )
        return False
    return True


def check_database_version(config: TemoaConfig, db_major_reqd: int, min_db_minor: int) -> bool:
    """
    check the db version
    :param config: TemoaConfig instance
    :param db_major_reqd: the required major version (equality test)
    :param min_db_minor: the required minimum minor version (GTE test)
    :return: T/F
    """
    db_paths = [config.input_database]
    if config.input_database != config.output_database:
        db_paths.append(config.output_database)

    # check for correct version
    all_good = True

    for name in db_paths:
        con = sqlite3.connect(name)
        try:
            db_major_row = con.execute(
                "SELECT value from metadata where element = 'DB_MAJOR'"
            ).fetchone()
            db_minor_row = con.execute(
                "SELECT value from metadata where element = 'DB_MINOR'"
            ).fetchone()
            db_major = int(db_major_row[0]) if db_major_row else -1
            db_minor = int(db_minor_row[0]) if db_minor_row else -1
        except sqlite3.OperationalError:
            logger.error(
                'Database %s does not appear to have metadata table. Is this v%d.%d+ compatible?'
                'If required, see docs on using the database migrator to move to v%d.%d.',
                str(name),
                db_major_reqd,
                min_db_minor,
                db_major_reqd,
                min_db_minor,
            )
            db_major, db_minor = -1, -1
        finally:
            con.close()

        good_version = db_major == db_major_reqd and db_minor >= min_db_minor
        if not good_version:
            logger.error(
                'Database %s version %d.%d does not match the major version %d and have '
                'at least minor version %d',
                str(name),
                db_major,
                db_minor,
                db_major_reqd,
                min_db_minor,
            )
        all_good &= good_version

    return all_good


def build_instance(
    loaded_portal: DataPortal,
    model_name: str | None = None,
    silent: bool = False,
    keep_lp_file: bool = False,
    lp_path: Path | None = None,
) -> TemoaModel:
    """
    Build a Temoa Instance from data
    :param lp_path: the path to save the LP file to
    :param keep_lp_file: True to keep the LP file
    :param loaded_portal: a DataPortal instance
    :param silent: Run silently
    :param model_name: Optional name for this instance
    :return: a built TemoaModel
    """
    model = TemoaModel()

    model.dual = Suffix(direction=Suffix.IMPORT)
    # self.model.rc = Suffix(direction=Suffix.IMPORT)
    # self.model.slack = Suffix(direction=Suffix.IMPORT)

    with task_timer('Creating model instance', silent=silent):
        instance = model.create_instance(loaded_portal, name=model_name)

    # save LP if requested
    if keep_lp_file and lp_path is not None:
        save_lp(instance, lp_path)

    # gather some stats...
    c_count = sum(len(c) for c in instance.component_objects(ctype=Constraint))
    v_count = sum(len(v) for v in instance.component_objects(ctype=Var))

    logger.info('Model built... Variables: %d, Constraints: %d', v_count, c_count)
    return instance


def save_lp(instance: TemoaModel, lp_path: Path) -> None:
    """
    quick utility to save the LP file to disc.
    Note:  if saving multiple LP's they need to be differentiated by path
    """
    if not lp_path:
        logger.warning('Requested "keep LP file", but no path is provided...skipped')
    else:
        lp_path.mkdir(parents=True, exist_ok=True)
        filename = lp_path / 'model.lp'
        instance.write(str(filename), format='lp', io_options={'symbolic_solver_labels': True})


def solve_instance(
    instance: TemoaModel,
    solver_name: str,
    silent: bool = False,
    solver_suffixes: Iterable[str] | None = None,
) -> tuple[TemoaModel, SolverResults]:
    """
    Solve the instance and return a loaded instance
    :param solver_suffixes: iterable of string names for suffixes.  See pyomo dox.  right now, only
    'duals' is supported in the Temoa Framework.  Some solvers may not support duals.
    :param silent: Run silently
    :param solver_name: The name of the solver to request from the SolverFactory
    :param instance: the instance to solve
    :return: loaded instance
    """

    # QA the solver name and get a handle on solver
    if not solver_name:
        logger.error('No solver specified in solve sequence')
        raise TypeError('Error occurred during solve, see log')

    optimizer = SolverFactory(solver_name)
    if isinstance(optimizer, UnknownSolver):
        logger.error(
            'Failed to create a solver instance for name: %s.  Check name and availability on '
            'this system',
            solver_name,
        )
        raise TypeError('Failed to make Solver instance.  See log.')

    if solver_name == 'neos':
        raise NotImplementedError('Neos based solve is not currently supported')

    # Solver Configuration
    if solver_name == 'cbc':
        pass

    elif solver_name == 'cplex':
        # Note: these parameter values are taken to be the same as those in PyPSA
        # (see: https://pypsa-eur.readthedocs.io/en/latest/configuration.html)
        optimizer.options['lpmethod'] = 4  # barrier
        optimizer.options['solutiontype'] = 2  # non basic solution, ie no crossover
        optimizer.options['barrier convergetol'] = 1.0e-5
        optimizer.options['feasopt tolerance'] = 1.0e-6

    elif solver_name == 'gurobi':
        # Note: these parameter values are taken to be the same as those in PyPSA (see: https://pypsa-eur.readthedocs.io/en/latest/configuration.html)
        optimizer.options['Method'] = 2  # barrier
        optimizer.options['Crossover'] = 0  # non basic solution, ie no crossover
        optimizer.options['BarConvTol'] = 1.0e-5
        optimizer.options['FeasibilityTol'] = 1.0e-6
        # optimizer.options["BarOrder"] = 0 # if solve times seem unusually long, try 0 or 1

    elif solver_name == 'appsi_highs':
        pass

    # Suffix Handling
    solver_suffixes_list: list[str] = []
    if solver_suffixes:
        solver_suffixes_set = set(solver_suffixes)
        legit_suffixes = {'dual', 'slack', 'rc'}
        bad_apples = solver_suffixes_set - legit_suffixes
        solver_suffixes_set &= legit_suffixes
        if bad_apples:
            logger.warning(
                'Solver suffix %s is not in pyomo standards (see pyomo dox).  Removed',
                bad_apples,
            )
        solver_suffixes_list = list(solver_suffixes_set)

    result: SolverResults | None = None

    with task_timer(f'Solving model {instance.name}', silent=silent):
        try:
            # currently, the highs solver call will puke if the suffixes are passed
            if solver_name == 'appsi_highs':
                result = optimizer.solve(instance)
            else:
                result = optimizer.solve(instance, suffixes=solver_suffixes_list)
        except RuntimeError as error:
            logger.exception('Solver failed to solve and returned an error: %s', error)
            logger.error(
                'This may be due to asking for suffixes (duals) for an incompatible solver.  '
                "Try de-selecting 'save_duals' in the config.  (see note in run_actions.py code)"
            )
            if result:
                try:
                    _ok, status_msg = check_solve_status(result)
                except Exception:
                    status_msg = '<unable to extract status>'
                logger.error(
                    'Solver reported termination/status (if any): %s',
                    status_msg,
                )
            raise RuntimeError('Solver failure. See log file.') from error

    if check_optimal_termination(result):
        if solver_suffixes_list:
            # Needed to capture the duals/suffixes from the Solutions obj
            instance.solutions.store_to(result)

    logger.debug('Solver results: \n %s', result.solver)

    return instance, result


def check_solve_status(result: SolverResults) -> tuple[bool, str]:
    """
    Check the status of the solve in a solver-agnostic way.
    Handles both legacy solver results and APPSI solver results.

    :param result: the results object returned by the solver
    :return: tuple of status boolean (True='optimal', others False), and string message if not
             optimal
    """
    # Use check_optimal_termination for solver-agnostic checking
    is_optimal = check_optimal_termination(result)

    # Safely extract termination condition for logging
    termination_condition = 'unknown'
    if hasattr(result, 'solver') and hasattr(result.solver, 'termination_condition'):
        termination_condition = result.solver.termination_condition
    elif hasattr(result, 'termination_condition'):
        # Some APPSI solvers expose this directly
        termination_condition = result.termination_condition

    logger.info(
        'Solver termination condition: %s (optimal: %s)',
        termination_condition,
        is_optimal,
    )

    if is_optimal:
        return True, ''

    # Safely extract status for error message
    status_msg = 'unknown status'

    # Try legacy solver result format first
    if hasattr(result, '__getitem__'):
        try:
            soln = result.get('Solution') if hasattr(result, 'get') else result['Solution']
            if soln and hasattr(soln, 'Status'):
                status_msg = str(soln.Status)
        except (KeyError, TypeError, AttributeError):
            pass

    # Try APPSI result format
    if status_msg == 'unknown status':
        for attr in ['status', 'problem_status', 'solver_status']:
            if hasattr(result, attr):
                status_msg = str(getattr(result, attr))
                break

    # Final fallback
    if status_msg == 'unknown status':
        status_msg = str(result) if result else 'no solution returned'

    return False, f'{status_msg} was returned from solve'


def handle_results(
    instance: TemoaModel,
    results: SolverResults,
    config: TemoaConfig,
    append: bool = False,
    iteration: int | None = None,
) -> None:
    with task_timer('Processing results', silent=config.silent):
        table_writer = TableWriter(config=config)
        table_writer.write_results(
            model=instance,
            results_with_duals=results if config.save_duals else None,
            save_storage_levels=config.save_storage_levels,
            append=append,
            iteration=iteration,
        )

    if config.save_excel:
        scenario_name = (
            f'{config.scenario}-{iteration}' if iteration is not None else config.scenario
        )
        temp_scenario = {scenario_name}
        excel_filename = config.output_path / scenario_name
        make_excel(str(config.output_database), excel_filename, temp_scenario)

    # normal (non-MGA) run will have a total_cost as the OBJ:
    if hasattr(instance, 'total_cost'):
        logger.info('Total Cost value: %0.2f', value(instance.total_cost))

    if config.graphviz_output:
        try:
            from temoa.utilities.graphviz_generator import GraphvizDiagramGenerator

            logger.info('Generating Graphviz plots...')
            # Determine output directory (same as other outputs)
            out_dir = str(config.output_path)

            # Initialize generator
            graph_gen = GraphvizDiagramGenerator(
                db_file=str(config.output_database),
                scenario=config.scenario,
                out_dir=out_dir,
                verbose=0,  # Less verbose for integrated run
            )
            graph_gen.connect()

            try:
                # Get periods from the model instance
                periods = sorted(instance.time_optimize)

                for period in periods:
                    # Generate main results diagram for the period
                    # We pass None for region to generate for all/default
                    graph_gen.create_main_results_diagram(period=period, region=None)
            except Exception as e:
                logger.error('Failed to generate Graphviz plots: %s', e, exc_info=True)
            finally:
                graph_gen.close()
            logger.info('Graphviz plots generated in %s', graph_gen.out_dir)

        except Exception as e:
            logger.error('Failed to generate Graphviz plots: %s', e, exc_info=True)
