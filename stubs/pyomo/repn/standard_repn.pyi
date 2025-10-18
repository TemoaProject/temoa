from _typeshed import Incomplete
from pyomo.common.numeric_types import native_numeric_types as native_numeric_types
from pyomo.common.numeric_types import native_types as native_types
from pyomo.core.base import ComponentMap as ComponentMap
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Expression as Expression
from pyomo.core.base import Objective as Objective
from pyomo.core.base.expression import ExpressionData as ExpressionData
from pyomo.core.base.expression import NamedExpressionData as NamedExpressionData
from pyomo.core.base.expression import ScalarExpression as ScalarExpression
from pyomo.core.base.objective import ObjectiveData as ObjectiveData
from pyomo.core.base.objective import ScalarObjective as ScalarObjective
from pyomo.core.base.param import ParamData as ParamData
from pyomo.core.base.param import ScalarParam as ScalarParam
from pyomo.core.base.var import ScalarVar as ScalarVar
from pyomo.core.base.var import Var as Var
from pyomo.core.base.var import VarData as VarData
from pyomo.core.base.var import value as value
from pyomo.core.expr.numvalue import NumericConstant as NumericConstant
from pyomo.core.kernel.expression import expression as expression
from pyomo.core.kernel.expression import noclone as noclone
from pyomo.core.kernel.objective import objective as objective
from pyomo.core.kernel.variable import IVariable as IVariable
from pyomo.core.kernel.variable import variable as variable

logger: Incomplete

def isclose_const(a, b, rel_tol: float = 1e-09, abs_tol: float = 0.0): ...

class StandardRepn:
    constant: int
    linear_vars: Incomplete
    linear_coefs: Incomplete
    quadratic_vars: Incomplete
    quadratic_coefs: Incomplete
    nonlinear_expr: Incomplete
    nonlinear_vars: Incomplete
    def __init__(self) -> None: ...
    def is_fixed(self): ...
    def polynomial_degree(self): ...
    def is_constant(self): ...
    def is_linear(self): ...
    def is_quadratic(self): ...
    def is_nonlinear(self): ...
    def to_expression(self, sort: bool = True): ...

def generate_standard_repn(
    expr,
    idMap=None,
    compute_values: bool = True,
    verbose: bool = False,
    quadratic: bool = True,
    repn=None,
): ...

class ResultsWithQuadratics:
    __slot__: Incomplete
    constant: Incomplete
    nonl: Incomplete
    linear: Incomplete
    quadratic: Incomplete
    def __init__(self, constant: int = 0, nonl: int = 0, linear=None, quadratic=None) -> None: ...

class ResultsWithoutQuadratics:
    __slot__: Incomplete
    constant: Incomplete
    nonl: Incomplete
    linear: Incomplete
    def __init__(self, constant: int = 0, nonl: int = 0, linear=None) -> None: ...

Results = ResultsWithQuadratics

def preprocess_block_objectives(block, idMap=None) -> None: ...
def preprocess_block_constraints(block, idMap=None) -> None: ...
def preprocess_constraint(block, constraint, idMap=None, block_repn=None) -> None: ...
def preprocess_constraint_data(block, constraint_data, idMap=None, block_repn=None) -> None: ...
