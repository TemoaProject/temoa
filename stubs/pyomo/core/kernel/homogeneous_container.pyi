from collections.abc import Generator

from _typeshed import Incomplete
from pyomo.core.kernel.base import ICategorizedObjectContainer as ICategorizedObjectContainer

class IHomogeneousContainer(ICategorizedObjectContainer):
    def components(self, active: bool = True) -> Generator[Incomplete]: ...
