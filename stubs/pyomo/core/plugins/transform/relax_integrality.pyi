from pyomo.common import deprecated as deprecated
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.plugins.transform.discrete_vars import RelaxIntegerVars as RelaxIntegerVars

class RelaxIntegrality(RelaxIntegerVars):
    def __init__(self, **kwds) -> None: ...
