from _typeshed import Incomplete
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import Objective as Objective
from pyomo.core import Set as Set
from pyomo.core import SortComponents as SortComponents
from pyomo.core import Transformation as Transformation
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import VarList as VarList
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.repn import generate_standard_repn as generate_standard_repn

logger: Incomplete

class Bilinear_Transformation(Transformation):
    def __init__(self) -> None: ...
