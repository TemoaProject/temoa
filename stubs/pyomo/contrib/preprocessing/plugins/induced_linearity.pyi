from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.preprocessing.util import (
    SuppressConstantObjectiveWarning as SuppressConstantObjectiveWarning,
)
from pyomo.core import Binary as Binary
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import Objective as Objective
from pyomo.core import Set as Set
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import Var as Var
from pyomo.core import summation as summation
from pyomo.core import value as value
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.repn import generate_standard_repn as generate_standard_repn

logger: Incomplete

class InducedLinearity(IsomorphicTransformation):
    CONFIG: Incomplete

def determine_valid_values(block, discr_var_to_constrs_map, config): ...
def prune_possible_values(block_scope, possible_values, config): ...
def zero_if_None(val): ...
def detect_effectively_discrete_vars(block, equality_tolerance): ...
