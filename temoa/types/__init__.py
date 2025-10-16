"""
Type definitions and stubs for Temoa energy model.

This module provides comprehensive type annotations for the Temoa codebase,
including core model types, data structures, and interfaces.
"""

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Set,
    Tuple,
    Union,
)

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

# Index tuples for different dimensions
RegionPeriod = Tuple[Region, Period]
RegionPeriodTech = Tuple[Region, Period, Technology]
RegionPeriodTechVintage = Tuple[Region, Period, Technology, Vintage]
RegionPeriodSeasonTimeInputTechVintageOutput = Tuple[
    Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity
]

# Type aliases for common data structures
SparseIndex = Union[
    RegionPeriod,
    RegionPeriodTech,
    RegionPeriodTechVintage,
    RegionPeriodSeasonTimeInputTechVintageOutput,
    Tuple[Any, ...],
]

# Database-related types
DatabaseConnection = Any  # sqlite3.Connection or similar
DatabaseCursor = Any  # sqlite3.Cursor or similar
QueryResult = list[tuple[Any, ...]]

# Model parameter types
ParameterValue = Union[int, float, str, bool]
ParameterDict = Dict[SparseIndex, ParameterValue]

# Set types
StringSet = Set[str]
TechSet = Set[Technology]
CommoditySet = Set[Commodity]
RegionSet = Set[Region]
PeriodSet = Set[Period]
VintageSet = Set[Vintage]

# DataFrame types for data processing
if TYPE_CHECKING:
    from .pandas_stubs import DataFrame as PandasDataFrame

    TemoaDataFrame = PandasDataFrame
else:
    TemoaDataFrame = Any  # pd.DataFrame at runtime

NumpyArray = Any  # np.ndarray at runtime

# Configuration types
ScenarioName = str
ConfigDict = Dict[str, Any]

# Export types for easy importing
__all__ = [
    # Core types
    'Region',
    'Period',
    'Technology',
    'Vintage',
    'Season',
    'TimeOfDay',
    'Commodity',
    'InputCommodity',
    'OutputCommodity',
    'Process',
    # Index types
    'RegionPeriod',
    'RegionPeriodTech',
    'RegionPeriodTechVintage',
    'RegionPeriodSeasonTimeInputTechVintageOutput',
    'SparseIndex',
    # Data structure types
    'ParameterValue',
    'ParameterDict',
    'StringSet',
    'TechSet',
    'CommoditySet',
    'RegionSet',
    'PeriodSet',
    'VintageSet',
    # Database types
    'DatabaseConnection',
    'DatabaseCursor',
    'QueryResult',
    # Data processing types
    'TemoaDataFrame',
    'NumpyArray',
    # Configuration types
    'ScenarioName',
    'ConfigDict',
    # Pyomo stub types (for type checking)
    'PyomoSet',
    'PyomoParam',
    'PyomoVar',
    'PyomoConstraint',
    'PyomoBuildAction',
    'PyomoObjective',
    'AbstractModel',
    # Pandas stub types (for type checking)
    'DataFrame',
    'Series',
    'PandasIndex',
    'PandasDtype',
]
