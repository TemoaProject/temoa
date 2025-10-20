from enum import Enum

from _typeshed import Incomplete
from pyomo.common.dependencies import numpy_available as numpy_available
from pyomo.common.dependencies import pathlib as pathlib
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.common.timing import TicTocTimer as TicTocTimer
from pyomo.contrib.sensitivity_toolbox.sens import get_dsdp as get_dsdp
from pyomo.opt import SolverStatus as SolverStatus

class ObjectiveLib(Enum):
    determinant = 'determinant'
    trace = 'trace'
    minimum_eigenvalue = 'minimum_eigenvalue'
    zero = 'zero'

class FiniteDifferenceStep(Enum):
    forward = 'forward'
    central = 'central'
    backward = 'backward'

class DesignOfExperiments:
    experiment: Incomplete
    fd_formula: Incomplete
    step: Incomplete
    objective_option: Incomplete
    scale_constant_value: Incomplete
    scale_nominal_param_value: Incomplete
    prior_FIM: Incomplete
    jac_initial: Incomplete
    fim_initial: Incomplete
    L_diagonal_lower_bound: Incomplete
    solver: Incomplete
    tee: Incomplete
    get_labeled_model_args: Incomplete
    logger: Incomplete
    Cholesky_option: Incomplete
    only_compute_fim_lower: Incomplete
    model: Incomplete
    results: Incomplete
    def __init__(
        self,
        experiment=None,
        fd_formula: str = 'central',
        step: float = 0.001,
        objective_option: str = 'determinant',
        scale_constant_value: float = 1.0,
        scale_nominal_param_value: bool = False,
        prior_FIM=None,
        jac_initial=None,
        fim_initial=None,
        L_diagonal_lower_bound: float = 1e-07,
        solver=None,
        tee: bool = False,
        get_labeled_model_args=None,
        logger_level=...,
        _Cholesky_option: bool = True,
        _only_compute_fim_lower: bool = True,
    ) -> None: ...
    def run_doe(self, model=None, results_file=None) -> None: ...
    def run_multi_doe_sequential(self, N_exp: int = 1) -> None: ...
    def run_multi_doe_simultaneous(self, N_exp: int = 1) -> None: ...
    compute_FIM_model: Incomplete
    n_parameters: Incomplete
    n_measurement_error: Incomplete
    n_experiment_inputs: Incomplete
    n_experiment_outputs: Incomplete
    def compute_FIM(self, model=None, method: str = 'sequential'): ...
    def create_doe_model(self, model=None): ...
    def create_objective_function(self, model=None): ...
    def check_model_labels(self, model=None) -> None: ...
    def check_model_FIM(self, model=None, FIM=None) -> None: ...
    def check_model_jac(self, jac=None) -> None: ...
    def update_FIM_prior(self, model=None, FIM=None) -> None: ...
    def update_unknown_parameter_values(self, model=None, param_vals=None) -> None: ...
    factorial_model: Incomplete
    fim_factorial_results: Incomplete
    def compute_FIM_full_factorial(
        self, model=None, design_ranges=None, method: str = 'sequential'
    ): ...
    figure_result_data: Incomplete
    figure_sens_des_vars: Incomplete
    figure_fixed_des_vars: Incomplete
    def draw_factorial_figure(
        self,
        results=None,
        sensitivity_design_variables=None,
        fixed_design_variables=None,
        full_design_variable_names=None,
        title_text: str = '',
        xlabel_text: str = '',
        ylabel_text: str = '',
        figure_file_name=None,
        font_axes: int = 16,
        font_tick: int = 14,
        log_scale: bool = True,
    ) -> None: ...
    def get_FIM(self, model=None): ...
    def get_sensitivity_matrix(self, model=None): ...
    def get_experiment_input_values(self, model=None): ...
    def get_unknown_parameter_values(self, model=None): ...
    def get_experiment_output_values(self, model=None): ...
    def get_measurement_error_values(self, model=None): ...
