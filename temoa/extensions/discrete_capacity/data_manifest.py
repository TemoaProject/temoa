from __future__ import annotations

from typing import TYPE_CHECKING, cast

from temoa.data_io.loader_manifest import LoadItem

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.extensions.discrete_capacity.core.model import DiscreteCapacityModel


def build_manifest_items(model: TemoaModel) -> list[LoadItem]:
    m = cast('DiscreteCapacityModel', model)
    return [
        LoadItem(
            component=m.limit_discrete_new_capacity,
            table='limit_discrete_new_capacity',
            columns=['region', 'tech_or_group', 'capacity'],
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_table_required=False,
            is_period_filtered=False,
        ),
        LoadItem(
            component=m.limit_discrete_capacity,
            table='limit_discrete_capacity',
            columns=['region', 'tech_or_group', 'capacity'],
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_table_required=False,
            is_period_filtered=False,
        ),
    ]
