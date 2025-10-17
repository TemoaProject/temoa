# temoa/data_io/loader_manifest.py
"""
Defines the data structure for the data loading manifest.

This module contains the `LoadItem` dataclass, which serves as the schema for
the declarative manifest used by the `HybridLoader`. Each `LoadItem` instance
provides the loader with all the necessary metadata to fetch, validate, and
load a single Pyomo component (a `Set` or `Param`) from the database.

"""

from dataclasses import dataclass, field
from typing import Optional

from pyomo.core import Param, Set


@dataclass
class LoadItem:  # type: ignore[no-any-unimported]
    """
    Describes a single data component to load from the database.

    Attributes:
        component: The target Pyomo `Set` or `Param` object to be loaded.
        table: The name of the source table in the SQLite database.
        columns: A list of column names to select from the table. The last
            column is assumed to be the value for a `Param`.
        validator_name: Optional. The name of a `ViableSet` attribute on the
            `HybridLoader` instance, used for source-trace filtering.
        validation_map: A tuple indicating which column indices in the data
            correspond to the elements needing validation (e.g., region, tech).
        where_clause: Optional. An SQL `WHERE` clause to apply when querying.
        is_period_filtered: If True, the loader automatically adds a `WHERE`
            clause to filter by the active periods in a myopic run.
        is_table_required: If True, the loader will raise an error if the
            table does not exist.
        custom_loader_name: Optional. The name of a specialized method in
            `HybridLoader` to handle non-standard loading logic for this component.
        fallback_data: Optional. A list of default data tuples to use if the
            table is missing or returns no data.
    """

    component: Set | Param  # type: ignore[no-any-unimported]
    table: str
    columns: list[str]
    validator_name: Optional[str] = None
    validation_map: tuple[int, ...] = field(default_factory=tuple)
    where_clause: Optional[str] = None
    is_period_filtered: bool = True
    is_table_required: bool = True
    custom_loader_name: Optional[str] = None
    fallback_data: Optional[list[tuple[object, ...]]] = None
