from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.contrib.alternative_solutions import Solution as Solution

logger: Incomplete

def enumerate_binary_solutions(
    model,
    *,
    num_solutions: int = 10,
    variables=None,
    rel_opt_gap=None,
    abs_opt_gap=None,
    search_mode: str = 'optimal',
    solver: str = 'gurobi',
    solver_options={},
    tee: bool = False,
    seed=None,
): ...
