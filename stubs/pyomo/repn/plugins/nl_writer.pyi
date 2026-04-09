import types
from typing import NamedTuple

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import InEnum as InEnum
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.deprecation import relocated_module_attribute as relocated_module_attribute
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.common.errors import InfeasibleConstraintException as InfeasibleConstraintException
from pyomo.common.gc_manager import PauseGC as PauseGC
from pyomo.common.timing import TicTocTimer as TicTocTimer
from pyomo.core.base import Block as Block
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Expression as Expression
from pyomo.core.base import ExternalFunction as ExternalFunction
from pyomo.core.base import NameLabeler as NameLabeler
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
from pyomo.core.base.constraint import ConstraintData as ConstraintData
from pyomo.core.base.expression import ExpressionData as ExpressionData
from pyomo.core.base.expression import ScalarExpression as ScalarExpression
from pyomo.core.base.objective import ObjectiveData as ObjectiveData
from pyomo.core.base.objective import ScalarObjective as ScalarObjective
from pyomo.core.base.suffix import SuffixFinder as SuffixFinder
from pyomo.core.base.var import VarData as VarData
from pyomo.core.pyomoobject import PyomoObject as PyomoObject
from pyomo.network import Port as Port
from pyomo.opt import WriterFactory as WriterFactory
from pyomo.repn.ampl import TOL as TOL
from pyomo.repn.ampl import AMPLRepnVisitor as AMPLRepnVisitor
from pyomo.repn.ampl import evaluate_ampl_nl_expression as evaluate_ampl_nl_expression
from pyomo.repn.plugins.ampl.ampl_ import set_pyomo_amplfunc_env as set_pyomo_amplfunc_env
from pyomo.repn.util import FileDeterminism as FileDeterminism
from pyomo.repn.util import FileDeterminism_to_SortComponents as FileDeterminism_to_SortComponents
from pyomo.repn.util import categorize_valid_components as categorize_valid_components
from pyomo.repn.util import (
    initialize_var_map_from_column_order as initialize_var_map_from_column_order,
)
from pyomo.repn.util import int_float as int_float
from pyomo.repn.util import ordered_active_constraints as ordered_active_constraints

logger: Incomplete
inf: Incomplete
minus_inf: Incomplete
allowable_binary_var_bounds: Incomplete

class ScalingFactors(NamedTuple):
    variables: Incomplete
    constraints: Incomplete
    objectives: Incomplete

class NLWriterInfo:
    variables: Incomplete
    constraints: Incomplete
    objectives: Incomplete
    external_function_libraries: Incomplete
    row_labels: Incomplete
    column_labels: Incomplete
    eliminated_vars: Incomplete
    scaling: Incomplete
    def __init__(
        self, var, con, obj, external_libs, row_labels, col_labels, eliminated_vars, scaling
    ) -> None: ...

class NLWriter:
    CONFIG: Incomplete
    config: Incomplete
    def __init__(self) -> None: ...
    def __call__(self, model, filename, solver_capability, io_options): ...
    def write(self, model, ostream, rowstream=None, colstream=None, **options) -> NLWriterInfo: ...

class _SuffixData:
    name: Incomplete
    obj: Incomplete
    con: Incomplete
    var: Incomplete
    prob: Incomplete
    datatype: Incomplete
    values: Incomplete
    def __init__(self, name) -> None: ...
    def update(self, suffix) -> None: ...
    def store(self, obj, val) -> None: ...
    def compile(self, column_order, row_order, obj_order, model_id) -> None: ...

class CachingNumericSuffixFinder(SuffixFinder):
    scale: bool
    suffix_cache: Incomplete
    def __init__(self, name, default=None, context=None) -> None: ...
    def __call__(self, obj): ...

class _NoScalingFactor:
    scale: bool
    def __call__(self, obj): ...

class _NLWriter_impl:
    ostream: Incomplete
    rowstream: Incomplete
    colstream: Incomplete
    config: Incomplete
    symbolic_solver_labels: Incomplete
    subexpression_cache: Incomplete
    subexpression_order: Incomplete
    external_functions: Incomplete
    used_named_expressions: Incomplete
    var_map: Incomplete
    var_id_to_nl_map: Incomplete
    sorter: Incomplete
    visitor: Incomplete
    next_V_line_id: int
    pause_gc: Incomplete
    template: Incomplete
    def __init__(self, ostream, rowstream, colstream, config) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None: ...
    column_order: Incomplete
    def write(self, model): ...
