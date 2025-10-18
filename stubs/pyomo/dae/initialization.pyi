from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.core.base import Block as Block
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import value as value
from pyomo.dae.set_utils import deactivate_model_at as deactivate_model_at
from pyomo.dae.set_utils import get_index_set_except as get_index_set_except
from pyomo.dae.set_utils import index_warning as index_warning
from pyomo.dae.set_utils import is_explicitly_indexed_by as is_explicitly_indexed_by
from pyomo.dae.set_utils import is_in_block_indexed_by as is_in_block_indexed_by

def get_inconsistent_initial_conditions(
    model,
    time,
    tol: float = 1e-08,
    t0=None,
    allow_skip: bool = True,
    suppress_warnings: bool = False,
): ...
def solve_consistent_initial_conditions(
    model, time, solver, tee: bool = False, allow_skip: bool = True, suppress_warnings: bool = False
): ...
