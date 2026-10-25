from _typeshed import Incomplete
from pyomo.contrib.fbbt.fbbt import compute_bounds_on_expr as compute_bounds_on_expr
from pyomo.contrib.piecewise.transform.piecewise_linear_transformation_base import (
    PiecewiseLinearTransformationBase as PiecewiseLinearTransformationBase,
)
from pyomo.core import Constraint as Constraint
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import Suffix as Suffix
from pyomo.core import Var as Var
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction

class InnerRepresentationGDPTransformation(PiecewiseLinearTransformationBase):
    CONFIG: Incomplete
