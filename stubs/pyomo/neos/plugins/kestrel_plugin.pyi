import types

from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.core.base import Block as Block
from pyomo.opt import OptSolver as OptSolver
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.opt import SolverManagerFactory as SolverManagerFactory
from pyomo.opt.parallel.async_solver import AsynchronousSolverManager as AsynchronousSolverManager
from pyomo.opt.parallel.manager import ActionManagerError as ActionManagerError
from pyomo.opt.parallel.manager import ActionStatus as ActionStatus

xmlrpc_client: Incomplete
logger: Incomplete

class SolverManager_NEOS(AsynchronousSolverManager):
    kestrel: Incomplete
    def clear(self) -> None: ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
