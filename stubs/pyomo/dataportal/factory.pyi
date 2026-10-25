from _typeshed import Incomplete
from pyomo.common import Factory as Factory
from pyomo.common.plugin_base import PluginError as PluginError

logger: Incomplete

class UnknownDataManager:
    type: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def available(self): ...

class DataManagerFactoryClass(Factory):
    def __call__(self, _name=None, args=[], **kwds): ...

DataManagerFactory: Incomplete
