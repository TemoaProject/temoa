from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.contrib.fbbt.interval import BoolFlag as BoolFlag
from pyomo.contrib.fbbt.interval import acos as acos
from pyomo.contrib.fbbt.interval import add as add
from pyomo.contrib.fbbt.interval import asin as asin
from pyomo.contrib.fbbt.interval import atan as atan
from pyomo.contrib.fbbt.interval import cos as cos
from pyomo.contrib.fbbt.interval import div as div
from pyomo.contrib.fbbt.interval import eq as eq
from pyomo.contrib.fbbt.interval import exp as exp
from pyomo.contrib.fbbt.interval import if_ as if_
from pyomo.contrib.fbbt.interval import ineq as ineq
from pyomo.contrib.fbbt.interval import interval_abs as interval_abs
from pyomo.contrib.fbbt.interval import log as log
from pyomo.contrib.fbbt.interval import log10 as log10
from pyomo.contrib.fbbt.interval import mul as mul
from pyomo.contrib.fbbt.interval import power as power
from pyomo.contrib.fbbt.interval import ranged as ranged
from pyomo.contrib.fbbt.interval import sin as sin
from pyomo.contrib.fbbt.interval import sub as sub
from pyomo.contrib.fbbt.interval import tan as tan
from pyomo.core.base.expression import Expression as Expression
from pyomo.core.expr.logical_expr import BooleanExpression as BooleanExpression
from pyomo.core.expr.numeric_expr import AbsExpression as AbsExpression
from pyomo.core.expr.numeric_expr import DivisionExpression as DivisionExpression
from pyomo.core.expr.numeric_expr import Expr_ifExpression as Expr_ifExpression
from pyomo.core.expr.numeric_expr import ExternalFunctionExpression as ExternalFunctionExpression
from pyomo.core.expr.numeric_expr import LinearExpression as LinearExpression
from pyomo.core.expr.numeric_expr import MonomialTermExpression as MonomialTermExpression
from pyomo.core.expr.numeric_expr import NegationExpression as NegationExpression
from pyomo.core.expr.numeric_expr import NumericExpression as NumericExpression
from pyomo.core.expr.numeric_expr import PowExpression as PowExpression
from pyomo.core.expr.numeric_expr import ProductExpression as ProductExpression
from pyomo.core.expr.numeric_expr import SumExpression as SumExpression
from pyomo.core.expr.numeric_expr import UnaryFunctionExpression as UnaryFunctionExpression
from pyomo.core.expr.numvalue import native_numeric_types as native_numeric_types
from pyomo.core.expr.numvalue import native_types as native_types
from pyomo.core.expr.numvalue import value as value
from pyomo.core.expr.relational_expr import EqualityExpression as EqualityExpression
from pyomo.core.expr.relational_expr import InequalityExpression as InequalityExpression
from pyomo.core.expr.relational_expr import RangedExpression as RangedExpression
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor
from pyomo.repn.util import BeforeChildDispatcher as BeforeChildDispatcher
from pyomo.repn.util import ExitNodeDispatcher as ExitNodeDispatcher

inf: Incomplete
logger: Incomplete

class ExpressionBoundsBeforeChildDispatcher(BeforeChildDispatcher):
    def __init__(self) -> None: ...

class ExpressionBoundsExitNodeDispatcher(ExitNodeDispatcher):
    def unexpected_expression_type(self, visitor, node, *args): ...

class ExpressionBoundsVisitor(StreamBasedExpressionVisitor):
    leaf_bounds: Incomplete
    feasibility_tol: Incomplete
    use_fixed_var_values_as_bounds: Incomplete
    def __init__(
        self,
        leaf_bounds=None,
        feasibility_tol: float = 1e-08,
        use_fixed_var_values_as_bounds: bool = False,
    ) -> None: ...
    def initializeWalker(self, expr): ...
    def beforeChild(self, node, child, child_idx): ...
    def exitNode(self, node, data): ...
