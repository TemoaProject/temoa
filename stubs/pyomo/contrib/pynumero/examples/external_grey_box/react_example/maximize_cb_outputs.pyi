from pyomo.contrib.pynumero.examples.external_grey_box.react_example.reactor_model_outputs import (
    ReactorConcentrationsOutputModel as ReactorConcentrationsOutputModel,
)
from pyomo.contrib.pynumero.interfaces.external_grey_box import (
    ExternalGreyBoxBlock as ExternalGreyBoxBlock,
)

def maximize_cb_outputs(show_solver_log: bool = False): ...
