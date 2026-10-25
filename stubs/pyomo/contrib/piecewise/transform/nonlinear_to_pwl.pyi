from _typeshed import Incomplete
from pyomo.common.autoslots import AutoSlots as AutoSlots
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import InEnum as InEnum
from pyomo.common.config import PositiveInt as PositiveInt
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.enums import IntEnum as IntEnum
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.piecewise import PiecewiseLinearExpression as PiecewiseLinearExpression
from pyomo.contrib.piecewise import PiecewiseLinearFunction as PiecewiseLinearFunction
from pyomo.core.expr import SumExpression as SumExpression
from pyomo.core.expr import identify_variables as identify_variables
from pyomo.core.util import target_list as target_list
from pyomo.environ import Any as Any
from pyomo.environ import Block as Block
from pyomo.environ import BooleanVar as BooleanVar
from pyomo.environ import Connector as Connector
from pyomo.environ import Constraint as Constraint
from pyomo.environ import Expression as Expression
from pyomo.environ import ExternalFunction as ExternalFunction
from pyomo.environ import LogicalConstraint as LogicalConstraint
from pyomo.environ import Objective as Objective
from pyomo.environ import Param as Param
from pyomo.environ import RangeSet as RangeSet
from pyomo.environ import Set as Set
from pyomo.environ import SetOf as SetOf
from pyomo.environ import SortComponents as SortComponents
from pyomo.environ import Suffix as Suffix
from pyomo.environ import Transformation as Transformation
from pyomo.environ import TransformationFactory as TransformationFactory
from pyomo.environ import Var as Var
from pyomo.environ import value as value
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.network import Port as Port
from pyomo.repn.quadratic import QuadraticRepnVisitor as QuadraticRepnVisitor
from pyomo.repn.util import ExprType as ExprType

lineartree: Incomplete
lineartree_available: Incomplete
sklearn_lm: Incomplete
sklearn_available: Incomplete
logger: Incomplete

class DomainPartitioningMethod(IntEnum):
    RANDOM_GRID = 1
    UNIFORM_GRID = 2
    LINEAR_MODEL_TREE_UNIFORM = 3
    LINEAR_MODEL_TREE_RANDOM = 4

class _NonlinearToPWLTransformationData(AutoSlots.Mixin):
    transformed_component: Incomplete
    src_component: Incomplete
    transformed_constraints: Incomplete
    transformed_objectives: Incomplete
    def __init__(self) -> None: ...

class NonlinearToPWL(Transformation):
    CONFIG: Incomplete
    def __init__(self) -> None: ...
    def get_src_component(self, cons): ...
    def get_transformed_component(self, cons): ...
    def get_transformed_nonlinear_constraints(self, model): ...
    def get_transformed_quadratic_constraints(self, model): ...
    def get_transformed_nonlinear_objectives(self, model): ...
    def get_transformed_quadratic_objectives(self, model): ...
