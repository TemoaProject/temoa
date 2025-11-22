"""
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


Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  6/2/24

This module contains the core "evaluation" function for Method Of Morris.  It needs to be isolated
(outside of class) to enable parallelization.
"""

import logging
import sqlite3
import sys
from logging.handlers import QueueHandler

from pyomo.dataportal import DataPortal

from temoa._internal import run_actions
from temoa._internal.table_writer import TableWriter
from temoa.core.config import TemoaConfig


def configure_worker_logger(log_queue, log_level):
    """configure the logger"""
    worker_logger = logging.getLogger('MM evaluate')
    if not worker_logger.hasHandlers():
        h = QueueHandler(log_queue)
        worker_logger.addHandler(h)
    root_logger = logging.root
    if not root_logger.hasHandlers():
        h = QueueHandler(log_queue)
        root_logger.addHandler(h)
    worker_logger.setLevel(log_level)
    root_logger.setLevel(logging.WARNING)
    return worker_logger


def evaluate(param_info, mm_sample, data, i, config: TemoaConfig, log_queue, log_level):
    """
    Run model for params provided and return objective value and emission value
    Note:  This function needs to be a static instance to enable the parallel
    processing, which requires parallelization of the parameters.  It cannot be
    a class or instance function, AFAIK
    :param param_info: The stack of parameter data to pull name/index from
    :param mm_sample: The values of the parameters to alter
    :param data: Data used to build the Data Portal
    :param i: indexing number
    :param config: The config file to pull run data from
    :return: list of objective value and CO2 emission value
    """
    # get the logger configured...
    logger = configure_worker_logger(log_queue, log_level)
    logger.info('Starting MM evaluation # %d', i + 1)
    log_entry = ['']
    for j in range(0, len(mm_sample)):
        param_name, *set_idx, _ = param_info[j]
        set_idx = tuple(set_idx)
        # tweak the parameter
        if data.get(param_name) is None:
            raise ValueError(f'Unrecognized parameter: {param_name}')
        if data[param_name].get(set_idx) is None:
            raise ValueError('index mismatch from data read-in')
        data[param_name][set_idx] = mm_sample[j]
        setting_entry = 'run # %d:  Setting param %s[%s] to value:  %f' % (
            i + 1,
            param_name,
            set_idx,
            mm_sample[j],
        )
        log_entry.append(setting_entry)
    logger.debug('\n  '.join(log_entry))

    dp = DataPortal(data_dict={None: data})
    instance = run_actions.build_instance(loaded_portal=dp, silent=True)
    mdl, res = run_actions.solve_instance(
        instance=instance, solver_name=config.solver_name, silent=True
    )
    status = run_actions.check_solve_status(res)
    if not status:
        raise RuntimeError('Bad solve during Method of Morris')
    table_writer = TableWriter(config)
    table_writer.write_mm_results(model=mdl, iteration=i)
    con = sqlite3.connect(config.input_database)
    cur = con.cursor()
    scenario_name = config.scenario + f'-{i}'
    cur.execute(
        'SELECT total_system_cost FROM output_objective where scenario = ?', (scenario_name,)
    )
    output_query = cur.fetchall()
    if len(output_query) > 1:
        raise RuntimeError(
            'Multiple outputs found in Objective table matching scenario name.  Coding error.'
        )
    else:
        Y_OF = output_query[0][0]
    cur.execute(
        "SELECT SUM(emission) FROM output_emission WHERE emis_comm='co2' AND scenario=?",
        (scenario_name,),
    )
    output_query = cur.fetchall()
    if len(output_query) == 0:
        Y_CumulativeCO2 = 0.0
    elif len(output_query) > 1:
        raise RuntimeError(
            'Multiple outputs found in output_emissions table matching scenario name.  Coding '
            'error.'
        )
    else:
        Y_CumulativeCO2 = output_query[0][0]
    morris_objectives = [float(Y_OF), float(Y_CumulativeCO2)]
    logger.info('Finished MM evaluation # %d with OBJ value: %0.2f ', i + 1, Y_OF)
    if not config.silent:
        sys.stdout.write(f'Completed MM run {i + 1}\n')
        sys.stdout.flush()
    return morris_objectives
