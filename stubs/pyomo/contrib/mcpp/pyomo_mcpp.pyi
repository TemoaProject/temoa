from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.fileutils import Library as Library
from pyomo.core import Expression as Expression
from pyomo.core import value as value
from pyomo.core.base.block import SubclassOf as SubclassOf
from pyomo.core.base.expression import NamedExpressionData as NamedExpressionData
from pyomo.core.expr.numeric_expr import AbsExpression as AbsExpression
from pyomo.core.expr.numeric_expr import DivisionExpression as DivisionExpression
from pyomo.core.expr.numeric_expr import LinearExpression as LinearExpression
from pyomo.core.expr.numeric_expr import NegationExpression as NegationExpression
from pyomo.core.expr.numeric_expr import NPV_AbsExpression as NPV_AbsExpression
from pyomo.core.expr.numeric_expr import NPV_DivisionExpression as NPV_DivisionExpression
from pyomo.core.expr.numeric_expr import (
    NPV_ExternalFunctionExpression as NPV_ExternalFunctionExpression,
)
from pyomo.core.expr.numeric_expr import NPV_NegationExpression as NPV_NegationExpression
from pyomo.core.expr.numeric_expr import NPV_PowExpression as NPV_PowExpression
from pyomo.core.expr.numeric_expr import NPV_ProductExpression as NPV_ProductExpression
from pyomo.core.expr.numeric_expr import NPV_SumExpression as NPV_SumExpression
from pyomo.core.expr.numeric_expr import NPV_UnaryFunctionExpression as NPV_UnaryFunctionExpression
from pyomo.core.expr.numeric_expr import PowExpression as PowExpression
from pyomo.core.expr.numeric_expr import ProductExpression as ProductExpression
from pyomo.core.expr.numeric_expr import SumExpression as SumExpression
from pyomo.core.expr.numeric_expr import UnaryFunctionExpression as UnaryFunctionExpression
from pyomo.core.expr.numvalue import nonpyomo_leaf_types as nonpyomo_leaf_types
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor
from pyomo.core.expr.visitor import identify_variables as identify_variables

logger: Incomplete
path: Incomplete
__version__: str

def mcpp_available(): ...

NPV_expressions: Incomplete

class MCPP_Error(Exception): ...

class MCPP_visitor(StreamBasedExpressionVisitor):
    mcpp: Incomplete
    missing_value_warnings: Incomplete
    expr: Incomplete
    num_vars: Incomplete
    known_vars: Incomplete
    var_to_idx: Incomplete
    refs: Incomplete
    def __init__(self, expression, improved_var_bounds=None) -> None: ...
    def walk_expression(self): ...
    def exitNode(self, node, data): ...
    def beforeChild(self, node, child, child_idx): ...
    def acceptChildResult(self, node, data, child_result, child_idx): ...
    def register_num(self, num): ...
    def register_var(self, var, lb, ub): ...
    def finalizeResult(self, node_result): ...

class McCormick:
    mc_expr: Incomplete
    mcpp: Incomplete
    pyomo_expr: Incomplete
    visitor: Incomplete
    def __init__(self, expression, improved_var_bounds=None) -> None: ...
    def __del__(self) -> None: ...
    def __repn__(self): ...
    def lower(self): ...
    def upper(self): ...
    def concave(self): ...
    def convex(self): ...
    def subcc(self): ...
    def subcv(self): ...
    def changePoint(self, var, point) -> None: ...
    def warn_if_var_missing_value(self) -> None: ...
