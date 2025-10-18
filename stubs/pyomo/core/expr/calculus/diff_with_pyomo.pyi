from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.core.expr import cos as cos
from pyomo.core.expr import exp as exp
from pyomo.core.expr import log as log
from pyomo.core.expr import sin as sin
from pyomo.core.expr.numvalue import is_constant as is_constant
from pyomo.core.expr.numvalue import value as value
from pyomo.core.expr.visitor import ExpressionValueVisitor as ExpressionValueVisitor
from pyomo.core.expr.visitor import nonpyomo_leaf_types as nonpyomo_leaf_types

class DifferentiationException(Exception): ...

class _LeafToRootVisitor(ExpressionValueVisitor):
    val_dict: Incomplete
    der_dict: Incomplete
    expr_list: Incomplete
    value_func: Incomplete
    operation_func: Incomplete
    def __init__(self, val_dict, der_dict, expr_list, numeric: bool = True) -> None: ...
    def visit(self, node, values): ...
    def visiting_potential_leaf(self, node): ...

def reverse_ad(expr): ...
def reverse_sd(expr): ...
