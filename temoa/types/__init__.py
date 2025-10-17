"""
Type definitions and stubs for Temoa energy model.

This module provides comprehensive type annotations for the Temoa codebase,
including core model types, data structures, and interfaces.
"""

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Optional,
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

# Core index types (11 types)
RegionTech = Tuple[Region, Technology]
RegionTechVintage = Tuple[Region, Technology, Vintage]
RegionPeriodCommodity = Tuple[Region, Period, Commodity]
PeriodSeasonTimeOfDay = Tuple[Period, Season, TimeOfDay]
RegionPeriodSeasonTimeOfDay = Tuple[Region, Period, Season, TimeOfDay]
RegionPeriodSeasonTimeOfDayTech = Tuple[Region, Period, Season, TimeOfDay, Technology]
RegionPeriodSeasonTimeOfDayTechVintage = Tuple[
    Region, Period, Season, TimeOfDay, Technology, Vintage
]
RegionPeriodSeasonTimeOfDayCommodity = Tuple[Region, Period, Season, TimeOfDay, Commodity]
RegionPeriodCommodityInputTechVintageOutput = Tuple[
    Region, Period, Commodity, Technology, Vintage, Commodity
]
RegionPeriodSeasonTimeOfDayCommodityTechVintageOutput = Tuple[
    Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity
]
PeriodSeasonSequential = Tuple[Period, Season]

# Process-related dictionary types (13 types)
ProcessInputsDict = Dict[Tuple[Region, Period, Technology, Vintage], Set[Commodity]]
ProcessOutputsDict = Dict[Tuple[Region, Period, Technology, Vintage], Set[Commodity]]
ProcessLoansDict = Dict[Tuple[Region, Technology, Vintage], float]
ProcessInputsByOutputDict = Dict[
    Tuple[Region, Period, Technology, Vintage, Commodity], Set[Commodity]
]
ProcessOutputsByInputDict = Dict[
    Tuple[Region, Period, Technology, Vintage, Commodity], Set[Commodity]
]
ProcessTechsDict = Dict[Tuple[Region, Period, Commodity], Set[Technology]]
ProcessReservePeriodsDict = Dict[Tuple[Region, Period], Set[Tuple[Technology, Vintage]]]
ProcessPeriodsDict = Dict[Tuple[Region, Technology, Vintage], Set[Period]]
RetirementPeriodsDict = Dict[Tuple[Region, Technology, Vintage], Set[Period]]
ProcessVintagesDict = Dict[Tuple[Region, Period, Technology], Set[Vintage]]
SurvivalCurvePeriodsDict = Dict[Tuple[Region, Technology, Vintage], Set[Period]]
CapacityConsumptionTechsDict = Dict[Tuple[Region, Period, Commodity], Set[Technology]]
RetirementProductionProcessesDict = Dict[
    Tuple[Region, Period, Commodity], Set[Tuple[Technology, Vintage]]
]

# Commodity flow dictionary types (2 types)
CommodityStreamProcessDict = Dict[Tuple[Region, Period, Commodity], Set[Tuple[Technology, Vintage]]]
CommodityBalanceDict = Dict[Tuple[Region, Period, Commodity], Any]

# Technology classification dictionary types (9 types)
BaseloadVintagesDict = Dict[Tuple[Region, Period, Technology], Set[Vintage]]
CurtailmentVintagesDict = Dict[Tuple[Region, Period, Technology], Set[Vintage]]
StorageVintagesDict = Dict[Tuple[Region, Period, Technology], Set[Vintage]]
RampUpVintagesDict = Dict[Tuple[Region, Period, Technology], Set[Vintage]]
RampDownVintagesDict = Dict[Tuple[Region, Period, Technology], Set[Vintage]]
InputSplitVintagesDict = Dict[Tuple[Region, Period, Commodity, Technology, str], Set[Vintage]]
InputSplitAnnualVintagesDict = Dict[Tuple[Region, Period, Commodity, Technology, str], Set[Vintage]]
OutputSplitVintagesDict = Dict[Tuple[Region, Period, Technology, Commodity, str], Set[Vintage]]
OutputSplitAnnualVintagesDict = Dict[
    Tuple[Region, Period, Technology, Commodity, str], Set[Vintage]
]

# Time sequencing dictionary types (3 types)
TimeNextDict = Dict[Tuple[Period, Season, TimeOfDay], Tuple[Season, TimeOfDay]]
TimeNextSequentialDict = Dict[Tuple[Period, Season], Season]
SequentialToSeasonDict = Dict[Tuple[Period, Season], Season]

# Geography/exchange dictionary types (3 types)
ExportRegionsDict = Dict[
    Tuple[Region, Period, Commodity], Set[Tuple[Region, Technology, Vintage, Commodity]]
]
ImportRegionsDict = Dict[
    Tuple[Region, Period, Commodity], Set[Tuple[Region, Technology, Vintage, Commodity]]
]
ActiveRegionsForTechDict = Dict[Tuple[Period, Technology], Set[Region]]

# Switching/boolean flag dictionary types (4 types)
EfficiencyVariableDict = Dict[
    Tuple[Region, Period, Commodity, Technology, Vintage, Commodity], bool
]
CapacityFactorProcessDict = Dict[Tuple[Region, Period, Technology, Vintage], bool]
SeasonalStorageDict = Dict[Technology, bool]
SurvivalCurveProcessDict = Dict[Tuple[Region, Technology, Vintage], bool]

# Set types for sparse indexing (13 types)
ActiveFlowSet = Optional[
    Set[Tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlowAnnualSet = Optional[
    Set[Tuple[Region, Period, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlexSet = Optional[
    Set[Tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlexAnnualSet = Optional[
    Set[Tuple[Region, Period, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlowInStorageSet = Optional[
    Set[Tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveCurtailmentSet = Optional[
    Set[Tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveActivitySet = Optional[Set[Tuple[Region, Period, Technology, Vintage]]]
StorageLevelIndicesSet = Optional[
    Set[Tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]
]
SeasonalStorageLevelIndicesSet = Optional[Set[Tuple[Region, Period, Season, Technology, Vintage]]]
NewCapacitySet = Optional[Set[Tuple[Region, Technology, Vintage]]]
ActiveCapacityAvailableSet = Optional[Set[Tuple[Region, Period, Technology]]]
ActiveCapacityAvailableVintageSet = Optional[Set[Tuple[Region, Period, Technology, Vintage]]]
GroupRegionActiveFlowSet = Optional[Set[Tuple[Region, Period, Technology]]]

# Pyomo domain types (2 types)
PyomoDomain = Any  # Pyomo domain objects (NonNegativeReals, Integers, etc.)
PyomoIndexSet = Any  # Pyomo Set objects used for indexing

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

# Constraint rule types
ConstraintRule = Callable[..., Any]
IndexSetRule = Callable[..., Set[Any]]

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
    # Core index types
    'RegionTech',
    'RegionTechVintage',
    'RegionPeriodCommodity',
    'PeriodSeasonTimeOfDay',
    'RegionPeriodSeasonTimeOfDay',
    'RegionPeriodSeasonTimeOfDayTech',
    'RegionPeriodSeasonTimeOfDayTechVintage',
    'RegionPeriodSeasonTimeOfDayCommodity',
    'RegionPeriodCommodityInputTechVintageOutput',
    'RegionPeriodSeasonTimeOfDayCommodityTechVintageOutput',
    'PeriodSeasonSequential',
    # Process-related dictionary types
    'ProcessInputsDict',
    'ProcessOutputsDict',
    'ProcessLoansDict',
    'ProcessInputsByOutputDict',
    'ProcessOutputsByInputDict',
    'ProcessTechsDict',
    'ProcessReservePeriodsDict',
    'ProcessPeriodsDict',
    'RetirementPeriodsDict',
    'ProcessVintagesDict',
    'SurvivalCurvePeriodsDict',
    'CapacityConsumptionTechsDict',
    'RetirementProductionProcessesDict',
    # Commodity flow dictionary types
    'CommodityStreamProcessDict',
    'CommodityBalanceDict',
    # Technology classification dictionary types
    'BaseloadVintagesDict',
    'CurtailmentVintagesDict',
    'StorageVintagesDict',
    'RampUpVintagesDict',
    'RampDownVintagesDict',
    'InputSplitVintagesDict',
    'InputSplitAnnualVintagesDict',
    'OutputSplitVintagesDict',
    'OutputSplitAnnualVintagesDict',
    # Time sequencing dictionary types
    'TimeNextDict',
    'TimeNextSequentialDict',
    'SequentialToSeasonDict',
    # Geography/exchange dictionary types
    'ExportRegionsDict',
    'ImportRegionsDict',
    'ActiveRegionsForTechDict',
    # Switching/boolean flag dictionary types
    'EfficiencyVariableDict',
    'CapacityFactorProcessDict',
    'SeasonalStorageDict',
    'SurvivalCurveProcessDict',
    # Set types for sparse indexing
    'ActiveFlowSet',
    'ActiveFlowAnnualSet',
    'ActiveFlexSet',
    'ActiveFlexAnnualSet',
    'ActiveFlowInStorageSet',
    'ActiveCurtailmentSet',
    'ActiveActivitySet',
    'StorageLevelIndicesSet',
    'SeasonalStorageLevelIndicesSet',
    'NewCapacitySet',
    'ActiveCapacityAvailableSet',
    'ActiveCapacityAvailableVintageSet',
    'GroupRegionActiveFlowSet',
    # Pyomo domain types
    'PyomoDomain',
    'PyomoIndexSet',
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
    # Constraint and rule types
    'ConstraintRule',
    'IndexSetRule',
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
