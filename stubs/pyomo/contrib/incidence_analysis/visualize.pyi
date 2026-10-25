from pyomo.common.dependencies import matplotlib as matplotlib
from pyomo.contrib.incidence_analysis.config import IncidenceOrder as IncidenceOrder
from pyomo.contrib.incidence_analysis.interface import (
    IncidenceGraphInterface as IncidenceGraphInterface,
)
from pyomo.contrib.incidence_analysis.interface import (
    get_structural_incidence_matrix as get_structural_incidence_matrix,
)

def spy_dulmage_mendelsohn(
    model,
    *,
    incidence_kwds=None,
    order=...,
    highlight_coarse: bool = True,
    highlight_fine: bool = True,
    skip_wellconstrained: bool = False,
    ax=None,
    linewidth: int = 2,
    spy_kwds=None,
): ...
