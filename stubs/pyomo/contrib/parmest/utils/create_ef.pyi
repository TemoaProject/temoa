from collections.abc import Generator

from _typeshed import Incomplete
from pyomo.core import Objective as Objective
from pyomo.core.expr.numeric_expr import LinearExpression as LinearExpression

def get_objs(scenario_instance): ...
def create_EF(
    scenario_names,
    scenario_creator,
    scenario_creator_kwargs=None,
    EF_name=None,
    suppress_warnings: bool = False,
    nonant_for_fixed_vars: bool = True,
): ...
def find_active_objective(pyomomodel): ...
def ef_nonants(ef) -> Generator[Incomplete]: ...
