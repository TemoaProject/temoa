"""
Core type aliases for Temoa energy model.

This module contains basic type aliases for commonly used dimensions
and fundamental data structures.
"""

from collections.abc import Callable
from typing import Any

# Core type aliases for commonly used dimensions
Region = str
Period = int
Technology = str
Vintage = int
Season = str
TimeOfDay = str
Commodity = str
InputCommodity = str
OutputCommodity = str
Process = str

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
Stringset = set[str]
Techset = set[Technology]
Commodityset = set[Commodity]
Regionset = set[Region]
Periodset = set[Period]
Vintageset = set[Vintage]

# Pyomo domain types
PyomoDomain = Any  # Pyomo domain objects (NonNegativeReals, Integers, etc.)
PyomoIndexset = Any  # Pyomo set objects used for indexing

# Configuration types
ScenarioName = str
Configdict = dict[str, Any]

# Constraint rule types
ConstraintRule = Callable[..., Any]
IndexsetRule = Callable[..., set[Any]]
