from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.core.base import Block as Block
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base.indexed_component import UnindexedComponent_set as UnindexedComponent_set
from pyomo.gdp import Disjunct as Disjunct
from pyomo.network import Arc as Arc
from pyomo.network.util import replicate_var as replicate_var

logger: Incomplete
obj_iter_kwds: Incomplete

class ExpandArcs(Transformation): ...
