from pyomo.contrib.gdpopt.util import time_code as time_code
from pyomo.contrib.mcpp.pyomo_mcpp import MCPP_Error as MCPP_Error
from pyomo.core import minimize as minimize
from pyomo.core import value as value

def add_oa_cuts(
    target_model,
    dual_values,
    jacobians,
    objective_sense,
    mip_constraint_polynomial_degree,
    mip_iter,
    config,
    timing,
    cb_opt=None,
    linearize_active: bool = True,
    linearize_violated: bool = True,
) -> None: ...
def add_oa_cuts_for_grey_box(
    target_model, jacobians_model, config, objective_sense, mip_iter, cb_opt=None
) -> None: ...
def add_ecp_cuts(
    target_model,
    jacobians,
    config,
    timing,
    linearize_active: bool = True,
    linearize_violated: bool = True,
) -> None: ...
def add_no_good_cuts(
    target_model, var_values, config, timing, mip_iter: int = 0, cb_opt=None
) -> None: ...
def add_affine_cuts(target_model, config, timing) -> None: ...
