from typing import NamedTuple

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.config import NonNegativeInt as NonNegativeInt
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.errors import PyomoException as PyomoException
from pyomo.common.log import LogStream as LogStream
from pyomo.common.tee import TeeStream as TeeStream
from pyomo.common.tee import capture_output as capture_output
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer
from pyomo.contrib.appsi.base import MIPSolverConfig as MIPSolverConfig
from pyomo.contrib.appsi.base import PersistentBase as PersistentBase
from pyomo.contrib.appsi.base import PersistentSolutionLoader as PersistentSolutionLoader
from pyomo.contrib.appsi.base import PersistentSolver as PersistentSolver
from pyomo.contrib.appsi.base import Results as Results
from pyomo.contrib.appsi.base import TerminationCondition as TerminationCondition
from pyomo.contrib.appsi.cmodel import cmodel as cmodel
from pyomo.contrib.appsi.cmodel import cmodel_available as cmodel_available
from pyomo.core.base import NumericLabeler as NumericLabeler
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import TextLabeler as TextLabeler
from pyomo.core.base.expression import ScalarExpression as ScalarExpression
from pyomo.core.base.var import ScalarVar as ScalarVar
from pyomo.core.base.var import Var as Var
from pyomo.core.expr.numvalue import is_constant as is_constant
from pyomo.core.expr.numvalue import is_fixed as is_fixed
from pyomo.core.expr.numvalue import native_numeric_types as native_numeric_types
from pyomo.core.expr.numvalue import native_types as native_types
from pyomo.core.expr.numvalue import nonpyomo_leaf_types as nonpyomo_leaf_types
from pyomo.core.expr.numvalue import value as value
from pyomo.core.kernel.objective import maximize as maximize
from pyomo.core.kernel.objective import minimize as minimize
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.repn.util import valid_expr_ctypes_minlp as valid_expr_ctypes_minlp

logger: Incomplete

class MaingoVar(NamedTuple):
    type: Incomplete
    name: Incomplete
    lb: Incomplete
    ub: Incomplete
    init: Incomplete

maingopy: Incomplete
maingopy_available: Incomplete
maingo_solvermodel: Incomplete

class MAiNGOConfig(MIPSolverConfig):
    tolerances: ConfigDict
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class MAiNGOSolutionLoader(PersistentSolutionLoader):
    def load_vars(self, vars_to_load=None) -> None: ...
    def get_primals(self, vars_to_load=None): ...

class MAiNGOResults(Results):
    wallclock_time: Incomplete
    cpu_time: Incomplete
    globally_optimal: Incomplete
    solution_loader: Incomplete
    def __init__(self, solver) -> None: ...

class MAiNGO(PersistentBase, PersistentSolver):
    def __init__(self, only_child_vars: bool = False) -> None: ...
    def available(self): ...
    def version(self): ...
    @property
    def config(self) -> MAiNGOConfig: ...
    @config.setter
    def config(self, val: MAiNGOConfig): ...
    @property
    def maingo_options(self): ...
    @maingo_options.setter
    def maingo_options(self, val: dict): ...
    @property
    def symbol_map(self): ...
    def solve(self, model, timer: HierarchicalTimer = None): ...
    def set_instance(self, model) -> None: ...
    def update_params(self) -> None: ...
    def load_vars(self, vars_to_load=None) -> None: ...
    def get_primals(self, vars_to_load=None): ...
    def get_reduced_costs(self, vars_to_load=None) -> None: ...
    def get_duals(self, cons_to_load=None) -> None: ...
    def update(self, timer: HierarchicalTimer = None): ...
