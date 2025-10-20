from pyomo.contrib.mpc.data.find_nearest_index import (
    find_nearest_interval_index as find_nearest_interval_index,
)
from pyomo.contrib.mpc.data.interval_data import IntervalData as IntervalData
from pyomo.contrib.mpc.data.scalar_data import ScalarData as ScalarData
from pyomo.contrib.mpc.data.series_data import TimeSeriesData as TimeSeriesData

def interval_to_series(
    data,
    time_points=None,
    tolerance: float = 0.0,
    use_left_endpoints: bool = False,
    prefer_left: bool = True,
): ...
def series_to_interval(data, use_left_endpoints: bool = False): ...
