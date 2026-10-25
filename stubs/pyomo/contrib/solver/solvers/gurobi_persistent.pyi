from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.collections import OrderedSet as OrderedSet
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.shutdown import python_is_shutting_down as python_is_shutting_down
from pyomo.common.tee import TeeStream as TeeStream
from pyomo.common.tee import capture_output as capture_output
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer
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
from pyomo.contrib.solver.solvers.gurobi_direct import GurobiConfigMixin as GurobiConfigMixin
from pyomo.contrib.solver.solvers.gurobi_direct import GurobiSolverMixin as GurobiSolverMixin
from pyomo.core.base import NumericLabeler as NumericLabeler
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import TextLabeler as TextLabeler
from pyomo.core.base.constraint import ConstraintData as ConstraintData
from pyomo.core.base.param import ParamData as ParamData
from pyomo.core.base.sos import SOSConstraintData as SOSConstraintData
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr.numeric_expr import NPV_MaxExpression as NPV_MaxExpression
from pyomo.core.expr.numeric_expr import NPV_MinExpression as NPV_MinExpression
from pyomo.core.expr.numvalue import is_constant as is_constant
from pyomo.core.expr.numvalue import is_fixed as is_fixed
from pyomo.core.expr.numvalue import native_numeric_types as native_numeric_types
from pyomo.core.expr.numvalue import value as value
from pyomo.core.kernel.objective import maximize as maximize
from pyomo.core.kernel.objective import minimize as minimize
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.repn import generate_standard_repn as generate_standard_repn

logger: Incomplete
gurobipy: Incomplete
gurobipy_available: Incomplete

class GurobiConfig(PersistentBranchAndBoundConfig, GurobiConfigMixin):
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class GurobiSolutionLoader(PersistentSolutionLoader):
    def load_vars(self, vars_to_load=None, solution_number: int = 0) -> None: ...
    def get_primals(self, vars_to_load=None, solution_number: int = 0): ...

class _MutableLowerBound:
    var: Incomplete
    expr: Incomplete
    def __init__(self, expr) -> None: ...
    def update(self) -> None: ...

class _MutableUpperBound:
    var: Incomplete
    expr: Incomplete
    def __init__(self, expr) -> None: ...
    def update(self) -> None: ...

class _MutableLinearCoefficient:
    expr: Incomplete
    var: Incomplete
    con: Incomplete
    gurobi_model: Incomplete
    def __init__(self) -> None: ...
    def update(self) -> None: ...

class _MutableRangeConstant:
    lhs_expr: Incomplete
    rhs_expr: Incomplete
    con: Incomplete
    slack_name: Incomplete
    gurobi_model: Incomplete
    def __init__(self) -> None: ...
    def update(self) -> None: ...

class _MutableConstant:
    expr: Incomplete
    con: Incomplete
    def __init__(self) -> None: ...
    def update(self) -> None: ...

class _MutableQuadraticConstraint:
    con: Incomplete
    gurobi_model: Incomplete
    constant: Incomplete
    last_constant_value: Incomplete
    linear_coefs: Incomplete
    last_linear_coef_values: Incomplete
    quadratic_coefs: Incomplete
    last_quadratic_coef_values: Incomplete
    def __init__(
        self, gurobi_model, gurobi_con, constant, linear_coefs, quadratic_coefs
    ) -> None: ...
    def get_updated_expression(self): ...
    def get_updated_rhs(self): ...

class _MutableObjective:
    gurobi_model: Incomplete
    constant: Incomplete
    linear_coefs: Incomplete
    quadratic_coefs: Incomplete
    last_quadratic_coef_values: Incomplete
    def __init__(self, gurobi_model, constant, linear_coefs, quadratic_coefs) -> None: ...
    def get_updated_expression(self): ...

class _MutableQuadraticCoefficient:
    expr: Incomplete
    var1: Incomplete
    var2: Incomplete
    def __init__(self) -> None: ...

class GurobiPersistent(
    GurobiSolverMixin, PersistentSolverMixin, PersistentSolverUtils, PersistentSolverBase
):
    CONFIG: Incomplete
    def __init__(self, **kwds) -> None: ...
    def release_license(self) -> None: ...
    def __del__(self) -> None: ...
    @property
    def symbol_map(self): ...
    def set_instance(self, model) -> None: ...
    def update_parameters(self) -> None: ...
    def update(self, timer: HierarchicalTimer = None): ...
    def get_model_attr(self, attr): ...
    def write(self, filename) -> None: ...
    def set_linear_constraint_attr(self, con, attr, val) -> None: ...
    def set_var_attr(self, var, attr, val) -> None: ...
    def get_var_attr(self, var, attr): ...
    def get_linear_constraint_attr(self, con, attr): ...
    def get_sos_attr(self, con, attr): ...
    def get_quadratic_constraint_attr(self, con, attr): ...
    def set_gurobi_param(self, param, val) -> None: ...
    def get_gurobi_param_info(self, param): ...
    def set_callback(self, func=None) -> None: ...
    def cbCut(self, con) -> None: ...
    def cbGet(self, what): ...
    def cbGetNodeRel(self, variables) -> None: ...
    def cbGetSolution(self, variables) -> None: ...
    def cbLazy(self, con) -> None: ...
    def cbSetSolution(self, variables, solution) -> None: ...
    def cbUseSolution(self): ...
    def reset(self) -> None: ...
