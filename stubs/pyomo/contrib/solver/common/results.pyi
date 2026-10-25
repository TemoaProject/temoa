import enum

from _typeshed import Incomplete
from pyomo.common.config import ADVANCED_OPTION as ADVANCED_OPTION
from pyomo.common.config import DEVELOPER_OPTION as DEVELOPER_OPTION
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import In as In
from pyomo.common.config import IsInstance as IsInstance
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.config import NonNegativeInt as NonNegativeInt

class TerminationCondition(enum.Enum):
    convergenceCriteriaSatisfied = 0
    maxTimeLimit = 1
    iterationLimit = 2
    objectiveLimit = 3
    minStepLength = 4
    unbounded = 5
    provenInfeasible = 6
    locallyInfeasible = 7
    infeasibleOrUnbounded = 8
    error = 9
    interrupted = 10
    licensingProblems = 11
    emptyModel = 12
    unknown = 42

class SolutionStatus(enum.Enum):
    noSolution = 0
    infeasible = 10
    feasible = 20
    optimal = 30

class Results(ConfigDict):
    solution_loader: Incomplete
    termination_condition: TerminationCondition
    solution_status: SolutionStatus
    incumbent_objective: float | None
    objective_bound: float | None
    solver_name: str | None
    solver_version: tuple[int, ...] | None
    iteration_count: int | None
    timing_info: ConfigDict
    extra_info: ConfigDict
    solver_config: ConfigDict
    solver_log: str
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...
    def display(
        self, content_filter=None, indent_spacing: int = 2, ostream=None, visibility: int = 0
    ): ...

legacy_termination_condition_map: Incomplete
legacy_solver_status_map: Incomplete

def legacy_solution_status_map(results): ...
