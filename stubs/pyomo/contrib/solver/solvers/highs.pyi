from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.tee import TeeStream as TeeStream
from pyomo.common.tee import capture_output as capture_output
from pyomo.contrib.solver.common.base import Availability as Availability
from pyomo.contrib.solver.common.base import PersistentSolverBase as PersistentSolverBase
from pyomo.contrib.solver.common.config import (
    PersistentBranchAndBoundConfig as PersistentBranchAndBoundConfig,
)
from pyomo.contrib.solver.common.persistent import PersistentSolverMixin as PersistentSolverMixin
from pyomo.contrib.solver.common.persistent import PersistentSolverUtils as PersistentSolverUtils
from pyomo.contrib.solver.common.results import Results as Results
from pyomo.contrib.solver.common.results import SolutionStatus as SolutionStatus
from pyomo.contrib.solver.common.results import TerminationCondition as TerminationCondition
from pyomo.contrib.solver.common.solution_loader import (
    PersistentSolutionLoader as PersistentSolutionLoader,
)
from pyomo.contrib.solver.common.util import IncompatibleModelError as IncompatibleModelError
from pyomo.contrib.solver.common.util import NoDualsError as NoDualsError
from pyomo.contrib.solver.common.util import NoFeasibleSolutionError as NoFeasibleSolutionError
from pyomo.contrib.solver.common.util import NoOptimalSolutionError as NoOptimalSolutionError
from pyomo.contrib.solver.common.util import NoReducedCostsError as NoReducedCostsError
from pyomo.contrib.solver.common.util import NoSolutionError as NoSolutionError
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

class Highs(PersistentSolverMixin, PersistentSolverUtils, PersistentSolverBase):
    CONFIG: Incomplete
    def __init__(self, **kwds) -> None: ...
    def available(self): ...
    def version(self): ...
    def set_instance(self, model) -> None: ...
    def update_parameters(self) -> None: ...
