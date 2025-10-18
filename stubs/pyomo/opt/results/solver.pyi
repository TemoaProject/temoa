import enum

from pyomo.opt.results.container import MapContainer as MapContainer
from pyomo.opt.results.container import ScalarType as ScalarType

class SolverStatus(str, enum.Enum):
    ok = 'ok'
    warning = 'warning'
    error = 'error'
    aborted = 'aborted'
    unknown = 'unknown'

class TerminationCondition(str, enum.Enum):
    unknown = 'unknown'
    maxTimeLimit = 'maxTimeLimit'
    maxIterations = 'maxIterations'
    minFunctionValue = 'minFunctionValue'
    minStepLength = 'minStepLength'
    globallyOptimal = 'globallyOptimal'
    locallyOptimal = 'locallyOptimal'
    feasible = 'feasible'
    optimal = 'optimal'
    maxEvaluations = 'maxEvaluations'
    other = 'other'
    unbounded = 'unbounded'
    infeasible = 'infeasible'
    infeasibleOrUnbounded = 'infeasibleOrUnbounded'
    invalidProblem = 'invalidProblem'
    intermediateNonInteger = 'intermediateNonInteger'
    noSolution = 'noSolution'
    solverFailure = 'solverFailure'
    internalSolverError = 'internalSolverError'
    error = 'error'
    userInterrupt = 'userInterrupt'
    resourceInterrupt = 'resourceInterrupt'
    licensingProblems = 'licensingProblems'
    @staticmethod
    def to_solver_status(tc): ...

def check_optimal_termination(results): ...
def assert_optimal_termination(results) -> None: ...

class BranchAndBoundStats(MapContainer):
    def __init__(self) -> None: ...

class BlackBoxStats(MapContainer):
    def __init__(self) -> None: ...

class SolverStatistics(MapContainer):
    def __init__(self) -> None: ...

class SolverInformation(MapContainer):
    def __init__(self) -> None: ...
