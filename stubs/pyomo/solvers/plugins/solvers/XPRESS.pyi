from _typeshed import Incomplete
from pyomo.opt.base import OptSolver as OptSolver
from pyomo.opt.base.solvers import SolverFactory as SolverFactory

logger: Incomplete

class XPRESS(OptSolver):
    def __new__(cls, *args, **kwds): ...
