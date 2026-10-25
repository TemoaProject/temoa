from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.contrib import appsi as appsi
from pyomo.contrib.alternative_solutions import aos_utils as aos_utils
from pyomo.contrib.alternative_solutions import shifted_lp as shifted_lp
from pyomo.contrib.alternative_solutions import solution as solution

logger: Incomplete
gurobipy: Incomplete
gurobi_available: Incomplete

class NoGoodCutGenerator:
    model: Incomplete
    zero_threshold: Incomplete
    variable_groups: Incomplete
    variables: Incomplete
    orig_model: Incomplete
    all_variables: Incomplete
    orig_objective: Incomplete
    solutions: Incomplete
    num_solutions: Incomplete
    def __init__(
        self,
        model,
        variable_groups,
        zero_threshold,
        orig_model,
        all_variables,
        orig_objective,
        num_solutions,
    ) -> None: ...
    def cut_generator_callback(self, cb_m, cb_opt, cb_where) -> None: ...

def enumerate_linear_solutions_soln_pool(
    model,
    num_solutions: int = 10,
    rel_opt_gap=None,
    abs_opt_gap=None,
    zero_threshold: float = 1e-05,
    solver_options={},
    tee: bool = False,
): ...
