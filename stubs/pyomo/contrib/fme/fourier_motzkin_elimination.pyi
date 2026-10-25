from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import ConstraintList as ConstraintList
from pyomo.core import Expression as Expression
from pyomo.core import Objective as Objective
from pyomo.core import Param as Param
from pyomo.core import Set as Set
from pyomo.core import SetOf as SetOf
from pyomo.core import SortComponents as SortComponents
from pyomo.core import Suffix as Suffix
from pyomo.core import Var as Var
from pyomo.core import value as value
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base import VarData as VarData
from pyomo.core.plugins.transform.hierarchy import Transformation as Transformation
from pyomo.opt import TerminationCondition as TerminationCondition
from pyomo.repn.standard_repn import generate_standard_repn as generate_standard_repn
from pyomo.util.config_domains import ComponentDataSet as ComponentDataSet

logger: Incomplete

def gcd(a, b): ...
def lcm(ints): ...

class Fourier_Motzkin_Elimination_Transformation(Transformation):
    CONFIG: Incomplete
    def __init__(self) -> None: ...
    def post_process_fme_constraints(
        self, m, solver_factory, projected_constraints=None, tolerance: int = 0
    ) -> None: ...
