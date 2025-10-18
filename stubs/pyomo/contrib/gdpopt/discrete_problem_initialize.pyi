from collections.abc import Generator
from contextlib import contextmanager

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.contrib.gdpopt.cut_generation import add_no_good_cut as add_no_good_cut
from pyomo.contrib.gdpopt.solve_discrete_problem import (
    solve_MILP_discrete_problem as solve_MILP_discrete_problem,
)
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import Objective as Objective
from pyomo.core import Var as Var
from pyomo.core import maximize as maximize
from pyomo.core import value as value
from pyomo.gdp import Disjunct as Disjunct

@contextmanager
def preserve_discrete_problem_feasible_region(
    discrete_problem_util_block, config, original_bounds=None
) -> Generator[None]: ...
def init_custom_disjuncts(
    util_block, discrete_problem_util_block, subprob_util_block, config, solver
) -> None: ...
def init_fixed_disjuncts(
    util_block, discrete_problem_util_block, subprob_util_block, config, solver
) -> None: ...
@contextmanager
def use_discrete_problem_for_max_binary_initialization(
    discrete_problem_util_block,
) -> Generator[None]: ...
def init_max_binaries(
    util_block, discrete_problem_util_block, subprob_util_block, config, solver
): ...
@contextmanager
def use_discrete_problem_for_set_covering(discrete_problem_util_block) -> Generator[None]: ...
def update_set_covering_objective(discrete_problem_util_block, disj_needs_cover) -> None: ...
def init_set_covering(
    util_block, discrete_problem_util_block, subprob_util_block, config, solver
): ...

valid_init_strategies: Incomplete
