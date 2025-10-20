from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.core.plugins.transform.add_slack_vars import AddSlackVariables as AddSlackVariables
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.opt import WriterFactory as WriterFactory

logger: Incomplete

class _VariableBoundsAsConstraints(IsomorphicTransformation): ...

def compute_infeasibility_explanation(
    model, solver, tee: bool = False, tolerance: float = 1e-08, logger=...
): ...
