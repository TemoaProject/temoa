from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import In as In
from pyomo.common.config import PositiveInt as PositiveInt
from pyomo.core import Expression as Expression
from pyomo.core import Objective as Objective
from pyomo.core import Var as Var
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.dae import ContinuousSet as ContinuousSet
from pyomo.dae import DerivativeVar as DerivativeVar
from pyomo.dae import Integral as Integral
from pyomo.dae.diffvar import DAE_Error as DAE_Error
from pyomo.dae.misc import add_discretization_equations as add_discretization_equations
from pyomo.dae.misc import block_fully_discretized as block_fully_discretized
from pyomo.dae.misc import create_partial_expression as create_partial_expression
from pyomo.dae.misc import expand_components as expand_components
from pyomo.dae.misc import generate_finite_elements as generate_finite_elements

logger: Incomplete

class Finite_Difference_Transformation(Transformation):
    CONFIG: Incomplete
    all_schemes: Incomplete
    def __init__(self) -> None: ...
