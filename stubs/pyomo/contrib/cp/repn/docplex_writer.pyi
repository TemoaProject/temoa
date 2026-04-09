import types

from _typeshed import Incomplete
from pyomo.common import DeveloperError as DeveloperError
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.fileutils import Executable as Executable
from pyomo.contrib.cp import IntervalVar as IntervalVar
from pyomo.contrib.cp.interval_var import IndexedIntervalVar as IndexedIntervalVar
from pyomo.contrib.cp.interval_var import IntervalVarData as IntervalVarData
from pyomo.contrib.cp.interval_var import IntervalVarEndTime as IntervalVarEndTime
from pyomo.contrib.cp.interval_var import IntervalVarLength as IntervalVarLength
from pyomo.contrib.cp.interval_var import IntervalVarPresence as IntervalVarPresence
from pyomo.contrib.cp.interval_var import IntervalVarStartTime as IntervalVarStartTime
from pyomo.contrib.cp.interval_var import ScalarIntervalVar as ScalarIntervalVar
from pyomo.contrib.cp.scheduling_expr.precedence_expressions import AtExpression as AtExpression
from pyomo.contrib.cp.scheduling_expr.precedence_expressions import (
    BeforeExpression as BeforeExpression,
)
from pyomo.contrib.cp.scheduling_expr.scheduling_logic import (
    AlternativeExpression as AlternativeExpression,
)
from pyomo.contrib.cp.scheduling_expr.scheduling_logic import SpanExpression as SpanExpression
from pyomo.contrib.cp.scheduling_expr.scheduling_logic import (
    SynchronizeExpression as SynchronizeExpression,
)
from pyomo.contrib.cp.scheduling_expr.sequence_expressions import (
    BeforeInSequenceExpression as BeforeInSequenceExpression,
)
from pyomo.contrib.cp.scheduling_expr.sequence_expressions import (
    FirstInSequenceExpression as FirstInSequenceExpression,
)
from pyomo.contrib.cp.scheduling_expr.sequence_expressions import (
    LastInSequenceExpression as LastInSequenceExpression,
)
from pyomo.contrib.cp.scheduling_expr.sequence_expressions import (
    NoOverlapExpression as NoOverlapExpression,
)
from pyomo.contrib.cp.scheduling_expr.sequence_expressions import (
    PredecessorToExpression as PredecessorToExpression,
)
from pyomo.contrib.cp.scheduling_expr.step_function_expressions import AlwaysIn as AlwaysIn
from pyomo.contrib.cp.scheduling_expr.step_function_expressions import (
    CumulativeFunction as CumulativeFunction,
)
from pyomo.contrib.cp.scheduling_expr.step_function_expressions import (
    NegatedStepFunction as NegatedStepFunction,
)
from pyomo.contrib.cp.scheduling_expr.step_function_expressions import Pulse as Pulse
from pyomo.contrib.cp.scheduling_expr.step_function_expressions import StepAt as StepAt
from pyomo.contrib.cp.scheduling_expr.step_function_expressions import StepAtEnd as StepAtEnd
from pyomo.contrib.cp.scheduling_expr.step_function_expressions import StepAtStart as StepAtStart
from pyomo.contrib.cp.sequence_var import ScalarSequenceVar as ScalarSequenceVar
from pyomo.contrib.cp.sequence_var import SequenceVar as SequenceVar
from pyomo.contrib.cp.sequence_var import SequenceVarData as SequenceVarData
from pyomo.core.base import Block as Block
from pyomo.core.base import BooleanVar as BooleanVar
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import LogicalConstraint as LogicalConstraint
from pyomo.core.base import Objective as Objective
from pyomo.core.base import Param as Param
from pyomo.core.base import RangeSet as RangeSet
from pyomo.core.base import Set as Set
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import Suffix as Suffix
from pyomo.core.base import Var as Var
from pyomo.core.base import maximize as maximize
from pyomo.core.base import minimize as minimize
from pyomo.core.base import value as value
from pyomo.core.base.boolean_var import BooleanVarData as BooleanVarData
from pyomo.core.base.boolean_var import IndexedBooleanVar as IndexedBooleanVar
from pyomo.core.base.boolean_var import ScalarBooleanVar as ScalarBooleanVar
from pyomo.core.base.expression import ExpressionData as ExpressionData
from pyomo.core.base.expression import ScalarExpression as ScalarExpression
from pyomo.core.base.param import IndexedParam as IndexedParam
from pyomo.core.base.param import ParamData as ParamData
from pyomo.core.base.param import ScalarParam as ScalarParam
from pyomo.core.base.set import SetProduct as SetProduct
from pyomo.core.base.var import IndexedVar as IndexedVar
from pyomo.core.base.var import ScalarVar as ScalarVar
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor
from pyomo.core.expr.visitor import identify_variables as identify_variables
from pyomo.network import Port as Port
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.opt import SolverResults as SolverResults
from pyomo.opt import TerminationCondition as TerminationCondition
from pyomo.opt import WriterFactory as WriterFactory
from pyomo.repn.util import ExitNodeDispatcher as ExitNodeDispatcher

cp: Incomplete
docplex_available: Incomplete
cp_solver: Incomplete
logger: Incomplete

class _GENERAL: ...
class _START_TIME: ...
class _END_TIME: ...
class _DEFERRED_ELEMENT_CONSTRAINT: ...
class _ELEMENT_CONSTRAINT: ...
class _DEFERRED_BEFORE: ...
class _DEFERRED_AFTER: ...
class _DEFERRED_AT: ...
class _BEFORE: ...
class _AT: ...
class _IMPLIES: ...
class _LAND: ...
class _LOR: ...
class _XOR: ...
class _EQUIVALENT_TO: ...

step_func_expression_types: Incomplete

class LogicalToDoCplex(StreamBasedExpressionVisitor):
    exit_node_dispatcher: Incomplete
    cpx: Incomplete
    symbolic_solver_labels: Incomplete
    var_map: Incomplete
    pyomo_to_docplex: Incomplete
    def __init__(self, cpx_model, symbolic_solver_labels: bool = False) -> None: ...
    def initializeWalker(self, expr): ...
    def beforeChild(self, node, child, child_idx): ...
    def exitNode(self, node, data): ...
    finalizeResult: Incomplete

def collect_valid_components(model, active: bool = True, sort=None, valid=..., targets=...): ...

class DocplexWriter:
    CONFIG: Incomplete
    config: Incomplete
    def __init__(self) -> None: ...
    def write(self, model, **options): ...

class CPOptimizerSolver:
    CONFIG: Incomplete
    config: Incomplete
    def __init__(self, **kwds) -> None: ...
    @property
    def options(self): ...
    def __enter__(self): ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
    def available(self, exception_flag: bool = True): ...
    def license_is_valid(self): ...
    def solve(self, model, **kwds): ...
