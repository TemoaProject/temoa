from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.errors import InfeasibleConstraintException as InfeasibleConstraintException
from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.core.base.suffix import Suffix as Suffix
from pyomo.core.base.transformation import TransformationFactory as TransformationFactory
from pyomo.core.expr.numvalue import value as value
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.repn.standard_repn import generate_standard_repn as generate_standard_repn

class FixedVarPropagator(IsomorphicTransformation):
    CONFIG: Incomplete
    def revert(self, instance) -> None: ...

class VarBoundPropagator(IsomorphicTransformation):
    CONFIG: Incomplete
    def revert(self, instance) -> None: ...
