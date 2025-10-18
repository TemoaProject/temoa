from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import In as In
from pyomo.common.config import PositiveInt as PositiveInt
from pyomo.common.dependencies import numpy as numpy
from pyomo.common.dependencies import numpy_available as numpy_available
from pyomo.core import ConstraintList as ConstraintList
from pyomo.core import Expression as Expression
from pyomo.core import Objective as Objective
from pyomo.core import Var as Var
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.dae import ContinuousSet as ContinuousSet
from pyomo.dae import DerivativeVar as DerivativeVar
from pyomo.dae import Integral as Integral
from pyomo.dae.diffvar import DAE_Error as DAE_Error
from pyomo.dae.misc import add_continuity_equations as add_continuity_equations
from pyomo.dae.misc import add_discretization_equations as add_discretization_equations
from pyomo.dae.misc import block_fully_discretized as block_fully_discretized
from pyomo.dae.misc import create_partial_expression as create_partial_expression
from pyomo.dae.misc import expand_components as expand_components
from pyomo.dae.misc import generate_colloc_points as generate_colloc_points
from pyomo.dae.misc import generate_finite_elements as generate_finite_elements
from pyomo.dae.misc import get_index_information as get_index_information

logger: Incomplete

def conv(a, b): ...
def calc_cp(alpha, beta, k): ...
def calc_adot(cp, order: int = 1): ...
def calc_afinal(cp): ...

class Collocation_Discretization_Transformation(Transformation):
    CONFIG: Incomplete
    all_schemes: Incomplete
    def __init__(self) -> None: ...
    def reduce_collocation_points(self, instance, var=None, ncp=None, contset=None): ...
