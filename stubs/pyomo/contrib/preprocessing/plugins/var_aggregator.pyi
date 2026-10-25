from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.core.base import Block as Block
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Objective as Objective
from pyomo.core.base import Reals as Reals
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base import VarList as VarList
from pyomo.core.expr import ExpressionReplacementVisitor as ExpressionReplacementVisitor
from pyomo.core.expr.numvalue import value as value
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.repn import generate_standard_repn as generate_standard_repn

logger: Incomplete

def min_if_not_None(iterable): ...
def max_if_not_None(iterable): ...

class VariableAggregator(IsomorphicTransformation):
    def update_variables(self, model) -> None: ...
