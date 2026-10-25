import types

from _typeshed import Incomplete
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.contrib.pyros.config import logger_domain as logger_domain
from pyomo.contrib.pyros.config import pyros_config as pyros_config
from pyomo.contrib.pyros.pyros_algorithm_methods import (
    ROSolver_iterative_solve as ROSolver_iterative_solve,
)
from pyomo.contrib.pyros.solve_data import ROSolveResults as ROSolveResults
from pyomo.contrib.pyros.util import IterationLogRecord as IterationLogRecord
from pyomo.contrib.pyros.util import ModelData as ModelData
from pyomo.contrib.pyros.util import TimingData as TimingData
from pyomo.contrib.pyros.util import load_final_solution as load_final_solution
from pyomo.contrib.pyros.util import log_model_statistics as log_model_statistics
from pyomo.contrib.pyros.util import pyrosTerminationCondition as pyrosTerminationCondition
from pyomo.contrib.pyros.util import setup_pyros_logger as setup_pyros_logger
from pyomo.contrib.pyros.util import time_code as time_code
from pyomo.contrib.pyros.util import validate_pyros_inputs as validate_pyros_inputs
from pyomo.core.expr import value as value
from pyomo.opt import SolverFactory as SolverFactory

__version__: str
default_pyros_solver_logger: Incomplete

class PyROS:
    CONFIG: Incomplete
    def available(self, exception_flag: bool = True): ...
    def version(self): ...
    def license_is_valid(self): ...
    def __enter__(self): ...
    def __exit__(
        self,
        et: type[BaseException] | None,
        ev: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None: ...
    def solve(
        self,
        model,
        first_stage_variables,
        second_stage_variables,
        uncertain_params,
        uncertainty_set,
        local_solver,
        global_solver,
        **kwds,
    ): ...
