from _typeshed import Incomplete
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.modeling import NOTSET as NOTSET
from pyomo.contrib.cp import IntervalVar as IntervalVar
from pyomo.core import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.component import ActiveComponentData as ActiveComponentData
from pyomo.core.base.global_set import UnindexedComponent_index as UnindexedComponent_index
from pyomo.core.base.indexed_component import ActiveIndexedComponent as ActiveIndexedComponent
from pyomo.core.base.initializer import Initializer as Initializer

logger: Incomplete

class SequenceVarData(ActiveComponentData):
    interval_vars: Incomplete
    def __init__(self, component=None) -> None: ...
    def set_value(self, expr) -> None: ...

class SequenceVar(ActiveIndexedComponent):
    def __new__(cls, *args, **kwds): ...
    def __init__(self, *args, **kwargs) -> None: ...
    def construct(self, data=None) -> None: ...

class ScalarSequenceVar(SequenceVarData, SequenceVar):
    def __init__(self, *args, **kwds) -> None: ...

class IndexedSequenceVar(SequenceVar): ...
