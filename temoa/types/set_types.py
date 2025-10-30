"""
Set types for Temoa energy model.

This module contains set type definitions used for sparse indexing
and various collections in the Temoa model.
"""

from typing import Optional

from .core_types import Commodity, Period, Region, Season, Technology, TimeOfDay, Vintage

# Set types for sparse indexing
ActiveFlowSet = Optional[
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlowAnnualSet = Optional[
    set[tuple[Region, Period, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlexSet = Optional[
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlexAnnualSet = Optional[
    set[tuple[Region, Period, Commodity, Technology, Vintage, Commodity]]
]
ActiveFlowInStorageSet = Optional[
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveCurtailmentSet = Optional[
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]]
]
ActiveActivitySet = Optional[set[tuple[Region, Period, Technology, Vintage]]]
StorageLevelIndicesSet = Optional[
    set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]
]
SeasonalStorageLevelIndicesSet = Optional[set[tuple[Region, Period, Season, Technology, Vintage]]]
NewCapacitySet = Optional[set[tuple[Region, Technology, Vintage]]]
ActiveCapacityAvailableSet = Optional[set[tuple[Region, Period, Technology]]]
ActiveCapacityAvailableVintageSet = Optional[set[tuple[Region, Period, Technology, Vintage]]]
GroupRegionActiveFlowSet = Optional[set[tuple[Region, Period, Technology]]]

CommodityBalancedSet = set[tuple[Region, Period, Commodity]]
