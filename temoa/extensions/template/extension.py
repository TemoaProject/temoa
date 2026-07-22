"""Declarative spec that wires the template extension into Temoa.

TEMPLATE: ``ExtensionSpec`` is pure metadata plus hook functions. Temoa reads it
to know which tables the extension owns, how to guard them, which model
components to attach, and how to load the extension's data.
"""

from __future__ import annotations

from pathlib import Path

from temoa.extensions.framework import ExtensionSpec
from temoa.extensions.template.core.model import register_model_components
from temoa.extensions.template.data_manifest import build_manifest_items

EXAMPLE_EXTENSION = ExtensionSpec(
    # Unique, lowercase id. This is what users put in ``extensions = [...]``.
    extension_id='template',
    # Database tables owned exclusively by this extension.
    owned_tables=('example_new_capacity_limit',),
    # Tables whose ``region`` column may contain a regional group name. Maps
    # table -> the column that holds the region/group. Merged into the loader's
    # regional-group handling.
    regional_group_tables={'example_new_capacity_limit': 'region'},
    # Hook: attach model components to the core model (see core/model.py).
    register_model_components=register_model_components,
    # Hook: describe how to load this extension's data (see data_manifest.py).
    build_manifest_items=build_manifest_items,
    # Schema applied (with consent) when enabled but tables are missing.
    schema_sql_path=str(Path(__file__).parents[0] / 'tables.sql'),
)
