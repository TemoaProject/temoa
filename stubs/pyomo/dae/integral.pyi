from _typeshed import Incomplete
from pyomo.common.deprecation import RenamedClass as RenamedClass
from pyomo.core.base.component import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.expression import Expression as Expression
from pyomo.core.base.expression import ExpressionData as ExpressionData
from pyomo.core.base.expression import IndexedExpression as IndexedExpression
from pyomo.core.base.expression import ScalarExpression as ScalarExpression
from pyomo.core.base.indexed_component import rule_wrapper as rule_wrapper
from pyomo.dae.contset import ContinuousSet as ContinuousSet
from pyomo.dae.diffvar import DAE_Error as DAE_Error

class Integral(Expression):
    def __new__(cls, *args, **kwds): ...
    loc: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def get_continuousset(self): ...

class ScalarIntegral(ScalarExpression, Integral):
    def __init__(self, *args, **kwds) -> None: ...
    def clear(self) -> None: ...
    def is_fully_discretized(self): ...

class SimpleIntegral(metaclass=RenamedClass):
    __renamed__new_class__ = ScalarIntegral
    __renamed__version__: str

class IndexedIntegral(IndexedExpression, Integral):
    def is_fully_discretized(self): ...
