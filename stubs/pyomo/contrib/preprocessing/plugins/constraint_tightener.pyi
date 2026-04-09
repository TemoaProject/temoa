from _typeshed import Incomplete
from pyomo.common import deprecated as deprecated
from pyomo.core import Constraint as Constraint
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import value as value
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.repn.standard_repn import generate_standard_repn as generate_standard_repn

logger: Incomplete

class TightenConstraintFromVars(IsomorphicTransformation):
    def __init__(self) -> None: ...
