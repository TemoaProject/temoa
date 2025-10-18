from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Objective as Objective
from pyomo.core.base import SOSConstraint as SOSConstraint
from pyomo.core.base import Suffix as Suffix
from pyomo.core.base import Var as Var
from pyomo.core.expr.numvalue import is_fixed as is_fixed
from pyomo.core.expr.numvalue import value as value
from pyomo.core.kernel.objective import maximize as maximize
from pyomo.core.kernel.objective import minimize as minimize
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.opt.base import SolverFactory as SolverFactory
from pyomo.opt.results.results_ import SolverResults as SolverResults
from pyomo.opt.results.solution import Solution as Solution
from pyomo.opt.results.solution import SolutionStatus as SolutionStatus
from pyomo.opt.results.solver import SolverStatus as SolverStatus
from pyomo.opt.results.solver import TerminationCondition as TerminationCondition
from pyomo.repn import generate_standard_repn as generate_standard_repn
from pyomo.solvers.plugins.solvers.direct_or_persistent_solver import (
    DirectOrPersistentSolver as DirectOrPersistentSolver,
)
from pyomo.solvers.plugins.solvers.direct_solver import DirectSolver as DirectSolver

logger: Incomplete

class DegreeError(ValueError): ...

class _CplexExpr:
    variables: Incomplete
    coefficients: Incomplete
    offset: Incomplete
    q_variables1: Incomplete
    q_variables2: Incomplete
    q_coefficients: Incomplete
    def __init__(
        self,
        variables,
        coefficients,
        offset=None,
        q_variables1=None,
        q_variables2=None,
        q_coefficients=None,
    ) -> None: ...

class _VariableData:
    lb: Incomplete
    ub: Incomplete
    types: Incomplete
    names: Incomplete
    def __init__(self, solver_model) -> None: ...
    def add(self, lb, ub, type_, name) -> None: ...
    def store_in_cplex(self) -> None: ...

class _LinearConstraintData:
    lin_expr: Incomplete
    senses: Incomplete
    rhs: Incomplete
    range_values: Incomplete
    names: Incomplete
    def __init__(self, solver_model) -> None: ...
    def add(self, cplex_expr, sense, rhs, range_values, name) -> None: ...
    def store_in_cplex(self) -> None: ...

class CPLEXDirect(DirectSolver):
    def __init__(self, **kwds) -> None: ...
    def warm_start_capable(self): ...
    def load_duals(self, cons_to_load=None) -> None: ...
    def load_rc(self, vars_to_load) -> None: ...
    def load_slacks(self, cons_to_load=None) -> None: ...
