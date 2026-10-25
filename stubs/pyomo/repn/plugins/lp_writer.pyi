from _typeshed import Incomplete
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import InEnum as InEnum
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.gc_manager import PauseGC as PauseGC
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
from pyomo.core.base import SOSConstraint as SOSConstraint
from pyomo.core.base import Suffix as Suffix
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import Var as Var
from pyomo.core.base import minimize as minimize
from pyomo.core.base.component import ActiveComponent as ActiveComponent
from pyomo.core.base.label import LPFileLabeler as LPFileLabeler
from pyomo.core.base.label import NumericLabeler as NumericLabeler
from pyomo.network import Port as Port
from pyomo.opt import WriterFactory as WriterFactory
from pyomo.repn.linear import LinearRepnVisitor as LinearRepnVisitor
from pyomo.repn.quadratic import QuadraticRepnVisitor as QuadraticRepnVisitor
from pyomo.repn.util import FileDeterminism as FileDeterminism
from pyomo.repn.util import FileDeterminism_to_SortComponents as FileDeterminism_to_SortComponents
from pyomo.repn.util import OrderedVarRecorder as OrderedVarRecorder
from pyomo.repn.util import categorize_valid_components as categorize_valid_components
from pyomo.repn.util import (
    initialize_var_map_from_column_order as initialize_var_map_from_column_order,
)
from pyomo.repn.util import int_float as int_float
from pyomo.repn.util import ordered_active_constraints as ordered_active_constraints

logger: Incomplete
inf: Incomplete
neg_inf: Incomplete

class LPWriterInfo:
    symbol_map: Incomplete
    def __init__(self, symbol_map) -> None: ...

class LPWriter:
    CONFIG: Incomplete
    config: Incomplete
    def __init__(self) -> None: ...
    def __call__(self, model, filename, solver_capability, io_options): ...
    def write(self, model, ostream, **options): ...

class _LPWriter_impl:
    ostream: Incomplete
    config: Incomplete
    symbol_map: Incomplete
    def __init__(self, ostream, config) -> None: ...
    sorter: Incomplete
    var_map: Incomplete
    var_order: Incomplete
    var_recorder: Incomplete
    def write(self, model): ...
    def write_expression(self, ostream, expr, is_objective): ...
