from _typeshed import Incomplete
from pyomo.core.base import Block as Block
from pyomo.core.base import ComponentUID as ComponentUID
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base import Var as Var
from pyomo.core.base import value as value
from pyomo.gdp import Disjunct as Disjunct
from pyomo.mpec.complementarity import Complementarity as Complementarity

logger: Incomplete

class MPEC4_Transformation(Transformation):
    def __init__(self) -> None: ...
    def print_nl_form(self, instance) -> None: ...
    def to_common_form(self, cdata, free_vars) -> None: ...
