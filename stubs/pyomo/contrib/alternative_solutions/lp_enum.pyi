from _typeshed import Incomplete
from pyomo.contrib import appsi as appsi
from pyomo.contrib.alternative_solutions import aos_utils as aos_utils
from pyomo.contrib.alternative_solutions import shifted_lp as shifted_lp
from pyomo.contrib.alternative_solutions import solnpool as solnpool
from pyomo.contrib.alternative_solutions import solution as solution

logger: Incomplete

def enumerate_linear_solutions(
    model,
    *,
    num_solutions: int = 10,
    rel_opt_gap=None,
    abs_opt_gap=None,
    zero_threshold: float = 1e-05,
    search_mode: str = 'optimal',
    solver: str = 'gurobi',
    solver_options={},
    tee: bool = False,
    seed=None,
): ...
