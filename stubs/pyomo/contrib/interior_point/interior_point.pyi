import enum
import types

from _typeshed import Incomplete
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer
from pyomo.contrib.pynumero.interfaces.utils import build_bounds_mask as build_bounds_mask
from pyomo.contrib.pynumero.interfaces.utils import (
    build_compression_matrix as build_compression_matrix,
)
from pyomo.contrib.pynumero.linalg.base import LinearSolverStatus as LinearSolverStatus

ip_logger: Incomplete

class InteriorPointStatus(enum.Enum):
    optimal = 0
    error = 1

class LinearSolveContext:
    interior_point_logger: Incomplete
    linear_solver_logger: Incomplete
    filename: Incomplete
    handler: Incomplete
    def __init__(
        self, interior_point_logger, linear_solver_logger, filename=None, level=...
    ) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        et: type[BaseException] | None,
        ev: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None: ...

class FactorizationContext:
    logger: Incomplete
    def __init__(self, logger) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        et: type[BaseException] | None,
        ev: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None: ...
    def log_header(self) -> None: ...
    def log_info(self, _iter, reg_iter, num_realloc, coef, neg_eig, status) -> None: ...

class InteriorPointSolver:
    linear_solver: Incomplete
    max_iter: Incomplete
    tol: Incomplete
    linear_solver_log_filename: Incomplete
    max_reallocation_iterations: Incomplete
    reallocation_factor: Incomplete
    base_eq_reg_coef: float
    hess_reg_coef: float
    max_reg_iter: int
    reg_factor_increase: int
    logger: Incomplete
    factorization_context: Incomplete
    linear_solver_logger: Incomplete
    linear_solve_context: Incomplete
    def __init__(
        self,
        linear_solver,
        max_iter: int = 100,
        tol: float = 1e-08,
        linear_solver_log_filename=None,
        max_reallocation_iterations: int = 5,
        reallocation_factor: int = 2,
    ) -> None: ...
    def update_barrier_parameter(self) -> None: ...
    def set_linear_solver(self, linear_solver) -> None: ...
    interface: Incomplete
    def set_interface(self, interface) -> None: ...
    def solve(self, interface, timer=None, report_timing: bool = False): ...
    def factorize(self, kkt, timer=None): ...
    def process_init(self, x, lb, ub) -> None: ...
    def process_init_duals_lb(self, x, lb) -> None: ...
    def process_init_duals_ub(self, x, ub) -> None: ...
    def check_convergence(self, barrier, timer=None): ...
    def fraction_to_the_boundary(self): ...

def try_factorization_and_reallocation(
    kkt, linear_solver, reallocation_factor, max_iter, timer=None
): ...
def fraction_to_the_boundary(interface, tau): ...
def process_init(x, lb, ub) -> None: ...
def process_init_duals_lb(x, lb) -> None: ...
def process_init_duals_ub(x, ub) -> None: ...
