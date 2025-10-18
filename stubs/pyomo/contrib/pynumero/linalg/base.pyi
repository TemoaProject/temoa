import enum
from abc import ABCMeta, abstractmethod

import numpy as np
from _typeshed import Incomplete
from pyomo.contrib.pynumero.sparse import BlockMatrix as BlockMatrix
from pyomo.contrib.pynumero.sparse import BlockVector as BlockVector
from pyomo.contrib.pynumero.sparse.base_block import BaseBlockMatrix as BaseBlockMatrix
from pyomo.contrib.pynumero.sparse.base_block import BaseBlockVector as BaseBlockVector
from scipy.sparse import spmatrix as spmatrix

class LinearSolverStatus(enum.Enum):
    successful = 0
    not_enough_memory = 1
    singular = 2
    error = 3
    warning = 4
    max_iter = 5

class LinearSolverResults:
    status: Incomplete
    def __init__(self, status: LinearSolverStatus | None = None) -> None: ...

class LinearSolverInterface(metaclass=ABCMeta):
    @abstractmethod
    def solve(
        self,
        matrix: spmatrix | BlockMatrix,
        rhs: np.ndarray | BlockVector,
        raise_on_error: bool = True,
    ) -> tuple[np.ndarray | BlockVector | None, LinearSolverResults]: ...

class DirectLinearSolverInterface(LinearSolverInterface, metaclass=ABCMeta):
    @abstractmethod
    def do_symbolic_factorization(
        self, matrix: spmatrix | BlockMatrix, raise_on_error: bool = True
    ) -> LinearSolverResults: ...
    @abstractmethod
    def do_numeric_factorization(
        self, matrix: spmatrix | BlockMatrix, raise_on_error: bool = True
    ) -> LinearSolverResults: ...
    @abstractmethod
    def do_back_solve(
        self, rhs: np.ndarray | BlockVector, raise_on_error: bool = True
    ) -> tuple[np.ndarray | BlockVector | None, LinearSolverResults]: ...
    def solve(
        self,
        matrix: spmatrix | BlockMatrix,
        rhs: np.ndarray | BlockVector,
        raise_on_error: bool = True,
    ) -> tuple[np.ndarray | BlockVector | None, LinearSolverResults]: ...
