from _typeshed import Incomplete
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.core import quicksum as quicksum
from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.core.base.transformation import TransformationFactory as TransformationFactory
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.repn import generate_standard_repn as generate_standard_repn

class RemoveZeroTerms(IsomorphicTransformation):
    CONFIG: Incomplete
