from _typeshed import Incomplete
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import ConstraintList as ConstraintList
from pyomo.core import Set as Set
from pyomo.core.base import Reference as Reference
from pyomo.gdp.disjunct import Disjunct as Disjunct
from pyomo.gdp.disjunct import Disjunction as Disjunction

logger: Incomplete

def apply_basic_step(disjunctions_or_constraints): ...
