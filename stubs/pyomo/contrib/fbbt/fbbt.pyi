from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import In as In
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.config import NonNegativeInt as NonNegativeInt
from pyomo.common.errors import InfeasibleConstraintException as InfeasibleConstraintException
from pyomo.common.errors import PyomoException as PyomoException
from pyomo.common.numeric_types import native_types as native_types
from pyomo.contrib.fbbt.expression_bounds_walker import (
    ExpressionBoundsVisitor as ExpressionBoundsVisitor,
)
from pyomo.core.base.block import Block as Block
from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.core.base.expression import ExpressionData as ExpressionData
from pyomo.core.base.expression import ScalarExpression as ScalarExpression
from pyomo.core.base.objective import ObjectiveData as ObjectiveData
from pyomo.core.base.objective import ScalarObjective as ScalarObjective
from pyomo.core.base.var import Var as Var
from pyomo.core.expr.numvalue import is_fixed as is_fixed
from pyomo.core.expr.numvalue import nonpyomo_leaf_types as nonpyomo_leaf_types
from pyomo.core.expr.numvalue import value as value
from pyomo.core.expr.visitor import ExpressionValueVisitor as ExpressionValueVisitor
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor
from pyomo.core.expr.visitor import identify_variables as identify_variables
from pyomo.gdp import Disjunct as Disjunct

logger: Incomplete
__doc__: str

class FBBTException(PyomoException): ...

class _FBBTVisitorLeafToRoot(StreamBasedExpressionVisitor):
    bnds_dict: Incomplete
    integer_tol: Incomplete
    feasibility_tol: Incomplete
    ignore_fixed: Incomplete
    def __init__(
        self,
        bnds_dict,
        integer_tol: float = 0.0001,
        feasibility_tol: float = 1e-08,
        ignore_fixed: bool = False,
    ) -> None: ...
    def initializeWalker(self, expr): ...
    def beforeChild(self, node, child, child_idx): ...
    def exitNode(self, node, data) -> None: ...

class _FBBTVisitorRootToLeaf(ExpressionValueVisitor):
    bnds_dict: Incomplete
    integer_tol: Incomplete
    feasibility_tol: Incomplete
    def __init__(
        self, bnds_dict, integer_tol: float = 0.0001, feasibility_tol: float = 1e-08
    ) -> None: ...
    def visit(self, node, values) -> None: ...
    def visiting_potential_leaf(self, node): ...

def fbbt(
    comp,
    deactivate_satisfied_constraints: bool = False,
    integer_tol: float = 1e-05,
    feasibility_tol: float = 1e-08,
    max_iter: int = 10,
    improvement_tol: float = 0.0001,
    descend_into: bool = True,
): ...
def compute_bounds_on_expr(expr, ignore_fixed: bool = False): ...

class BoundsManager:
    def __init__(self, comp) -> None: ...
    def save_bounds(self) -> None: ...
    def pop_bounds(self, ndx: int = -1) -> None: ...
    def load_bounds(self, bnds, save_current_bounds: bool = True) -> None: ...
