from __future__ import annotations

from pathlib import Path

from temoa.extensions.framework import ExtensionSpec
from temoa.extensions.growth_rates.core.model import register_model_components
from temoa.extensions.growth_rates.data_manifest import build_manifest_items

GROWTH_RATES_EXTENSION = ExtensionSpec(
    extension_id='growth_rates',
    owned_tables=(
        'limit_growth_capacity',
        'limit_degrowth_capacity',
        'limit_growth_new_capacity',
        'limit_degrowth_new_capacity',
        'limit_growth_new_capacity_delta',
        'limit_degrowth_new_capacity_delta',
    ),
    regional_group_tables={
        'limit_growth_capacity': 'region',
        'limit_degrowth_capacity': 'region',
        'limit_growth_new_capacity': 'region',
        'limit_degrowth_new_capacity': 'region',
        'limit_growth_new_capacity_delta': 'region',
        'limit_degrowth_new_capacity_delta': 'region',
    },
    register_model_components=register_model_components,
    build_manifest_items=build_manifest_items,
    schema_sql_path=str(Path(__file__).parent / 'tables.sql'),
)
