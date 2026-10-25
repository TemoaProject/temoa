from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.contrib.alternative_solutions import aos_utils as aos_utils
from pyomo.contrib.fbbt.fbbt import compute_bounds_on_expr as compute_bounds_on_expr
from pyomo.gdp.util import (
    clone_without_expression_components as clone_without_expression_components,
)

def get_shifted_linear_model(model, block=None): ...
