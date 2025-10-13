# temoa/data_io/loader_manifest.py
from dataclasses import dataclass, field
from typing import Optional

from pyomo.core import Param, Set

from temoa.model_checking.element_checker import ViableSet


@dataclass
class LoadItem:
    """Describes a single data component to load from the database."""

    component: Set | Param
    table: str
    columns: list[str]
    validator: Optional[ViableSet] = None
    validation_map: tuple[int, ...] = field(default_factory=tuple)
    is_period_filtered: bool = True
    is_table_required: bool = True
