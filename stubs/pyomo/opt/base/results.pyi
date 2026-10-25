import types

from _typeshed import Incomplete
from pyomo.common import Factory as Factory

ReaderFactory: Incomplete

class AbstractResultsReader:
    format: Incomplete
    def __init__(self, results_format) -> None: ...
    def __call__(self, filename, res=None, suffixes=[]) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
