from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.contrib import appsi as appsi
from pyomo.contrib.alternative_solutions import Solution as Solution

logger: Incomplete

def gurobi_generate_solutions(
    model,
    *,
    num_solutions: int = 10,
    rel_opt_gap=None,
    abs_opt_gap=None,
    solver_options={},
    tee: bool = False,
): ...
