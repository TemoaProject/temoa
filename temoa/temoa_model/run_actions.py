"""
Basic-level atomic functions that can be used by a sequencer, as needed

Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  11/15/23

Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.
"""

import sqlite3
import sys
from logging import getLogger
from pathlib import Path
from sys import stderr as SE, version_info
from time import time
from typing import Tuple

from pyomo.environ import (
    DataPortal,
    Suffix,
    Var,
    Constraint,
    value,
    UnknownSolver,
    SolverFactory,
    check_optimal_termination,
)
from pyomo.opt import SolverResults

from temoa.data_processing.DB_to_Excel import make_excel
from temoa.temoa_model.table_writer import TableWriter
from temoa.temoa_model.temoa_config import TemoaConfig
from temoa.temoa_model.temoa_model import TemoaModel

logger = getLogger(__name__)


def check_python_version(min_major, min_minor) -> bool:
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


def check_database_version(config: TemoaConfig, db_major_reqd: int, min_db_minor) -> bool:
    """
    check the db version
    :param config: TemoaConfig instance
    :param db_major_reqd: the required major version (equality test)
    :param min_db_minor: the required minimum minor version (GTE test)
    :return: T/F
    """
    input_conn, input_path = sqlite3.connect(config.input_database), config.input_database
    if config.input_database == config.output_database:
        output_conn = None
    else:
        output_conn = sqlite3.connect(config.output_database)
    cons = [
        (input_conn, input_path),
    ]
    if output_conn is not None:
        cons.append((output_conn, config.output_database))
    # check for correct version
    all_good = True

    for con, name in cons:
        try:
            db_major = con.execute(
                "SELECT value from MetaData where element = 'DB_MAJOR'"
            ).fetchone()
            db_minor = con.execute(
                "SELECT value from MetaData where element = 'DB_MINOR'"
            ).fetchone()
            db_major = db_major[0] if db_major else -1
            db_minor = db_minor[0] if db_minor else -1
        except sqlite3.OperationalError:
            logger.error(
                'Database does not appear to have MetaData table with required versioning info.  See schema for v3+.'
            )
            SE.write(
                'Database does not appear to have MetaData table with required.  Is this version 3+ compatible?\n'
                'If required, see dox on using the database migrator to move to v3.'
            )
            db_major, db_minor = -1, -1
        finally:
            con.close()

        good_version = db_major == db_major_reqd and db_minor >= min_db_minor
        if not good_version:
            logger.error(
                'Database %s version %d.%d does not match the major version %d and have at least minor version %d',
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
    model_name=None,
    silent=False,
    keep_lp_file=False,
    lp_path: Path = None,
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

    hack = time()
    if not silent:
        SE.write('[        ] Creating model instance.')
        SE.flush()
    logger.info('Started creating model instance from data')
    instance = model.create_instance(loaded_portal, name=model_name)
    if not silent:
        SE.write('\r[%8.2f] Instance created.\n' % (time() - hack))
        SE.flush()
    logger.info('Finished creating model instance from data')

    # save LP if requested
    if keep_lp_file:
        save_lp(instance, lp_path)

    # gather some stats...
    c_count = 0
    v_count = 0
    for constraint in instance.component_objects(ctype=Constraint):
        c_count += len(constraint)
    for var in instance.component_objects(ctype=Var):
        v_count += len(var)
    logger.info('model built...  Variables: %d, Constraints: %d', v_count, c_count)
    return instance


def save_lp(instance: TemoaModel, lp_path: Path) -> None:
    """
    quick utility to save the LP file to disc.
    Note:  if saving multiple LP's they need to be differentiated by path
    """
    if not lp_path:
        logger.warning('Requested "keep LP file", but no path is provided...skipped')
    else:
        if not Path.is_dir(lp_path):
            Path.mkdir(lp_path)
        filename = lp_path / 'model.lp'
        instance.write(filename, format='lp', io_options={'symbolic_solver_labels': True})


def solve_instance(
    instance: TemoaModel, solver_name, silent: bool = False, solver_suffixes=None
) -> Tuple[TemoaModel, SolverResults]:
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

    hack = time()
    if not silent:
        SE.write('[        ] Solving.')
        SE.flush()

    logger.info(
        'Starting the solve process using %s solver on model %s', solver_name, instance.name
    )
    if solver_name == 'neos':
        raise NotImplementedError('Neos based solve is not currently supported')

    else:
        if solver_name == 'cbc':
            pass
            # dev note:  I think these options are outdated.  Getting decent results without them...
            #            preserved for now.
            # Solver options. Reference:
            # https://genxproject.github.io/GenX/dev/solver_configuration/
            # optimizer.options["dualTolerance"] = 1e-6
            # optimizer.options["primalTolerance"] = 1e-6
            # optimizer.options["zeroTolerance"] = 1e-12
            # optimizer.options["crossover"] = 'off'

        elif solver_name == 'cplex':
            # Note: these parameter values are taken to be the same as those in PyPSA
            # (see: https://pypsa-eur.readthedocs.io/en/latest/configuration.html)
            optimizer.options['lpmethod'] = 4  # barrier
            optimizer.options['solutiontype'] = 2  # non basic solution, ie no crossover
            optimizer.options['barrier convergetol'] = 1.0e-5
            optimizer.options['feasopt tolerance'] = 1.0e-6

        elif solver_name == 'gurobi':
            # Note: these parameter values are taken to be the same as those in PyPSA (see: https://pypsa-eur.readthedocs.io/en/latest/configuration.html)
            optimizer.options["Method"] = 2 # barrier
            optimizer.options["Crossover"] = 0 # non basic solution, ie no crossover
            optimizer.options["BarConvTol"] = 1.e-5
            optimizer.options["FeasibilityTol"] = 1.e-6

        elif solver_name == 'appsi_highs':
            pass

        # dev note:  The handling of suffixes is pretty weak.  As of today 4/4/2024, highspy crashes if
        #            the keyword suffixes is passed in (regardless if there are any requested).  CBC only
        #            supports some.  Perhaps in the future, this will be easier.  For now, we need a different
        #            solve command for highspy and no suffixes because it works so well.
        if solver_suffixes:
            solver_suffixes = set(solver_suffixes)
            legit_suffixes = {'dual', 'slack', 'rc'}
            bad_apples = solver_suffixes - legit_suffixes
            solver_suffixes &= legit_suffixes
            if bad_apples:
                logger.warning(
                    'Solver suffix %s is not in pyomo standards (see pyomo dox).  Removed',
                    bad_apples,
                )
            # convert back to list...
            solver_suffixes = list(solver_suffixes)
        else:
            solver_suffixes = []
        result: SolverResults | None = None
        try:
            # currently, the highs solver call will puke if the suffixes are passed, so we need to
            # differentiate...
            if solver_name == 'appsi_highs':
                result = optimizer.solve(instance)
            else:
                result = optimizer.solve(instance, suffixes=solver_suffixes)
        except RuntimeError as error:
            logger.error('Solver failed to solve and returned an error: %s', error)
            logger.error(
                'This may be due to asking for suffixes (duals) for an incompatible solver.  '
                "Try de-selecting 'save_duals' in the config.  (see note in run_actions.py code)"
            )
            if result:
                logger.error(
                    'Solver reported termination condition (if any): %s', result['Solution'].Status
                )
            SE.write('solver failure.  See log file.')
            sys.exit(-1)

        if check_optimal_termination(result):
            if solver_suffixes:
                instance.solutions.store_to(
                    result
                )  # this is needed to capture the duals/suffixes from the Solutions obj

        logger.info('Solve process complete')
        logger.debug('Solver results: \n %s', result.solver)

    if not silent:
        SE.write('\r[%8.2f] Model solved.\n' % (time() - hack))
        SE.flush()

    return instance, result


def check_solve_status(result: SolverResults) -> tuple[bool, str]:
    """
    Check the status of the solve.
    :param result: the results object returned by the solver
    :return: tuple of status boolean (True='optimal', others False), and string message if not optimal
    """
    soln = result['Solution']

    lesser_responses = ('feasible', 'globallyOptimal', 'locallyOptimal')
    logger.info('The solver reported status as: %s', soln.Status)
    if check_optimal_termination(results=result):
        return True, ''
    else:
        return False, f'{soln.Status} was returned from solve'


def handle_results(
    instance: TemoaModel, results, config: TemoaConfig, append=False, iteration=None
):
    hack = time()
    if not config.silent:
        msg = '[        ] Calculating reporting variables and formatting results.'
        # yield 'Calculating reporting variables and formatting results.'
        SE.write(msg)
        SE.flush()

    table_writer = TableWriter(config=config)
    if config.save_duals:
        table_writer.write_results(
            M=instance, results_with_duals=results, append=append, iteration=iteration
        )
    else:
        table_writer.write_results(M=instance, append=append, iteration=iteration)

    if not config.silent:
        SE.write(
            '\r[%8.2f] Results processed.                                    \n' % (time() - hack)
        )
        SE.flush()

    if config.save_excel:
        scenario_name = (
            config.scenario + f'-{iteration}' if iteration is not None else config.scenario
        )
        temp_scenario = set()
        temp_scenario.add(scenario_name)
        excel_filename = config.output_path / scenario_name
        make_excel(str(config.output_database), excel_filename, temp_scenario)

    # normal (non-MGA) run will have a TotalCost as the OBJ:
    if hasattr(instance, 'TotalCost'):
        logger.info('TotalCost value: %0.2f', value(instance.TotalCost))
    return
