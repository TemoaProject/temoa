from _typeshed import Incomplete
from pyomo.core import Constraint as Constraint
from pyomo.core import TraversalStrategy as TraversalStrategy
from pyomo.core import Var as Var

logger: Incomplete

def has_discrete_variables(block): ...
def log_model_constraints(m, logger=..., active: bool = True) -> None: ...
