from pyomo.contrib.pynumero.examples.external_grey_box.react_example.reactor_model_residuals import (
    ReactorModel as ReactorModel,
)
from pyomo.contrib.pynumero.examples.external_grey_box.react_example.reactor_model_residuals import (
    ReactorModelNoOutputs as ReactorModelNoOutputs,
)
from pyomo.contrib.pynumero.examples.external_grey_box.react_example.reactor_model_residuals import (
    ReactorModelScaled as ReactorModelScaled,
)
from pyomo.contrib.pynumero.examples.external_grey_box.react_example.reactor_model_residuals import (
    ReactorModelWithHessian as ReactorModelWithHessian,
)
from pyomo.contrib.pynumero.examples.external_grey_box.react_example.reactor_model_residuals import (
    create_pyomo_reactor_model as create_pyomo_reactor_model,
)
from pyomo.contrib.pynumero.interfaces.external_grey_box import (
    ExternalGreyBoxBlock as ExternalGreyBoxBlock,
)

def maximize_cb_ratio_residuals_with_output(
    show_solver_log: bool = False, additional_options={}
): ...
def maximize_cb_ratio_residuals_with_hessian_with_output(
    show_solver_log: bool = False, additional_options={}
): ...
def maximize_cb_ratio_residuals_with_hessian_with_output_pyomo(
    show_solver_log: bool = False, additional_options={}
): ...
def maximize_cb_ratio_residuals_with_output_scaling(
    show_solver_log: bool = False, additional_options={}
): ...
def maximize_cb_ratio_residuals_with_obj(show_solver_log: bool = False, additional_options={}): ...
def maximize_cb_ratio_residuals_with_pyomo_variables(
    show_solver_log: bool = False, additional_options={}
): ...
