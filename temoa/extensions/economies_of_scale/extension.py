from __future__ import annotations

from pathlib import Path

from temoa.extensions.economies_of_scale.core.model import register_model_components
from temoa.extensions.economies_of_scale.data_manifest import build_manifest_items
from temoa.extensions.framework import ExtensionSpec

EOS_EXTENSION = ExtensionSpec(
    extension_id='eos',
    owned_tables=('cost_invest_eos', 'cost_fixed_eos', 'cost_variable_eos'),
    regional_group_tables={
        'cost_invest_eos': 'region',
        'cost_fixed_eos': 'region',
        'cost_variable_eos': 'region',
    },
    register_model_components=register_model_components,
    build_manifest_items=build_manifest_items,
    schema_sql_path=str(Path(__file__).parent / 'tables.sql'),
    fail_if_tables_populated_when_disabled=True,
)
