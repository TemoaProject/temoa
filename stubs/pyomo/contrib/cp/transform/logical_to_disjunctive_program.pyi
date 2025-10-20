from _typeshed import Incomplete
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.cp.transform.logical_to_disjunctive_walker import (
    LogicalToDisjunctiveVisitor as LogicalToDisjunctiveVisitor,
)
from pyomo.core import Binary as Binary
from pyomo.core import Block as Block
from pyomo.core import ConstraintList as ConstraintList
from pyomo.core import LogicalConstraint as LogicalConstraint
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import Transformation as Transformation
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import VarList as VarList
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.util import target_list as target_list
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction

class LogicalToDisjunctive(Transformation):
    CONFIG: Incomplete
