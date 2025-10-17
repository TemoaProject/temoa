"""
Dictionary types for Temoa energy model.

This module contains dictionary type definitions used throughout
the Temoa model for various data structures and mappings.
"""

from typing import Any

from .core_types import Commodity, Period, Region, Season, Technology, TimeOfDay, Vintage

# Process-related dictionary types
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

# Commodity flow dictionary types
CommodityStreamProcessdict = dict[tuple[Region, Period, Commodity], set[tuple[Technology, Vintage]]]
CommodityBalancedict = dict[tuple[Region, Period, Commodity], Any]

# Capitalized aliases for compatibility
CommodityStreamProcessDict = CommodityStreamProcessdict
CommodityBalanceDict = CommodityBalancedict

# Technology classification dictionary types
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

# Time sequencing dictionary types
TimeNextdict = dict[tuple[Period, Season, TimeOfDay], tuple[Season, TimeOfDay]]
TimeNextSequentialdict = dict[tuple[Period, Season], Season]
SequentialToSeasondict = dict[tuple[Period, Season], Season]

# Capitalized aliases for compatibility
TimeNextDict = TimeNextdict
TimeNextSequentialDict = TimeNextSequentialdict
SequentialToSeasonDict = SequentialToSeasondict

# Geography/exchange dictionary types
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

# Switching/boolean flag dictionary types
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
