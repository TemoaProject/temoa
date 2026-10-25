from _typeshed import Incomplete
from pyomo.common.autoslots import AutoSlots as AutoSlots
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import DefaultComponentMap as DefaultComponentMap
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.core import Any as Any
from pyomo.core import Block as Block
from pyomo.core import BooleanVar as BooleanVar
from pyomo.core import Connector as Connector
from pyomo.core import Constraint as Constraint
from pyomo.core import Expression as Expression
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import Param as Param
from pyomo.core import RangeSet as RangeSet
from pyomo.core import Reference as Reference
from pyomo.core import Set as Set
from pyomo.core import SetOf as SetOf
from pyomo.core import Suffix as Suffix
from pyomo.core import Var as Var
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base.external import ExternalFunction as ExternalFunction
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.gdp import GDP_Error as GDP_Error
from pyomo.gdp.util import get_gdp_tree as get_gdp_tree
from pyomo.gdp.util import get_src_constraint as get_src_constraint
from pyomo.gdp.util import get_src_disjunct as get_src_disjunct
from pyomo.gdp.util import get_src_disjunction as get_src_disjunction
from pyomo.gdp.util import get_transformed_constraints as get_transformed_constraints
from pyomo.network import Port as Port

class _GDPTransformationData(AutoSlots.Mixin):
    src_constraint: Incomplete
    transformed_constraints: Incomplete
    def __init__(self) -> None: ...

class GDP_to_MIP_Transformation(Transformation):
    logger: Incomplete
    handlers: Incomplete
    def __init__(self, logger) -> None: ...
    def get_src_disjunct(self, transBlock): ...
    def get_src_disjunction(self, xor_constraint): ...
    def get_src_constraint(self, transformedConstraint): ...
    def get_transformed_constraints(self, srcConstraint): ...
