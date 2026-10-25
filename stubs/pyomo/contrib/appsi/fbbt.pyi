from _typeshed import Incomplete
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.config import NonNegativeInt as NonNegativeInt
from pyomo.common.errors import InfeasibleConstraintException as InfeasibleConstraintException
from pyomo.contrib.appsi.base import PersistentBase as PersistentBase
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import TextLabeler as TextLabeler
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.constraint import ConstraintData as ConstraintData
from pyomo.core.base.objective import ObjectiveData as ObjectiveData
from pyomo.core.base.objective import maximize as maximize
from pyomo.core.base.objective import minimize as minimize
from pyomo.core.base.param import ParamData as ParamData
from pyomo.core.base.sos import SOSConstraintData as SOSConstraintData
from pyomo.core.base.var import VarData as VarData

from .cmodel import cmodel as cmodel
from .cmodel import cmodel_available as cmodel_available

class IntervalConfig(ConfigDict):
    feasibility_tol: float
    integer_tol: float
    improvement_tol: float
    max_iter: int
    deactivate_satisfied_constraints: bool
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class IntervalTightener(PersistentBase):
    def __init__(self) -> None: ...
    @property
    def config(self): ...
    @config.setter
    def config(self, val: IntervalConfig): ...
    update_config: Incomplete
    def set_instance(self, model, symbolic_solver_labels: bool | None = None): ...
    def update_params(self) -> None: ...
    def set_objective(self, obj: ObjectiveData): ...
    def perform_fbbt(self, model: BlockData, symbolic_solver_labels: bool | None = None): ...
    def perform_fbbt_with_seed(self, model: BlockData, seed_var: VarData): ...
