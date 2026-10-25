from _typeshed import Incomplete
from pyomo.common.numeric_types import native_numeric_types as native_numeric_types
from pyomo.core.expr.numeric_expr import DivisionExpression as DivisionExpression
from pyomo.core.expr.numeric_expr import Expr_ifExpression as Expr_ifExpression
from pyomo.core.expr.numeric_expr import PowExpression as PowExpression
from pyomo.core.expr.numeric_expr import ProductExpression as ProductExpression
from pyomo.core.expr.numeric_expr import mutable_expression as mutable_expression
from pyomo.repn.linear import ExitNodeDispatcher as ExitNodeDispatcher
from pyomo.repn.linear import initialize_exit_node_dispatcher as initialize_exit_node_dispatcher
from pyomo.repn.parameterized_linear import (
    ParameterizedLinearRepnVisitor as ParameterizedLinearRepnVisitor,
)
from pyomo.repn.parameterized_linear import to_expression as to_expression
from pyomo.repn.quadratic import QuadraticRepn as QuadraticRepn
from pyomo.repn.util import ExprType as ExprType

class ParameterizedQuadraticRepn(QuadraticRepn):
    def walker_exitNode(self): ...
    def to_expression(self, visitor): ...
    quadratic: Incomplete
    nonlinear: Incomplete
    def append(self, other) -> None: ...

def is_zero(obj): ...
def is_zero_product(e1, e2): ...
def is_equal_to(obj, val): ...
def define_exit_node_handlers(exit_node_handlers=None): ...

class ParameterizedQuadraticRepnVisitor(ParameterizedLinearRepnVisitor):
    Result = ParameterizedQuadraticRepn
    exit_node_dispatcher: Incomplete
    max_exponential_expansion: int
    expand_nonlinear_products: bool
    def finalizeResult(self, result): ...
