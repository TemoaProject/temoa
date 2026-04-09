from __future__ import annotations

from typing import TYPE_CHECKING, Any

from temoa.extensions.modeling_to_generate_alternatives.mga_constants import MgaAxis, MgaWeighting
from temoa.extensions.modeling_to_generate_alternatives.tech_activity_vector_manager import (
    TechActivityVectorManager,
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
    match axis:
        case MgaAxis.TECH_CATEGORY_ACTIVITY:
            if weighting != MgaWeighting.HULL_EXPANSION:
                raise NotImplementedError(
                    'TECH_CATEGORY_ACTIVITY is only implemented for HULL_EXPANSION'
                )
            if con is None:
                raise ValueError('Connection is required for TECH_CATEGORY_ACTIVITY')
            return TechActivityVectorManager(
                base_model=model, conn=con, weighting=weighting, **kwargs
            )
        case _:
            raise NotImplementedError('This axis is not yet supported')
