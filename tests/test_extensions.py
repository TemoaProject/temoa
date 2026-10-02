"""Tests for the optional model extensions and their wiring into TemoaModel."""

from __future__ import annotations

from pathlib import Path

import pytest
from pyomo.environ import Constraint

from temoa.core.model import TemoaModel
from temoa.extensions.framework import (
    get_known_extension_specs,
    resolve_extension_specs,
)

# Parametrize over every registered extension so new extensions are covered
# automatically without listing their components here.
EXTENSION_IDS = sorted(get_known_extension_specs())


def _component_map(model: TemoaModel) -> dict[str, object]:
    """Map of component name -> component object declared on a model."""
    return {component.name: component for component in model.component_objects()}


# Cache abstract models so each extension is only built once per test session.
_abstract_models: dict[str | None, TemoaModel] = {}


def _model_with(extension_id: str | None) -> TemoaModel:
    if extension_id not in _abstract_models:
        extensions = [extension_id] if extension_id else None
        _abstract_models[extension_id] = TemoaModel(extensions=extensions)
    return _abstract_models[extension_id]


def _added_components(extension_id: str) -> dict[str, object]:
    """Components present with the extension enabled but absent without it."""
    base = _component_map(_model_with(None))
    enabled = _component_map(_model_with(extension_id))
    return {name: comp for name, comp in enabled.items() if name not in base}


@pytest.mark.parametrize('extension_id', EXTENSION_IDS)
def test_extension_registered(extension_id: str) -> None:
    """The extension is discoverable by its id and resolves to its spec."""
    spec = get_known_extension_specs()[extension_id]
    assert spec.extension_id == extension_id
    assert resolve_extension_specs([extension_id]) == (spec,)


@pytest.mark.parametrize('extension_id', EXTENSION_IDS)
def test_extension_spec_fields(extension_id: str) -> None:
    """The spec declares consistent region-group columns and a registration hook."""
    spec = get_known_extension_specs()[extension_id]
    # Region-group tables must refer to declared owned tables via string columns.
    assert set(spec.regional_group_tables) <= set(spec.owned_tables)
    assert all(isinstance(column, str) and column for column in spec.regional_group_tables.values())
    # Every extension attaches model components; data loading is optional.
    assert spec.register_model_components is not None


@pytest.mark.parametrize('extension_id', EXTENSION_IDS)
def test_extension_schema_matches_owned_tables(extension_id: str) -> None:
    """If the extension ships a schema, it defines every owned table.

    Extensions that only add components feeding from existing tables own no
    tables and need not provide a schema file.
    """
    spec = get_known_extension_specs()[extension_id]
    if spec.schema_sql_path is None:
        # No schema means the extension introduces no tables of its own.
        assert not spec.owned_tables
        return
    schema_path = Path(spec.schema_sql_path)
    assert schema_path.is_file()
    schema_sql = schema_path.read_text(encoding='utf-8')
    for table in spec.owned_tables:
        assert table in schema_sql


@pytest.mark.parametrize('extension_id', EXTENSION_IDS)
def test_extension_adds_components(extension_id: str) -> None:
    """Enabling the extension attaches new model components, including constraints."""
    added = _added_components(extension_id)
    assert added, f'{extension_id} should attach components to the model'
    assert any(isinstance(component, Constraint) for component in added.values()), (
        f'{extension_id} should contribute at least one constraint'
    )


def test_unknown_extension_id_rejected() -> None:
    """Resolving an unregistered extension id raises a descriptive error."""
    with pytest.raises(ValueError, match='Unknown extension id'):
        resolve_extension_specs(['not_a_real_extension'])
