from _typeshed import Incomplete
from pyomo.core.base import Block as Block
from pyomo.core.base import ComponentUID as ComponentUID
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Param as Param
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.gdp import Disjunct as Disjunct
from pyomo.mpec.complementarity import Complementarity as Complementarity

logger: Incomplete

class MPEC1_Transformation(Transformation):
    def __init__(self) -> None: ...
