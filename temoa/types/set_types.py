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
ActiveFlowSet = (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
)
ActiveFlowAnnualSet = set[tuple[Region, Period, Commodity, Technology, Vintage, Commodity]] | None
ActiveFlexSet = (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
)
ActiveFlexAnnualSet = set[tuple[Region, Period, Commodity, Technology, Vintage, Commodity]] | None
ActiveFlowInStorageSet = (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
)
ActiveCurtailmentSet = (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
)
ActiveActivitySet = set[tuple[Region, Period, Technology, Vintage]] | None
StorageLevelIndicesSet = set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]] | None
SeasonalStorageLevelIndicesSet = set[tuple[Region, Period, Season, Technology, Vintage]] | None
NewCapacitySet = set[tuple[Region, Technology, Vintage]] | None
ActiveCapacityAvailableSet = set[tuple[Region, Period, Technology]] | None
ActiveCapacityAvailableVintageSet = set[tuple[Region, Period, Technology, Vintage]] | None
GroupRegionActiveFlowSet = set[tuple[Region, Period, Technology]] | None

CommodityBalancedSet = set[tuple[Region, Period, Commodity]]
