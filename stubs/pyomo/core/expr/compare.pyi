import collections

from _typeshed import Incomplete
from pyomo.common.collections import Sequence as Sequence
from pyomo.common.errors import PyomoException as PyomoException
from pyomo.common.formatting import tostr as tostr
from pyomo.common.numeric_types import native_types as native_types
from pyomo.core.expr import AbsExpression as AbsExpression
from pyomo.core.expr import DivisionExpression as DivisionExpression
from pyomo.core.expr import EqualityExpression as EqualityExpression
from pyomo.core.expr import Expr_ifExpression as Expr_ifExpression
from pyomo.core.expr import ExpressionBase as ExpressionBase
from pyomo.core.expr import ExternalFunctionExpression as ExternalFunctionExpression
from pyomo.core.expr import GetItemExpression as GetItemExpression
from pyomo.core.expr import InequalityExpression as InequalityExpression
from pyomo.core.expr import LinearExpression as LinearExpression
from pyomo.core.expr import MonomialTermExpression as MonomialTermExpression
from pyomo.core.expr import NegationExpression as NegationExpression
from pyomo.core.expr import NPV_AbsExpression as NPV_AbsExpression
from pyomo.core.expr import NPV_DivisionExpression as NPV_DivisionExpression
from pyomo.core.expr import NPV_ExternalFunctionExpression as NPV_ExternalFunctionExpression
from pyomo.core.expr import NPV_NegationExpression as NPV_NegationExpression
from pyomo.core.expr import NPV_PowExpression as NPV_PowExpression
from pyomo.core.expr import NPV_ProductExpression as NPV_ProductExpression
from pyomo.core.expr import NPV_SumExpression as NPV_SumExpression
from pyomo.core.expr import NPV_UnaryFunctionExpression as NPV_UnaryFunctionExpression
from pyomo.core.expr import NumericValue as NumericValue
from pyomo.core.expr import PowExpression as PowExpression
from pyomo.core.expr import ProductExpression as ProductExpression
from pyomo.core.expr import RangedExpression as RangedExpression
from pyomo.core.expr import SumExpression as SumExpression
from pyomo.core.expr import UnaryFunctionExpression as UnaryFunctionExpression

from .numvalue import nonpyomo_leaf_types as nonpyomo_leaf_types
from .visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor

def handle_expression(node: ExpressionBase, pn: list): ...
def handle_named_expression(node, pn: list, include_named_exprs: bool = True): ...
def handle_unary_expression(node: UnaryFunctionExpression, pn: list): ...
def handle_external_function_expression(node: ExternalFunctionExpression, pn: list): ...
def handle_sequence(node: collections.abc.Sequence, pn: list): ...
def handle_inequality(node: collections.abc.Sequence, pn: list): ...

handler: Incomplete

class PrefixVisitor(StreamBasedExpressionVisitor):
    def __init__(self, include_named_exprs: bool = True) -> None: ...
    def initializeWalker(self, expr): ...
    def enterNode(self, node): ...
    def finalizeResult(self, result): ...

def convert_expression_to_prefix_notation(expr, include_named_exprs: bool = True): ...
def compare_expressions(expr1, expr2, include_named_exprs: bool = True): ...
def assertExpressionsEqual(test, a, b, include_named_exprs: bool = True, places=None) -> None: ...
def assertExpressionsStructurallyEqual(
    test, a, b, include_named_exprs: bool = True, places=None
) -> None: ...
