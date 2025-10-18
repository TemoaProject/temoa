from _typeshed import Incomplete
from pyomo.common import Executable as Executable
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.enums import maximize as maximize
from pyomo.common.enums import minimize as minimize
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core import Var as Var
from pyomo.core.kernel.block import IBlock as IBlock
from pyomo.opt.base import OptSolver as OptSolver
from pyomo.opt.base import ProblemFormat as ProblemFormat
from pyomo.opt.base import ResultsFormat as ResultsFormat
from pyomo.opt.base.solvers import SolverFactory as SolverFactory
from pyomo.opt.results import Solution as Solution
from pyomo.opt.results import SolutionStatus as SolutionStatus
from pyomo.opt.results import SolverResults as SolverResults
from pyomo.opt.results import SolverStatus as SolverStatus
from pyomo.opt.results import TerminationCondition as TerminationCondition
from pyomo.opt.solver import SystemCallSolver as SystemCallSolver
from pyomo.solvers.mockmip import MockMIP as MockMIP

logger: Incomplete

class CBC(OptSolver):
    def __new__(cls, *args, **kwds): ...

class CBCSHELL(SystemCallSolver):
    def __init__(self, **kwds) -> None: ...
    def set_problem_format(self, format) -> None: ...
    def warm_start_capable(self): ...
    def create_command_line(self, executable, problem_files): ...
    def process_logfile(self): ...
    def process_soln_file(self, results) -> None: ...

class MockCBC(CBCSHELL, MockMIP):
    def __init__(self, **kwds) -> None: ...
    def available(self, exception_flag: bool = True): ...
    def create_command_line(self, executable, problem_files): ...
    def executable(self): ...
