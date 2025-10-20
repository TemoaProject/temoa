from collections.abc import Generator

from _typeshed import Incomplete
from pyomo.core.kernel.base import ICategorizedObjectContainer as ICategorizedObjectContainer

def heterogeneous_containers(
    node, ctype=..., active: bool = True, descend_into: bool = True
) -> Generator[Incomplete, Incomplete]: ...

class IHeterogeneousContainer(ICategorizedObjectContainer):
    def collect_ctypes(self, active: bool = True, descend_into: bool = True): ...
    def child_ctypes(self, *args, **kwds) -> None: ...
    def components(
        self, ctype=..., active: bool = True, descend_into: bool = True
    ) -> Generator[Incomplete, Incomplete]: ...
