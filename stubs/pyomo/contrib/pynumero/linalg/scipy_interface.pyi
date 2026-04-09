from typing import Callable

import numpy as np
from _typeshed import Incomplete
from pyomo.contrib.pynumero.sparse import BlockMatrix as BlockMatrix
from pyomo.contrib.pynumero.sparse import BlockVector as BlockVector
from scipy.linalg import eigvals as eigvals
from scipy.sparse import spmatrix as spmatrix
from scipy.sparse.linalg import LinearOperator

from .base import DirectLinearSolverInterface as DirectLinearSolverInterface
from .base import LinearSolverInterface as LinearSolverInterface
from .base import LinearSolverResults as LinearSolverResults
from .base import LinearSolverStatus as LinearSolverStatus

class ScipyLU(DirectLinearSolverInterface):
    def __init__(self) -> None: ...
    def do_symbolic_factorization(
        self, matrix: spmatrix | BlockMatrix, raise_on_error: bool = True
    ) -> LinearSolverResults: ...
    def do_numeric_factorization(
        self, matrix: spmatrix | BlockMatrix, raise_on_error: bool = True
    ) -> LinearSolverResults: ...
    def do_back_solve(
        self, rhs: np.ndarray | BlockVector, raise_on_error: bool = True
    ) -> tuple[np.ndarray | BlockVector | None, LinearSolverResults]: ...

class _LinearOperator(LinearOperator):
    def __init__(self, matrix: spmatrix | BlockMatrix) -> None: ...

class ScipyIterative(LinearSolverInterface):
    method: Incomplete
    options: Incomplete
    def __init__(self, method: Callable, options=None) -> None: ...
    def solve(
        self,
        matrix: spmatrix | BlockMatrix,
        rhs: np.ndarray | BlockVector,
        raise_on_error: bool = True,
    ) -> tuple[np.ndarray | BlockVector | None, LinearSolverResults]: ...
