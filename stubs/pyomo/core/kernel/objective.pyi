from _typeshed import Incomplete
from pyomo.common.enums import ObjectiveSense as ObjectiveSense
from pyomo.common.enums import maximize as maximize
from pyomo.common.enums import minimize as minimize
from pyomo.core.expr.numvalue import as_numeric as as_numeric
from pyomo.core.kernel.container_utils import define_simple_containers as define_simple_containers
from pyomo.core.kernel.expression import IExpression as IExpression

class IObjective(IExpression):
    sense: Incomplete
    def is_minimizing(self): ...

class objective(IObjective):
    def __init__(self, expr=None, sense=...) -> None: ...
    @property
    def expr(self): ...
    @expr.setter
    def expr(self, expr) -> None: ...
    @property
    def sense(self): ...
    @sense.setter
    def sense(self, sense) -> None: ...
