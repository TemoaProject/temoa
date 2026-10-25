"""Tests for the extension-agnostic helper functions in temoa.extensions.framework.

These cover the plumbing (id normalization, manifest/hook merging, and the
enabled/disabled extension table checks) that isn't exercised by
tests/test_extensions.py, which focuses on each concrete extension's model
components.
"""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, cast

import pytest

from temoa.extensions.framework import (
    ExtensionSpec,
    _append_extension_schema,
    _table_exists,
    _table_has_rows,
    append_extension_manifest_items,
    apply_model_extension_hooks,
    assert_disabled_extension_tables_are_empty,
    ensure_enabled_extension_tables_exist,
    get_known_extension_specs,
    merge_regional_group_tables,
    normalize_extension_ids,
)

if TYPE_CHECKING:
    from pathlib import Path

    from temoa.data_io.loader_manifest import LoadItem


# =============================================================================
# normalize_extension_ids
# =============================================================================


def test_normalize_extension_ids_none_returns_empty() -> None:
    assert normalize_extension_ids(None) == ()


def test_normalize_extension_ids_empty_list_returns_empty() -> None:
    assert normalize_extension_ids([]) == ()


def test_normalize_extension_ids_dedupes_and_lowercases_preserving_order() -> None:
    result = normalize_extension_ids(['Growth_Rates', ' growth_rates ', 'discrete_capacity'])
    assert result == ('growth_rates', 'discrete_capacity')


def test_normalize_extension_ids_skips_blank_entries() -> None:
    assert normalize_extension_ids(['  ', 'growth_rates']) == ('growth_rates',)


def test_normalize_extension_ids_rejects_non_string() -> None:
    with pytest.raises(TypeError, match='Extension ids must be strings'):
        normalize_extension_ids([123])


# =============================================================================
# merge_regional_group_tables
# =============================================================================


def test_merge_regional_group_tables_merges_specs_into_base() -> None:
    spec = ExtensionSpec(extension_id='ext_a', regional_group_tables={'tbl_a': 'field_a'})
    merged = merge_regional_group_tables({'tbl_base': 'field_base'}, [spec])
    assert merged == {'tbl_base': 'field_base', 'tbl_a': 'field_a'}


def test_merge_regional_group_tables_allows_identical_duplicate_mapping() -> None:
    spec = ExtensionSpec(extension_id='ext_a', regional_group_tables={'tbl_base': 'field_base'})
    merged = merge_regional_group_tables({'tbl_base': 'field_base'}, [spec])
    assert merged == {'tbl_base': 'field_base'}


def test_merge_regional_group_tables_conflict_raises() -> None:
    spec = ExtensionSpec(extension_id='ext_a', regional_group_tables={'tbl_base': 'field_other'})
    with pytest.raises(ValueError, match='conflicting field mappings'):
        merge_regional_group_tables({'tbl_base': 'field_base'}, [spec])


# =============================================================================
# apply_model_extension_hooks / append_extension_manifest_items
# =============================================================================


def test_apply_model_extension_hooks_calls_each_registered_hook() -> None:
    calls: list[object] = []
    spec = ExtensionSpec(extension_id='ext_a', register_model_components=calls.append)
    model = object()

    apply_model_extension_hooks(model, [spec])  # type: ignore[arg-type]

    assert calls == [model]


def test_apply_model_extension_hooks_skips_specs_without_hook() -> None:
    spec = ExtensionSpec(extension_id='ext_a')
    # Should not raise even though register_model_components is None.
    apply_model_extension_hooks(object(), [spec])  # type: ignore[arg-type]


def test_append_extension_manifest_items_merges_in_order() -> None:
    # Strings stand in for LoadItem; only list order matters here.
    item_a = cast('LoadItem', 'item_a')
    item_b = cast('LoadItem', 'item_b')
    base_item = cast('LoadItem', 'base_item')
    spec_a = ExtensionSpec(extension_id='ext_a', build_manifest_items=lambda _model: [item_a])
    spec_b = ExtensionSpec(extension_id='ext_b', build_manifest_items=lambda _model: [item_b])

    merged = append_extension_manifest_items(
        object(),  # type: ignore[arg-type]
        [base_item],
        [spec_a, spec_b],
    )

    assert merged == [base_item, item_a, item_b]


# =============================================================================
# _table_exists / _table_has_rows
# =============================================================================


def test_table_exists_and_has_rows() -> None:
    con = sqlite3.connect(':memory:')
    try:
        assert _table_exists(con, 'missing_table') is False
        assert _table_has_rows(con, 'missing_table') is False

        con.execute('CREATE TABLE populated (id INTEGER)')
        con.execute('CREATE TABLE empty_table (id INTEGER)')
        con.execute('INSERT INTO populated VALUES (1)')
        con.commit()

        assert _table_exists(con, 'populated') is True
        assert _table_has_rows(con, 'populated') is True
        assert _table_exists(con, 'empty_table') is True
        assert _table_has_rows(con, 'empty_table') is False
    finally:
        con.close()


# =============================================================================
# assert_disabled_extension_tables_are_empty
# =============================================================================


def test_assert_disabled_extension_tables_are_empty_warns_when_populated(
    caplog: pytest.LogCaptureFixture,
) -> None:
    con = sqlite3.connect(':memory:')
    try:
        con.execute('CREATE TABLE limit_growth_capacity (region TEXT)')
        con.execute("INSERT INTO limit_growth_capacity VALUES ('R1')")
        con.commit()

        with caplog.at_level('WARNING'):
            assert_disabled_extension_tables_are_empty(con, enabled_specs=())

        assert any('growth_rates' in record.message for record in caplog.records)
    finally:
        con.close()


def test_assert_disabled_extension_tables_are_empty_silent_when_enabled(
    caplog: pytest.LogCaptureFixture,
) -> None:
    con = sqlite3.connect(':memory:')
    try:
        con.execute('CREATE TABLE limit_growth_capacity (region TEXT)')
        con.execute("INSERT INTO limit_growth_capacity VALUES ('R1')")
        con.commit()

        growth_rates_spec = get_known_extension_specs()['growth_rates']
        with caplog.at_level('WARNING'):
            assert_disabled_extension_tables_are_empty(con, enabled_specs=(growth_rates_spec,))

        assert not caplog.records
    finally:
        con.close()


# =============================================================================
# ensure_enabled_extension_tables_exist / _append_extension_schema
# =============================================================================


def test_ensure_enabled_extension_tables_exist_noop_when_tables_present() -> None:
    con = sqlite3.connect(':memory:')
    try:
        con.execute('CREATE TABLE owned_table (id INTEGER)')
        con.commit()
        spec = ExtensionSpec(extension_id='ext_a', owned_tables=('owned_table',))

        # Should not raise or prompt.
        ensure_enabled_extension_tables_exist(con, [spec], input_database='db.sqlite', silent=True)
    finally:
        con.close()


def test_ensure_enabled_extension_tables_exist_no_schema_path_raises() -> None:
    con = sqlite3.connect(':memory:')
    try:
        spec = ExtensionSpec(extension_id='ext_a', owned_tables=('missing_table',))
        with pytest.raises(RuntimeError, match='No schema SQL path is registered'):
            ensure_enabled_extension_tables_exist(
                con, [spec], input_database='db.sqlite', silent=True
            )
    finally:
        con.close()


def test_ensure_enabled_extension_tables_exist_silent_skips_prompt_and_raises() -> None:
    con = sqlite3.connect(':memory:')
    try:
        spec = ExtensionSpec(
            extension_id='ext_a', owned_tables=('missing_table',), schema_sql_path='unused.sql'
        )
        # silent=True means the prompt is never asked, so should_apply stays False.
        with pytest.raises(RuntimeError, match='Re-run and accept the prompt'):
            ensure_enabled_extension_tables_exist(
                con, [spec], input_database='db.sqlite', silent=True
            )
    finally:
        con.close()


def test_ensure_enabled_extension_tables_exist_prompt_declined_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    con = sqlite3.connect(':memory:')
    try:
        spec = ExtensionSpec(
            extension_id='ext_a', owned_tables=('missing_table',), schema_sql_path='unused.sql'
        )
        monkeypatch.setattr('builtins.input', lambda _prompt: 'n')
        with pytest.raises(RuntimeError, match='Re-run and accept the prompt'):
            ensure_enabled_extension_tables_exist(
                con, [spec], input_database='db.sqlite', silent=False
            )
    finally:
        con.close()


def test_ensure_enabled_extension_tables_exist_prompt_accepted_applies_schema(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    schema_file = tmp_path / 'extra_schema.sql'
    schema_file.write_text('CREATE TABLE missing_table (id INTEGER);')

    con = sqlite3.connect(':memory:')
    try:
        spec = ExtensionSpec(
            extension_id='ext_a',
            owned_tables=('missing_table',),
            schema_sql_path=str(schema_file),
        )
        monkeypatch.setattr('builtins.input', lambda _prompt: 'y')

        ensure_enabled_extension_tables_exist(con, [spec], input_database='db.sqlite', silent=False)

        assert _table_exists(con, 'missing_table') is True
    finally:
        con.close()


def test_ensure_enabled_extension_tables_exist_still_missing_after_apply_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Schema file exists but doesn't actually create the owned table.
    schema_file = tmp_path / 'noop_schema.sql'
    schema_file.write_text('CREATE TABLE unrelated_table (id INTEGER);')

    con = sqlite3.connect(':memory:')
    try:
        spec = ExtensionSpec(
            extension_id='ext_a',
            owned_tables=('missing_table',),
            schema_sql_path=str(schema_file),
        )
        monkeypatch.setattr('builtins.input', lambda _prompt: 'y')

        with pytest.raises(RuntimeError, match='still missing'):
            ensure_enabled_extension_tables_exist(
                con, [spec], input_database='db.sqlite', silent=False
            )
    finally:
        con.close()


def test_append_extension_schema_no_path_raises() -> None:
    con = sqlite3.connect(':memory:')
    try:
        spec = ExtensionSpec(extension_id='ext_a')
        with pytest.raises(RuntimeError, match='no schema SQL path configured'):
            _append_extension_schema(con, spec)
    finally:
        con.close()


def test_append_extension_schema_missing_file_raises() -> None:
    con = sqlite3.connect(':memory:')
    try:
        spec = ExtensionSpec(extension_id='ext_a', schema_sql_path='/no/such/file.sql')
        with pytest.raises(FileNotFoundError, match='not found'):
            _append_extension_schema(con, spec)
    finally:
        con.close()


def test_append_extension_schema_executes_and_commits(tmp_path: Path) -> None:
    schema_file = tmp_path / 'schema.sql'
    schema_file.write_text('CREATE TABLE new_table (id INTEGER);')

    con = sqlite3.connect(':memory:')
    try:
        spec = ExtensionSpec(extension_id='ext_a', schema_sql_path=str(schema_file))
        _append_extension_schema(con, spec)
        assert _table_exists(con, 'new_table') is True
    finally:
        con.close()
