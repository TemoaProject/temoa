from _typeshed import Incomplete
from pyomo.common import Executable as Executable
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.tempfiles import TempfileManager as TempfileManager
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

logger: Incomplete

class BARONSHELL(SystemCallSolver):
    def __init__(self, **kwds) -> None: ...
    def license_is_valid(self): ...
    def create_command_line(self, executable, problem_files): ...
    def warm_start_capable(self): ...
    def process_logfile(self): ...
    def process_soln_file(self, results) -> None: ...
