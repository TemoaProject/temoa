"""
Core type aliases for Temoa energy model.

This module contains basic type aliases for commonly used dimensions
and fundamental data structures.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, NewType

# Core type aliases for commonly used dimensions
Region = NewType('Region', str)
Period = NewType('Period', int)
Technology = NewType('Technology', str)
Sector = NewType('Sector', str)
Vintage = NewType('Vintage', int)
Season = NewType('Season', str)
TimeOfDay = NewType('TimeOfDay', str)
Commodity = NewType('Commodity', str)
Process = NewType('Process', str)

# Type aliases for common data structures
SparseIndex = (
    tuple[Region, Period]
    | tuple[Region, Period, Technology]
    | tuple[Region, Period, Technology, Vintage]
    | tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]
    | tuple[Any, ...]
)

# Database-related types
DatabaseConnection = Any  # sqlite3.Connection or similar
DatabaseCursor = Any  # sqlite3.Cursor or similar
QueryResult = list[tuple[Any, ...]]

# Model parameter types
ParameterValue = int | float | str | bool
Parameterdict = dict[SparseIndex, ParameterValue]

# Basic set types
StringSet = set[str]
TechSet = set[Technology]
CommoditySet = set[Commodity]
RegionSet = set[Region]
PeriodSet = set[Period]
VintageSet = set[Vintage]

# Pyomo domain types
PyomoDomain = Any  # Pyomo domain objects (NonNegativeReals, Integers, etc.)
PyomoIndexSet = Any  # Pyomo set objects used for indexing

# Configuration types
ScenarioName = str
Configdict = dict[str, Any]

# Enhanced Configuration Types
SolverName = str
"""Type alias for solver names (e.g., 'gurobi', 'cplex', 'glpk', 'cbc')."""


@dataclass(slots=True)
class ScenarioConfig:
    """
    Structured configuration for scenario-specific settings.

    This type represents configuration options that are specific to a particular
    scenario run, including solver settings, output options, and analysis modes.
    """

    scenario: str
    """Name of the scenario."""

    input_database: str
    """Path to the input database file."""

    output_database: str
    """Path to the output database file."""

    solver_name: SolverName
    """Name of the solver to use."""

    save_excel: bool
    """Whether to save results to Excel format."""

    save_duals: bool
    """Whether to save dual variables."""

    save_storage_levels: bool
    """Whether to save storage level information."""


@dataclass(slots=True)
class SolverConfig:
    """
    Configuration for solver-specific settings.

    This type represents solver options and parameters that control
    the optimization process.
    """

    solver_name: SolverName
    """Name of the solver."""

    options: dict[str, Any] = field(default_factory=dict)
    """Solver-specific options dictionary."""

    time_limit: float | None = None
    """Maximum time limit for solving (in seconds)."""

    mip_gap: float | None = None
    """MIP gap tolerance for mixed-integer problems."""


@dataclass(slots=True)
class OutputConfig:
    """
    Configuration for output format and content settings.

    This type represents options that control what results are saved
    and in what format.
    """

    save_excel: bool
    """Whether to save results to Excel format."""

    save_duals: bool
    """Whether to save dual variables."""

    save_storage_levels: bool
    """Whether to save storage level information."""

    save_lp_file: bool
    """Whether to save the LP file."""

    output_path: str
    """Path where output files should be saved."""


# Constraint rule types
ConstraintRule = Callable[..., object]
IndexsetRule = Callable[..., set[object]]
