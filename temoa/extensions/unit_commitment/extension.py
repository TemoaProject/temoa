from __future__ import annotations

from pathlib import Path

from temoa.extensions.framework import ExtensionSpec
from temoa.extensions.unit_commitment.core.model import register_model_components
from temoa.extensions.unit_commitment.data_manifest import build_manifest_items

UNIT_COMMITMENT_EXTENSION = ExtensionSpec(
    extension_id='unit_commitment',
    owned_tables=(
        'unit_commitment',
        'unit_commitment_startup_cost',
        'unit_commitment_startup_emissions',
        'unit_commitment_startup_input',
        'output_unit_commitment',
    ),
    regional_group_tables={},
    register_model_components=register_model_components,
    build_manifest_items=build_manifest_items,
    schema_sql_path=str(Path(__file__).parent / 'tables.sql'),
    fail_if_tables_populated_when_disabled=True,
)
