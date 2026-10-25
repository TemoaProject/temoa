from typing import NamedTuple

from _typeshed import Incomplete
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import InEnum as InEnum
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.dependencies import scipy as scipy
from pyomo.common.enums import ObjectiveSense as ObjectiveSense
from pyomo.common.gc_manager import PauseGC as PauseGC
from pyomo.common.numeric_types import native_types as native_types
from pyomo.common.numeric_types import value as value
from pyomo.common.timing import TicTocTimer as TicTocTimer
from pyomo.core.base import Block as Block
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Expression as Expression
from pyomo.core.base import ExternalFunction as ExternalFunction
from pyomo.core.base import Objective as Objective
from pyomo.core.base import Param as Param
from pyomo.core.base import RangeSet as RangeSet
from pyomo.core.base import Set as Set
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import Suffix as Suffix
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import Var as Var
from pyomo.network import Port as Port
from pyomo.opt import WriterFactory as WriterFactory
from pyomo.repn.linear import LinearRepnVisitor as LinearRepnVisitor
from pyomo.repn.linear_template import LinearTemplateRepnVisitor as LinearTemplateRepnVisitor
from pyomo.repn.util import FileDeterminism as FileDeterminism
from pyomo.repn.util import FileDeterminism_to_SortComponents as FileDeterminism_to_SortComponents
from pyomo.repn.util import TemplateVarRecorder as TemplateVarRecorder
from pyomo.repn.util import categorize_valid_components as categorize_valid_components
from pyomo.repn.util import (
    initialize_var_map_from_column_order as initialize_var_map_from_column_order,
)
from pyomo.repn.util import ordered_active_constraints as ordered_active_constraints

logger: Incomplete

class RowEntry(NamedTuple):
    constraint: Incomplete
    bound_type: Incomplete

class LinearStandardFormInfo:
    c: Incomplete
    c_offset: Incomplete
    A: Incomplete
    rhs: Incomplete
    rows: Incomplete
    columns: Incomplete
    objectives: Incomplete
    eliminated_vars: Incomplete
    def __init__(self, c, c_offset, A, rhs, rows, columns, objectives, eliminated_vars) -> None: ...
    @property
    def x(self): ...
    @property
    def b(self): ...

class LinearStandardFormCompiler:
    CONFIG: Incomplete
    config: Incomplete
    def __init__(self) -> None: ...
    def write(self, model, ostream=None, **options): ...

class _LinearStandardFormCompiler_impl:
    config: Incomplete
    def __init__(self, config) -> None: ...
    var_map: Incomplete
    def write(self, model): ...
