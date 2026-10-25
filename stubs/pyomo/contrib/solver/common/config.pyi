from typing import TextIO

from pyomo.common.config import Bool as Bool
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.config import NonNegativeInt as NonNegativeInt
from pyomo.common.config import Path as Path
from pyomo.common.log import LogStream as LogStream
from pyomo.common.numeric_types import native_logical_types as native_logical_types
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer

def TextIO_or_Logger(val): ...

class SolverConfig(ConfigDict):
    tee: list[TextIO]
    working_dir: Path | None
    load_solutions: bool
    raise_exception_on_nonoptimal_result: bool
    symbolic_solver_labels: bool
    timer: HierarchicalTimer | None
    threads: int | None
    time_limit: float | None
    solver_options: ConfigDict
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class BranchAndBoundConfig(SolverConfig):
    rel_gap: float | None
    abs_gap: float | None
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class AutoUpdateConfig(ConfigDict):
    check_for_new_or_removed_constraints: bool
    check_for_new_or_removed_vars: bool
    check_for_new_or_removed_params: bool
    check_for_new_objective: bool
    update_constraints: bool
    update_vars: bool
    update_parameters: bool
    update_named_expressions: bool
    update_objective: bool
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class PersistentSolverConfig(SolverConfig):
    auto_updates: AutoUpdateConfig
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class PersistentBranchAndBoundConfig(PersistentSolverConfig, BranchAndBoundConfig):
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...
