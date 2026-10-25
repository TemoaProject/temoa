from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.core.base.set import Set as Set

def get_piecewise_constant_constraints(inputs, time, sample_points, use_next: bool = True): ...
