import io
import logging
import types
from collections.abc import Generator

from _typeshed import Incomplete
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.common.fileutils import PYOMO_ROOT_DIR as PYOMO_ROOT_DIR
from pyomo.common.flags import building_documentation as building_documentation
from pyomo.common.flags import in_testing_environment as in_testing_environment
from pyomo.common.formatting import wrap_reStructuredText as wrap_reStructuredText
from pyomo.version.info import releaselevel as releaselevel

def RTD(_id): ...
def is_debug_set(logger): ...

class WrappingFormatter(logging.Formatter):
    basepath: Incomplete
    def __init__(self, **kwds) -> None: ...
    def format(self, record): ...

class LegacyPyomoFormatter(logging.Formatter):
    verbosity: Incomplete
    standard_formatter: Incomplete
    verbose_formatter: Incomplete
    def __init__(self, **kwds) -> None: ...
    def format(self, record): ...

class StdoutHandler(logging.StreamHandler):
    stream: Incomplete
    def flush(self) -> None: ...
    def emit(self, record) -> None: ...

class Preformatted:
    msg: Incomplete
    def __init__(self, msg) -> None: ...

class _GlobalLogFilter:
    logger: Incomplete
    def __init__(self) -> None: ...
    def filter(self, record): ...

pyomo_logger: Incomplete
pyomo_handler: Incomplete
pyomo_formatter: Incomplete

class LogHandler(logging.StreamHandler):
    def __init__(self, base: str = '', stream=None, level=..., verbosity=None) -> None: ...

class LoggingIntercept:
    handler: Incomplete
    output: Incomplete
    def __init__(
        self, output=None, module=None, level=..., formatter=None, logger=None
    ) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        et: type[BaseException] | None,
        ev: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None: ...
    @property
    def module(self): ...

class LogStream(io.TextIOBase):
    def __init__(self, level, logger) -> None: ...
    def write(self, s: str) -> int: ...
    def flush(self) -> None: ...
    def redirect_streams(self, redirects) -> Generator[Incomplete]: ...

class _StreamRedirector:
    handler: Incomplete
    fd: Incomplete
    orig_stream: Incomplete
    def __init__(self, handler, fd) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        et: type[BaseException] | None,
        ev: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None: ...

class _LastResortRedirector:
    fd: Incomplete
    orig_stream: Incomplete
    def __init__(self, fd) -> None: ...
    orig: Incomplete
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        et: type[BaseException] | None,
        ev: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None: ...
