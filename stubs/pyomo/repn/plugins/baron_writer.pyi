from _typeshed import Incomplete
from pyomo.common.collections import OrderedSet as OrderedSet
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import NumericLabeler as NumericLabeler
from pyomo.core.base import Objective as Objective
from pyomo.core.base import Param as Param
from pyomo.core.base import ShortNameLabeler as ShortNameLabeler
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base.component import ActiveComponent as ActiveComponent
from pyomo.core.expr.numvalue import native_numeric_types as native_numeric_types
from pyomo.core.expr.numvalue import native_types as native_types
from pyomo.core.expr.numvalue import nonpyomo_leaf_types as nonpyomo_leaf_types
from pyomo.core.expr.numvalue import value as value
from pyomo.core.expr.visitor import _ToStringVisitor
from pyomo.core.kernel.block import IBlock as IBlock
from pyomo.opt import ProblemFormat as ProblemFormat
from pyomo.opt.base import AbstractProblemWriter as AbstractProblemWriter
from pyomo.opt.base import WriterFactory as WriterFactory
from pyomo.repn.util import ftoa as ftoa
from pyomo.repn.util import valid_active_ctypes_minlp as valid_active_ctypes_minlp
from pyomo.repn.util import valid_expr_ctypes_minlp as valid_expr_ctypes_minlp

logger: Incomplete

class ToBaronVisitor(_ToStringVisitor):
    variables: Incomplete
    def __init__(self, variables, smap) -> None: ...
    def visiting_potential_leaf(self, node): ...

def expression_to_string(expr, variables, smap): ...

class ProblemWriter_bar(AbstractProblemWriter):
    def __init__(self) -> None: ...
    def __call__(self, model, output_filename, solver_capability, io_options): ...
