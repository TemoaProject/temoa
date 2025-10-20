from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.enums import ObjectiveSense as ObjectiveSense
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.errors import MouseTrap as MouseTrap
from pyomo.common.shutdown import python_is_shutting_down as python_is_shutting_down
from pyomo.common.tee import TeeStream as TeeStream
from pyomo.common.tee import capture_output as capture_output
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer
from pyomo.contrib.solver.common.base import Availability as Availability
from pyomo.contrib.solver.common.base import SolverBase as SolverBase
from pyomo.contrib.solver.common.config import BranchAndBoundConfig as BranchAndBoundConfig
from pyomo.contrib.solver.common.results import Results as Results
from pyomo.contrib.solver.common.results import SolutionStatus as SolutionStatus
from pyomo.contrib.solver.common.results import TerminationCondition as TerminationCondition
from pyomo.contrib.solver.common.solution_loader import SolutionLoaderBase as SolutionLoaderBase
from pyomo.contrib.solver.common.util import IncompatibleModelError as IncompatibleModelError
from pyomo.contrib.solver.common.util import NoDualsError as NoDualsError
from pyomo.contrib.solver.common.util import NoFeasibleSolutionError as NoFeasibleSolutionError
from pyomo.contrib.solver.common.util import NoOptimalSolutionError as NoOptimalSolutionError
from pyomo.contrib.solver.common.util import NoReducedCostsError as NoReducedCostsError
from pyomo.contrib.solver.common.util import NoSolutionError as NoSolutionError
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.repn.plugins.standard_form import (
    LinearStandardFormCompiler as LinearStandardFormCompiler,
)

gurobipy: Incomplete
gurobipy_available: Incomplete

class GurobiConfigMixin:
    use_mipstart: bool
    def __init__(self) -> None: ...

class GurobiConfig(BranchAndBoundConfig, GurobiConfigMixin):
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class GurobiDirectSolutionLoader(SolutionLoaderBase):
    def __init__(self, grb_model, grb_cons, grb_vars, pyo_cons, pyo_vars, pyo_obj) -> None: ...
    def __del__(self) -> None: ...
    def load_vars(self, vars_to_load=None, solution_number: int = 0): ...
    def get_primals(self, vars_to_load=None, solution_number: int = 0): ...
    def get_duals(self, cons_to_load=None): ...
    def get_reduced_costs(self, vars_to_load=None): ...

class GurobiSolverMixin:
    def available(self): ...
    def version(self): ...

class GurobiDirect(GurobiSolverMixin, SolverBase):
    CONFIG: Incomplete
    def __init__(self, **kwds) -> None: ...
    @staticmethod
    def release_license() -> None: ...
    def __del__(self) -> None: ...
    def solve(self, model, **kwds) -> Results: ...
