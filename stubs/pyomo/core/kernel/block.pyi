from collections.abc import Generator

from _typeshed import Incomplete
from pyomo.core.expr.symbol_map import SymbolMap as SymbolMap
from pyomo.core.kernel.container_utils import define_simple_containers as define_simple_containers
from pyomo.core.kernel.heterogeneous_container import (
    IHeterogeneousContainer as IHeterogeneousContainer,
)
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager

logger: Incomplete

class IBlock(IHeterogeneousContainer):
    def child(self, key): ...

class block(IBlock):
    def __init__(self) -> None: ...
    def child_ctypes(self): ...
    def children(self, ctype=...) -> Generator[Incomplete, Incomplete]: ...
    def __setattr__(self, name, obj) -> None: ...
    def __delattr__(self, name) -> None: ...
    def write(
        self,
        filename,
        format=None,
        _solver_capability=None,
        _called_by_solver: bool = False,
        **kwds,
    ): ...
    def load_solution(
        self,
        solution,
        allow_consistent_values_for_fixed_vars: bool = False,
        comparison_tolerance_for_fixed_vars: float = 1e-05,
    ) -> None: ...
