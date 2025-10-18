from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.contrib.fbbt.fbbt import compute_bounds_on_expr as compute_bounds_on_expr
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.var import Var as Var
from pyomo.core.expr.calculus.diff_with_pyomo import reverse_sd as reverse_sd

logger: Incomplete

def report_scaling(m: BlockData, too_large: float = 50000.0, too_small: float = 1e-06) -> bool: ...
