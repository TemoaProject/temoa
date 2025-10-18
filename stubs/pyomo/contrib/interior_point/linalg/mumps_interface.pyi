import numpy as np
from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.contrib.pynumero.linalg.base import LinearSolverResults as LinearSolverResults
from pyomo.contrib.pynumero.linalg.base import LinearSolverStatus as LinearSolverStatus
from pyomo.contrib.pynumero.linalg.mumps_interface import (
    MumpsCentralizedAssembledLinearSolver as MumpsCentralizedAssembledLinearSolver,
)
from pyomo.contrib.pynumero.sparse import BlockVector as BlockVector

from .base_linear_solver_interface import IPLinearSolverInterface as IPLinearSolverInterface

mumps: Incomplete
mumps_available: Incomplete

class MumpsInterface(MumpsCentralizedAssembledLinearSolver, IPLinearSolverInterface):
    @classmethod
    def getLoggerName(cls): ...
    error_level: Incomplete
    log_error: Incomplete
    logger: Incomplete
    def __init__(self, par: int = 1, comm=None, cntl_options=None, icntl_options=None) -> None: ...
    def do_back_solve(
        self, rhs: np.ndarray | BlockVector, raise_on_error: bool = True
    ) -> tuple[np.ndarray | BlockVector | None, LinearSolverResults]: ...
    def get_inertia(self): ...
    def get_error_info(self): ...
    def log_header(self, include_error: bool = True, extra_fields=None) -> None: ...
    def log_info(self) -> None: ...
