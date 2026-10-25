from _typeshed import Incomplete
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer
from pyomo.contrib.appsi.base import PersistentBase as PersistentBase
from pyomo.core.base import NumericLabeler as NumericLabeler
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import TextLabeler as TextLabeler
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.constraint import ConstraintData as ConstraintData
from pyomo.core.base.objective import ObjectiveData as ObjectiveData
from pyomo.core.base.param import ParamData as ParamData
from pyomo.core.base.sos import SOSConstraintData as SOSConstraintData
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr.numvalue import value as value
from pyomo.core.kernel.objective import maximize as maximize
from pyomo.core.kernel.objective import minimize as minimize
from pyomo.repn.standard_repn import generate_standard_repn as generate_standard_repn

from ..cmodel import cmodel as cmodel
from ..cmodel import cmodel_available as cmodel_available
from .config import WriterConfig as WriterConfig

class LPWriter(PersistentBase):
    def __init__(self, only_child_vars: bool = False) -> None: ...
    @property
    def config(self): ...
    @config.setter
    def config(self, val: WriterConfig): ...
    update_config: Incomplete
    def set_instance(self, model) -> None: ...
    def update_params(self) -> None: ...
    def write(self, model: BlockData, filename: str, timer: HierarchicalTimer = None): ...
    def get_vars(self): ...
    def get_ordered_cons(self): ...
    def get_active_objective(self): ...
    @property
    def symbol_map(self): ...
