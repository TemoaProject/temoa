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
Created on:  5/5/24

Class to contain Workers that execute solves in separate processes

dev note:
This class is derived from the original Worker class in MGA extension, but is just different enough
that it is a separate class.  In future, it may make sense to re-combine these.  RN, this worker will
ingest DataPortal objects to make new models.  The MGA will (in future) likely just take in new obj functions

"""
import logging.handlers
from datetime import datetime
from logging import getLogger
from multiprocessing import Process, Queue
from pathlib import Path

from pyomo.dataportal import DataPortal
from pyomo.opt import SolverFactory, SolverResults, check_optimal_termination

from temoa.temoa_model.data_brick import DataBrick, data_brick_factory
from temoa.temoa_model.temoa_model import TemoaModel

verbose = False  # for T/S or monitoring...


class MCWorker(Process):
    worker_idx = 1

    def __init__(
        self,
        dp_queue: Queue,
        results_queue: Queue,
        log_root_name,
        log_queue,
        log_level,
        solver_log_path: Path | None = None,
        **kwargs,
    ):
        super(MCWorker, self).__init__(daemon=True)
        self.worker_number = MCWorker.worker_idx
        MCWorker.worker_idx += 1
        self.dp_queue: Queue[DataPortal | str] = dp_queue
        self.results_queue: Queue[DataBrick | str] = results_queue
        self.solver_name = kwargs['solver_name']
        self.solver_options = kwargs['solver_options']
        self.opt = SolverFactory(self.solver_name, options=self.solver_options)
        self.log_queue = log_queue
        self.log_level = log_level
        self.root_logger_name = log_root_name
        self.solver_log_path = solver_log_path
        self.solve_count = 0

    def run(self):
        logger = getLogger('.'.join((self.root_logger_name, 'worker', str(self.worker_number))))
        logger.setLevel(self.log_level)
        logger.propagate = (
            False  # not propagating up the chain fixes issue on TRACE where we were getting dupes.
        )
        handler = logging.handlers.QueueHandler(self.log_queue)
        logger.addHandler(handler)
        logger.info('Worker %d spun up', self.worker_number)

        # update the solver options to pass in a log location
        while True:
            if self.solver_log_path:
                # add the solver log path to options, if one is provided
                log_location = Path(
                    self.solver_log_path,
                    f'solver_log_{str(self.worker_number)}_{self.solve_count}.log',
                )
                log_location = str(log_location)
                match self.solver_name:
                    case 'gurobi':
                        self.solver_options.update({'LogFile': log_location})
                    # case 'appsi_highs':
                    #     self.solver_options.update({'log_file': log_location})
                    case _:
                        pass

            self.opt.options = self.solver_options

            # wait for a DataPortal object to show up, then get to work
            tic = datetime.now()
            data = self.dp_queue.get()
            toc = datetime.now()
            logger.debug(
                'Worker %d waited for and pulled a DataPortal from work queue in %0.2f seconds',
                self.worker_number,
                (toc - tic).total_seconds(),
            )
            if data == 'ZEBRA':  # shutdown signal
                if verbose:
                    print(f'worker {self.worker_number} got shutdown signal')
                logger.debug('Worker %d received shutdown signal', self.worker_number)
                self.results_queue.put('COYOTE')
                break
            name, dp = data
            abstract_model = TemoaModel()
            model: TemoaModel = abstract_model.create_instance(data=dp)
            model.name = name  # set the name from the input
            tic = datetime.now()
            try:
                self.solve_count += 1
                res: SolverResults | None = self.opt.solve(model)

            except Exception as e:
                if verbose:
                    print('bad solve')
                logger.warning(
                    'Worker %d failed to solve model: %s... skipping.  Exception: %s',
                    self.worker_number,
                    model.name,
                    e,
                )
                res = None
            toc = datetime.now()

            # guard against a bad "res" object...
            try:
                good_solve = check_optimal_termination(res)
                if good_solve:
                    data_brick = data_brick_factory(model)
                    self.results_queue.put(data_brick)
                    logger.info(
                        'Worker %d solved a model in %0.2f minutes',
                        self.worker_number,
                        (toc - tic).total_seconds() / 60,
                    )
                    if verbose:
                        print(f'Worker {self.worker_number} completed a successful solve')
                else:
                    status = res['Solver'].termination_condition
                    logger.info(
                        'Worker %d did not solve.  Results status: %s', self.worker_number, status
                    )
            except AttributeError:
                pass
        logger.info('Worker %d finished', self.worker_number)
