import types

from _typeshed import Incomplete
from pyomo.common import Factory as Factory

WriterFactory: Incomplete

class AbstractProblemWriter:
    format: Incomplete
    def __init__(self, problem_format) -> None: ...
    def __call__(self, model, filename, solver_capability, **kwds) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...

class BranchDirection:
    default: int
    down: int
    up: int
    ALL: Incomplete
