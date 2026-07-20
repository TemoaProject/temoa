from __future__ import annotations

from pathlib import Path

from temoa.extensions.discrete_capacity.core.model import register_model_components
from temoa.extensions.discrete_capacity.data_manifest import build_manifest_items
from temoa.extensions.framework import ExtensionSpec

DISCRETE_CAPACITY_EXTENSION = ExtensionSpec(
    extension_id='discrete_capacity',
    owned_tables=('limit_discrete_new_capacity', 'limit_discrete_capacity'),
    regional_group_tables={
        'limit_discrete_new_capacity': 'region',
        'limit_discrete_capacity': 'region',
    },
    register_model_components=register_model_components,
    build_manifest_items=build_manifest_items,
    schema_sql_path=str(Path(__file__).parent / 'tables.sql'),
    fail_if_tables_populated_when_disabled=True,
)
