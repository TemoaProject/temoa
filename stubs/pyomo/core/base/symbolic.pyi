from pyomo.common.deprecation import deprecated as deprecated
from pyomo.common.errors import NondifferentiableError as NondifferentiableError
from pyomo.core.expr.calculus.diff_with_sympy import (
    differentiate_available as differentiate_available,
)

def differentiate(expr, wrt=None, wrt_list=None): ...
