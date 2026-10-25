from _typeshed import Incomplete
from pyomo.common.enums import NamedIntEnum as NamedIntEnum
from pyomo.core.expr.numeric_expr import NumericExpression as NumericExpression
from pyomo.core.expr.numvalue import is_constant as is_constant
from pyomo.core.expr.numvalue import value as value
from pyomo.core.expr.sympy_tools import sympy2pyomo_expression as sympy2pyomo_expression
from pyomo.core.expr.sympy_tools import sympyify_expression as sympyify_expression

def simplify_with_sympy(expr: NumericExpression): ...
def simplify_with_ginac(expr: NumericExpression, ginac_interface): ...

class Simplifier:
    class Mode(NamedIntEnum):
        auto = 0
        sympy = 1
        ginac = 2

    gi: Incomplete
    simplify: Incomplete
    def __init__(self, suppress_no_ginac_warnings: bool = False, mode: Mode = ...) -> None: ...
