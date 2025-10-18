from _typeshed import Incomplete
from pyomo.common.modeling import NOTSET as NOTSET
from pyomo.contrib.mpc.data.find_nearest_index import find_nearest_index as find_nearest_index
from pyomo.contrib.mpc.data.get_cuid import get_indexed_cuid as get_indexed_cuid
from pyomo.contrib.mpc.data.interval_data import IntervalData as IntervalData
from pyomo.contrib.mpc.data.scalar_data import ScalarData as ScalarData
from pyomo.contrib.mpc.data.series_data import TimeSeriesData as TimeSeriesData
from pyomo.contrib.mpc.interfaces.copy_values import copy_values_at_time as copy_values_at_time
from pyomo.contrib.mpc.interfaces.load_data import (
    load_data_from_interval as load_data_from_interval,
)
from pyomo.contrib.mpc.interfaces.load_data import load_data_from_scalar as load_data_from_scalar
from pyomo.contrib.mpc.interfaces.load_data import load_data_from_series as load_data_from_series
from pyomo.contrib.mpc.modeling.constraints import (
    get_piecewise_constant_constraints as get_piecewise_constant_constraints,
)
from pyomo.contrib.mpc.modeling.cost_expressions import (
    get_penalty_from_constant_target as get_penalty_from_constant_target,
)
from pyomo.contrib.mpc.modeling.cost_expressions import (
    get_penalty_from_target as get_penalty_from_target,
)
from pyomo.core.base.componentuid import ComponentUID as ComponentUID
from pyomo.core.base.expression import Expression as Expression
from pyomo.core.base.var import Var as Var
from pyomo.dae.flatten import flatten_dae_components as flatten_dae_components

iterable_scalars: Incomplete

class DynamicModelInterface:
    model: Incomplete
    time: Incomplete
    def __init__(self, model, time, context=...) -> None: ...
    def get_scalar_variables(self): ...
    def get_indexed_variables(self): ...
    def get_scalar_expressions(self): ...
    def get_indexed_expressions(self): ...
    def get_scalar_variable_data(self): ...
    def get_data_at_time(self, time=None, include_expr: bool = False): ...
    def load_data(
        self,
        data,
        time_points=None,
        tolerance: float = 0.0,
        prefer_left=None,
        exclude_left_endpoint=None,
        exclude_right_endpoint=None,
    ) -> None: ...
    def copy_values_at_time(self, source_time=None, target_time=None) -> None: ...
    def shift_values_by_time(self, dt) -> None: ...
    def get_penalty_from_target(
        self,
        target_data,
        time=None,
        variables=None,
        weight_data=None,
        variable_set=None,
        tolerance=None,
        prefer_left=None,
    ): ...
    def get_piecewise_constant_constraints(
        self, variables, sample_points, use_next: bool = True, tolerance: float = 0.0
    ): ...
