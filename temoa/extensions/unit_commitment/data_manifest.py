from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from temoa.data_io.loader_manifest import LoadItem

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.extensions.unit_commitment.core.model import UnitCommitmentModel


def build_manifest_items(model: TemoaModel) -> list[LoadItem]:
    m = cast('UnitCommitmentModel', model)
    uc: dict[str, Any] = {
        'table': 'unit_commitment',
        'validator_name': 'viable_rt',
        'validation_map': (0, 1),
        'is_table_required': False,
        'is_period_filtered': False,
    }
    return [
        LoadItem(
            component=m.uc_unit_capacity,
            columns=['region', 'tech', 'unit_capacity'],
            **uc,
        ),
        LoadItem(
            component=m.uc_min_output_fraction,
            columns=['region', 'tech', 'min_output_fraction'],
            **uc,
        ),
        LoadItem(
            component=m.uc_max_output_fraction,
            columns=['region', 'tech', 'max_output_fraction'],
            **uc,
        ),
        LoadItem(
            component=m.uc_min_up_time_hours,
            columns=['region', 'tech', 'min_up_time_hours'],
            **uc,
        ),
        LoadItem(
            component=m.uc_min_down_time_hours,
            columns=['region', 'tech', 'min_down_time_hours'],
            **uc,
        ),
        LoadItem(
            component=m.uc_linearized,
            columns=['region', 'tech', 'linearized'],
            **uc,
        ),
        LoadItem(
            component=m.uc_startup_cost,
            table='unit_commitment_startup_cost',
            columns=['region', 'tech', 'cost_per_cap'],
            is_period_filtered=False,
            is_table_required=False,
            validator_name='viable_rt',
            validation_map=(0, 1),
        ),
        LoadItem(
            component=m.uc_startup_emissions,
            table='unit_commitment_startup_emissions',
            columns=['region', 'emis_comm', 'tech', 'emis_per_cap'],
            is_period_filtered=False,
            is_table_required=False,
            validator_name='viable_rt',
            validation_map=(0, 2),
        ),
        LoadItem(
            component=m.uc_startup_input,
            table='unit_commitment_startup_input',
            columns=['region', 'input_comm', 'tech', 'input_per_cap'],
            is_period_filtered=False,
            is_table_required=False,
            validator_name='viable_rt',
            validation_map=(0, 2),
        ),
        *_operating_reserve_items(m),
    ]


def _operating_reserve_items(m: UnitCommitmentModel) -> list[LoadItem]:
    margin: dict[str, Any] = {
        'table': 'operating_reserve_margin',
        'validator_name': 'viable_rt',
        'validation_map': (1, 2),
        'is_table_required': False,
        'is_period_filtered': False,
    }
    credit: dict[str, Any] = {
        'table': 'operating_reserve_credit',
        'validator_name': 'viable_rt',
        'validation_map': (1, 2),
        'is_table_required': False,
        'is_period_filtered': False,
    }
    return [
        LoadItem(
            component=m.operating_reserves,
            table='operating_reserve_margin',
            columns=['reserve_name'],
            is_table_required=False,
            is_period_filtered=False,
        ),
        LoadItem(
            component=m.operating_reserve_margin,
            columns=['reserve_name', 'region', 'tech_or_group', 'margin'],
            where_clause='margin IS NOT NULL and margin != 0',
            **margin,
        ),
        LoadItem(
            component=m.operating_reserve_sustain_hours,
            columns=['reserve_name', 'region', 'tech_or_group', 'sustain_hours'],
            where_clause='sustain_hours IS NOT NULL and sustain_hours != 0',
            **margin,
        ),
        LoadItem(
            component=m.operating_reserve_activity_credit,
            columns=['reserve_name', 'region', 'tech', 'activity_credit'],
            where_clause='activity_credit IS NOT NULL and activity_credit != 0',
            **credit,
        ),
        LoadItem(
            component=m.operating_reserve_online_credit,
            columns=['reserve_name', 'region', 'tech', 'online_credit'],
            where_clause='online_credit IS NOT NULL and online_credit != 0',
            **credit,
        ),
        LoadItem(
            component=m.operating_reserve_offline_credit,
            columns=['reserve_name', 'region', 'tech', 'offline_credit'],
            where_clause='offline_credit IS NOT NULL and offline_credit != 0',
            **credit,
        ),
    ]
