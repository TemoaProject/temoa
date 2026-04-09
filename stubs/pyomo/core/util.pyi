from _typeshed import Incomplete
from pyomo.common.deprecation import deprecation_warning as deprecation_warning
from pyomo.core.base.component import ComponentBase as ComponentBase
from pyomo.core.base.expression import Expression as Expression
from pyomo.core.base.var import Var as Var
from pyomo.core.expr.numeric_expr import NPV_SumExpression as NPV_SumExpression
from pyomo.core.expr.numeric_expr import mutable_expression as mutable_expression
from pyomo.core.expr.numvalue import native_numeric_types as native_numeric_types

logger: Incomplete

def prod(terms): ...
def quicksum(args, start: int = 0, linear=None): ...
def sum_product(*args, **kwds): ...

dot_product = sum_product
summation = sum_product

def sequence(*args): ...
def target_list(x): ...
