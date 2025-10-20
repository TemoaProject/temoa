from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.numeric_types import native_numeric_types as native_numeric_types
from pyomo.core import Var as Var
from pyomo.core.expr.numeric_expr import AbsExpression as AbsExpression
from pyomo.core.expr.numeric_expr import DivisionExpression as DivisionExpression
from pyomo.core.expr.numeric_expr import LinearExpression as LinearExpression
from pyomo.core.expr.numeric_expr import MonomialTermExpression as MonomialTermExpression
from pyomo.core.expr.numeric_expr import NegationExpression as NegationExpression
from pyomo.core.expr.numeric_expr import PowExpression as PowExpression
from pyomo.core.expr.numeric_expr import ProductExpression as ProductExpression
from pyomo.core.expr.numeric_expr import SumExpression as SumExpression
from pyomo.core.expr.numeric_expr import UnaryFunctionExpression as UnaryFunctionExpression
from pyomo.core.expr.numeric_expr import mutable_expression as mutable_expression
from pyomo.repn.linear import ExitNodeDispatcher as ExitNodeDispatcher
from pyomo.repn.linear import LinearBeforeChildDispatcher as LinearBeforeChildDispatcher
from pyomo.repn.linear import LinearRepn as LinearRepn
from pyomo.repn.linear import LinearRepnVisitor as LinearRepnVisitor
from pyomo.repn.linear import initialize_exit_node_dispatcher as initialize_exit_node_dispatcher
from pyomo.repn.util import ExprType as ExprType

def to_expression(visitor, arg): ...

class ParameterizedLinearRepn(LinearRepn):
    def walker_exitNode(self): ...
    def to_expression(self, visitor): ...
    nonlinear: Incomplete
    def append(self, other) -> None: ...

class ParameterizedLinearBeforeChildDispatcher(LinearBeforeChildDispatcher):
    def __init__(self) -> None: ...

def define_exit_node_handlers(exit_node_handlers=None): ...

class ParameterizedLinearRepnVisitor(LinearRepnVisitor):
    Result = ParameterizedLinearRepn
    exit_node_dispatcher: Incomplete
    wrt: Incomplete
    def __init__(
        self,
        subexpression_cache,
        var_map=None,
        var_order=None,
        sorter=None,
        wrt=None,
        var_recorder=None,
    ) -> None: ...
    def beforeChild(self, node, child, child_idx): ...
    def finalizeResult(self, result): ...
