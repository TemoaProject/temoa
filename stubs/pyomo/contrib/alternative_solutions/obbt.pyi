from _typeshed import Incomplete
from pyomo.contrib import appsi as appsi
from pyomo.contrib.alternative_solutions import Solution as Solution
from pyomo.contrib.alternative_solutions import aos_utils as aos_utils

logger: Incomplete

def obbt_analysis(
    model,
    *,
    variables=None,
    rel_opt_gap=None,
    abs_opt_gap=None,
    refine_discrete_bounds: bool = False,
    warmstart: bool = True,
    solver: str = 'gurobi',
    solver_options={},
    tee: bool = False,
): ...
def obbt_analysis_bounds_and_solutions(
    model,
    *,
    variables=None,
    rel_opt_gap=None,
    abs_opt_gap=None,
    refine_discrete_bounds: bool = False,
    warmstart: bool = True,
    solver: str = 'gurobi',
    solver_options={},
    tee: bool = False,
): ...
