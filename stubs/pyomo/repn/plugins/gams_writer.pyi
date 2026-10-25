from _typeshed import Incomplete
from pyomo.common.gc_manager import PauseGC as PauseGC
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import NumericLabeler as NumericLabeler
from pyomo.core.base import Objective as Objective
from pyomo.core.base import ShortNameLabeler as ShortNameLabeler
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import Var as Var
from pyomo.core.base import minimize as minimize
from pyomo.core.base.component import ActiveComponent as ActiveComponent
from pyomo.core.expr.numvalue import as_numeric as as_numeric
from pyomo.core.expr.numvalue import native_numeric_types as native_numeric_types
from pyomo.core.expr.numvalue import native_types as native_types
from pyomo.core.expr.numvalue import nonpyomo_leaf_types as nonpyomo_leaf_types
from pyomo.core.expr.numvalue import value as value
from pyomo.core.expr.visitor import _ToStringVisitor
from pyomo.core.kernel.base import ICategorizedObject as ICategorizedObject
from pyomo.opt import ProblemFormat as ProblemFormat
from pyomo.opt.base import AbstractProblemWriter as AbstractProblemWriter
from pyomo.opt.base import WriterFactory as WriterFactory
from pyomo.repn.util import ftoa as ftoa
from pyomo.repn.util import valid_active_ctypes_minlp as valid_active_ctypes_minlp
from pyomo.repn.util import valid_expr_ctypes_minlp as valid_expr_ctypes_minlp

logger: Incomplete

class ToGamsVisitor(_ToStringVisitor):
    treechecker: Incomplete
    is_discontinuous: bool
    output_fixed_variables: Incomplete
    def __init__(self, smap, treechecker, output_fixed_variables: bool = False) -> None: ...
    def visiting_potential_leaf(self, node): ...

def expression_to_string(expr, treechecker, smap=None, output_fixed_variables: bool = False): ...

class Categorizer:
    binary: Incomplete
    ints: Incomplete
    positive: Incomplete
    reals: Incomplete
    fixed: Incomplete
    def __init__(self, var_list, symbol_map) -> None: ...
    def __iter__(self): ...

class StorageTreeChecker:
    tree: Incomplete
    model: Incomplete
    def __init__(self, model) -> None: ...
    def __call__(self, comp, exception_flag: bool = True): ...
    def parent_block(self, comp): ...
    def raise_error(self, comp) -> None: ...

def split_long_line(line): ...

class GAMSSymbolMap(SymbolMap):
    var_labeler: Incomplete
    var_list: Incomplete
    def __init__(self, var_labeler, var_list) -> None: ...
    def var_label(self, obj): ...
    def var_recorder(self, obj): ...

class ProblemWriter_gams(AbstractProblemWriter):
    def __init__(self) -> None: ...
    def __call__(self, model, output_filename, solver_capability, io_options): ...

valid_solvers: Incomplete
