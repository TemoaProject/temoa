from _typeshed import Incomplete
from pyomo.common.deprecation import RenamedClass as RenamedClass
from pyomo.common.formatting import tabular_writer as tabular_writer
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.modeling import NOTSET as NOTSET
from pyomo.common.timing import ConstructionTimer as ConstructionTimer
from pyomo.core.base.component import ActiveComponentData as ActiveComponentData
from pyomo.core.base.component import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.global_set import UnindexedComponent_index as UnindexedComponent_index
from pyomo.core.base.indexed_component import ActiveIndexedComponent as ActiveIndexedComponent
from pyomo.core.base.indexed_component import UnindexedComponent_set as UnindexedComponent_set
from pyomo.core.base.misc import apply_indexed_rule as apply_indexed_rule
from pyomo.core.base.set import Set as Set
from pyomo.core.expr.boolean_value import BooleanConstant as BooleanConstant
from pyomo.core.expr.boolean_value import as_boolean as as_boolean
from pyomo.core.expr.numvalue import native_logical_types as native_logical_types
from pyomo.core.expr.numvalue import native_types as native_types

logger: Incomplete

class LogicalConstraintData(ActiveComponentData):
    def __init__(self, expr=None, component=None) -> None: ...
    def __call__(self, exception=...): ...
    @property
    def body(self): ...
    @property
    def expr(self): ...
    def set_value(self, expr) -> None: ...
    def get_value(self): ...

class _LogicalConstraintData(metaclass=RenamedClass):
    __renamed__new_class__ = LogicalConstraintData
    __renamed__version__: str

class _GeneralLogicalConstraintData(metaclass=RenamedClass):
    __renamed__new_class__ = LogicalConstraintData
    __renamed__version__: str

class LogicalConstraint(ActiveIndexedComponent):
    class Infeasible: ...
    Feasible: Incomplete
    NoConstraint: Incomplete
    Violated = Infeasible
    Satisfied = Feasible
    def __new__(cls, *args, **kwds): ...
    rule: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def construct(self, data=None) -> None: ...
    def display(self, prefix: str = '', ostream=None): ...

class ScalarLogicalConstraint(LogicalConstraintData, LogicalConstraint):
    def __init__(self, *args, **kwds) -> None: ...
    @property
    def body(self): ...
    def set_value(self, expr): ...
    def add(self, index, expr): ...

class SimpleLogicalConstraint(metaclass=RenamedClass):
    __renamed__new_class__ = ScalarLogicalConstraint
    __renamed__version__: str

class IndexedLogicalConstraint(LogicalConstraint):
    def add(self, index, expr): ...

class LogicalConstraintList(IndexedLogicalConstraint):
    End: Incomplete
    def __init__(self, **kwargs) -> None: ...
    def construct(self, data=None) -> None: ...
    def add(self, expr): ...
