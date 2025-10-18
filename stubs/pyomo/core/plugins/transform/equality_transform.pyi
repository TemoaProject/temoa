from pyomo.core import NonNegativeReals as NonNegativeReals
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import Var as Var
from pyomo.core.base.misc import create_name as create_name
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.core.plugins.transform.util import collectAbstractComponents as collectAbstractComponents

class EqualityTransform(IsomorphicTransformation):
    def __init__(self, **kwds) -> None: ...
