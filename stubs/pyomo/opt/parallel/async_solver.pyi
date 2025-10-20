import types

from _typeshed import Incomplete
from pyomo.common import Factory as Factory
from pyomo.opt.parallel.manager import AsynchronousActionManager as AsynchronousActionManager

SolverManagerFactory: Incomplete

class AsynchronousSolverManager(AsynchronousActionManager):
    def __init__(self, **kwds) -> None: ...
    def solve(self, *args, **kwds): ...
    def solve_all(self, solver, instances, **kwds) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
