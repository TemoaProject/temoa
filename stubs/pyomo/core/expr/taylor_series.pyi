from _typeshed import Incomplete
from pyomo.core.expr import differentiate as differentiate
from pyomo.core.expr import identify_variables as identify_variables
from pyomo.core.expr import value as value

logger: Incomplete

def taylor_series_expansion(expr, diff_mode=..., order: int = 1): ...
