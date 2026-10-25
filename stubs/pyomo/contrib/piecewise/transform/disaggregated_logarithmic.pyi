from _typeshed import Incomplete
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.contrib.piecewise.transform.piecewise_linear_transformation_base import (
    PiecewiseLinearTransformationBase as PiecewiseLinearTransformationBase,
)
from pyomo.core import Binary as Binary
from pyomo.core import Constraint as Constraint
from pyomo.core import RangeSet as RangeSet
from pyomo.core import Set as Set
from pyomo.core import Var as Var
from pyomo.core.base import TransformationFactory as TransformationFactory

class DisaggregatedLogarithmicMIPTransformation(PiecewiseLinearTransformationBase):
    CONFIG: Incomplete
