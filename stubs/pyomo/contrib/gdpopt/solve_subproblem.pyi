import types

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.common.errors import InfeasibleConstraintException as InfeasibleConstraintException
from pyomo.contrib import appsi as appsi
from pyomo.contrib.appsi.cmodel import cmodel_available as cmodel_available
from pyomo.contrib.fbbt.fbbt import fbbt as fbbt
from pyomo.contrib.gdpopt.solve_discrete_problem import (
    distinguish_mip_infeasible_or_unbounded as distinguish_mip_infeasible_or_unbounded,
)
from pyomo.contrib.gdpopt.util import SuppressInfeasibleWarning as SuppressInfeasibleWarning
from pyomo.contrib.gdpopt.util import get_main_elapsed_time as get_main_elapsed_time
from pyomo.contrib.gdpopt.util import is_feasible as is_feasible
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import Objective as Objective
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.opt import SolverResults as SolverResults

def configure_and_call_solver(model, solver, args, problem_type, timing, time_limit): ...
def process_nonlinear_problem_results(results, model, problem_type, config): ...
def solve_linear_subproblem(subproblem, config, timing): ...
def solve_NLP(nlp_model, config, timing): ...
def solve_MINLP(util_block, config, timing): ...
def detect_unfixed_discrete_vars(model): ...

class preprocess_subproblem:
    util_block: Incomplete
    config: Incomplete
    not_infeas: bool
    unfixed_vars: Incomplete
    original_bounds: Incomplete
    constraints_deactivated: Incomplete
    constraints_modified: Incomplete
    def __init__(self, util_block, config) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...

def call_appropriate_subproblem_solver(subprob_util_block, solver, config): ...
def solve_subproblem(subprob_util_block, solver, config): ...
