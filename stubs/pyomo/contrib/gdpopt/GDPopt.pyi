import types

from _typeshed import Incomplete
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.contrib.gdpopt import __version__ as __version__
from pyomo.opt.base import SolverFactory as SolverFactory

class GDPoptSolver:
    CONFIG: Incomplete
    def solve(self, model, **kwds): ...
    def __enter__(self): ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
    def available(self, exception_flag: bool = True): ...
    def license_is_valid(self): ...
    def version(self): ...
