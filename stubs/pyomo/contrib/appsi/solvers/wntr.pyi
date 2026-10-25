from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.errors import PyomoException as PyomoException
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer
from pyomo.contrib.appsi.base import PersistentBase as PersistentBase
from pyomo.contrib.appsi.base import PersistentSolutionLoader as PersistentSolutionLoader
from pyomo.contrib.appsi.base import PersistentSolver as PersistentSolver
from pyomo.contrib.appsi.base import Results as Results
from pyomo.contrib.appsi.base import SolverConfig as SolverConfig
from pyomo.contrib.appsi.base import TerminationCondition as TerminationCondition
from pyomo.contrib.appsi.cmodel import cmodel as cmodel
from pyomo.contrib.appsi.cmodel import cmodel_available as cmodel_available
from pyomo.core.base import NumericLabeler as NumericLabeler
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import TextLabeler as TextLabeler
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.constraint import ConstraintData as ConstraintData
from pyomo.core.base.param import ParamData as ParamData
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr.numeric_expr import AbsExpression as AbsExpression
from pyomo.core.expr.numeric_expr import DivisionExpression as DivisionExpression
from pyomo.core.expr.numeric_expr import LinearExpression as LinearExpression
from pyomo.core.expr.numeric_expr import MonomialTermExpression as MonomialTermExpression
from pyomo.core.expr.numeric_expr import NegationExpression as NegationExpression
from pyomo.core.expr.numeric_expr import NPV_AbsExpression as NPV_AbsExpression
from pyomo.core.expr.numeric_expr import NPV_DivisionExpression as NPV_DivisionExpression
from pyomo.core.expr.numeric_expr import NPV_NegationExpression as NPV_NegationExpression
from pyomo.core.expr.numeric_expr import NPV_PowExpression as NPV_PowExpression
from pyomo.core.expr.numeric_expr import NPV_ProductExpression as NPV_ProductExpression
from pyomo.core.expr.numeric_expr import NPV_SumExpression as NPV_SumExpression
from pyomo.core.expr.numeric_expr import NPV_UnaryFunctionExpression as NPV_UnaryFunctionExpression
from pyomo.core.expr.numeric_expr import PowExpression as PowExpression
from pyomo.core.expr.numeric_expr import ProductExpression as ProductExpression
from pyomo.core.expr.numeric_expr import SumExpression as SumExpression
from pyomo.core.expr.numeric_expr import UnaryFunctionExpression as UnaryFunctionExpression
from pyomo.core.expr.numvalue import native_numeric_types as native_numeric_types
from pyomo.core.expr.visitor import ExpressionValueVisitor as ExpressionValueVisitor
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager

wntr: Incomplete
wntr_available: Incomplete
logger: Incomplete

class WntrConfig(SolverConfig):
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class WntrResults(Results):
    wallclock_time: Incomplete
    solution_loader: Incomplete
    def __init__(self, solver) -> None: ...

class Wntr(PersistentBase, PersistentSolver):
    def __init__(self, only_child_vars: bool = True) -> None: ...
    def available(self): ...
    def version(self): ...
    @property
    def config(self) -> WntrConfig: ...
    @config.setter
    def config(self, val: WntrConfig): ...
    @property
    def wntr_options(self): ...
    @wntr_options.setter
    def wntr_options(self, val: dict): ...
    @property
    def symbol_map(self): ...
    def solve(self, model: BlockData, timer: HierarchicalTimer = None) -> Results: ...
    def set_instance(self, model) -> None: ...
    def update_params(self) -> None: ...
    def load_vars(self, vars_to_load=None) -> None: ...
    def get_primals(self, vars_to_load=None): ...

class PyomoToWntrVisitor(ExpressionValueVisitor):
    var_map: Incomplete
    param_map: Incomplete
    def __init__(self, var_map, param_map) -> None: ...
    def visit(self, node, values): ...
    def visiting_potential_leaf(self, node): ...
