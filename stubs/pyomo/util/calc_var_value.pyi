from _typeshed import Incomplete
from pyomo.common.errors import IterationLimitError as IterationLimitError
from pyomo.common.numeric_types import native_complex_types as native_complex_types
from pyomo.common.numeric_types import native_numeric_types as native_numeric_types
from pyomo.common.numeric_types import value as value
from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.core.expr.calculus.derivatives import differentiate as differentiate

logger: Incomplete

def calculate_variable_from_constraint(
    variable,
    constraint,
    eps: float = 1e-08,
    iterlim: int = 1000,
    linesearch: bool = True,
    alpha_min: float = 1e-08,
    diff_mode=None,
) -> None: ...
