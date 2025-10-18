from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.suffix import active_import_suffix_generator as active_import_suffix_generator
from pyomo.core.kernel.block import IBlock as IBlock
from pyomo.core.kernel.suffix import import_suffix_generator as import_suffix_generator
from pyomo.solvers.plugins.solvers.direct_or_persistent_solver import (
    DirectOrPersistentSolver as DirectOrPersistentSolver,
)

logger: Incomplete

class DirectSolver(DirectOrPersistentSolver):
    options: Incomplete
    def solve(self, *args, **kwds): ...
