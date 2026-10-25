import enum

from _typeshed import Incomplete
from pyomo.common.deprecation import RenamedClass as RenamedClass
from pyomo.common.deprecation import deprecation_warning as deprecation_warning
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.numeric_types import value as value
from pyomo.common.timing import ConstructionTimer as ConstructionTimer
from pyomo.core.base.block import Block as Block
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.component import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.core.base.constraint import ConstraintList as ConstraintList
from pyomo.core.base.set_types import Binary as Binary
from pyomo.core.base.set_types import NonNegativeReals as NonNegativeReals
from pyomo.core.base.set_types import PositiveReals as PositiveReals
from pyomo.core.base.sos import SOSConstraint as SOSConstraint
from pyomo.core.base.util import flatten_tuple as flatten_tuple
from pyomo.core.base.var import IndexedVar as IndexedVar
from pyomo.core.base.var import Var as Var
from pyomo.core.base.var import VarData as VarData

logger: Incomplete

class PWRepn(str, enum.Enum):
    SOS2 = 'SOS2'
    BIGM_BIN = 'BIGM_BIN'
    BIGM_SOS1 = 'BIGM_SOS1'
    CC = 'CC'
    DCC = 'DCC'
    DLOG = 'DLOG'
    LOG = 'LOG'
    MC = 'MC'
    INC = 'INC'

class Bound(str, enum.Enum):
    Lower = 'Lower'
    Upper = 'Upper'
    Equal = 'Equal'

class PiecewiseData(BlockData):
    def __init__(self, parent) -> None: ...
    def updateBoundType(self, bound_type) -> None: ...
    def updatePoints(self, domain_pts, range_pts) -> None: ...
    def build_constraints(self, functor, x_var, y_var) -> None: ...
    def referenced_variables(self): ...
    def __call__(self, x): ...

class _PiecewiseData(metaclass=RenamedClass):
    __renamed__new_class__ = PiecewiseData
    __renamed__version__: str

class _SimpleSinglePiecewise:
    def construct(self, pblock, x_var, y_var) -> None: ...

class _SimplifiedPiecewise:
    def construct(self, pblock, x_var, y_var) -> None: ...

class _SOS2Piecewise:
    def construct(self, pblock, x_var, y_var): ...

class _DCCPiecewise:
    def construct(self, pblock, x_var, y_var): ...

class _DLOGPiecewise:
    def construct(self, pblock, x_var, y_var): ...

class _CCPiecewise:
    def construct(self, pblock, x_var, y_var): ...

class _LOGPiecewise:
    def construct(self, pblock, x_var, y_var): ...

class _MCPiecewise:
    def construct(self, pblock, x_var, y_var): ...

class _INCPiecewise:
    def construct(self, pblock, x_var, y_var): ...

class _BIGMPiecewise:
    binary: Incomplete
    def __init__(self, binary: bool = True) -> None: ...
    def construct(self, pblock, x_var, y_var): ...

class Piecewise(Block):
    def __new__(cls, *args, **kwds): ...
    def __init__(self, *args, **kwds) -> None: ...
    def construct(self, *args, **kwds) -> None: ...
    def add(self, index, _is_indexed=None) -> None: ...

class SimplePiecewise(PiecewiseData, Piecewise):
    def __init__(self, *args, **kwds) -> None: ...

class IndexedPiecewise(Piecewise):
    def __init__(self, *args, **kwds) -> None: ...
