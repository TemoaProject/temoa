from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.core.base.block import Block as Block
from pyomo.core.base.transformation import TransformationFactory as TransformationFactory
from pyomo.core.base.var import Var as Var
from pyomo.core.expr.numvalue import value as value
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.gdp import Disjunct as Disjunct

class FixedVarDetector(IsomorphicTransformation):
    CONFIG: Incomplete
    def revert(self, instance) -> None: ...
