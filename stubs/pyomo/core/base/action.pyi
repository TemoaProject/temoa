from _typeshed import Incomplete
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.timing import ConstructionTimer as ConstructionTimer
from pyomo.core.base.component import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.indexed_component import IndexedComponent as IndexedComponent
from pyomo.core.base.misc import apply_indexed_rule as apply_indexed_rule

logger: Incomplete

class BuildAction(IndexedComponent):
    def __init__(self, *args, **kwd) -> None: ...
    def construct(self, data=None) -> None: ...
