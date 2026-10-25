from math import fabs as fabs

from _typeshed import Incomplete
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.contrib.cp.transform.logical_to_disjunctive_program import (
    LogicalToDisjunctive as LogicalToDisjunctive,
)
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base.block import Block as Block
from pyomo.core.expr.numvalue import value as value
from pyomo.gdp import GDP_Error as GDP_Error
from pyomo.gdp.disjunct import Disjunct as Disjunct
from pyomo.gdp.disjunct import Disjunction as Disjunction
from pyomo.gdp.plugins.bigm import BigM_Transformation as BigM_Transformation

logger: Incomplete

class GDP_Disjunct_Fixer(Transformation):
    def __init__(self, **kwargs) -> None: ...
    CONFIG: Incomplete
