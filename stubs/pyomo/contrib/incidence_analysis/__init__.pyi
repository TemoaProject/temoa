from pyomo.common.deprecation import moved_module as moved_module

from .config import IncidenceMethod as IncidenceMethod
from .incidence import get_incident_variables as get_incident_variables
from .interface import IncidenceGraphInterface as IncidenceGraphInterface
from .interface import get_bipartite_incidence_graph as get_bipartite_incidence_graph
from .matching import maximum_matching as maximum_matching
from .scc_solver import (
    generate_strongly_connected_components as generate_strongly_connected_components,
)
from .scc_solver import solve_strongly_connected_components as solve_strongly_connected_components
from .triangularize import block_triangularize as block_triangularize
