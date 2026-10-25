from _typeshed import Incomplete
from pyomo.core.base.expression import Expression as Expression
from pyomo.core.expr.numeric_expr import AbsExpression as AbsExpression
from pyomo.core.expr.numeric_expr import DivisionExpression as DivisionExpression
from pyomo.core.expr.numeric_expr import Expr_ifExpression as Expr_ifExpression
from pyomo.core.expr.numeric_expr import LinearExpression as LinearExpression
from pyomo.core.expr.numeric_expr import MonomialTermExpression as MonomialTermExpression
from pyomo.core.expr.numeric_expr import NegationExpression as NegationExpression
from pyomo.core.expr.numeric_expr import PowExpression as PowExpression
from pyomo.core.expr.numeric_expr import ProductExpression as ProductExpression
from pyomo.core.expr.numeric_expr import UnaryFunctionExpression as UnaryFunctionExpression
from pyomo.core.expr.numeric_expr import mutable_expression as mutable_expression
from pyomo.core.expr.relational_expr import EqualityExpression as EqualityExpression
from pyomo.core.expr.relational_expr import InequalityExpression as InequalityExpression
from pyomo.core.expr.relational_expr import RangedExpression as RangedExpression

from . import linear as linear
from . import util as util
from .linear import to_expression as to_expression

class QuadraticRepn:
    multiplier: int
    constant: int
    linear: Incomplete
    quadratic: Incomplete
    nonlinear: Incomplete
    def __init__(self) -> None: ...
    def walker_exitNode(self): ...
    def duplicate(self): ...
    def to_expression(self, visitor): ...
    def append(self, other) -> None: ...

def define_exit_node_handlers(_exit_node_handlers=None): ...

class QuadraticRepnVisitor(linear.LinearRepnVisitor):
    Result = QuadraticRepn
    exit_node_dispatcher: Incomplete
    max_exponential_expansion: int
