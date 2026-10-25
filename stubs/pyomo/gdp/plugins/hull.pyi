from _typeshed import Incomplete
from pyomo.common import deprecated as deprecated
from pyomo.common.autoslots import AutoSlots as AutoSlots
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.collections import DefaultComponentMap as DefaultComponentMap
from pyomo.common.modeling import unique_component_name as unique_component_name
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
from pyomo.core import Reals as Reals
from pyomo.core import Set as Set
from pyomo.core import SetOf as SetOf
from pyomo.core import SortComponents as SortComponents
from pyomo.core import Suffix as Suffix
from pyomo.core import TraversalStrategy as TraversalStrategy
from pyomo.core import Var as Var
from pyomo.core import value as value
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.expr.numvalue import ZeroConstant as ZeroConstant
from pyomo.core.util import target_list as target_list
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.gdp import GDP_Error as GDP_Error
from pyomo.gdp.disjunct import DisjunctData as DisjunctData
from pyomo.gdp.plugins.gdp_to_mip_transformation import (
    GDP_to_MIP_Transformation as GDP_to_MIP_Transformation,
)
from pyomo.gdp.util import (
    clone_without_expression_components as clone_without_expression_components,
)
from pyomo.gdp.util import is_child_of as is_child_of
from pyomo.util.vars_from_expressions import get_vars_from_components as get_vars_from_components

logger: Incomplete

class _HullTransformationData(AutoSlots.Mixin):
    disaggregated_var_map: Incomplete
    original_var_map: Incomplete
    bigm_constraint_map: Incomplete
    disaggregation_constraint_map: Incomplete
    def __init__(self) -> None: ...

class Hull_Reformulation(GDP_to_MIP_Transformation):
    CONFIG: Incomplete
    transformation_name: str
    def __init__(self) -> None: ...
    def get_disaggregated_var(self, v, disjunct, raise_exception: bool = True): ...
    def get_src_var(self, disaggregated_var): ...
    def get_disaggregation_constraint(
        self, original_var, disjunction, raise_exception: bool = True
    ): ...
    def get_var_bounds_constraint(self, v, disjunct=None): ...
    def get_transformed_constraints(self, cons): ...

class _Deprecated_Name_Hull(Hull_Reformulation):
    def __init__(self) -> None: ...
