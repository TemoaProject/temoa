from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.core.base import Block as Block
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Objective as Objective
from pyomo.core.base import Suffix as Suffix
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base import Var as Var
from pyomo.core.base import value as value
from pyomo.core.base.suffix import SuffixFinder as SuffixFinder
from pyomo.core.expr import replace_expressions as replace_expressions
from pyomo.core.plugins.transform.hierarchy import Transformation as Transformation
from pyomo.util.components import rename_components as rename_components

logger: Incomplete

class ScaleModel(Transformation):
    def __init__(self, **kwds) -> None: ...
    def propagate_solution(self, scaled_model, original_model) -> None: ...
