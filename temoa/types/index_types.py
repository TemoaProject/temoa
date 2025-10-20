"""
Index tuple types for Temoa energy model.

This module contains tuple type definitions used for indexing
various data structures in the Temoa model.
"""

from .core_types import Commodity, Period, Region, Season, Technology, TimeOfDay, Vintage

# Basic index tuples
RegionPeriod = tuple[Region, Period]
RegionPeriodTech = tuple[Region, Period, Technology]
RegionPeriodTechVintage = tuple[Region, Period, Technology, Vintage]
RegionPeriodSeasonTimeInputTechVintageOutput = tuple[
    Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity
]

# Extended index types
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
