from _typeshed import Incomplete
from pyomo.common import Executable as Executable
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core.kernel.block import IBlock as IBlock
from pyomo.opt.base import ProblemFormat as ProblemFormat
from pyomo.opt.base import ResultsFormat as ResultsFormat
from pyomo.opt.base.solvers import SolverFactory as SolverFactory
from pyomo.opt.solver import SystemCallSolver as SystemCallSolver
from pyomo.solvers.amplfunc_merge import amplfunc_merge as amplfunc_merge
from pyomo.solvers.mockmip import MockMIP as MockMIP

logger: Incomplete

class ASL(SystemCallSolver):
    def __init__(self, **kwds) -> None: ...
    def available(self, exception_flag: bool = True): ...
    def create_command_line(self, executable, problem_files): ...

class MockASL(ASL, MockMIP):
    def __init__(self, **kwds) -> None: ...
    def available(self, exception_flag: bool = True): ...
    def create_command_line(self, executable, problem_files): ...
    def executable(self): ...
