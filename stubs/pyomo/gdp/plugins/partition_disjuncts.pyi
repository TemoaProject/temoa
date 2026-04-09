from math import floor as floor

from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.fbbt.fbbt import compute_bounds_on_expr as compute_bounds_on_expr
from pyomo.core import Binary as Binary
from pyomo.core import Block as Block
from pyomo.core import BooleanVar as BooleanVar
from pyomo.core import ComponentMap as ComponentMap
from pyomo.core import ConcreteModel as ConcreteModel
from pyomo.core import Connector as Connector
from pyomo.core import Constraint as Constraint
from pyomo.core import Expression as Expression
from pyomo.core import LogicalConstraint as LogicalConstraint
from pyomo.core import LogicalConstraintList as LogicalConstraintList
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import Objective as Objective
from pyomo.core import Param as Param
from pyomo.core import RangeSet as RangeSet
from pyomo.core import Reference as Reference
from pyomo.core import Set as Set
from pyomo.core import SetOf as SetOf
from pyomo.core import SortComponents as SortComponents
from pyomo.core import Suffix as Suffix
from pyomo.core import Transformation as Transformation
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import TraversalStrategy as TraversalStrategy
from pyomo.core import Var as Var
from pyomo.core import maximize as maximize
from pyomo.core import value as value
from pyomo.core.base.external import ExternalFunction as ExternalFunction
from pyomo.core.util import target_list as target_list
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.gdp import GDP_Error as GDP_Error
from pyomo.gdp.util import NORMAL as NORMAL
from pyomo.gdp.util import (
    clone_without_expression_components as clone_without_expression_components,
)
from pyomo.gdp.util import get_gdp_tree as get_gdp_tree
from pyomo.gdp.util import is_child_of as is_child_of
from pyomo.gdp.util import verify_successful_solve as verify_successful_solve
from pyomo.network import Port as Port
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.repn import generate_standard_repn as generate_standard_repn
from pyomo.util.vars_from_expressions import get_vars_from_components as get_vars_from_components

logger: Incomplete

def arbitrary_partition(disjunction, P): ...
def compute_optimal_bounds(expr, global_constraints, opt): ...
def compute_fbbt_bounds(expr, global_constraints, opt): ...

class PartitionDisjuncts_Transformation(Transformation):
    CONFIG: Incomplete
    handlers: Incomplete
    def __init__(self) -> None: ...
