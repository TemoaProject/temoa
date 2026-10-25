from networkx.algorithms.components import connected_components as connected_components
from pyomo.common.dependencies import networkx_available as networkx_available

def dulmage_mendelsohn(bg, top_nodes=None, matching=None): ...
