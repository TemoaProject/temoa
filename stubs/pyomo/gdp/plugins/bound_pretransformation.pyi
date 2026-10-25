from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.core import Any as Any
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import SortComponents as SortComponents
from pyomo.core import Var as Var
from pyomo.core import value as value
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.expr import identify_variables as identify_variables
from pyomo.core.util import target_list as target_list
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.gdp import GDP_Error as GDP_Error
from pyomo.gdp.util import get_gdp_tree as get_gdp_tree
from pyomo.gdp.util import is_child_of as is_child_of
from pyomo.repn.standard_repn import generate_standard_repn as generate_standard_repn

logger: Incomplete

class BoundPretransformation(Transformation):
    CONFIG: Incomplete
    transformation_name: str
    logger: Incomplete
    def __init__(self) -> None: ...
    def get_transformed_constraints(self, v, disjunction): ...
