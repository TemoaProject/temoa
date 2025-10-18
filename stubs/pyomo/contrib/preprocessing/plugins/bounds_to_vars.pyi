from _typeshed import Incomplete
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.core.base.transformation import TransformationFactory as TransformationFactory
from pyomo.core.expr.numvalue import value as value
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.repn import generate_standard_repn as generate_standard_repn

class ConstraintToVarBoundTransform(IsomorphicTransformation):
    CONFIG: Incomplete
