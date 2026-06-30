from __future__ import annotations

from pathlib import Path

from temoa.extensions.framework import ExtensionSpec
from temoa.extensions.integer_capacity.core.model import register_model_components
from temoa.extensions.integer_capacity.data_manifest import build_manifest_items

INTEGER_CAPACITY_EXTENSION = ExtensionSpec(
    extension_id='integer_capacity',
    owned_tables=('limit_integer_new_capacity', 'limit_integer_net_capacity'),
    regional_group_tables={
        'limit_integer_new_capacity': 'region',
        'limit_integer_net_capacity': 'region'
    },
    register_model_components=register_model_components,
    build_manifest_items=build_manifest_items,
    schema_sql_path=str(Path(__file__).parents[0] / 'tables.sql'),
    fail_if_tables_populated_when_disabled=True,
)
