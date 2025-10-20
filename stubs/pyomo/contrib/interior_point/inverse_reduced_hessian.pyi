from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.opt import check_optimal_termination as check_optimal_termination

from .interface import InteriorPointInterface as InteriorPointInterface
from .linalg.scipy_interface import ScipyInterface as ScipyInterface

np: Incomplete
numpy_available: Incomplete

def inv_reduced_hessian_barrier(
    model,
    independent_variables,
    bound_tolerance: float = 1e-06,
    solver_options=None,
    tee: bool = False,
): ...
