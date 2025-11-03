# Types module for TEMOA


# Define public API for this module
# ruff: noqa: RUF022
__all__ = [
    # Core types
    'Commodity',
    'CommoditySet',
    'Period',
    'Region',
    'RegionSet',
    'Season',
    'SparseIndex',
    'Technology',
    'TechSet',
    'TimeOfDay',
    'Vintage',
    'Sector',
    # Dictionary types
    'ActiveRegionsForTechDict',
    'BaseloadVintagesDict',
    'CapacityConsumptionTechsDict',
    'CapacityFactorProcessDict',
    'CommodityStreamProcessDict',
    'CurtailmentVintagesDict',
    'EfficiencyVariableDict',
    'ExportRegionsDict',
    'ImportRegionsDict',
    'InputSplitAnnualVintagesDict',
    'InputSplitVintagesDict',
    'OutputSplitAnnualVintagesDict',
    'OutputSplitVintagesDict',
    'ProcessInputsByOutputDict',
    'ProcessInputsDict',
    'ProcessLoansDict',
    'ProcessOutputsByInputDict',
    'ProcessOutputsDict',
    'ProcessPeriodsDict',
    'ProcessReservePeriodsDict',
    'ProcessTechsDict',
    'ProcessVintagesDict',
    'RampDownVintagesDict',
    'RampUpVintagesDict',
    'RetirementPeriodsDict',
    'RetirementProductionProcessesDict',
    'SeasonalStorageDict',
    'SequentialToSeasonDict',
    'StorageVintagesDict',
    'SurvivalCurvePeriodsDict',
    'SurvivalCurveProcessDict',
    'TimeNextDict',
    'TimeNextSequentialDict',
    # Index types
    'RegionPeriodSeasonTimeInputTechVintageOutput',
    'RegionPeriodTechVintage',
    # Set types
    'CommodityBalancedSet',
    'ActiveActivitySet',
    'ActiveCapacityAvailableSet',
    'ActiveCapacityAvailableVintageSet',
    'ActiveCurtailmentSet',
    'ActiveFlexAnnualSet',
    'ActiveFlexSet',
    'ActiveFlowAnnualSet',
    'ActiveFlowInStorageSet',
    'ActiveFlowSet',
    'GroupRegionActiveFlowSet',
    'NewCapacitySet',
    'SeasonalStorageLevelIndicesSet',
    'StorageLevelIndicesSet',
    # Type aliases
    'ExprLike',
]

# Core type aliases for commonly used dimensions
# ruff: noqa: RUF022
from .core_types import (
    Commodity,
    CommoditySet,
    Period,
    Region,
    RegionSet,
    Season,
    Sector,
    SparseIndex,
    Technology,
    TechSet,
    TimeOfDay,
    Vintage,
)

# Dictionary types used by the model
# ruff: noqa: RUF022
from .dict_types import (
    ActiveRegionsForTechDict,
    BaseloadVintagesDict,
    CapacityConsumptionTechsDict,
    CapacityFactorProcessDict,
    CommodityStreamProcessDict,
    CurtailmentVintagesDict,
    EfficiencyVariableDict,
    ExportRegionsDict,
    ImportRegionsDict,
    InputSplitAnnualVintagesDict,
    InputSplitVintagesDict,
    OutputSplitAnnualVintagesDict,
    OutputSplitVintagesDict,
    ProcessInputsByOutputDict,
    ProcessInputsDict,
    ProcessLoansDict,
    ProcessOutputsByInputDict,
    ProcessOutputsDict,
    ProcessPeriodsDict,
    ProcessReservePeriodsDict,
    ProcessTechsDict,
    ProcessVintagesDict,
    RampDownVintagesDict,
    RampUpVintagesDict,
    RetirementPeriodsDict,
    RetirementProductionProcessesDict,
    SeasonalStorageDict,
    SequentialToSeasonDict,
    StorageVintagesDict,
    SurvivalCurvePeriodsDict,
    SurvivalCurveProcessDict,
    TimeNextDict,
    TimeNextSequentialDict,
)

# Index tuple types
# ruff: noqa: RUF022
from .index_types import (
    RegionPeriodSeasonTimeInputTechVintageOutput,
    RegionPeriodTechVintage,
)

# Set types for sparse indexing
# ruff: noqa: RUF022
from .set_types import (
    ActiveActivitySet,
    ActiveCapacityAvailableSet,
    ActiveCapacityAvailableVintageSet,
    ActiveCurtailmentSet,
    ActiveFlexAnnualSet,
    ActiveFlexSet,
    ActiveFlowAnnualSet,
    ActiveFlowInStorageSet,
    ActiveFlowSet,
    CommodityBalancedSet,
    GroupRegionActiveFlowSet,
    NewCapacitySet,
    SeasonalStorageLevelIndicesSet,
    StorageLevelIndicesSet,
)

# Type alias for expressions that can be returned from reserve margin functions
# This covers Pyomo expressions, boolean expressions, and Constraint.Skip
ExprLike = float | bool | object  # covers Pyomo expressions and Constraint.Skip
