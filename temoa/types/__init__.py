# Types module for TEMOA

from typing import Union

# Define public API for this module
__all__ = [
    # Core types
    'Commodity',
    'Commodityset',
    'Period',
    'Region',
    'Regionset',
    'Season',
    'SparseIndex',
    'Technology',
    'Techset',
    'TimeOfDay',
    'Vintage',
    # Dictionary types
    'ActiveRegionsForTechDict',
    'BaseloadVintagesDict',
    'CapacityConsumptionTechsDict',
    'CapacityFactorProcessDict',
    'CommodityBalanceDict',
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
from .core_types import (
    Commodity,
    Commodityset,
    Period,
    Region,
    Regionset,
    Season,
    SparseIndex,
    Technology,
    Techset,
    TimeOfDay,
    Vintage,
)

# Dictionary types used by the model
from .dict_types import (
    ActiveRegionsForTechDict,
    BaseloadVintagesDict,
    CapacityConsumptionTechsDict,
    CapacityFactorProcessDict,
    CommodityBalanceDict,
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
from .index_types import (
    RegionPeriodSeasonTimeInputTechVintageOutput,
    RegionPeriodTechVintage,
)

# Set types for sparse indexing
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
    GroupRegionActiveFlowSet,
    NewCapacitySet,
    SeasonalStorageLevelIndicesSet,
    StorageLevelIndicesSet,
)

# Type alias for expressions that can be returned from reserve margin functions
# This covers Pyomo expressions, boolean expressions, and Constraint.Skip
ExprLike = Union[
    float,  # Numeric expressions from calculations
    bool,  # Boolean expressions from constraint comparisons
]
