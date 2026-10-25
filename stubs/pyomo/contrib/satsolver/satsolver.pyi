from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.core import Constraint as Constraint
from pyomo.core import NumericLabeler as NumericLabeler
from pyomo.core import SymbolMap as SymbolMap
from pyomo.core import Var as Var
from pyomo.core import value as value
from pyomo.core.expr import AbsExpression as AbsExpression
from pyomo.core.expr import DivisionExpression as DivisionExpression
from pyomo.core.expr import EqualityExpression as EqualityExpression
from pyomo.core.expr import InequalityExpression as InequalityExpression
from pyomo.core.expr import MonomialTermExpression as MonomialTermExpression
from pyomo.core.expr import NegationExpression as NegationExpression
from pyomo.core.expr import PowExpression as PowExpression
from pyomo.core.expr import ProductExpression as ProductExpression
from pyomo.core.expr import SumExpression as SumExpression
from pyomo.core.expr import UnaryFunctionExpression as UnaryFunctionExpression
from pyomo.core.expr.numvalue import nonpyomo_leaf_types as nonpyomo_leaf_types
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor
from pyomo.gdp import Disjunction as Disjunction

z3: Incomplete
z3_available: Incomplete

def satisfiable(model, logger=None): ...

class SMTSatSolver:
    variable_label_map: Incomplete
    prefix_expr_list: Incomplete
    variable_list: Incomplete
    bounds_list: Incomplete
    expression_list: Incomplete
    disjunctions_list: Incomplete
    walker: Incomplete
    solver: Incomplete
    logger: Incomplete
    def __init__(self, model=None, logger=None) -> None: ...
    def add_var(self, var): ...
    def add_expr(self, expression) -> None: ...
    def get_SMT_string(self): ...
    def get_var_dict(self): ...
    def check(self): ...

class SMT_visitor(StreamBasedExpressionVisitor):
    variable_label_map: Incomplete
    def __init__(self, varmap) -> None: ...
    def exitNode(self, node, data): ...
    def beforeChild(self, node, child, child_idx): ...
    def finalizeResult(self, node_result): ...
