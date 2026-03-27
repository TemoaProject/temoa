"""Type aliases for Temoa set types."""

from temoa.types.core_types import (
    Commodity,
    Period,
    Region,
    Season,
    Technology,
    TimeOfDay,
    Vintage,
)

# Set types for sparse indexing
ActiveFlowSet = set[
    tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]
]
ActiveFlowAnnualSet = set[tuple[Region, Period, Commodity, Technology, Vintage, Commodity]]
ActiveFlexSet = set[
    tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]
]
ActiveFlexAnnualSet = set[tuple[Region, Period, Commodity, Technology, Vintage, Commodity]]
ActiveFlowInStorageSet = set[
    tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]
]
ActiveCurtailmentSet = set[
    tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]
]
ActiveActivitySet = set[tuple[Region, Period, Technology, Vintage]]
StorageLevelIndicesSet = set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]
SeasonalStorageLevelIndicesSet = set[tuple[Region, Period, Season, Technology, Vintage]]
NewCapacitySet = set[tuple[Region, Technology, Vintage]]
ActiveCapacityAvailableSet = set[tuple[Region, Period, Technology]]
ActiveCapacityAvailableVintageSet = set[tuple[Region, Period, Technology, Vintage]]
GroupRegionActiveFlowSet = set[tuple[Region, Period, Technology]]

CommodityBalancedSet = set[tuple[Region, Period, Commodity]]
SingletonDemandsSet = set[tuple[Region, Period, Commodity]]
