from __future__ import annotations

from typing import TYPE_CHECKING, cast

from temoa.data_io.loader_manifest import LoadItem

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.extensions.economies_of_scale.core.model import EOSModel


def build_manifest_items(model: TemoaModel) -> list[LoadItem]:
    m = cast('EOSModel', model)
    return [
        LoadItem(
            component=m.cost_invest_eos,
            table='cost_invest_eos',
            columns=[
                'region',
                'tech_or_group',
                'segment',
                'capacity_lower',
                'capacity_upper',
                'cost_lower',
                'cost_upper',
            ],
            index_length=3,
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_table_required=False,
            is_period_filtered=False,
            index_set=m.cost_invest_eos_rtn,
        ),
        LoadItem(
            component=m.cost_fixed_eos,
            table='cost_fixed_eos',
            columns=[
                'region',
                'period',
                'tech_or_group',
                'segment',
                'capacity_lower',
                'capacity_upper',
                'cost_lower',
                'cost_upper',
            ],
            index_length=4,
            validator_name='viable_rpt',
            validation_map=(0, 1, 2),
            is_table_required=False,
            is_period_filtered=True,
            index_set=m.cost_fixed_eos_rptn,
        ),
        LoadItem(
            component=m.cost_variable_eos,
            table='cost_variable_eos',
            columns=[
                'region',
                'period',
                'tech_or_group',
                'segment',
                'activity_lower',
                'activity_upper',
                'cost_lower',
                'cost_upper',
            ],
            index_length=4,
            validator_name='viable_rpt',
            validation_map=(0, 1, 2),
            is_table_required=False,
            is_period_filtered=True,
            index_set=m.cost_variable_eos_rptn,
        ),
    ]
