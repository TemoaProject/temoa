from _typeshed import Incomplete
from pyomo.common import Executable as Executable
from pyomo.common.collections import Bunch as Bunch
from pyomo.opt.base.solvers import SolverFactory as SolverFactory
from pyomo.solvers.plugins.solvers.ASL import ASL as ASL

logger: Incomplete

class PATHAMPL(ASL):
    def __init__(self, **kwds) -> None: ...
    def create_command_line(self, executable, problem_files): ...
