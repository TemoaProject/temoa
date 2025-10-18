from pyomo.core.expr.sympy_tools import sympy2pyomo_expression as sympy2pyomo_expression
from pyomo.core.expr.sympy_tools import sympy_available as sympy_available
from pyomo.core.expr.sympy_tools import sympyify_expression as sympyify_expression

differentiate_available = sympy_available

def differentiate(expr, wrt=None, wrt_list=None): ...
