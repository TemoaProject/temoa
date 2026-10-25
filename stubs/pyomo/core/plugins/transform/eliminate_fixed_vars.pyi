from pyomo.core import Constraint as Constraint
from pyomo.core import Objective as Objective
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core.base.var import Var as Var
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr import ExpressionBase as ExpressionBase
from pyomo.core.expr import as_numeric as as_numeric
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.core.util import sequence as sequence

class EliminateFixedVars(IsomorphicTransformation):
    def __init__(self, **kwds) -> None: ...
