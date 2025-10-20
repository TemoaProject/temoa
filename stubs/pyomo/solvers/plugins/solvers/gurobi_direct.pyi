import types

from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.tee import capture_output as capture_output
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core.base.suffix import Suffix as Suffix
from pyomo.core.expr.numvalue import is_fixed as is_fixed
from pyomo.core.expr.numvalue import value as value
from pyomo.core.kernel.objective import maximize as maximize
from pyomo.core.kernel.objective import minimize as minimize
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.opt.base import SolverFactory as SolverFactory
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

class DegreeError(ValueError): ...

gurobipy: Incomplete
gurobipy_available: Incomplete

class GurobiDirect(DirectSolver):
    def __init__(self, manage_env: bool = False, **kwds) -> None: ...
    def available(self, exception_flag: bool = True): ...
    def close_global(self) -> None: ...
    def close(self) -> None: ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
    def warm_start_capable(self): ...
    def load_duals(self, cons_to_load=None) -> None: ...
    def load_rc(self, vars_to_load) -> None: ...
    def load_slacks(self, cons_to_load=None) -> None: ...
