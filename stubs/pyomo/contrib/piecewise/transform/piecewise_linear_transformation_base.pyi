from _typeshed import Incomplete
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.piecewise import PiecewiseLinearFunction as PiecewiseLinearFunction
from pyomo.contrib.piecewise.transform.piecewise_to_mip_visitor import (
    PiecewiseLinearToMIP as PiecewiseLinearToMIP,
)
from pyomo.core import Any as Any
from pyomo.core import BooleanVar as BooleanVar
from pyomo.core import Connector as Connector
from pyomo.core import Constraint as Constraint
from pyomo.core import Expression as Expression
from pyomo.core import ExternalFunction as ExternalFunction
from pyomo.core import LogicalConstraint as LogicalConstraint
from pyomo.core import Objective as Objective
from pyomo.core import Param as Param
from pyomo.core import RangeSet as RangeSet
from pyomo.core import Set as Set
from pyomo.core import SetOf as SetOf
from pyomo.core import SortComponents as SortComponents
from pyomo.core import Suffix as Suffix
from pyomo.core import Var as Var
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base.block import Block as Block
from pyomo.core.util import target_list as target_list
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.gdp.util import is_child_of as is_child_of
from pyomo.network import Port as Port

class PiecewiseLinearTransformationBase(Transformation):
    CONFIG: Incomplete
    handlers: Incomplete
    def __init__(self) -> None: ...
