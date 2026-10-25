from weakref import ReferenceType as ReferenceType

from _typeshed import Incomplete
from pyomo.common.autoslots import AutoSlots as AutoSlots
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.common.deprecation import deprecation_warning as deprecation_warning
from pyomo.common.gc_manager import PauseGC as PauseGC
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.cp.transform.logical_to_disjunctive_program import (
    LogicalToDisjunctive as LogicalToDisjunctive,
)
from pyomo.core import Any as Any
from pyomo.core import Binary as Binary
from pyomo.core import Block as Block
from pyomo.core import BooleanVar as BooleanVar
from pyomo.core import Connector as Connector
from pyomo.core import Constraint as Constraint
from pyomo.core import Expression as Expression
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import Param as Param
from pyomo.core import RangeSet as RangeSet
from pyomo.core import Set as Set
from pyomo.core import SetOf as SetOf
from pyomo.core import SortComponents as SortComponents
from pyomo.core import TraversalStrategy as TraversalStrategy
from pyomo.core import Var as Var
from pyomo.core import value as value
from pyomo.core.base import Reference as Reference
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.util import target_list as target_list
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.gdp import GDP_Error as GDP_Error
from pyomo.gdp.plugins.bigm_mixin import _BigM_MixIn
from pyomo.gdp.plugins.gdp_to_mip_transformation import (
    GDP_to_MIP_Transformation as GDP_to_MIP_Transformation,
)
from pyomo.gdp.util import is_child_of as is_child_of
from pyomo.network import Port as Port
from pyomo.repn import generate_standard_repn as generate_standard_repn

logger: Incomplete

class _BigMData(AutoSlots.Mixin):
    bigm_src: Incomplete
    def __init__(self) -> None: ...

class BigM_Transformation(GDP_to_MIP_Transformation, _BigM_MixIn):
    CONFIG: Incomplete
    transformation_name: str
    def __init__(self) -> None: ...
    def get_m_value_src(self, constraint): ...
    def get_M_value_src(self, constraint): ...
    def get_M_value(self, constraint): ...
    def get_all_M_values_by_constraint(self, model): ...
    def get_largest_M_value(self, model): ...
