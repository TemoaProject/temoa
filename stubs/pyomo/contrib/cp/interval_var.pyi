from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.pyomo_typing import overload as overload
from pyomo.contrib.cp.scheduling_expr.precedence_expressions import AtExpression as AtExpression
from pyomo.contrib.cp.scheduling_expr.precedence_expressions import (
    BeforeExpression as BeforeExpression,
)
from pyomo.contrib.cp.scheduling_expr.scheduling_logic import SpanExpression as SpanExpression
from pyomo.core import Integers as Integers
from pyomo.core import value as value
from pyomo.core.base import Any as Any
from pyomo.core.base import ScalarBooleanVar as ScalarBooleanVar
from pyomo.core.base import ScalarVar as ScalarVar
from pyomo.core.base.block import Block as Block
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.component import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.global_set import UnindexedComponent_index as UnindexedComponent_index
from pyomo.core.base.indexed_component import IndexedComponent as IndexedComponent
from pyomo.core.base.indexed_component import UnindexedComponent_set as UnindexedComponent_set
from pyomo.core.base.initializer import BoundInitializer as BoundInitializer
from pyomo.core.base.initializer import Initializer as Initializer
from pyomo.core.expr import GetItemExpression as GetItemExpression

class IntervalVarTimePoint(ScalarVar):
    def get_associated_interval_var(self): ...
    def before(self, time, delay: int = 0): ...
    def after(self, time, delay: int = 0): ...
    def at(self, time, delay: int = 0): ...

class IntervalVarStartTime(IntervalVarTimePoint):
    def __init__(self, *args, **kwd) -> None: ...

class IntervalVarEndTime(IntervalVarTimePoint):
    def __init__(self, *args, **kwd) -> None: ...

class IntervalVarLength(ScalarVar):
    def __init__(self, *args, **kwd) -> None: ...
    def get_associated_interval_var(self): ...

class IntervalVarPresence(ScalarBooleanVar):
    def __init__(self, *args, **kwd) -> None: ...
    def get_associated_interval_var(self): ...

class IntervalVarData(BlockData):
    is_present: Incomplete
    start_time: Incomplete
    end_time: Incomplete
    length: Incomplete
    def __init__(self, component=None) -> None: ...
    @property
    def optional(self): ...
    @optional.setter
    def optional(self, val) -> None: ...
    def spans(self, *args): ...

class IntervalVar(Block):
    def __new__(cls, *args, **kwds): ...

class ScalarIntervalVar(IntervalVarData, IntervalVar):
    def __init__(self, *args, **kwds) -> None: ...

class IndexedIntervalVar(IntervalVar):
    def __getitem__(self, args): ...
