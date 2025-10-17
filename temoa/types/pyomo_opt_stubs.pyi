"""
Type stubs for Pyomo optimization module.

This module provides minimal type definitions for Pyomo solver-related classes
to avoid requiring Pyomo as a dependency during type checking.
"""

from enum import Enum
from typing import Any

class SolverResults:
    """Stub for Pyomo SolverResults class."""

    def __init__(self, solver: Any = None) -> None: ...
    def __getitem__(self, key: str) -> Any: ...
    @property
    def solver(self) -> Any: ...

class SolverStatus(Enum):
    """Stub for Pyomo SolverStatus enum."""

    OK = 'ok'
    WARNING = 'warning'
    ERROR = 'error'
    ABORTED = 'aborted'
    UNKNOWN = 'unknown'

class TerminationCondition(Enum):
    """Stub for Pyomo TerminationCondition enum."""

    OPTIMAL = 'optimal'
    INFEASIBLE = 'infeasible'
    UNBOUNDED = 'unbounded'
    INFEASIBLE_OR_UNBOUNDED = 'infeasibleOrUnbounded'
    MAX_TIME_LIMIT = 'maxTimeLimit'
    MAX_ITERATIONS = 'maxIterations'
    MAX_EVALUATIONS = 'maxEvaluations'
    MIN_STEP_LENGTH = 'minStepLength'
    MIN_FUNCTION_VALUE = 'minFunctionValue'
    OTHER = 'other'
    UNKNOWN = 'unknown'
    SOLVER_FAILURE = 'solverFailure'
    INTERNAL_SOLVER_ERROR = 'internalSolverError'
    ERROR = 'error'
    USER_INTERRUPT = 'userInterrupt'
    RESOURCE_INTERRUPT = 'resourceInterrupt'
    LICENSING_PROBLEMS = 'licensingProblems'
