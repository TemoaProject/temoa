from _typeshed import Incomplete
from pyomo.common.autoslots import AutoSlots as AutoSlots
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.dependencies import scipy as scipy
from pyomo.core import Block as Block
from pyomo.core import ConcreteModel as ConcreteModel
from pyomo.core import Constraint as Constraint
from pyomo.core import NonNegativeReals as NonNegativeReals
from pyomo.core import NonPositiveReals as NonPositiveReals
from pyomo.core import Objective as Objective
from pyomo.core import Reals as Reals
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import Var as Var
from pyomo.core import maximize as maximize
from pyomo.core import minimize as minimize
from pyomo.opt import WriterFactory as WriterFactory
from pyomo.repn.standard_repn import isclose_const as isclose_const
from pyomo.util.config_domains import ComponentDataSet as ComponentDataSet

class _LPDualData(AutoSlots.Mixin):
    primal_var: Incomplete
    dual_var: Incomplete
    primal_constraint: Incomplete
    dual_constraint: Incomplete
    def __init__(self) -> None: ...

class LinearProgrammingDual:
    CONFIG: Incomplete
    def apply_to(self, model, **options) -> None: ...
    def create_using(self, model, ostream=None, **kwds): ...
    def get_primal_constraint(self, model, dual_var): ...
    def get_dual_constraint(self, model, primal_var): ...
    def get_primal_var(self, model, dual_constraint): ...
    def get_dual_var(self, model, primal_constraint): ...
