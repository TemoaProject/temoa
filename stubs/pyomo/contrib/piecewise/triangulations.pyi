from enum import Enum

from _typeshed import Incomplete
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.contrib.piecewise.ordered_3d_j1_triangulation_data import (
    get_hamiltonian_paths as get_hamiltonian_paths,
)

class Triangulation(Enum):
    Unknown = 0
    AssumeValid = 1
    Delaunay = 2
    J1 = 3
    OrderedJ1 = 4

class _Triangulation:
    points: Incomplete
    simplices: Incomplete
    coplanar: Incomplete
    def __init__(self, points, simplices, coplanar) -> None: ...

def get_unordered_j1_triangulation(points, dimension): ...
def get_ordered_j1_triangulation(points, dimension): ...

class Direction(Enum):
    left = 0
    down = 1
    up = 2
    right = 3
