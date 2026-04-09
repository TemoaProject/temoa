import abc
import enum
import types
from typing import Mapping, MutableMapping, NoReturn, Sequence

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.enums import IntEnum as IntEnum
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.factory import Factory as Factory
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base.block import Block as Block
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.core.base.constraint import ConstraintData as ConstraintData
from pyomo.core.base.objective import ObjectiveData as ObjectiveData
from pyomo.core.base.param import Param as Param
from pyomo.core.base.param import ParamData as ParamData
from pyomo.core.base.sos import SOSConstraint as SOSConstraint
from pyomo.core.base.sos import SOSConstraintData as SOSConstraintData
from pyomo.core.base.var import Var as Var
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr.numvalue import NumericConstant as NumericConstant
from pyomo.core.kernel.objective import minimize as minimize
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager

from .cmodel import cmodel as cmodel
from .cmodel import cmodel_available as cmodel_available
from .utils.collect_vars_and_named_exprs import (
    collect_vars_and_named_exprs as collect_vars_and_named_exprs,
)
from .utils.get_objective import get_objective as get_objective

class TerminationCondition(enum.Enum):
    unknown = 0
    maxTimeLimit = 1
    maxIterations = 2
    objectiveLimit = 3
    minStepLength = 4
    optimal = 5
    unbounded = 8
    infeasible = 9
    infeasibleOrUnbounded = 10
    error = 11
    interrupted = 12
    licensingProblems = 13

class SolverConfig(ConfigDict):
    time_limit: float | None
    warmstart: bool
    stream_solver: bool
    load_solution: bool
    symbolic_solver_labels: bool
    report_timing: bool
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class MIPSolverConfig(SolverConfig):
    mip_gap: float | None
    relax_integrality: bool
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class SolutionLoaderBase(abc.ABC, metaclass=abc.ABCMeta):
    def load_vars(self, vars_to_load: Sequence[VarData] | None = None) -> NoReturn: ...
    @abc.abstractmethod
    def get_primals(
        self, vars_to_load: Sequence[VarData] | None = None
    ) -> Mapping[VarData, float]: ...
    def get_duals(
        self, cons_to_load: Sequence[ConstraintData] | None = None
    ) -> dict[ConstraintData, float]: ...
    def get_slacks(
        self, cons_to_load: Sequence[ConstraintData] | None = None
    ) -> dict[ConstraintData, float]: ...
    def get_reduced_costs(
        self, vars_to_load: Sequence[VarData] | None = None
    ) -> Mapping[VarData, float]: ...

class SolutionLoader(SolutionLoaderBase):
    def __init__(
        self,
        primals: MutableMapping | None,
        duals: MutableMapping | None,
        slacks: MutableMapping | None,
        reduced_costs: MutableMapping | None,
    ) -> None: ...
    def get_primals(
        self, vars_to_load: Sequence[VarData] | None = None
    ) -> Mapping[VarData, float]: ...
    def get_duals(
        self, cons_to_load: Sequence[ConstraintData] | None = None
    ) -> dict[ConstraintData, float]: ...
    def get_slacks(
        self, cons_to_load: Sequence[ConstraintData] | None = None
    ) -> dict[ConstraintData, float]: ...
    def get_reduced_costs(
        self, vars_to_load: Sequence[VarData] | None = None
    ) -> Mapping[VarData, float]: ...

class Results:
    solution_loader: SolutionLoaderBase
    termination_condition: TerminationCondition
    best_feasible_objective: float | None
    best_objective_bound: float | None
    def __init__(self) -> None: ...

class UpdateConfig(ConfigDict):
    check_for_new_or_removed_constraints: bool
    check_for_new_or_removed_vars: bool
    check_for_new_or_removed_params: bool
    check_for_new_objective: bool
    update_constraints: bool
    update_vars: bool
    update_params: bool
    update_named_expressions: bool
    update_objective: bool
    treat_fixed_vars_as_params: bool
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class Solver(abc.ABC, metaclass=abc.ABCMeta):
    class Availability(IntEnum):
        NotFound = 0
        BadVersion = -1
        BadLicense = -2
        FullLicense = 1
        LimitedLicense = 2
        NeedsCompiledExtension = -3
        def __bool__(self) -> bool: ...
        def __format__(self, format_spec) -> str: ...

    @abc.abstractmethod
    def solve(self, model: BlockData, timer: HierarchicalTimer = None) -> Results: ...
    @abc.abstractmethod
    def available(self): ...
    @abc.abstractmethod
    def version(self) -> tuple: ...
    @property
    @abc.abstractmethod
    def config(self): ...
    @property
    @abc.abstractmethod
    def symbol_map(self): ...
    def is_persistent(self): ...

class PersistentSolver(Solver, metaclass=abc.ABCMeta):
    def is_persistent(self): ...
    def load_vars(self, vars_to_load: Sequence[VarData] | None = None) -> NoReturn: ...
    @abc.abstractmethod
    def get_primals(
        self, vars_to_load: Sequence[VarData] | None = None
    ) -> Mapping[VarData, float]: ...
    def get_duals(
        self, cons_to_load: Sequence[ConstraintData] | None = None
    ) -> dict[ConstraintData, float]: ...
    def get_slacks(
        self, cons_to_load: Sequence[ConstraintData] | None = None
    ) -> dict[ConstraintData, float]: ...
    def get_reduced_costs(
        self, vars_to_load: Sequence[VarData] | None = None
    ) -> Mapping[VarData, float]: ...
    @property
    @abc.abstractmethod
    def update_config(self) -> UpdateConfig: ...
    @abc.abstractmethod
    def set_instance(self, model): ...
    @abc.abstractmethod
    def add_variables(self, variables: list[VarData]): ...
    @abc.abstractmethod
    def add_params(self, params: list[ParamData]): ...
    @abc.abstractmethod
    def add_constraints(self, cons: list[ConstraintData]): ...
    @abc.abstractmethod
    def add_block(self, block: BlockData): ...
    @abc.abstractmethod
    def remove_variables(self, variables: list[VarData]): ...
    @abc.abstractmethod
    def remove_params(self, params: list[ParamData]): ...
    @abc.abstractmethod
    def remove_constraints(self, cons: list[ConstraintData]): ...
    @abc.abstractmethod
    def remove_block(self, block: BlockData): ...
    @abc.abstractmethod
    def set_objective(self, obj: ObjectiveData): ...
    @abc.abstractmethod
    def update_variables(self, variables: list[VarData]): ...
    @abc.abstractmethod
    def update_params(self): ...

class PersistentSolutionLoader(SolutionLoaderBase):
    def __init__(self, solver: PersistentSolver) -> None: ...
    def get_primals(self, vars_to_load=None): ...
    def get_duals(
        self, cons_to_load: Sequence[ConstraintData] | None = None
    ) -> dict[ConstraintData, float]: ...
    def get_slacks(
        self, cons_to_load: Sequence[ConstraintData] | None = None
    ) -> dict[ConstraintData, float]: ...
    def get_reduced_costs(
        self, vars_to_load: Sequence[VarData] | None = None
    ) -> Mapping[VarData, float]: ...
    def invalidate(self) -> None: ...

class PersistentBase(abc.ABC, metaclass=abc.ABCMeta):
    use_extensions: bool
    def __init__(self, only_child_vars: bool = False) -> None: ...
    @property
    def update_config(self): ...
    @update_config.setter
    def update_config(self, val: UpdateConfig): ...
    def set_instance(self, model) -> None: ...
    def add_variables(self, variables: list[VarData]): ...
    def add_params(self, params: list[ParamData]): ...
    def add_constraints(self, cons: list[ConstraintData]): ...
    def add_sos_constraints(self, cons: list[SOSConstraintData]): ...
    def set_objective(self, obj: ObjectiveData): ...
    def add_block(self, block) -> None: ...
    def remove_constraints(self, cons: list[ConstraintData]): ...
    def remove_sos_constraints(self, cons: list[SOSConstraintData]): ...
    def remove_variables(self, variables: list[VarData]): ...
    def remove_params(self, params: list[ParamData]): ...
    def remove_block(self, block) -> None: ...
    def update_variables(self, variables: list[VarData]): ...
    @abc.abstractmethod
    def update_params(self): ...
    def update(self, timer: HierarchicalTimer = None): ...

legacy_termination_condition_map: Incomplete
legacy_solver_status_map: Incomplete
legacy_solution_status_map: Incomplete

class LegacySolverInterface:
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
        warmstart: bool = False,
    ): ...
    def available(self, exception_flag: bool = True): ...
    def license_is_valid(self) -> bool: ...
    @property
    def options(self): ...
    @options.setter
    def options(self, val) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...

class SolverFactoryClass(Factory):
    def register(self, name, doc=None): ...

SolverFactory: Incomplete
