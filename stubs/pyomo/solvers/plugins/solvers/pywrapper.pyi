from _typeshed import Incomplete
from pyomo.opt import OptSolver as OptSolver
from pyomo.opt import SolverFactory as SolverFactory

logger: Incomplete

class pywrapper(OptSolver):
    def __new__(cls, *args, **kwds): ...
