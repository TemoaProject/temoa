from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core.base import NumericLabeler as NumericLabeler
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import TextLabeler as TextLabeler
from pyomo.core.base.block import Block as Block
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.PyomoModel import Model as Model
from pyomo.core.kernel.block import IBlock as IBlock
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.opt.base.formats import ResultsFormat as ResultsFormat
from pyomo.opt.base.solvers import OptSolver as OptSolver

class DirectOrPersistentSolver(OptSolver):
    results: Incomplete
    def __init__(self, **kwds) -> None: ...
    def load_vars(self, vars_to_load=None) -> None: ...
    def warm_start_capable(self) -> None: ...
    def available(self, exception_flag: bool = True): ...
