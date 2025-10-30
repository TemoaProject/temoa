"""
Solver-related type definitions for Temoa energy model.

This module provides type definitions for solver results, status, and termination
conditions used throughout the Temoa codebase.
"""

from collections.abc import Mapping
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from pyomo.opt.results import SolverResults, SolverStatus, TerminationCondition
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


class TerminationConditionEnum(int, Enum):
    """
    Enumeration of possible solver termination conditions.

    These represent the specific reason why the solver terminated.
    Updated to match Pyomo 6.9.2 integer-based enum values.
    """

    convergence_criteria_satisfied = 0
    max_time_limit = 1
    iteration_limit = 2
    objective_limit = 3
    min_step_length = 4
    unbounded = 5
    proven_infeasible = 6
    locally_infeasible = 7
    infeasible_or_unbounded = 8
    error = 9
    interrupted = 10
    licensing_problems = 11
    empty_model = 12
    unknown = 42


class SolverResultsProtocol(Protocol):
    """
    Protocol defining the interface for solver results objects.

    This protocol describes the expected structure of solver results returned
    by Pyomo solvers, allowing for type-safe access to solver information.
    """

    solver: object
    """Solver information and statistics."""

    def __getitem__(self, key: str) -> object:
        """Access result components by key (e.g., 'Solution', 'Problem')."""
        ...


# Type aliases for solver-related types
SolverResults = SolverResults
"""Type alias for Pyomo SolverResults objects."""

SolverStatus = SolverStatus
"""Type alias for Pyomo SolverStatus enum."""

TerminationCondition = TerminationCondition
"""Type alias for Pyomo TerminationCondition enum."""

SolverOptions = Mapping[str, object]
"""Type alias for solver option dictionaries."""


# Export all types
# ruff: noqa: RUF022
__all__ = [
    'SolverStatusEnum',
    'TerminationConditionEnum',
    'SolverResultsProtocol',
    'SolverResults',
    'SolverStatus',
    'TerminationCondition',
    'SolverOptions',
]
