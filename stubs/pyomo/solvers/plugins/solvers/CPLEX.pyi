from _typeshed import Incomplete
from pyomo.common import Executable as Executable
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.enums import maximize as maximize
from pyomo.common.enums import minimize as minimize
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core.base import Suffix as Suffix
from pyomo.core.base import Var as Var
from pyomo.core.base import active_export_suffix_generator as active_export_suffix_generator
from pyomo.core.kernel.block import IBlock as IBlock
from pyomo.core.kernel.suffix import export_suffix_generator as export_suffix_generator
from pyomo.opt.base import BranchDirection as BranchDirection
from pyomo.opt.base import OptSolver as OptSolver
from pyomo.opt.base import ProblemFormat as ProblemFormat
from pyomo.opt.base import ResultsFormat as ResultsFormat
from pyomo.opt.base.solvers import SolverFactory as SolverFactory
from pyomo.opt.results import Solution as Solution
from pyomo.opt.results import SolutionStatus as SolutionStatus
from pyomo.opt.results import SolverResults as SolverResults
from pyomo.opt.results import SolverStatus as SolverStatus
from pyomo.opt.results import TerminationCondition as TerminationCondition
from pyomo.opt.solver import ILMLicensedSystemCallSolver as ILMLicensedSystemCallSolver
from pyomo.solvers.mockmip import MockMIP as MockMIP
from pyomo.util.components import iter_component as iter_component

logger: Incomplete

class CPLEX(OptSolver):
    def __new__(cls, *args, **kwds): ...

class ORDFileSchema:
    HEADER: str
    FOOTER: str
    @classmethod
    def ROW(cls, name, priority, branch_direction=None): ...

class CPLEXSHELL(ILMLicensedSystemCallSolver):
    def __init__(self, **kwds) -> None: ...
    def warm_start_capable(self): ...
    SUFFIX_PRIORITY_NAME: str
    SUFFIX_DIRECTION_NAME: str
    def create_command_line(self, executable, problem_files): ...
    def process_logfile(self): ...
    def process_soln_file(self, results) -> None: ...

class MockCPLEX(CPLEXSHELL, MockMIP):
    def __init__(self, **kwds) -> None: ...
    def available(self, exception_flag: bool = True): ...
    def create_command_line(self, executable, problem_files): ...
