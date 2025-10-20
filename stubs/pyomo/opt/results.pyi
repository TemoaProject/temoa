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
