from _typeshed import Incomplete
from pyomo.common import timing as timing
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.dependencies import pympler as pympler
from pyomo.common.dependencies import pympler_available as pympler_available
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.common.gc_manager import PauseGC as PauseGC
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.numeric_types import value as value
from pyomo.core.base.block import ScalarBlock as ScalarBlock
from pyomo.core.base.component import ModelComponentFactory as ModelComponentFactory
from pyomo.core.base.componentuid import ComponentUID as ComponentUID
from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.core.base.label import CNameLabeler as CNameLabeler
from pyomo.core.base.label import CuidLabeler as CuidLabeler
from pyomo.core.base.objective import Objective as Objective
from pyomo.core.base.set import Set as Set
from pyomo.core.base.suffix import active_import_suffix_generator as active_import_suffix_generator
from pyomo.core.base.var import Var as Var
from pyomo.core.expr.symbol_map import SymbolMap as SymbolMap
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.dataportal.DataPortal import DataPortal as DataPortal
from pyomo.opt.results import Solution as Solution
from pyomo.opt.results import SolverStatus as SolverStatus
from pyomo.opt.results import UndefinedData as UndefinedData

logger: Incomplete
id_func = id

def global_option(function, name, value): ...

class PyomoConfig(Bunch):
    def __init__(self, *args, **kw) -> None: ...

class ModelSolution:
    def __init__(self) -> None: ...
    def __getattr__(self, name): ...
    def __setattr__(self, name, val) -> None: ...

class ModelSolutions:
    def __init__(self, instance) -> None: ...
    symbol_map: Incomplete
    solutions: Incomplete
    index: Incomplete
    def clear(self, clear_symbol_maps: bool = True) -> None: ...
    def __len__(self) -> int: ...
    def __getitem__(self, index): ...
    def add_symbol_map(self, symbol_map) -> None: ...
    def delete_symbol_map(self, smap_id) -> None: ...
    def load_from(
        self,
        results,
        allow_consistent_values_for_fixed_vars: bool = False,
        comparison_tolerance_for_fixed_vars: float = 1e-05,
        ignore_invalid_labels: bool = False,
        id=None,
        delete_symbol_map: bool = True,
        clear: bool = True,
        default_variable_value=None,
        select: int = 0,
        ignore_fixed_vars: bool = True,
    ) -> None: ...
    def store_to(self, results, cuid: bool = False, skip_stale_vars: bool = False) -> None: ...
    def add_solution(
        self,
        solution,
        smap_id,
        delete_symbol_map: bool = True,
        cache=None,
        ignore_invalid_labels: bool = False,
        ignore_missing_symbols: bool = True,
        default_variable_value=None,
    ): ...
    def select(
        self,
        index: int = 0,
        allow_consistent_values_for_fixed_vars: bool = False,
        comparison_tolerance_for_fixed_vars: float = 1e-05,
        ignore_invalid_labels: bool = False,
        ignore_fixed_vars: bool = True,
    ) -> None: ...

class Model(ScalarBlock):
    def __new__(cls, *args, **kwds): ...
    statistics: Incomplete
    config: Incomplete
    solutions: Incomplete
    def __init__(self, name: str = 'unknown', **kwargs) -> None: ...
    def compute_statistics(self, active: bool = True) -> None: ...
    def nvariables(self): ...
    def nconstraints(self): ...
    def nobjectives(self): ...
    def create_instance(
        self,
        filename=None,
        data=None,
        name=None,
        namespace=None,
        namespaces=None,
        profile_memory: int = 0,
        report_timing: bool = False,
        **kwds,
    ): ...
    def preprocess(self, preprocessor=None) -> None: ...
    def load(self, arg, namespaces=[None], profile_memory: int = 0) -> None: ...

class ConcreteModel(Model):
    def __init__(self, *args, **kwds) -> None: ...

class AbstractModel(Model):
    def __init__(self, *args, **kwds) -> None: ...
