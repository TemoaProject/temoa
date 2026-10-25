from collections import namedtuple as namedtuple

from _typeshed import Incomplete
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer
from pyomo.util.subsystems import create_subsystem_block as create_subsystem_block

class SquareNlpSolverBase:
    OPTIONS: Incomplete
    options: Incomplete
    def __init__(self, nlp, timer=None, options=None) -> None: ...
    def solve(self, x0=None) -> None: ...
    def evaluate_function(self, x0): ...
    def evaluate_jacobian(self, x0): ...

class DenseSquareNlpSolver(SquareNlpSolverBase):
    def evaluate_jacobian(self, x0): ...

class ScalarDenseSquareNlpSolver(DenseSquareNlpSolver):
    def __init__(self, nlp, timer=None, options=None) -> None: ...
