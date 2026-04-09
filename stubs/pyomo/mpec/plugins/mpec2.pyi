from _typeshed import Incomplete
from pyomo.core.base import Block as Block
from pyomo.core.base import ComponentUID as ComponentUID
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.expr import inequality as inequality
from pyomo.gdp.disjunct import Disjunct as Disjunct
from pyomo.gdp.disjunct import Disjunction as Disjunction
from pyomo.mpec.complementarity import Complementarity as Complementarity

logger: Incomplete

class MPEC2_Transformation(Transformation):
    def __init__(self) -> None: ...
