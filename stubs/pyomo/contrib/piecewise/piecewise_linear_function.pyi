from _typeshed import Incomplete
from pyomo.common import DeveloperError as DeveloperError
from pyomo.common.autoslots import AutoSlots as AutoSlots
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.dependencies.scipy import spatial as spatial
from pyomo.contrib.piecewise.piecewise_linear_expression import (
    PiecewiseLinearExpression as PiecewiseLinearExpression,
)
from pyomo.contrib.piecewise.triangulations import Triangulation as Triangulation
from pyomo.contrib.piecewise.triangulations import (
    get_ordered_j1_triangulation as get_ordered_j1_triangulation,
)
from pyomo.contrib.piecewise.triangulations import (
    get_unordered_j1_triangulation as get_unordered_j1_triangulation,
)
from pyomo.core import Any as Any
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import value as value
from pyomo.core.base.block import Block as Block
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.component import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.expression import Expression as Expression
from pyomo.core.base.global_set import UnindexedComponent_index as UnindexedComponent_index
from pyomo.core.base.indexed_component import UnindexedComponent_set as UnindexedComponent_set
from pyomo.core.base.initializer import Initializer as Initializer

ZERO_TOLERANCE: float
logger: Incomplete

class PiecewiseLinearFunctionData(BlockData):
    def __init__(self, component=None) -> None: ...
    @property
    def triangulation(self): ...
    def __call__(self, *args): ...
    def map_transformation_var(self, pw_expr, v) -> None: ...
    def get_transformation_var(self, pw_expr): ...

class _univariate_linear_functor(AutoSlots.Mixin):
    slope: Incomplete
    intercept: Incomplete
    def __init__(self, slope, intercept) -> None: ...
    def __call__(self, x): ...

class _multivariate_linear_functor(AutoSlots.Mixin):
    normal: Incomplete
    def __init__(self, normal) -> None: ...
    def __call__(self, *args): ...

class _tabular_data_functor(AutoSlots.Mixin):
    tabular_data: Incomplete
    def __init__(self, tabular_data, tupleize: bool = False) -> None: ...
    def __call__(self, *args): ...

class PiecewiseLinearFunction(Block):
    def __new__(cls, *args, **kwds): ...
    def __init__(self, *args, **kwargs) -> None: ...

class ScalarPiecewiseLinearFunction(PiecewiseLinearFunctionData, PiecewiseLinearFunction):
    def __init__(self, *args, **kwds) -> None: ...

class IndexedPiecewiseLinearFunction(PiecewiseLinearFunction): ...
