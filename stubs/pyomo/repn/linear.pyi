from _typeshed import Incomplete
from pyomo.common.deprecation import deprecation_warning as deprecation_warning
from pyomo.common.numeric_types import native_complex_types as native_complex_types
from pyomo.common.numeric_types import native_numeric_types as native_numeric_types
from pyomo.common.numeric_types import native_types as native_types
from pyomo.core.base.expression import Expression as Expression
from pyomo.core.expr import is_fixed as is_fixed
from pyomo.core.expr import value as value
from pyomo.core.expr.numeric_expr import AbsExpression as AbsExpression
from pyomo.core.expr.numeric_expr import DivisionExpression as DivisionExpression
from pyomo.core.expr.numeric_expr import Expr_ifExpression as Expr_ifExpression
from pyomo.core.expr.numeric_expr import ExternalFunctionExpression as ExternalFunctionExpression
from pyomo.core.expr.numeric_expr import LinearExpression as LinearExpression
from pyomo.core.expr.numeric_expr import MonomialTermExpression as MonomialTermExpression
from pyomo.core.expr.numeric_expr import NegationExpression as NegationExpression
from pyomo.core.expr.numeric_expr import PowExpression as PowExpression
from pyomo.core.expr.numeric_expr import ProductExpression as ProductExpression
from pyomo.core.expr.numeric_expr import SumExpression as SumExpression
from pyomo.core.expr.numeric_expr import UnaryFunctionExpression as UnaryFunctionExpression
from pyomo.core.expr.numeric_expr import mutable_expression as mutable_expression
from pyomo.core.expr.relational_expr import EqualityExpression as EqualityExpression
from pyomo.core.expr.relational_expr import InequalityExpression as InequalityExpression
from pyomo.core.expr.relational_expr import RangedExpression as RangedExpression
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor
from pyomo.repn.util import BeforeChildDispatcher as BeforeChildDispatcher
from pyomo.repn.util import ExitNodeDispatcher as ExitNodeDispatcher
from pyomo.repn.util import ExprType as ExprType
from pyomo.repn.util import FileDeterminism as FileDeterminism
from pyomo.repn.util import FileDeterminism_to_SortComponents as FileDeterminism_to_SortComponents
from pyomo.repn.util import InvalidNumber as InvalidNumber
from pyomo.repn.util import OrderedVarRecorder as OrderedVarRecorder
from pyomo.repn.util import VarRecorder as VarRecorder
from pyomo.repn.util import apply_node_operation as apply_node_operation
from pyomo.repn.util import complex_number_error as complex_number_error
from pyomo.repn.util import initialize_exit_node_dispatcher as initialize_exit_node_dispatcher
from pyomo.repn.util import nan as nan
from pyomo.repn.util import sum_like_expression_types as sum_like_expression_types

logger: Incomplete

class LinearRepn:
    multiplier: int
    constant: int
    linear: Incomplete
    nonlinear: Incomplete
    def __init__(self) -> None: ...
    def walker_exitNode(self): ...
    def duplicate(self): ...
    def to_expression(self, visitor): ...
    def append(self, other) -> None: ...

def to_expression(visitor, arg): ...
def define_exit_node_handlers(_exit_node_handlers=None): ...

class LinearBeforeChildDispatcher(BeforeChildDispatcher):
    def __init__(self) -> None: ...

class LinearRepnVisitor(StreamBasedExpressionVisitor):
    Result = LinearRepn
    before_child_dispatcher: Incomplete
    exit_node_dispatcher: Incomplete
    expand_nonlinear_products: bool
    max_exponential_expansion: int
    subexpression_cache: Incomplete
    var_recorder: Incomplete
    var_map: Incomplete
    evaluate: Incomplete
    def __init__(
        self, subexpression_cache, var_map=None, var_order=None, sorter=None, var_recorder=None
    ) -> None: ...
    def check_constant(self, ans, obj): ...
    def initializeWalker(self, expr): ...
    def beforeChild(self, node, child, child_idx): ...
    def enterNode(self, node): ...
    def exitNode(self, node, data): ...
    def finalizeResult(self, result): ...
