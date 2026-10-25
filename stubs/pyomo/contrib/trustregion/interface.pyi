from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.trustregion.util import maxIgnoreNone as maxIgnoreNone
from pyomo.contrib.trustregion.util import minIgnoreNone as minIgnoreNone
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import ExternalFunction as ExternalFunction
from pyomo.core import Objective as Objective
from pyomo.core import Param as Param
from pyomo.core import Set as Set
from pyomo.core import VarList as VarList
from pyomo.core import maximize as maximize
from pyomo.core import minimize as minimize
from pyomo.core import value as value
from pyomo.core.expr.calculus.derivatives import differentiate as differentiate
from pyomo.core.expr.numeric_expr import ExternalFunctionExpression as ExternalFunctionExpression
from pyomo.core.expr.numvalue import native_types as native_types
from pyomo.core.expr.visitor import ExpressionReplacementVisitor as ExpressionReplacementVisitor
from pyomo.core.expr.visitor import identify_variables as identify_variables
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.opt import check_optimal_termination as check_optimal_termination

logger: Incomplete

class EFReplacement(ExpressionReplacementVisitor):
    trfData: Incomplete
    efSet: Incomplete
    def __init__(self, trfData, efSet) -> None: ...
    def beforeChild(self, node, child, child_idx): ...
    def exitNode(self, node, data): ...

class TRFInterface:
    original_model: Incomplete
    config: Incomplete
    model: Incomplete
    decision_variables: Incomplete
    data: Incomplete
    basis_expression_rule: Incomplete
    efSet: Incomplete
    solver: Incomplete
    def __init__(self, model, decision_variables, ext_fcn_surrogate_map_rule, config) -> None: ...
    def replaceEF(self, expr): ...
    degrees_of_freedom: Incomplete
    def replaceExternalFunctionsWithVariables(self) -> None: ...
    def createConstraints(self): ...
    def getCurrentDecisionVariableValues(self): ...
    def updateDecisionVariableBounds(self, radius) -> None: ...
    def updateSurrogateModel(self) -> None: ...
    def getCurrentModelState(self): ...
    def calculateFeasibility(self): ...
    def calculateStepSizeInfNorm(self, original_values, new_values): ...
    initial_decision_bounds: Incomplete
    def initializeProblem(self): ...
    def solveModel(self): ...
    def rejectStep(self) -> None: ...
