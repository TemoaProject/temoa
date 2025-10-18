from _typeshed import Incomplete
from pyomo.common.collections import OrderedDict as OrderedDict
from pyomo.opt.parallel.async_solver import AsynchronousSolverManager as AsynchronousSolverManager
from pyomo.opt.parallel.async_solver import SolverManagerFactory as SolverManagerFactory
from pyomo.opt.parallel.manager import ActionHandle as ActionHandle
from pyomo.opt.parallel.manager import ActionManagerError as ActionManagerError
from pyomo.opt.parallel.manager import ActionStatus as ActionStatus

class SolverManager_Serial(AsynchronousSolverManager):
    results: Incomplete
    def clear(self) -> None: ...
