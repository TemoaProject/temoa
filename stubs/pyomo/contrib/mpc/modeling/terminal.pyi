from pyomo.contrib.mpc.data.scalar_data import ScalarData as ScalarData
from pyomo.contrib.mpc.data.series_data import get_indexed_cuid as get_indexed_cuid
from pyomo.core.base.componentuid import ComponentUID as ComponentUID
from pyomo.core.base.expression import Expression as Expression
from pyomo.core.base.set import Set as Set

def get_penalty_at_time(
    variables, t, target_data, weight_data=None, time_set=None, variable_set=None
): ...
def get_terminal_penalty(variables, time_set, target_data, weight_data=None, variable_set=None): ...
