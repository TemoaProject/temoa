"""
Database schema type definitions for Temoa energy model.

This module provides type definitions for database tables, columns, and schema
versioning used throughout the Temoa codebase.
"""

from collections.abc import Mapping, Sequence
from typing import Protocol

# Type aliases for database schema elements
TableName = str
"""Type alias for database table names."""

ColumnName = str
"""Type alias for database column names."""

SchemaVersion = tuple[int, int]
"""Type alias for schema version (major, minor)."""


class DatabaseSchema(Protocol):
    """
    Protocol defining the interface for database schema objects.

    This protocol describes the expected structure of database schema
    information, allowing for type-safe access to schema metadata.
    """

    version: SchemaVersion
    """Schema version as (major, minor) tuple."""

    tables: Mapping[TableName, Sequence[ColumnName]]
    """Mapping of table names to their column names."""

    def get_table_columns(self, table: TableName) -> Sequence[ColumnName]:
        """
        Get the list of columns for a given table.

        Args:
            table: Name of the table

        Returns:
            Sequence of column names for the table
        """
        ...

    def validate_table(self, table: TableName) -> bool:
        """
        Validate that a table exists in the schema.

        Args:
            table: Name of the table to validate

        Returns:
            True if table exists, False otherwise
        """
        ...


# Common table row types for major Temoa tables
class TechnologyRow(Protocol):
    """Protocol for Technology table rows."""

    region: str
    tech: str
    flag: str
    sector: str
    tech_desc: str | None


class CommodityRow(Protocol):
    """Protocol for Commodity table rows."""

    region: str
    comm_name: str
    flag: str
    comm_desc: str | None


class TimePeriodsRow(Protocol):
    """Protocol for TimePeriods table rows."""

    t_periods: int
    flag: str


class EfficiencyRow(Protocol):
    """Protocol for Efficiency table rows."""

    region: str
    input_comm: str
    tech: str
    vintage: int
    output_comm: str
    efficiency: float
    eff_notes: str | None


class CapacityFactorRow(Protocol):
    """Protocol for CapacityFactor table rows."""

    region: str
    season: str
    time_of_day: str
    tech: str
    vintage: int
    cf_process: float
    cf_process_notes: str | None


class DemandRow(Protocol):
    """Protocol for Demand table rows."""

    region: str
    periods: int
    demand_comm: str
    demand: float
    demand_units: str
    demand_notes: str | None


class EmissionActivityRow(Protocol):
    """Protocol for EmissionActivity table rows."""

    region: str
    emis_comm: str
    input_comm: str
    tech: str
    vintage: int
    output_comm: str
    emis_act: float
    emis_act_units: str
    emis_act_notes: str | None


# Query result types
TechnologyQueryResult = Sequence[Mapping[str, object]]
"""Type alias for technology query results."""
CommodityQueryResult = Sequence[Mapping[str, object]]
"""Type alias for commodity query results."""
EfficiencyQueryResult = Sequence[Mapping[str, object]]
"""Type alias for efficiency query results."""
GenericQueryResult = Sequence[Mapping[str, object]]
"""Type alias for generic query results."""


# Export all types
# ruff: noqa: RUF022
__all__ = [
    'TableName',
    'ColumnName',
    'SchemaVersion',
    'DatabaseSchema',
    'TechnologyRow',
    'CommodityRow',
    'TimePeriodsRow',
    'EfficiencyRow',
    'CapacityFactorRow',
    'DemandRow',
    'EmissionActivityRow',
    'TechnologyQueryResult',
    'CommodityQueryResult',
    'EfficiencyQueryResult',
    'GenericQueryResult',
]
