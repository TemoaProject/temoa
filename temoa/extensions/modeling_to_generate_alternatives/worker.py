"""
Class to contain Workers that execute solves in separate processes
"""

import logging.handlers
from datetime import datetime
from logging import getLogger
from multiprocessing import Process, Queue
from pathlib import Path
from typing import TYPE_CHECKING

from pyomo.opt import SolverFactory, SolverResults, check_optimal_termination

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

verbose = False  # for T/S or monitoring...


class Worker(Process):
    worker_idx = 1

    def __init__(
        self,
        model_queue: Queue,
        results_queue: Queue,
        log_root_name: str,
        log_queue: Queue,
        log_level: int = logging.INFO,
        solver_name: str = 'appsi_highs',
        solver_options: dict | None = None,
        solver_log_path: Path | None = None,
    ):
        super().__init__(daemon=True)
        self.worker_number = Worker.worker_idx
        Worker.worker_idx += 1
        self.model_queue: Queue = model_queue
        self.results_queue: Queue = results_queue
        self.log_queue = log_queue
        self.solver_name = solver_name
        self.solver_options = solver_options or {}
        self.solver_log_path = solver_log_path
        self.opt = None # Initialize in run()

        self.log_root_name = log_root_name
        self.log_level = log_level
        self.solve_count = 0

    def run(self):
        logger = getLogger('.'.join((self.log_root_name, 'worker', str(self.worker_number))))
        logger.propagate = False  # prevent duplicate logs
        # add a handler that pushes to the queue
        handler = logging.handlers.QueueHandler(self.log_queue)
        logger.setLevel(self.log_level)
        logger.addHandler(handler)
        logger.info('Worker %d spun up', self.worker_number)

        # Initialize the solver here  in the child process to avoid pickling issues
        # Note: We do not set the options here because appsi_highs does not accept options in
        # __init__. We can set them later via self.opt.options
        self.opt = SolverFactory(self.solver_name)

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

            model: TemoaModel = self.model_queue.get()
            if model == 'ZEBRA':  # shutdown signal
                if verbose:
                    print(f'worker {self.worker_number} got shutdown signal')
                logger.info('Worker %d received shutdown signal', self.worker_number)
                self.results_queue.put('COYOTE')
                break
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
                    self.results_queue.put(model)
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
