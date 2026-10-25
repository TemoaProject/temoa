from _typeshed import Incomplete
from pyomo.common import Executable as Executable
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.enums import maximize as maximize
from pyomo.common.enums import minimize as minimize
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.fileutils import this_file_dir as this_file_dir
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.tee import TeeStream as TeeStream
from pyomo.common.tee import capture_output as capture_output
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core import ConcreteModel as ConcreteModel
from pyomo.core import Objective as Objective
from pyomo.core import Var as Var
from pyomo.core.kernel.block import IBlock as IBlock
from pyomo.opt.base import OptSolver as OptSolver
from pyomo.opt.base import ProblemFormat as ProblemFormat
from pyomo.opt.base import ResultsFormat as ResultsFormat
from pyomo.opt.base.solvers import SolverFactory as SolverFactory
from pyomo.opt.results import Solution as Solution
from pyomo.opt.results import SolutionStatus as SolutionStatus
from pyomo.opt.results import SolverStatus as SolverStatus
from pyomo.opt.results import TerminationCondition as TerminationCondition
from pyomo.opt.solver import ILMLicensedSystemCallSolver as ILMLicensedSystemCallSolver
from pyomo.solvers.plugins.solvers.ASL import ASL as ASL
from pyomo.solvers.plugins.solvers.gurobi_direct import gurobipy as gurobipy
from pyomo.solvers.plugins.solvers.gurobi_direct import gurobipy_available as gurobipy_available

logger: Incomplete
GUROBI_RUN: Incomplete

class GUROBI(OptSolver):
    def __new__(cls, *args, **kwds): ...

class GUROBINL(ASL):
    def license_is_valid(self): ...

class GUROBISHELL(ILMLicensedSystemCallSolver):
    def __init__(self, **kwds) -> None: ...
    def license_is_valid(self): ...
    def warm_start_capable(self): ...
    def create_command_line(self, executable, problem_files): ...
    def process_soln_file(self, results) -> None: ...

class GUROBIFILE(GUROBISHELL):
    def available(self, exception_flag: bool = False): ...
    def license_is_valid(self): ...
    def create_command_line(self, executable, problem_files): ...
    def process_soln_file(self, results) -> None: ...
