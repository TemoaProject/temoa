"""
Dictionary types for Temoa energy model.

This module contains dictionary type definitions used throughout
the Temoa model for various data structures and mappings.
"""

from .core_types import Commodity, Period, Region, Season, Technology, TimeOfDay, Vintage

# Process-related dictionary types
ProcessInputsDict = dict[tuple[Region, Period, Technology, Vintage], set[Commodity]]
ProcessOutputsDict = dict[tuple[Region, Period, Technology, Vintage], set[Commodity]]
ProcessLoansDict = dict[tuple[Region, Technology, Vintage], float]
ProcessInputsByOutputDict = dict[
    tuple[Region, Period, Technology, Vintage, Commodity], set[Commodity]
]
ProcessOutputsByInputDict = dict[
    tuple[Region, Period, Technology, Vintage, Commodity], set[Commodity]
]
ProcessTechsDict = dict[tuple[Region, Period, Commodity], set[Technology]]
ProcessReservePeriodsDict = dict[tuple[Region, Period], set[tuple[Technology, Vintage]]]
ProcessPeriodsDict = dict[tuple[Region, Technology, Vintage], set[Period]]
RetirementPeriodsDict = dict[tuple[Region, Technology, Vintage], set[Period]]
ProcessVintagesDict = dict[tuple[Region, Period, Technology], set[Vintage]]
SurvivalCurvePeriodsDict = dict[tuple[Region, Technology, Vintage], set[Period]]
CapacityConsumptionTechsDict = dict[tuple[Region, Period, Commodity], set[Technology]]
RetirementProductionProcessesDict = dict[
    tuple[Region, Period, Commodity], set[tuple[Technology, Vintage]]
]


# Commodity flow dictionary types
CommodityStreamProcessDict = dict[tuple[Region, Period, Commodity], set[tuple[Technology, Vintage]]]


# Technology classification dictionary types
BaseloadVintagesDict = dict[tuple[Region, Period, Technology], set[Vintage]]
CurtailmentVintagesDict = dict[tuple[Region, Period, Technology], set[Vintage]]
StorageVintagesDict = dict[tuple[Region, Period, Technology], set[Vintage]]
RampUpVintagesDict = dict[tuple[Region, Period, Technology], set[Vintage]]
RampDownVintagesDict = dict[tuple[Region, Period, Technology], set[Vintage]]
InputSplitVintagesDict = dict[tuple[Region, Period, Commodity, Technology, str], set[Vintage]]
InputSplitAnnualVintagesDict = dict[tuple[Region, Period, Commodity, Technology, str], set[Vintage]]
OutputSplitVintagesDict = dict[tuple[Region, Period, Technology, Commodity, str], set[Vintage]]
OutputSplitAnnualVintagesDict = dict[
    tuple[Region, Period, Technology, Commodity, str], set[Vintage]
]


# Time sequencing dictionary types
TimeNextDict = dict[tuple[Period, Season, TimeOfDay], tuple[Season, TimeOfDay]]
TimeNextSequentialDict = dict[tuple[Period, Season], Season]
SequentialToSeasonDict = dict[tuple[Period, Season], Season]


# Geography/exchange dictionary types
ExportRegionsDict = dict[
    tuple[Region, Period, Commodity], set[tuple[Region, Technology, Vintage, Commodity]]
]
ImportRegionsDict = dict[
    tuple[Region, Period, Commodity], set[tuple[Region, Technology, Vintage, Commodity]]
]
ActiveRegionsForTechDict = dict[tuple[Period, Technology], set[Region]]


# Switching/boolean flag dictionary types
EfficiencyVariableDict = dict[
    tuple[Region, Period, Commodity, Technology, Vintage, Commodity], bool
]
CapacityFactorProcessDict = dict[tuple[Region, Period, Technology, Vintage], bool]
SeasonalStorageDict = dict[Technology, bool]
SurvivalCurveProcessDict = dict[tuple[Region, Technology, Vintage], bool]
