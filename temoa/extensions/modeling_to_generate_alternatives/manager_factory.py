from __future__ import annotations

from typing import TYPE_CHECKING, Any

from temoa.extensions.modeling_to_generate_alternatives.mga_constants import MgaAxis, MgaWeighting
from temoa.extensions.modeling_to_generate_alternatives.tech_activity_vector_manager import (
    TechActivityVectorManager,
)
from temoa.extensions.modeling_to_generate_alternatives.tech_capacity_vector_manager import (
    TechCapacityVectorManager,
)
from temoa.extensions.modeling_to_generate_alternatives.tech_emission_vector_manager import (
    TechEmissionVectorManager,
)

if TYPE_CHECKING:
    import sqlite3

    from temoa.core.model import TemoaModel
    from temoa.extensions.modeling_to_generate_alternatives.vector_manager import VectorManager


def get_manager(
    axis: MgaAxis,
    weighting: MgaWeighting,
    model: TemoaModel,
    con: sqlite3.Connection | None,
    **kwargs: Any,
) -> VectorManager:
    manager_class: type[TechActivityVectorManager]
    match axis:
        case MgaAxis.TECH_CATEGORY_ACTIVITY:
            manager_class = TechActivityVectorManager
        case MgaAxis.TECH_CATEGORY_CAPACITY:
            manager_class = TechCapacityVectorManager
        case MgaAxis.TECH_CATEGORY_EMISSION:
            manager_class = TechEmissionVectorManager
        case _:
            raise NotImplementedError('This axis is not yet supported')
    if weighting != MgaWeighting.HULL_EXPANSION:
        raise NotImplementedError(f'{axis.name} is only implemented for HULL_EXPANSION')
    if con is None:
        raise ValueError(f'Connection is required for {axis.name}')
    return manager_class(base_model=model, conn=con, weighting=weighting, **kwargs)
