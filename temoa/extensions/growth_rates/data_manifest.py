from __future__ import annotations

from typing import TYPE_CHECKING, cast

from temoa.data_io.loader_manifest import LoadItem

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.extensions.growth_rates.core.model import GrowthRatesModel


def build_manifest_items(model: TemoaModel) -> list[LoadItem]:
    """Return LoadItems for growth/degrowth constraints."""
    m = cast('GrowthRatesModel', model)
    return [
        LoadItem(
            component=m.limit_growth_capacity,
            table='limit_growth_capacity',
            columns=['region', 'tech_or_group', 'operator', 'rate', 'seed'],
            index_length=3,
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=m.limit_growth_new_capacity,
            table='limit_growth_new_capacity',
            columns=['region', 'tech_or_group', 'operator', 'rate', 'seed'],
            index_length=3,
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=m.limit_growth_new_capacity_delta,
            table='limit_growth_new_capacity_delta',
            columns=['region', 'tech_or_group', 'operator', 'rate', 'seed'],
            index_length=3,
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=m.limit_degrowth_capacity,
            table='limit_degrowth_capacity',
            columns=['region', 'tech_or_group', 'operator', 'rate', 'seed'],
            index_length=3,
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=m.limit_degrowth_new_capacity,
            table='limit_degrowth_new_capacity',
            columns=['region', 'tech_or_group', 'operator', 'rate', 'seed'],
            index_length=3,
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=m.limit_degrowth_new_capacity_delta,
            table='limit_degrowth_new_capacity_delta',
            columns=['region', 'tech_or_group', 'operator', 'rate', 'seed'],
            index_length=3,
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
    ]
