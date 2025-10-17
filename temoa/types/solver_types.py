"""
Solver-related type definitions for Temoa energy model.

This module provides type definitions for solver results, status, and termination
conditions used throughout the Temoa codebase.
"""

from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from pyomo.opt import SolverResults as PyomoSolverResults
    from pyomo.opt import SolverStatus as PyomoSolverStatus
    from pyomo.opt import TerminationCondition as PyomoTerminationCondition
else:
    # Runtime fallbacks
    PyomoSolverResults = Any
    PyomoSolverStatus = Any
    PyomoTerminationCondition = Any


class SolverStatusEnum(str, Enum):
    """
    Enumeration of possible solver status values.

    These represent the high-level status of the solver after attempting to solve.
    """

    OK = 'ok'
    WARNING = 'warning'
    ERROR = 'error'
    ABORTED = 'aborted'
    UNKNOWN = 'unknown'


class TerminationConditionEnum(str, Enum):
    """
    Enumeration of possible solver termination conditions.

    These represent the specific reason why the solver terminated.
    """

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


class SolverResultsProtocol(Protocol):
    """
    Protocol defining the interface for solver results objects.

    This protocol describes the expected structure of solver results returned
    by Pyomo solvers, allowing for type-safe access to solver information.
    """

    solver: Any
    """Solver information and statistics."""

    def __getitem__(self, key: str) -> Any:
        """Access result components by key (e.g., 'Solution', 'Problem')."""
        ...


# Type aliases for solver-related types
SolverResults = PyomoSolverResults
"""Type alias for Pyomo SolverResults objects."""

SolverStatus = PyomoSolverStatus
"""Type alias for Pyomo SolverStatus enum."""

TerminationCondition = PyomoTerminationCondition
"""Type alias for Pyomo TerminationCondition enum."""

SolverOptions = dict[str, Any]
"""Type alias for solver option dictionaries."""


# Export all types
__all__ = [
    'SolverStatusEnum',
    'TerminationConditionEnum',
    'SolverResultsProtocol',
    'SolverResults',
    'SolverStatus',
    'TerminationCondition',
    'SolverOptions',
]
