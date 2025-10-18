from pyomo.common.deprecation import deprecated as deprecated

from .doe import DesignOfExperiments as DesignOfExperiments
from .doe import FiniteDifferenceStep as FiniteDifferenceStep
from .doe import ObjectiveLib as ObjectiveLib
from .utils import rescale_FIM as rescale_FIM

deprecation_message: str

class MeasurementVariables:
    def __init__(self, *args) -> None: ...

class DesignVariables:
    def __init__(self, *args) -> None: ...

class ModelOptionLib:
    def __init__(self, *args) -> None: ...
