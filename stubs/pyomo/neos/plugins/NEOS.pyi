from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.opt.base import ProblemFormat as ProblemFormat
from pyomo.opt.base import ResultsFormat as ResultsFormat
from pyomo.opt.base import SolverFactory as SolverFactory
from pyomo.opt.solver import SystemCallSolver as SystemCallSolver

logger: Incomplete

class NEOSRemoteSolver(SystemCallSolver):
    def __init__(self, **kwds) -> None: ...
    def create_command_line(self, executable, problem_files): ...
