from pyomo.core.base.transformation import TransformationFactory as TransformationFactory
from pyomo.core.base.var import Var as Var
from pyomo.core.expr.numvalue import value as value
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)

class InitMidpoint(IsomorphicTransformation): ...
class InitZero(IsomorphicTransformation): ...
