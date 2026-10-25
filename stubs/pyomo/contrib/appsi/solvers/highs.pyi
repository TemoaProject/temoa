from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import NonNegativeInt as NonNegativeInt
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.errors import PyomoException as PyomoException
from pyomo.common.log import LogStream as LogStream
from pyomo.common.tee import TeeStream as TeeStream
from pyomo.common.tee import capture_output as capture_output
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer
from pyomo.contrib.appsi.base import MIPSolverConfig as MIPSolverConfig
from pyomo.contrib.appsi.base import PersistentBase as PersistentBase
from pyomo.contrib.appsi.base import PersistentSolutionLoader as PersistentSolutionLoader
from pyomo.contrib.appsi.base import PersistentSolver as PersistentSolver
from pyomo.contrib.appsi.base import Results as Results
from pyomo.contrib.appsi.base import TerminationCondition as TerminationCondition
from pyomo.contrib.appsi.cmodel import cmodel as cmodel
from pyomo.contrib.appsi.cmodel import cmodel_available as cmodel_available
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base.constraint import ConstraintData as ConstraintData
from pyomo.core.base.param import ParamData as ParamData
from pyomo.core.base.sos import SOSConstraintData as SOSConstraintData
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr.numeric_expr import NPV_MaxExpression as NPV_MaxExpression
from pyomo.core.expr.numeric_expr import NPV_MinExpression as NPV_MinExpression
from pyomo.core.expr.numvalue import is_constant as is_constant
from pyomo.core.expr.numvalue import value as value
from pyomo.core.kernel.objective import maximize as maximize
from pyomo.core.kernel.objective import minimize as minimize
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.repn import generate_standard_repn as generate_standard_repn

logger: Incomplete
highspy: Incomplete
highspy_available: Incomplete

class DegreeError(PyomoException): ...

class HighsConfig(MIPSolverConfig):
    logfile: str
    solver_output_logger: Incomplete
    log_level: Incomplete
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class HighsResults(Results):
    wallclock_time: Incomplete
    solution_loader: Incomplete
    def __init__(self, solver) -> None: ...

class _MutableVarBounds:
    pyomo_var_id: Incomplete
    lower_expr: Incomplete
    upper_expr: Incomplete
    var_map: Incomplete
    highs: Incomplete
    def __init__(self, lower_expr, upper_expr, pyomo_var_id, var_map, highs) -> None: ...
    def update(self) -> None: ...

class _MutableLinearCoefficient:
    expr: Incomplete
    highs: Incomplete
    pyomo_var_id: Incomplete
    pyomo_con: Incomplete
    con_map: Incomplete
    var_map: Incomplete
    def __init__(self, pyomo_con, pyomo_var_id, con_map, var_map, expr, highs) -> None: ...
    def update(self) -> None: ...

class _MutableObjectiveCoefficient:
    expr: Incomplete
    highs: Incomplete
    pyomo_var_id: Incomplete
    var_map: Incomplete
    def __init__(self, pyomo_var_id, var_map, expr, highs) -> None: ...
    def update(self) -> None: ...

class _MutableObjectiveOffset:
    expr: Incomplete
    highs: Incomplete
    def __init__(self, expr, highs) -> None: ...
    def update(self) -> None: ...

class _MutableConstraintBounds:
    lower_expr: Incomplete
    upper_expr: Incomplete
    con: Incomplete
    con_map: Incomplete
    highs: Incomplete
    def __init__(self, lower_expr, upper_expr, pyomo_con, con_map, highs) -> None: ...
    def update(self) -> None: ...

class Highs(PersistentBase, PersistentSolver):
    def __init__(self, only_child_vars: bool = False) -> None: ...
    def available(self): ...
    def version(self): ...
    @property
    def config(self) -> HighsConfig: ...
    @config.setter
    def config(self, val: HighsConfig): ...
    @property
    def highs_options(self): ...
    @highs_options.setter
    def highs_options(self, val: dict): ...
    @property
    def symbol_map(self): ...
    def warm_start_capable(self): ...
    def solve(self, model, timer: HierarchicalTimer = None) -> Results: ...
    def set_instance(self, model) -> None: ...
    def update_params(self) -> None: ...
    def load_vars(self, vars_to_load=None) -> None: ...
    def get_primals(self, vars_to_load=None, solution_number: int = 0): ...
    def get_reduced_costs(self, vars_to_load=None): ...
    def get_duals(self, cons_to_load=None): ...
    def get_slacks(self, cons_to_load=None): ...
