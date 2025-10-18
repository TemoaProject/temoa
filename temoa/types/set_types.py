"""
Set types for Temoa energy model.

This module contains set type definitions used for sparse indexing
and various collections in the Temoa model.
"""

from typing import Optional

from .core_types import Commodity, Period, Region, Season, Technology, TimeOfDay, Vintage

# Set types for sparse indexing
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

CommodityBalancedSet = set[tuple[Region, Period, Commodity]]


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
