from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core import is_fixed as is_fixed
from pyomo.core import maximize as maximize
from pyomo.core import minimize as minimize
from pyomo.core import value as value
from pyomo.core.base.suffix import Suffix as Suffix
from pyomo.core.kernel.conic import dual_exponential as dual_exponential
from pyomo.core.kernel.conic import dual_geomean as dual_geomean
from pyomo.core.kernel.conic import dual_power as dual_power
from pyomo.core.kernel.conic import primal_exponential as primal_exponential
from pyomo.core.kernel.conic import primal_geomean as primal_geomean
from pyomo.core.kernel.conic import primal_power as primal_power
from pyomo.core.kernel.conic import quadratic as quadratic
from pyomo.core.kernel.conic import rotated_quadratic as rotated_quadratic
from pyomo.core.kernel.conic import svec_psdcone as svec_psdcone
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.opt.base.solvers import OptSolver as OptSolver
from pyomo.opt.results.results_ import SolverResults as SolverResults
from pyomo.opt.results.solution import Solution as Solution
from pyomo.opt.results.solution import SolutionStatus as SolutionStatus
from pyomo.opt.results.solver import SolverStatus as SolverStatus
from pyomo.opt.results.solver import TerminationCondition as TerminationCondition
from pyomo.repn import generate_standard_repn as generate_standard_repn
from pyomo.solvers.plugins.solvers.direct_or_persistent_solver import (
    DirectOrPersistentSolver as DirectOrPersistentSolver,
)
from pyomo.solvers.plugins.solvers.direct_solver import DirectSolver as DirectSolver

logger: Incomplete
inf: Incomplete
mosek: Incomplete
mosek_available: Incomplete

class DegreeError(ValueError): ...
class UnsupportedDomainError(TypeError): ...

class MOSEK(OptSolver):
    def __new__(cls, *args, **kwds): ...

class MOSEKDirect(DirectSolver):
    def __init__(self, **kwds) -> None: ...
    def license_is_valid(self): ...
    def warm_start_capable(self): ...
    def load_duals(self, cons_to_load=None) -> None: ...
    def load_rc(self, vars_to_load) -> None: ...
    def load_slacks(self, cons_to_load=None) -> None: ...
