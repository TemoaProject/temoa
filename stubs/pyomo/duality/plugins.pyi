from _typeshed import Incomplete
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.core.base import Block as Block
from pyomo.core.base import ConcreteModel as ConcreteModel
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Model as Model
from pyomo.core.base import NonNegativeReals as NonNegativeReals
from pyomo.core.base import NonPositiveReals as NonPositiveReals
from pyomo.core.base import Objective as Objective
from pyomo.core.base import Reals as Reals
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base import Var as Var
from pyomo.core.base import minimize as minimize
from pyomo.duality.collect import collect_linear_terms as collect_linear_terms

def load() -> None: ...

logger: Incomplete

class LinearDual_PyomoTransformation(Transformation):
    def __init__(self) -> None: ...
