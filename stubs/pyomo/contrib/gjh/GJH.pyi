from _typeshed import Incomplete
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.solvers.plugins.solvers.ASL import ASL as ASL

logger: Incomplete

def readgjh(fname=None): ...

class GJHSolver(ASL):
    def __init__(self, **kwds) -> None: ...
