"""
Type stubs for Pyomo optimization module.

This module provides type definitions for Pyomo solver-related classes
to avoid requiring Pyomo as a dependency during type checking.
"""

# Import SolverResults from results module
from .results import SolverResults

__all__ = ['SolverResults']
