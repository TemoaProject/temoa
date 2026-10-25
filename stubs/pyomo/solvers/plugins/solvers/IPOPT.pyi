from _typeshed import Incomplete
from pyomo.common import Executable as Executable
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.tee import capture_output as capture_output
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.opt.base import ProblemFormat as ProblemFormat
from pyomo.opt.base import ResultsFormat as ResultsFormat
from pyomo.opt.base.solvers import SolverFactory as SolverFactory
from pyomo.opt.results import SolverResults as SolverResults
from pyomo.opt.results import SolverStatus as SolverStatus
from pyomo.opt.results import TerminationCondition as TerminationCondition
from pyomo.opt.solver import SystemCallSolver as SystemCallSolver
from pyomo.solvers.amplfunc_merge import amplfunc_merge as amplfunc_merge

logger: Incomplete

class IPOPT(SystemCallSolver):
    def __init__(self, **kwds) -> None: ...
    def create_command_line(self, executable, problem_files): ...
    def process_output(self, rc): ...
    def has_linear_solver(self, linear_solver): ...
