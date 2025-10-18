import enum

from _typeshed import Incomplete
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import InEnum as InEnum
from pyomo.common.modeling import NOTSET as NOTSET
from pyomo.repn.ampl import AMPLRepnVisitor as AMPLRepnVisitor
from pyomo.repn.util import FileDeterminism as FileDeterminism
from pyomo.repn.util import FileDeterminism_to_SortComponents as FileDeterminism_to_SortComponents

class IncidenceMethod(enum.Enum):
    identify_variables = 0
    standard_repn = 1
    standard_repn_compute_values = 2
    ampl_repn = 3

class IncidenceOrder(enum.Enum):
    dulmage_mendelsohn_upper = 0
    dulmage_mendelsohn_lower = 1

IncidenceConfig: Incomplete

def get_config_from_kwds(**kwds): ...
