from _typeshed import Incomplete
from pyomo.common.deprecation import deprecation_warning as deprecation_warning
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.common.errors import InfeasibleConstraintException as InfeasibleConstraintException
from pyomo.common.errors import MouseTrap as MouseTrap
from pyomo.common.numeric_types import native_complex_types as native_complex_types
from pyomo.common.numeric_types import native_numeric_types as native_numeric_types
from pyomo.common.numeric_types import native_types as native_types
from pyomo.common.numeric_types import value as value
from pyomo.core.base import Expression as Expression
from pyomo.core.expr import AbsExpression as AbsExpression
from pyomo.core.expr import DivisionExpression as DivisionExpression
from pyomo.core.expr import EqualityExpression as EqualityExpression
from pyomo.core.expr import Expr_ifExpression as Expr_ifExpression
from pyomo.core.expr import ExternalFunctionExpression as ExternalFunctionExpression
from pyomo.core.expr import InequalityExpression as InequalityExpression
from pyomo.core.expr import LinearExpression as LinearExpression
from pyomo.core.expr import MonomialTermExpression as MonomialTermExpression
from pyomo.core.expr import NegationExpression as NegationExpression
from pyomo.core.expr import PowExpression as PowExpression
from pyomo.core.expr import ProductExpression as ProductExpression
from pyomo.core.expr import RangedExpression as RangedExpression
from pyomo.core.expr import SumExpression as SumExpression
from pyomo.core.expr import UnaryFunctionExpression as UnaryFunctionExpression
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor
from pyomo.repn.util import BeforeChildDispatcher as BeforeChildDispatcher
from pyomo.repn.util import ExitNodeDispatcher as ExitNodeDispatcher
from pyomo.repn.util import ExprType as ExprType
from pyomo.repn.util import InvalidNumber as InvalidNumber
from pyomo.repn.util import apply_node_operation as apply_node_operation
from pyomo.repn.util import complex_number_error as complex_number_error
from pyomo.repn.util import nan as nan
from pyomo.repn.util import sum_like_expression_types as sum_like_expression_types

TOL: float

class TextNLDebugTemplate:
    unary: Incomplete
    binary_sum: str
    product: str
    division: str
    pow: str
    abs: str
    negation: str
    nary_sum: str
    exprif: str
    and_expr: str
    less_than: str
    less_equal: str
    equality: str
    external_fcn: str
    var: str
    const: str
    string: str
    monomial: Incomplete
    multiplier: Incomplete

nl_operators: Incomplete

class TextNLTemplate(TextNLDebugTemplate): ...

class NLFragment:
    def __init__(self, repn, node) -> None: ...
    @property
    def name(self): ...

class AMPLRepn:
    template = TextNLTemplate
    nl: Incomplete
    mult: int
    const: Incomplete
    linear: Incomplete
    nonlinear: Incomplete
    def __init__(self, const, linear, nonlinear) -> None: ...
    def __eq__(self, other): ...
    def __hash__(self): ...
    def duplicate(self): ...
    def compile_repn(self, prefix: str = '', args=None, named_exprs=None): ...
    def compile_nonlinear_fragment(self) -> None: ...
    named_exprs: Incomplete
    def append(self, other) -> None: ...
    def to_expr(self, var_map): ...

class DebugAMPLRepn(AMPLRepn):
    template = TextNLDebugTemplate

def handle_negation_node(visitor, node, arg1): ...
def handle_product_node(visitor, node, arg1, arg2): ...
def handle_division_node(visitor, node, arg1, arg2): ...
def handle_pow_node(visitor, node, arg1, arg2): ...
def handle_abs_node(visitor, node, arg1): ...
def handle_unary_node(visitor, node, arg1): ...
def handle_exprif_node(visitor, node, arg1, arg2, arg3): ...
def handle_equality_node(visitor, node, arg1, arg2): ...
def handle_inequality_node(visitor, node, arg1, arg2): ...
def handle_ranged_inequality_node(visitor, node, arg1, arg2, arg3): ...
def handle_named_expression_node(visitor, node, arg1): ...
def handle_external_function_node(visitor, node, *args): ...

class AMPLBeforeChildDispatcher(BeforeChildDispatcher):
    def __init__(self) -> None: ...

class AMPLRepnVisitor(StreamBasedExpressionVisitor):
    subexpression_cache: Incomplete
    external_functions: Incomplete
    active_expression_source: Incomplete
    var_map: Incomplete
    used_named_expressions: Incomplete
    symbolic_solver_labels: Incomplete
    use_named_exprs: Incomplete
    encountered_string_arguments: bool
    fixed_vars: Incomplete
    evaluate: Incomplete
    sorter: Incomplete
    Result: Incomplete
    template: Incomplete
    def __init__(
        self,
        subexpression_cache,
        external_functions,
        var_map,
        used_named_expressions,
        symbolic_solver_labels,
        use_named_exprs,
        sorter,
    ) -> None: ...
    def check_constant(self, ans, obj): ...
    def cache_fixed_var(self, _id, child) -> None: ...
    def node_result_to_amplrepn(self, data): ...
    def initializeWalker(self, expr): ...
    def beforeChild(self, node, child, child_idx): ...
    def enterNode(self, node): ...
    def exitNode(self, node, data): ...
    def finalizeResult(self, result): ...

def evaluate_ampl_nl_expression(nl, external_functions): ...
