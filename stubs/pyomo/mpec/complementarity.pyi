from typing import NamedTuple

from _typeshed import Incomplete
from pyomo.common.deprecation import RenamedClass as RenamedClass
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.timing import ConstructionTimer as ConstructionTimer
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import Set as Set
from pyomo.core import Var as Var
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.component import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.disable_methods import disable_methods as disable_methods
from pyomo.core.base.global_set import UnindexedComponent_index as UnindexedComponent_index
from pyomo.core.base.initializer import CountedCallInitializer as CountedCallInitializer
from pyomo.core.base.initializer import IndexedCallInitializer as IndexedCallInitializer
from pyomo.core.base.initializer import Initializer as Initializer
from pyomo.core.expr.numvalue import ZeroConstant as ZeroConstant
from pyomo.core.expr.numvalue import as_numeric as as_numeric
from pyomo.core.expr.numvalue import native_numeric_types as native_numeric_types

logger: Incomplete

class ComplementarityTuple(NamedTuple):
    arg0: Incomplete
    arg1: Incomplete

def complements(a, b): ...

class ComplementarityData(BlockData):
    c: Incomplete
    v: Incomplete
    ve: Incomplete
    def to_standard_form(self) -> None: ...
    def set_value(self, cc): ...

class _ComplementarityData(metaclass=RenamedClass):
    __renamed__new_class__ = ComplementarityData
    __renamed__version__: str

class Complementarity(Block):
    def __new__(cls, *args, **kwds): ...
    def __init__(self, *args, **kwargs) -> None: ...
    def add(self, index, cc): ...

class ScalarComplementarity(ComplementarityData, Complementarity):
    def __init__(self, *args, **kwds) -> None: ...

class SimpleComplementarity(metaclass=RenamedClass):
    __renamed__new_class__ = ScalarComplementarity
    __renamed__version__: str

class AbstractScalarComplementarity(ScalarComplementarity): ...

class AbstractSimpleComplementarity(metaclass=RenamedClass):
    __renamed__new_class__ = AbstractScalarComplementarity
    __renamed__version__: str

class IndexedComplementarity(Complementarity): ...

class ComplementarityList(IndexedComplementarity):
    End: Incomplete
    def __init__(self, **kwargs) -> None: ...
    def add(self, expr): ...
    def construct(self, data=None) -> None: ...
