from collections.abc import Generator

from _typeshed import Incomplete
from pyomo.contrib.incidence_analysis.config import IncidenceMethod as IncidenceMethod
from pyomo.contrib.incidence_analysis.interface import (
    IncidenceGraphInterface as IncidenceGraphInterface,
)
from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.util.calc_var_value import (
    calculate_variable_from_constraint as calculate_variable_from_constraint,
)
from pyomo.util.subsystems import TemporarySubsystemManager as TemporarySubsystemManager
from pyomo.util.subsystems import generate_subsystem_blocks as generate_subsystem_blocks

def generate_strongly_connected_components(
    constraints, variables=None, include_fixed: bool = False, igraph=None
) -> Generator[Incomplete]: ...
def solve_strongly_connected_components(
    block, *, solver=None, solve_kwds=None, use_calc_var: bool = True, calc_var_kwds=None
): ...
