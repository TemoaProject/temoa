import logging
import types
from collections.abc import Generator
from contextlib import contextmanager

from _typeshed import Incomplete
from pyomo.common import timing as timing
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.deprecation import deprecation_warning as deprecation_warning
from pyomo.contrib.fbbt.fbbt import compute_bounds_on_expr as compute_bounds_on_expr
from pyomo.contrib.mcpp.pyomo_mcpp import McCormick as McCormick
from pyomo.contrib.mcpp.pyomo_mcpp import mcpp_available as mcpp_available
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import Objective as Objective
from pyomo.core import Reals as Reals
from pyomo.core import Reference as Reference
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import Var as Var
from pyomo.core import minimize as minimize
from pyomo.core import value as value
from pyomo.core.expr.numvalue import native_types as native_types
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.opt import SolverFactory as SolverFactory

class _DoNothing:
    def __init__(self, *args, **kwargs) -> None: ...
    def __call__(self, *args, **kwargs) -> None: ...
    def __getattr__(self, attr): ...

class SuppressInfeasibleWarning:
    class InfeasibleWarningFilter(logging.Filter):
        def filter(self, record): ...

    warning_filter: Incomplete
    def __enter__(self): ...
    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...

def solve_continuous_problem(m, config): ...
def move_nonlinear_objective_to_constraints(util_block, logger): ...
def a_logger(str_or_logger): ...
def copy_var_list_values(
    from_list,
    to_list,
    config,
    skip_stale: bool = False,
    skip_fixed: bool = True,
    ignore_integrality: bool = False,
) -> None: ...
def fix_discrete_var(var, val, config) -> None: ...

class fix_discrete_solution_in_subproblem:
    True_disjuncts: Incomplete
    boolean_var_values: Incomplete
    discrete_var_values: Incomplete
    subprob_util_block: Incomplete
    config: Incomplete
    def __init__(
        self,
        true_disjuncts,
        boolean_var_values,
        integer_var_values,
        subprob_util_block,
        config,
        solver,
    ) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...

class fix_discrete_problem_solution_in_subproblem(fix_discrete_solution_in_subproblem):
    discrete_prob_util_block: Incomplete
    subprob_util_block: Incomplete
    solver: Incomplete
    config: Incomplete
    def __init__(self, discrete_prob_util_block, subproblem_util_block, solver, config) -> None: ...
    def __enter__(self): ...

def is_feasible(model, config): ...
@contextmanager
def time_code(timing_data_obj, code_block_name, is_main_timer: bool = False) -> Generator[None]: ...
def get_main_elapsed_time(timing_data_obj): ...
@contextmanager
def lower_logger_level_to(logger, level=None, tee: bool = False) -> Generator[None]: ...
