from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import In as In
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.core import Any as Any
from pyomo.core import Binary as Binary
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import RangeSet as RangeSet
from pyomo.core import Reals as Reals
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import Var as Var
from pyomo.core import value as value
from pyomo.core.expr import identify_variables as identify_variables
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.gdp import Disjunct as Disjunct

logger: Incomplete

class IntegerToBinary(IsomorphicTransformation):
    CONFIG: Incomplete
