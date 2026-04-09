from ctypes import Structure

from _typeshed import Incomplete
from pyomo.common.autoslots import AutoSlots as AutoSlots
from pyomo.common.fileutils import find_library as find_library
from pyomo.common.numeric_types import check_if_native_type as check_if_native_type
from pyomo.common.numeric_types import native_numeric_types as native_numeric_types
from pyomo.common.numeric_types import native_types as native_types
from pyomo.common.numeric_types import value as value
from pyomo.common.pyomo_typing import overload as overload
from pyomo.core.base.component import Component as Component
from pyomo.core.base.units_container import units as units
from pyomo.core.expr.numvalue import NonNumericValue as NonNumericValue
from pyomo.core.expr.numvalue import NumericConstant as NumericConstant

logger: Incomplete
nan: Incomplete

class ExternalFunction(Component):
    def __new__(cls, *args, **kwargs): ...
    def get_units(self): ...
    def get_arg_units(self): ...
    def __call__(self, *args): ...
    def evaluate(self, args): ...
    def evaluate_fgh(self, args, fixed=None, fgh: int = 2): ...

class AMPLExternalFunction(ExternalFunction):
    __autoslot_mappers__: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def load_library(self) -> None: ...

class _PythonCallbackFunctionID(NumericConstant):
    __autoslot_mappers__: Incomplete
    def is_constant(self): ...

class PythonCallbackFunction(ExternalFunction):
    __autoslot_mappers__: Incomplete
    global_registry: Incomplete
    global_id_to_fid: Incomplete
    @classmethod
    def register_instance(cls, instance): ...
    def __init__(self, *args, **kwargs) -> None: ...
    def __call__(self, *args): ...

class _ARGLIST(Structure):
    n: Incomplete
    at: Incomplete
    nr: Incomplete
    ra: Incomplete
    sa: Incomplete
    derivs: Incomplete
    hes: Incomplete
    dig: Incomplete
    def __init__(self, args, fgh: int = 0, fixed=None) -> None: ...

class _AMPLEXPORTS(Structure): ...

class _AMPLEXPORTS(Structure):
    AMPLFUNC: Incomplete
    ADDFUNC: Incomplete
    RANDSEEDSETTER: Incomplete
    ADDRANDINIT: Incomplete
    ATRESET: Incomplete
