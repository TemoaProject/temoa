from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.errors import MouseTrap as MouseTrap
from pyomo.core.base import Binary as Binary
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import ConstraintList as ConstraintList
from pyomo.core.base import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core.base import VarList as VarList
from pyomo.core.base import value as value
from pyomo.core.base.expression import ExpressionData as ExpressionData
from pyomo.core.base.expression import ScalarExpression as ScalarExpression
from pyomo.core.base.param import ParamData as ParamData
from pyomo.core.base.param import ScalarParam as ScalarParam
from pyomo.core.base.var import ScalarVar as ScalarVar
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr.expr_common import ExpressionType as ExpressionType
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor
from pyomo.gdp.disjunct import AutoLinkedBooleanVar as AutoLinkedBooleanVar
from pyomo.gdp.disjunct import Disjunct as Disjunct
from pyomo.gdp.disjunct import Disjunction as Disjunction

class LogicalToDisjunctiveVisitor(StreamBasedExpressionVisitor):
    z_vars: Incomplete
    constraints: Incomplete
    disjuncts: Incomplete
    disjunctions: Incomplete
    expansions: Incomplete
    boolean_to_binary_map: Incomplete
    def __init__(self) -> None: ...
    def initializeWalker(self, expr): ...
    def beforeChild(self, node, child, child_idx): ...
    def exitNode(self, node, data): ...
    def finalizeResult(self, result): ...
