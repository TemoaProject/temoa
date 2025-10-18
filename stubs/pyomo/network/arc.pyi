from _typeshed import Incomplete
from pyomo.common.deprecation import RenamedClass as RenamedClass
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.modeling import NOTSET as NOTSET
from pyomo.common.timing import ConstructionTimer as ConstructionTimer
from pyomo.core.base.component import ActiveComponentData as ActiveComponentData
from pyomo.core.base.component import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.global_set import UnindexedComponent_index as UnindexedComponent_index
from pyomo.core.base.indexed_component import ActiveIndexedComponent as ActiveIndexedComponent
from pyomo.core.base.indexed_component import UnindexedComponent_set as UnindexedComponent_set
from pyomo.core.base.misc import apply_indexed_rule as apply_indexed_rule
from pyomo.network.port import Port as Port

logger: Incomplete

class ArcData(ActiveComponentData):
    def __init__(self, component=None, **kwds) -> None: ...
    def __getattr__(self, name): ...
    @property
    def source(self): ...
    src = source
    @property
    def destination(self): ...
    dest = destination
    @property
    def ports(self): ...
    @property
    def directed(self): ...
    @property
    def expanded_block(self): ...
    def set_value(self, vals) -> None: ...

class _ArcData(metaclass=RenamedClass):
    __renamed__new_class__ = ArcData
    __renamed__version__: str

class Arc(ActiveIndexedComponent):
    def __new__(cls, *args, **kwds): ...
    def __init__(self, *args, **kwds) -> None: ...
    def construct(self, data=None) -> None: ...

class ScalarArc(ArcData, Arc):
    index: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def set_value(self, vals) -> None: ...

class SimpleArc(metaclass=RenamedClass):
    __renamed__new_class__ = ScalarArc
    __renamed__version__: str

class IndexedArc(Arc):
    def __init__(self, *args, **kwds) -> None: ...
    @property
    def expanded_block(self): ...
