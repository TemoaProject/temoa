import types

from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.gdpopt import __version__ as __version__
from pyomo.contrib.gdpopt.create_oa_subproblems import (
    add_algebraic_variable_list as add_algebraic_variable_list,
)
from pyomo.contrib.gdpopt.create_oa_subproblems import (
    add_boolean_variable_lists as add_boolean_variable_lists,
)
from pyomo.contrib.gdpopt.create_oa_subproblems import add_disjunct_list as add_disjunct_list
from pyomo.contrib.gdpopt.create_oa_subproblems import add_util_block as add_util_block
from pyomo.contrib.gdpopt.util import get_main_elapsed_time as get_main_elapsed_time
from pyomo.contrib.gdpopt.util import lower_logger_level_to as lower_logger_level_to
from pyomo.contrib.gdpopt.util import solve_continuous_problem as solve_continuous_problem
from pyomo.contrib.gdpopt.util import time_code as time_code
from pyomo.core.base import Objective as Objective
from pyomo.core.base import maximize as maximize
from pyomo.core.base import minimize as minimize
from pyomo.core.base import value as value
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.opt import SolverResults as SolverResults
from pyomo.util.model_size import build_model_size_report as build_model_size_report

class _GDPoptAlgorithm:
    CONFIG: Incomplete
    config: Incomplete
    LB: Incomplete
    UB: Incomplete
    timing: Incomplete
    initialization_iteration: int
    iteration: int
    incumbent_boolean_soln: Incomplete
    incumbent_continuous_soln: Incomplete
    original_obj: Incomplete
    original_util_block: Incomplete
    log_formatter: str
    def __init__(self, **kwds) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
    def available(self, exception_flag: bool = True): ...
    def license_is_valid(self): ...
    def version(self): ...
    def solve(self, model, **kwds): ...
    @property
    def objective_sense(self): ...
    def relative_gap(self): ...
    def primal_bound(self): ...
    def update_incumbent(self, util_block) -> None: ...
    def bounds_converged(self, config): ...
    def reached_iteration_limit(self, config): ...
    def reached_time_limit(self, config): ...
    def any_termination_criterion_met(self, config): ...
