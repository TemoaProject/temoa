from pyomo.contrib.incidence_analysis.config import IncidenceMethod as IncidenceMethod
from pyomo.contrib.incidence_analysis.config import get_config_from_kwds as get_config_from_kwds
from pyomo.core.expr.visitor import identify_variables as identify_variables
from pyomo.repn import generate_standard_repn as generate_standard_repn
from pyomo.util.subsystems import TemporarySubsystemManager as TemporarySubsystemManager

def get_incident_variables(expr, **kwds): ...
