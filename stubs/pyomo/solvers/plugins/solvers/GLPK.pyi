from _typeshed import Incomplete
from pyomo.common import Executable as Executable
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.enums import maximize as maximize
from pyomo.common.enums import minimize as minimize
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.opt import OptSolver as OptSolver
from pyomo.opt import ProblemFormat as ProblemFormat
from pyomo.opt import ResultsFormat as ResultsFormat
from pyomo.opt import SolutionStatus as SolutionStatus
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.opt import SolverResults as SolverResults
from pyomo.opt import TerminationCondition as TerminationCondition
from pyomo.opt.solver import SystemCallSolver as SystemCallSolver
from pyomo.solvers.mockmip import MockMIP as MockMIP

logger: Incomplete
GLP_BS: int
GLP_NL: int
GLP_NU: int
GLP_NF: int
GLP_NS: int
GLP_UNDEF: str
GLP_FEAS: str
GLP_INFEAS: str
GLP_NOFEAS: str
GLP_OPT: str

class GLPK(OptSolver):
    def __new__(cls, *args, **kwds): ...

class GLPKSHELL(SystemCallSolver):
    def __init__(self, **kwargs) -> None: ...
    def create_command_line(self, executable, problem_files): ...
    def process_logfile(self): ...
    is_integer: Incomplete
    def process_soln_file(self, results) -> None: ...

class MockGLPK(GLPKSHELL, MockMIP):
    def __init__(self, **kwds) -> None: ...
    def available(self, exception_flag: bool = True): ...
    def create_command_line(self, executable, problem_files): ...
    def executable(self): ...
