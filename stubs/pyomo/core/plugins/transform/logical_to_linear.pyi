from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.common.errors import MouseTrap as MouseTrap
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.fbbt.fbbt import compute_bounds_on_expr as compute_bounds_on_expr
from pyomo.core import Binary as Binary
from pyomo.core import Block as Block
from pyomo.core import BooleanVar as BooleanVar
from pyomo.core import BooleanVarList as BooleanVarList
from pyomo.core import ConstraintList as ConstraintList
from pyomo.core import LogicalConstraint as LogicalConstraint
from pyomo.core import SortComponents as SortComponents
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import VarList as VarList
from pyomo.core import native_types as native_types
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.expr import AndExpression as AndExpression
from pyomo.core.expr import AtLeastExpression as AtLeastExpression
from pyomo.core.expr import AtMostExpression as AtMostExpression
from pyomo.core.expr import EqualityExpression as EqualityExpression
from pyomo.core.expr import ExactlyExpression as ExactlyExpression
from pyomo.core.expr import InequalityExpression as InequalityExpression
from pyomo.core.expr import NotExpression as NotExpression
from pyomo.core.expr import OrExpression as OrExpression
from pyomo.core.expr import RangedExpression as RangedExpression
from pyomo.core.expr import identify_variables as identify_variables
from pyomo.core.expr import special_boolean_atom_types as special_boolean_atom_types
from pyomo.core.expr.cnf_walker import to_cnf as to_cnf
from pyomo.core.expr.numvalue import native_logical_types as native_logical_types
from pyomo.core.expr.numvalue import value as value
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.core.util import target_list as target_list

class LogicalToLinear(IsomorphicTransformation):
    CONFIG: Incomplete

def update_boolean_vars_from_binary(model, integer_tolerance: float = 1e-05) -> None: ...

class CnfToLinearVisitor(StreamBasedExpressionVisitor):
    def __init__(self, indicator_var, binary_varlist) -> None: ...
    def exitNode(self, node, values): ...
    def beforeChild(self, node, child, child_idx): ...
    def finalizeResult(self, result): ...
