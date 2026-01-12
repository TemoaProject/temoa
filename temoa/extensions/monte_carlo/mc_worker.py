"""

Class to contain Workers that execute solves in separate processes

dev note:
This class is derived from the original Worker class in MGA extension, but is just different enough
that it is a separate class.  In future, it may make sense to re-combine these.  RN, this worker
will ingest DataPortal objects to make new models.  The MGA will (in future) likely just take in
new obj functions

"""
from __future__ import annotations

import logging.handlers
from datetime import datetime
from logging import getLogger
from typing import TYPE_CHECKING, Any

from pyomo.opt import SolverFactory, SolverResults, check_optimal_termination

from temoa._internal.data_brick import DataBrick, data_brick_factory
from temoa.core.model import TemoaModel

verbose = False  # for T/S or monitoring...

if TYPE_CHECKING:
    from multiprocessing import Queue
    from pathlib import Path


class MCWorker:
    worker_idx = 1

    worker_number: int
    dp_queue: Queue[Any]
    results_queue: Queue[DataBrick | str]
    solver_name: str
    solver_options: dict[str, Any]
    opt: Any
    log_queue: Queue[logging.LogRecord]
    log_level: int
    root_logger_name: str
    solver_log_path: Path | None
    solve_count: int

    def __init__(
        self,
        dp_queue: Queue[Any],
        results_queue: Queue[DataBrick | str],
        log_root_name: str,
        log_queue: Queue[logging.LogRecord],
        log_level: int = logging.INFO,
        solver_log_path: Path | None = None,
        **kwargs: Any,
    ):
        self.worker_number = MCWorker.worker_idx
        MCWorker.worker_idx += 1
        self.dp_queue = dp_queue
        self.results_queue = results_queue
        self.solver_name = kwargs['solver_name']
        self.solver_options = kwargs['solver_options']
        self.opt = None # Initialize in run()
        self.log_queue = log_queue
        self.log_level = log_level
        self.root_logger_name = log_root_name
        self.solver_log_path = solver_log_path
        self.solve_count = 0

    def run(self) -> None:
        msg = '.'.join((self.root_logger_name, 'worker', str(self.worker_number)))
        logger: logging.Logger = getLogger(msg)
        logger.setLevel(self.log_level)
        logger.propagate = (
            False  # not propagating up the chain fixes issue on TRACE where we were getting dupes.
        )
        handler = logging.handlers.QueueHandler(self.log_queue)
        logger.addHandler(handler)
        logger.info('Worker %d spun up', self.worker_number)

        # Initialize the solver here in the child process to avoid pickling issues
        # Note: We do not set the options here because appsi_highs does not accept options in
        # __init__. We can set them later via self.opt.options
        self.opt = SolverFactory(self.solver_name)

        while True:
            # wait for a DataPortal object to show up, then get to work
            tic = datetime.now()
            data = self.dp_queue.get()
            toc = datetime.now()

            # log data pull
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

            # update the solver options
            self.opt.options = self.solver_options
            if self.solver_name.startswith('appsi_'):
                for k, v in self.solver_options.items():
                    try:
                        setattr(self.opt.config, k, v)
                    except (ValueError, AttributeError):
                        # Key not defined in ConfigDict, skip it
                        pass

                # Handle solver log path for appsi
                if self.solver_log_path:
                    log_location = (
                        self.solver_log_path
                        / f'solver_log_{self.worker_number}_{self.solve_count}.log'
                    )
                    try:
                        self.opt.config.log_file = str(log_location)
                    except (ValueError, AttributeError):
                        pass

            abstract_model = TemoaModel()
            model: TemoaModel = abstract_model.create_instance(data=dp)
            model.name = name  # set the name from the input
            tic = datetime.now()
            try:
                self.solve_count += 1
                solve_res: SolverResults | None
                if self.solver_name.startswith('appsi_'):
                    # For appsi, we can set tee on the config
                    try:
                        self.opt.config.tee = True
                    except (ValueError, AttributeError):
                        pass
                    solve_res = self.opt.solve(model)
                else:
                    solve_res = self.opt.solve(model, tee=True)

            except Exception as e:
                if verbose:
                    print('bad solve')
                logger.warning(
                    'Worker %d failed to solve model: %s... skipping.  Exception: %s',
                    self.worker_number,
                    model.name,
                    e,
                )
                # Try to get more info if it's a known solver error
                if hasattr(self.opt, 'results') and self.opt.results:
                    logger.warning(
                        'Solver results status: %s', self.opt.results.solver.termination_condition
                    )
                solve_res = None
            toc = datetime.now()

            # guard against a bad "res" object...
            try:
                good_solve = check_optimal_termination(solve_res)
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
                    if solve_res is not None:
                        status = solve_res['Solver'].termination_condition
                        logger.info(
                            'Worker %d did not solve.  Results status: %s',
                            self.worker_number,
                            status,
                        )
            except AttributeError:
                pass
        logger.info('Worker %d finished', self.worker_number)
