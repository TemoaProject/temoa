import enum

from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.collections import OrderedDict as OrderedDict
from pyomo.opt.results.container import ListContainer as ListContainer
from pyomo.opt.results.container import MapContainer as MapContainer
from pyomo.opt.results.container import ignore as ignore

default_print_options: Incomplete

class SolutionStatus(str, enum.Enum):
    bestSoFar = 'bestSoFar'
    error = 'error'
    feasible = 'feasible'
    globallyOptimal = 'globallyOptimal'
    infeasible = 'infeasible'
    locallyOptimal = 'locallyOptimal'
    optimal = 'optimal'
    other = 'other'
    stoppedByLimit = 'stoppedByLimit'
    unbounded = 'unbounded'
    unknown = 'unknown'
    unsure = 'unsure'

intlist: Incomplete
numlist: Incomplete

class Solution(MapContainer):
    def __init__(self) -> None: ...
    variable: Incomplete
    constraint: Incomplete
    problem: Incomplete
    objective: Incomplete
    def load(self, repn) -> None: ...
    def pprint(self, ostream, option, from_list: bool = False, prefix: str = '', repn=None): ...

class SolutionSet(ListContainer):
    def __init__(self) -> None: ...
    def __len__(self) -> int: ...
    def __call__(self, i: int = 1): ...
    def pprint(self, ostream, option, prefix: str = '', repn=None): ...
    def load(self, repn) -> None: ...
