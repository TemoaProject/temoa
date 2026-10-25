from functools import singledispatchmethod

from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.dependencies import numpy_available as numpy_available
from pyomo.common.dependencies import pandas_available as pandas_available
from pyomo.common.dependencies import scipy as scipy
from pyomo.common.dependencies import scipy_available as scipy_available
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.common.deprecation import deprecation_warning as deprecation_warning
from pyomo.common.tee import capture_output as capture_output
from pyomo.dae import ContinuousSet as ContinuousSet
from pyomo.environ import Block as Block
from pyomo.environ import ComponentUID as ComponentUID
from pyomo.opt import SolverFactory as SolverFactory

use_mpisppy: bool
parmest_available: Incomplete
inverse_reduced_hessian: Incomplete
inverse_reduced_hessian_available: Incomplete
logger: Incomplete

def ef_nonants(ef): ...
def SSE(model): ...

class Estimator:
    exp_list: Incomplete
    obj_function: Incomplete
    tee: Incomplete
    diagnostic_mode: Incomplete
    solver_options: Incomplete
    pest_deprecated: Incomplete
    estimator_theta_names: Incomplete
    model_initialized: bool
    @singledispatchmethod
    def __init__(
        self,
        experiment_list,
        obj_function=None,
        tee: bool = False,
        diagnostic_mode: bool = False,
        solver_options=None,
    ) -> None: ...
    def theta_est(
        self, solver: str = 'ef_ipopt', return_values=[], calc_cov: bool = False, cov_n=None
    ): ...
    def theta_est_bootstrap(
        self,
        bootstrap_samples,
        samplesize=None,
        replacement: bool = True,
        seed=None,
        return_samples: bool = False,
    ): ...
    def theta_est_leaveNout(
        self, lNo, lNo_samples=None, seed=None, return_samples: bool = False
    ): ...
    def leaveNout_bootstrap_test(
        self, lNo, lNo_samples, bootstrap_samples, distribution, alphas, seed=None
    ): ...
    theta_names_updated: Incomplete
    def objective_at_theta(self, theta_values=None, initialize_parmest_model: bool = False): ...
    def likelihood_ratio_test(
        self, obj_at_theta, obj_value, alphas, return_thresholds: bool = False
    ): ...
    def confidence_region_test(
        self, theta_values, distribution, alphas, test_theta_values=None
    ): ...

def group_data(data, groupby_column_name, use_mean=None): ...

class _DeprecatedSecondStageCostExpr:
    def __init__(self, ssc_function, data) -> None: ...
    def __call__(self, model): ...

class _DeprecatedEstimator:
    model_function: Incomplete
    callback_data: Incomplete
    theta_names: Incomplete
    obj_function: Incomplete
    tee: Incomplete
    diagnostic_mode: Incomplete
    solver_options: Incomplete
    model_initialized: bool
    def __init__(
        self,
        model_function,
        data,
        theta_names,
        obj_function=None,
        tee: bool = False,
        diagnostic_mode: bool = False,
        solver_options=None,
    ) -> None: ...
    def theta_est(
        self, solver: str = 'ef_ipopt', return_values=[], calc_cov: bool = False, cov_n=None
    ): ...
    def theta_est_bootstrap(
        self,
        bootstrap_samples,
        samplesize=None,
        replacement: bool = True,
        seed=None,
        return_samples: bool = False,
    ): ...
    def theta_est_leaveNout(
        self, lNo, lNo_samples=None, seed=None, return_samples: bool = False
    ): ...
    def leaveNout_bootstrap_test(
        self, lNo, lNo_samples, bootstrap_samples, distribution, alphas, seed=None
    ): ...
    theta_names_updated: Incomplete
    def objective_at_theta(self, theta_values=None, initialize_parmest_model: bool = False): ...
    def likelihood_ratio_test(
        self, obj_at_theta, obj_value, alphas, return_thresholds: bool = False
    ): ...
    def confidence_region_test(
        self, theta_values, distribution, alphas, test_theta_values=None
    ): ...
