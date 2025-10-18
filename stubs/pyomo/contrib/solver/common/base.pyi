import types
from typing import Sequence

from _typeshed import Incomplete
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.deprecation import deprecation_warning as deprecation_warning
from pyomo.common.enums import IntEnum as IntEnum
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.modeling import NOTSET as NOTSET
from pyomo.contrib.solver.common.config import PersistentSolverConfig as PersistentSolverConfig
from pyomo.contrib.solver.common.config import SolverConfig as SolverConfig
from pyomo.contrib.solver.common.results import Results as Results
from pyomo.contrib.solver.common.results import (
    legacy_solution_status_map as legacy_solution_status_map,
)
from pyomo.contrib.solver.common.results import legacy_solver_status_map as legacy_solver_status_map
from pyomo.contrib.solver.common.results import (
    legacy_termination_condition_map as legacy_termination_condition_map,
)
from pyomo.contrib.solver.common.util import get_objective as get_objective
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.constraint import ConstraintData as ConstraintData
from pyomo.core.base.label import NumericLabeler as NumericLabeler
from pyomo.core.base.objective import Objective as Objective
from pyomo.core.base.objective import ObjectiveData as ObjectiveData
from pyomo.core.base.param import ParamData as ParamData
from pyomo.core.base.var import VarData as VarData
from pyomo.core.kernel.objective import minimize as minimize
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.scripting.solve_config import default_config_block as default_config_block

class Availability(IntEnum):
    FullLicense = 2
    LimitedLicense = 1
    NotFound = 0
    BadVersion = -1
    BadLicense = -2
    NeedsCompiledExtension = -3
    def __bool__(self) -> bool: ...
    def __format__(self, format_spec) -> str: ...

class SolverBase:
    CONFIG: Incomplete
    name: Incomplete
    config: Incomplete
    def __init__(self, **kwds) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: types.TracebackType | None,
    ) -> None: ...
    def solve(self, model: BlockData, **kwargs) -> Results: ...
    def available(self) -> Availability: ...
    def version(self) -> tuple: ...
    def is_persistent(self) -> bool: ...

class PersistentSolverBase(SolverBase):
    CONFIG: Incomplete
    def __init__(self, **kwds) -> None: ...
    def solve(self, model: BlockData, **kwargs) -> Results: ...
    def is_persistent(self) -> bool: ...
    def set_instance(self, model: BlockData): ...
    def set_objective(self, obj: ObjectiveData): ...
    def add_variables(self, variables: list[VarData]): ...
    def add_parameters(self, params: list[ParamData]): ...
    def add_constraints(self, cons: list[ConstraintData]): ...
    def add_block(self, block: BlockData): ...
    def remove_variables(self, variables: list[VarData]): ...
    def remove_parameters(self, params: list[ParamData]): ...
    def remove_constraints(self, cons: list[ConstraintData]): ...
    def remove_block(self, block: BlockData): ...
    def update_variables(self, variables: list[VarData]): ...
    def update_parameters(self) -> None: ...

class LegacySolverWrapper:
    options: Incomplete
    def __init__(self, **kwargs) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: types.TracebackType | None,
    ) -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    config: Incomplete
    def solve(
        self,
        model: BlockData,
        tee: bool = False,
        load_solutions: bool = True,
        logfile: str | None = None,
        solnfile: str | None = None,
        timelimit: float | None = None,
        report_timing: bool = False,
        solver_io: str | None = None,
        suffixes: Sequence | None = None,
        options: dict | None = None,
        keepfiles: bool = False,
        symbolic_solver_labels: bool = False,
        raise_exception_on_nonoptimal_result: bool = False,
        solver_options: dict | None = None,
        writer_config: dict | None = None,
    ): ...
    def available(self, exception_flag: bool = True): ...
    def license_is_valid(self) -> bool: ...
    def config_block(self, init: bool = False): ...
    def set_options(self, options) -> None: ...
