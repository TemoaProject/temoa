from _typeshed import Incomplete
from pyomo.contrib.pynumero.linalg.base import LinearSolverResults as LinearSolverResults
from pyomo.contrib.pynumero.linalg.scipy_interface import ScipyLU as ScipyLU
from pyomo.contrib.pynumero.sparse import BlockMatrix as BlockMatrix
from scipy.sparse import spmatrix as spmatrix

from .base_linear_solver_interface import IPLinearSolverInterface as IPLinearSolverInterface

class ScipyInterface(ScipyLU, IPLinearSolverInterface):
    @classmethod
    def getLoggerName(cls): ...
    compute_inertia: Incomplete
    logger: Incomplete
    def __init__(self, compute_inertia: bool = False) -> None: ...
    def do_numeric_factorization(
        self, matrix: spmatrix | BlockMatrix, raise_on_error: bool = True
    ) -> LinearSolverResults: ...
    def get_inertia(self): ...
