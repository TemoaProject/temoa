from pyomo.core import ComponentMap as ComponentMap
from pyomo.core import Constraint as Constraint
from pyomo.core import Objective as Objective
from pyomo.core import SortComponents as SortComponents
from pyomo.core import Var as Var
from pyomo.core.expr import identify_variables as identify_variables

def generate_model_graph(
    model,
    type_of_graph,
    with_objective: bool = True,
    weighted_graph: bool = True,
    use_only_active_components: bool = True,
): ...
