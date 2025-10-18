from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.contrib.mpc.data.convert import interval_to_series as interval_to_series
from pyomo.contrib.mpc.data.interval_data import IntervalData as IntervalData
from pyomo.contrib.mpc.data.scalar_data import ScalarData as ScalarData
from pyomo.contrib.mpc.data.series_data import TimeSeriesData as TimeSeriesData
from pyomo.contrib.mpc.data.series_data import get_indexed_cuid as get_indexed_cuid
from pyomo.core.base.componentuid import ComponentUID as ComponentUID
from pyomo.core.base.expression import Expression as Expression
from pyomo.core.base.set import Set as Set

def get_penalty_from_constant_target(
    variables, time, setpoint_data, weight_data=None, variable_set=None
): ...
def get_penalty_from_piecewise_constant_target(
    variables,
    time,
    setpoint_data,
    weight_data=None,
    variable_set=None,
    tolerance: float = 0.0,
    prefer_left: bool = True,
): ...
def get_quadratic_penalty_at_time(var, t, setpoint, weight=None): ...
def get_penalty_from_time_varying_target(
    variables, time, setpoint_data, weight_data=None, variable_set=None
): ...
def get_penalty_from_target(
    variables,
    time,
    setpoint_data,
    weight_data=None,
    variable_set=None,
    tolerance=None,
    prefer_left=None,
): ...
