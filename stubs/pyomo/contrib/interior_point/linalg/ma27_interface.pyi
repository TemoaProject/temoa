from pyomo.contrib.pynumero.linalg.base import LinearSolverResults as LinearSolverResults
from pyomo.contrib.pynumero.linalg.base import LinearSolverStatus as LinearSolverStatus
from pyomo.contrib.pynumero.linalg.ma27_interface import MA27 as MA27
from pyomo.contrib.pynumero.sparse import BlockMatrix as BlockMatrix
from pyomo.contrib.pynumero.sparse import BlockVector as BlockVector
from scipy.sparse import isspmatrix_coo as isspmatrix_coo
from scipy.sparse import spmatrix as spmatrix
from scipy.sparse import tril as tril

from .base_linear_solver_interface import IPLinearSolverInterface as IPLinearSolverInterface

class InteriorPointMA27Interface(MA27, IPLinearSolverInterface):
    @classmethod
    def getLoggerName(cls): ...
    def __init__(
        self, cntl_options=None, icntl_options=None, iw_factor: float = 1.2, a_factor: int = 2
    ) -> None: ...
    def do_symbolic_factorization(
        self, matrix: spmatrix | BlockMatrix, raise_on_error: bool = True
    ) -> LinearSolverResults: ...
    def do_numeric_factorization(
        self, matrix: spmatrix | BlockMatrix, raise_on_error: bool = True
    ) -> LinearSolverResults: ...
    def get_inertia(self): ...
