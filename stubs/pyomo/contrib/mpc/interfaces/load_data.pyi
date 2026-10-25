from pyomo.contrib.mpc.data.find_nearest_index import find_nearest_index as find_nearest_index
from pyomo.contrib.mpc.data.find_nearest_index import (
    find_nearest_interval_index as find_nearest_interval_index,
)

def load_data_from_scalar(data, model, time) -> None: ...
def load_data_from_series(data, model, time, tolerance: float = 0.0) -> None: ...
def load_data_from_interval(
    data,
    model,
    time,
    tolerance: float = 0.0,
    prefer_left: bool = True,
    exclude_left_endpoint: bool = True,
    exclude_right_endpoint: bool = False,
) -> None: ...
