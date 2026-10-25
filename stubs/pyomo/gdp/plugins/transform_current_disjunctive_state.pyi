from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.errors import InfeasibleConstraintException as InfeasibleConstraintException
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.core.base import Any as Any
from pyomo.core.base import Block as Block
from pyomo.core.base import ReverseTransformationToken as ReverseTransformationToken
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.util import target_list as target_list
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.gdp.util import GDP_Error as GDP_Error

class TransformCurrentDisjunctiveState(Transformation):
    CONFIG: Incomplete
