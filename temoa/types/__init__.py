"""
Type definitions and stubs for Temoa energy model.

This module provides comprehensive type annotations for the Temoa codebase,
including core model types, data structures, and interfaces.
"""

from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
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
RegionPeriod = tuple[Region, Period]
RegionPeriodTech = tuple[Region, Period, Technology]
RegionPeriodTechVintage = tuple[Region, Period, Technology, Vintage]
RegionPeriodSeasonTimeInputTechVintageOutput = tuple[
    Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity
]

# Type aliases for common data structures
SparseIndex = (
    RegionPeriod
    | RegionPeriodTech
    | RegionPeriodTechVintage
    | RegionPeriodSeasonTimeInputTechVintageOutput
    | tuple[Any, ...]
)

# Database-related types
DatabaseConnection = Any  # sqlite3.Connection or similar
DatabaseCursor = Any  # sqlite3.Cursor or similar
QueryResult = list[tuple[Any, ...]]

# Model parameter types
ParameterValue = int | float | str | bool
Parameterdict = dict[SparseIndex, ParameterValue]

# set types
Stringset = set[str]
Techset = set[Technology]
Commodityset = set[Commodity]
Regionset = set[Region]
Periodset = set[Period]
Vintageset = set[Vintage]

# Core index types (11 types)
RegionTech = tuple[Region, Technology]
RegionTechVintage = tuple[Region, Technology, Vintage]
RegionPeriodCommodity = tuple[Region, Period, Commodity]
PeriodSeasonTimeOfDay = tuple[Period, Season, TimeOfDay]
RegionPeriodSeasonTimeOfDay = tuple[Region, Period, Season, TimeOfDay]
RegionPeriodSeasonTimeOfDayTech = tuple[Region, Period, Season, TimeOfDay, Technology]
RegionPeriodSeasonTimeOfDayTechVintage = tuple[
    Region, Period, Season, TimeOfDay, Technology, Vintage
]
RegionPeriodSeasonTimeOfDayCommodity = tuple[Region, Period, Season, TimeOfDay, Commodity]
RegionPeriodCommodityInputTechVintageOutput = tuple[
    Region, Period, Commodity, Technology, Vintage, Commodity
]
RegionPeriodSeasonTimeOfDayCommodityTechVintageOutput = tuple[
    Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity
]
PeriodSeasonSequential = tuple[Period, Season]

# Process-related dictionary types (13 types)
ProcessInputsdict = dict[tuple[Region, Period, Technology, Vintage], set[Commodity]]
ProcessOutputsdict = dict[tuple[Region, Period, Technology, Vintage], set[Commodity]]
ProcessLoansdict = dict[tuple[Region, Technology, Vintage], float]
ProcessInputsByOutputdict = dict[
    tuple[Region, Period, Technology, Vintage, Commodity], set[Commodity]
]
ProcessOutputsByInputdict = dict[
    tuple[Region, Period, Technology, Vintage, Commodity], set[Commodity]
]
ProcessTechsdict = dict[tuple[Region, Period, Commodity], set[Technology]]
ProcessReservePeriodsdict = dict[tuple[Region, Period], set[tuple[Technology, Vintage]]]
ProcessPeriodsdict = dict[tuple[Region, Technology, Vintage], set[Period]]
RetirementPeriodsdict = dict[tuple[Region, Technology, Vintage], set[Period]]
ProcessVintagesdict = dict[tuple[Region, Period, Technology], set[Vintage]]
SurvivalCurvePeriodsdict = dict[tuple[Region, Technology, Vintage], set[Period]]
CapacityConsumptionTechsdict = dict[tuple[Region, Period, Commodity], set[Technology]]
RetirementProductionProcessesdict = dict[
    tuple[Region, Period, Commodity], set[tuple[Technology, Vintage]]
]

# Capitalized aliases for compatibility
ProcessInputsDict = ProcessInputsdict
ProcessOutputsDict = ProcessOutputsdict
ProcessLoansDict = ProcessLoansdict
ProcessInputsByOutputDict = ProcessInputsByOutputdict
ProcessOutputsByInputDict = ProcessOutputsByInputdict
ProcessTechsDict = ProcessTechsdict
ProcessReservePeriodsDict = ProcessReservePeriodsdict
ProcessPeriodsDict = ProcessPeriodsdict
RetirementPeriodsDict = RetirementPeriodsdict
ProcessVintagesDict = ProcessVintagesdict
SurvivalCurvePeriodsDict = SurvivalCurvePeriodsdict
CapacityConsumptionTechsDict = CapacityConsumptionTechsdict
RetirementProductionProcessesDict = RetirementProductionProcessesdict

# Commodity flow dictionary types (2 types)
CommodityStreamProcessdict = dict[tuple[Region, Period, Commodity], set[tuple[Technology, Vintage]]]
CommodityBalancedict = dict[tuple[Region, Period, Commodity], Any]

# Capitalized aliases for compatibility
CommodityStreamProcessDict = CommodityStreamProcessdict
CommodityBalanceDict = CommodityBalancedict

# Technology classification dictionary types (9 types)
BaseloadVintagesdict = dict[tuple[Region, Period, Technology], set[Vintage]]
CurtailmentVintagesdict = dict[tuple[Region, Period, Technology], set[Vintage]]
StorageVintagesdict = dict[tuple[Region, Period, Technology], set[Vintage]]
RampUpVintagesdict = dict[tuple[Region, Period, Technology], set[Vintage]]
RampDownVintagesdict = dict[tuple[Region, Period, Technology], set[Vintage]]
InputSplitVintagesdict = dict[tuple[Region, Period, Commodity, Technology, str], set[Vintage]]
InputSplitAnnualVintagesdict = dict[tuple[Region, Period, Commodity, Technology, str], set[Vintage]]
OutputSplitVintagesdict = dict[tuple[Region, Period, Technology, Commodity, str], set[Vintage]]
OutputSplitAnnualVintagesdict = dict[
    tuple[Region, Period, Technology, Commodity, str], set[Vintage]
]

# Capitalized aliases for compatibility
BaseloadVintagesDict = BaseloadVintagesdict
CurtailmentVintagesDict = CurtailmentVintagesdict
StorageVintagesDict = StorageVintagesdict
RampUpVintagesDict = RampUpVintagesdict
RampDownVintagesDict = RampDownVintagesdict
InputSplitVintagesDict = InputSplitVintagesdict
InputSplitAnnualVintagesDict = InputSplitAnnualVintagesdict
OutputSplitVintagesDict = OutputSplitVintagesdict
OutputSplitAnnualVintagesDict = OutputSplitAnnualVintagesdict

# Time sequencing dictionary types (3 types)
TimeNextdict = dict[tuple[Period, Season, TimeOfDay], tuple[Season, TimeOfDay]]
TimeNextSequentialdict = dict[tuple[Period, Season], Season]
SequentialToSeasondict = dict[tuple[Period, Season], Season]

# Capitalized aliases for compatibility
TimeNextDict = TimeNextdict
TimeNextSequentialDict = TimeNextSequentialdict
SequentialToSeasonDict = SequentialToSeasondict

# Geography/exchange dictionary types (3 types)
ExportRegionsdict = dict[
    tuple[Region, Period, Commodity], set[tuple[Region, Technology, Vintage, Commodity]]
]
ImportRegionsdict = dict[
    tuple[Region, Period, Commodity], set[tuple[Region, Technology, Vintage, Commodity]]
]
ActiveRegionsForTechdict = dict[tuple[Period, Technology], set[Region]]

# Capitalized aliases for compatibility
ExportRegionsDict = ExportRegionsdict
ImportRegionsDict = ImportRegionsdict
ActiveRegionsForTechDict = ActiveRegionsForTechdict

# Switching/boolean flag dictionary types (4 types)
EfficiencyVariabledict = dict[
    tuple[Region, Period, Commodity, Technology, Vintage, Commodity], bool
]
CapacityFactorProcessdict = dict[tuple[Region, Period, Technology, Vintage], bool]
SeasonalStoragedict = dict[Technology, bool]
SurvivalCurveProcessdict = dict[tuple[Region, Technology, Vintage], bool]

# Capitalized aliases for compatibility
EfficiencyVariableDict = EfficiencyVariabledict
CapacityFactorProcessDict = CapacityFactorProcessdict
SeasonalStorageDict = SeasonalStoragedict
SurvivalCurveProcessDict = SurvivalCurveProcessdict

# set types for sparse indexing (13 types)
ActiveFlowset = Optional[
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlowAnnualset = Optional[
    set[tuple[Region, Period, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlexset = Optional[
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlexAnnualset = Optional[
    set[tuple[Region, Period, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlowInStorageset = Optional[
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveCurtailmentset = Optional[
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveActivityset = Optional[set[tuple[Region, Period, Technology, Vintage]]]
StorageLevelIndicesset = Optional[
    set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]
]
SeasonalStorageLevelIndicesset = Optional[set[tuple[Region, Period, Season, Technology, Vintage]]]
NewCapacityset = Optional[set[tuple[Region, Technology, Vintage]]]
ActiveCapacityAvailableset = Optional[set[tuple[Region, Period, Technology]]]
ActiveCapacityAvailableVintageset = Optional[set[tuple[Region, Period, Technology, Vintage]]]
GroupRegionActiveFlowset = Optional[set[tuple[Region, Period, Technology]]]

# Capitalized aliases for compatibility
ActiveFlowSet = ActiveFlowset
ActiveFlowAnnualSet = ActiveFlowAnnualset
ActiveFlexSet = ActiveFlexset
ActiveFlexAnnualSet = ActiveFlexAnnualset
ActiveFlowInStorageSet = ActiveFlowInStorageset
ActiveCurtailmentSet = ActiveCurtailmentset
ActiveActivitySet = ActiveActivityset
StorageLevelIndicesSet = StorageLevelIndicesset
SeasonalStorageLevelIndicesSet = SeasonalStorageLevelIndicesset
NewCapacitySet = NewCapacityset
ActiveCapacityAvailableSet = ActiveCapacityAvailableset
ActiveCapacityAvailableVintageSet = ActiveCapacityAvailableVintageset
GroupRegionActiveFlowSet = GroupRegionActiveFlowset

# Pyomo domain types (2 types)
PyomoDomain = Any  # Pyomo domain objects (NonNegativeReals, Integers, etc.)
PyomoIndexset = Any  # Pyomo set objects used for indexing

# DataFrame types for data processing

if TYPE_CHECKING:
    from .pandas_stubs import (
        DataFrame,
        PandasDtype,
        PandasIndex,
        Series,
    )

    TemoaDataFrame = DataFrame

    from numpy.typing import NDArray

    NumpyArray = NDArray[Any]

else:
    DataFrame = Any
    Series = Any
    PandasIndex = Any
    PandasDtype = Any
    TemoaDataFrame = Any  # pd.DataFrame at runtime

    NumpyArray = Any  # np.ndarray at runtime

# Configuration types
ScenarioName = str
Configdict = dict[str, Any]

# Constraint rule types
ConstraintRule = Callable[..., Any]
IndexsetRule = Callable[..., set[Any]]

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
    'ProcessInputsdict',
    'ProcessOutputsdict',
    'ProcessLoansdict',
    'ProcessInputsByOutputdict',
    'ProcessOutputsByInputdict',
    'ProcessTechsdict',
    'ProcessReservePeriodsdict',
    'ProcessPeriodsdict',
    'RetirementPeriodsdict',
    'ProcessVintagesdict',
    'SurvivalCurvePeriodsdict',
    'CapacityConsumptionTechsdict',
    'RetirementProductionProcessesdict',
    # Commodity flow dictionary types
    'CommodityStreamProcessdict',
    'CommodityBalancedict',
    # Technology classification dictionary types
    'BaseloadVintagesdict',
    'CurtailmentVintagesdict',
    'StorageVintagesdict',
    'RampUpVintagesdict',
    'RampDownVintagesdict',
    'InputSplitVintagesdict',
    'InputSplitAnnualVintagesdict',
    'OutputSplitVintagesdict',
    'OutputSplitAnnualVintagesdict',
    # Time sequencing dictionary types
    'TimeNextdict',
    'TimeNextSequentialdict',
    'SequentialToSeasondict',
    # Geography/exchange dictionary types
    'ExportRegionsdict',
    'ImportRegionsdict',
    'ActiveRegionsForTechdict',
    # Switching/boolean flag dictionary types
    'EfficiencyVariabledict',
    'CapacityFactorProcessdict',
    'SeasonalStoragedict',
    'SurvivalCurveProcessdict',
    # set types for sparse indexing
    'ActiveFlowset',
    'ActiveFlowAnnualset',
    'ActiveFlexset',
    'ActiveFlexAnnualset',
    'ActiveFlowInStorageset',
    'ActiveCurtailmentset',
    'ActiveActivityset',
    'StorageLevelIndicesset',
    'SeasonalStorageLevelIndicesset',
    'NewCapacityset',
    'ActiveCapacityAvailableset',
    'ActiveCapacityAvailableVintageset',
    'GroupRegionActiveFlowset',
    # Pyomo domain types
    'PyomoDomain',
    'PyomoIndexset',
    # Data structure types
    'ParameterValue',
    'Parameterdict',
    'Stringset',
    'Techset',
    'Commodityset',
    'Regionset',
    'Periodset',
    'Vintageset',
    # Database types
    'DatabaseConnection',
    'DatabaseCursor',
    'QueryResult',
    # Data processing types
    'TemoaDataFrame',
    'NumpyArray',
    # Configuration types
    'ScenarioName',
    'Configdict',
    # Constraint and rule types
    'ConstraintRule',
    'IndexsetRule',
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
