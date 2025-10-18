from _typeshed import Incomplete
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.util import target_list as target_list
from pyomo.gdp import Disjunction as Disjunction

from .gdp_to_mip_transformation import GDP_to_MIP_Transformation as GDP_to_MIP_Transformation

logger: Incomplete

class GDPBinaryMultiplicationTransformation(GDP_to_MIP_Transformation):
    CONFIG: Incomplete
    transformation_name: str
    def __init__(self) -> None: ...
