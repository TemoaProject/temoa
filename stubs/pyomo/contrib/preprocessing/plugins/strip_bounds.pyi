from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.core.base.set_types import Reals as Reals
from pyomo.core.base.transformation import TransformationFactory as TransformationFactory
from pyomo.core.base.var import Var as Var
from pyomo.core.plugins.transform.hierarchy import (
    NonIsomorphicTransformation as NonIsomorphicTransformation,
)

class VariableBoundStripper(NonIsomorphicTransformation):
    CONFIG: Incomplete
    def revert(self, instance) -> None: ...
