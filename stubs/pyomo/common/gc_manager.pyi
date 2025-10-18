import types

from _typeshed import Incomplete
from pyomo.common.multithread import MultiThreadWrapper as MultiThreadWrapper

class __PauseGCCompanion:
    def __init__(self) -> None: ...

PauseGCCompanion: __PauseGCCompanion

class PauseGC:
    stack_pointer: Incomplete
    reenable_gc: Incomplete
    def __init__(self) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        type: type[BaseException] | None,
        value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
    def close(self) -> None: ...
