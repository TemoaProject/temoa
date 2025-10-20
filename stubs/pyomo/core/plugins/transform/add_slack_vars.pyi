from _typeshed import Incomplete
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.deprecation import deprecation_warning as deprecation_warning
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import NonNegativeReals as NonNegativeReals
from pyomo.core import Objective as Objective
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import Var as Var
from pyomo.core import value as value
from pyomo.core.base import ComponentUID as ComponentUID
from pyomo.core.plugins.transform.hierarchy import (
    NonIsomorphicTransformation as NonIsomorphicTransformation,
)

def target_list(x): ...

logger: Incomplete

class AddSlackVariables(NonIsomorphicTransformation):
    CONFIG: Incomplete
    def __init__(self, **kwds) -> None: ...
