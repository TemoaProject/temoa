from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, field
from sqlite3 import Connection
from typing import TYPE_CHECKING

from collections.abc import Callable

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from temoa.core.model import TemoaModel
    from temoa.data_io.loader_manifest import LoadItem

ModelHook = Callable[['TemoaModel'], None]
ManifestHook = Callable[['TemoaModel'], list['LoadItem']]


@dataclass(frozen=True)
class ExtensionSpec:
    """Declarative metadata and hooks for an optional modeling extension."""

    extension_id: str
    owned_tables: tuple[str, ...] = ()
    regional_group_tables: dict[str, str] = field(default_factory=dict)
    register_model_components: ModelHook | None = None
    build_manifest_items: ManifestHook | None = None
    schema_sql_path: str | None = None
    fail_if_tables_populated_when_disabled: bool = False


def normalize_extension_ids(extension_ids: Sequence[str] | None) -> tuple[str, ...]:
    """Normalize configured extension ids while preserving user-provided order."""
    if not extension_ids:
        return ()

    normalized: list[str] = []
    seen: set[str] = set()
    for ext_id in extension_ids:
        if not isinstance(ext_id, str):
            raise ValueError(f'Extension ids must be strings. Received: {type(ext_id).__name__}')
        cleaned = ext_id.strip().lower()
        if not cleaned:
            continue
        if cleaned not in seen:
            normalized.append(cleaned)
            seen.add(cleaned)

    return tuple(normalized)


def get_known_extension_specs() -> dict[str, ExtensionSpec]:
    """Return all extension specs known to this installation."""
    from temoa.extensions.growth_rates.extension import GROWTH_RATES_EXTENSION

    # TEMPLATE: To activate a new extension copied from ``temoa/extensions/template``,
    # import its spec here and add it to ``specs`` below, e.g.:
    #   from temoa.extensions.<your_extension>.extension import <YOUR_EXTENSION>
    #   specs = [GROWTH_RATES_EXTENSION, <YOUR_EXTENSION>]
    specs = [GROWTH_RATES_EXTENSION]
    return {spec.extension_id: spec for spec in specs}


def resolve_extension_specs(extension_ids: Sequence[str] | None) -> tuple[ExtensionSpec, ...]:
    """Validate enabled extension ids and return corresponding specs in user order."""
    normalized_ids = normalize_extension_ids(extension_ids)
    known = get_known_extension_specs()
    unknown = [ext_id for ext_id in normalized_ids if ext_id not in known]
    if unknown:
        known_ids = ', '.join(sorted(known))
        unknown_ids = ', '.join(sorted(unknown))
        raise ValueError(
            f'Unknown extension id(s): {unknown_ids}. Known extension ids: {known_ids}.'
        )

    return tuple(known[ext_id] for ext_id in normalized_ids)


def apply_model_extension_hooks(model: TemoaModel, specs: Sequence[ExtensionSpec]) -> None:
    """Attach extension-owned model components to a model instance."""
    for spec in specs:
        if spec.register_model_components is not None:
            spec.register_model_components(model)


def append_extension_manifest_items(
    model: TemoaModel, manifest: list[LoadItem], specs: Sequence[ExtensionSpec]
) -> list[LoadItem]:
    """Append extension-specific manifest items to the base manifest."""
    merged = list(manifest)
    for spec in specs:
        if spec.build_manifest_items is not None:
            merged.extend(spec.build_manifest_items(model))
    return merged


def merge_regional_group_tables(
    base_tables: Mapping[str, str], specs: Sequence[ExtensionSpec]
) -> dict[str, str]:
    """Merge base regional-group table map with extension-contributed entries."""
    merged = dict(base_tables)
    for spec in specs:
        for table_name, field_name in spec.regional_group_tables.items():
            existing = merged.get(table_name)
            if existing is not None and existing != field_name:
                raise ValueError(
                    f"Regional-group table '{table_name}' has conflicting field mappings: "
                    f"'{existing}' vs '{field_name}' from extension '{spec.extension_id}'."
                )
            merged[table_name] = field_name
    return merged


def assert_disabled_extension_tables_are_empty(
    con: Connection, enabled_specs: Sequence[ExtensionSpec]
) -> None:
    """Fail if disabled extensions with strict guards own tables populated with data."""
    enabled_ids = {spec.extension_id for spec in enabled_specs}
    for spec in get_known_extension_specs().values():
        if spec.extension_id in enabled_ids:
            continue
        if not spec.fail_if_tables_populated_when_disabled:
            continue

        populated: list[str] = []
        for table in spec.owned_tables:
            if _table_has_rows(con, table):
                populated.append(table)

        if populated:
            table_list = ', '.join(sorted(populated))
            raise RuntimeError(
                f"Extension '{spec.extension_id}' is not enabled, but extension-owned table(s) "
                f'contain data: {table_list}. Enable the extension or remove those rows.'
            )


def ensure_enabled_extension_tables_exist(
    con: Connection,
    enabled_specs: Sequence[ExtensionSpec],
    *,
    input_database: str,
    silent: bool,
) -> None:
    """Ensure enabled extensions have required tables, offering to append schema if missing."""
    for spec in enabled_specs:
        missing_tables = [table for table in spec.owned_tables if not _table_exists(con, table)]
        if not missing_tables:
            continue

        missing_list = ', '.join(sorted(missing_tables))
        if not spec.schema_sql_path:
            raise RuntimeError(
                f"Extension '{spec.extension_id}' is enabled, but required table(s) are missing: "
                f'{missing_list}. No schema SQL path is registered for this extension.'
            )

        should_apply = False
        if not silent:
            prompt = (
                f"Extension '{spec.extension_id}' is enabled but missing table(s): {missing_list}. "
                f"Append schema from '{spec.schema_sql_path}' to input database '{input_database}' now? "
                '[y/N]: '
            )
            response = input(prompt).strip().lower()
            should_apply = response in {'y', 'yes'}

        if not should_apply:
            raise RuntimeError(
                f"Extension '{spec.extension_id}' is enabled, but required table(s) are missing: "
                f"{missing_list}. Re-run and accept the prompt, or append schema manually from "
                f"'{spec.schema_sql_path}' to '{input_database}'."
            )

        _append_extension_schema(con, spec)
        still_missing = [table for table in spec.owned_tables if not _table_exists(con, table)]
        if still_missing:
            still_missing_list = ', '.join(sorted(still_missing))
            raise RuntimeError(
                f"Schema append for extension '{spec.extension_id}' completed but table(s) are still "
                f'missing: {still_missing_list}.'
            )


def _table_has_rows(con: Connection, table_name: str) -> bool:
    cur = con.cursor()
    table_exists = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (table_name,)
    ).fetchone()
    if not table_exists:
        return False

    query = f'SELECT 1 FROM main.{table_name} LIMIT 1'
    return cur.execute(query).fetchone() is not None


def _table_exists(con: Connection, table_name: str) -> bool:
    cur = con.cursor()
    exists = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (table_name,)
    ).fetchone()
    return bool(exists)


def _append_extension_schema(con: Connection, spec: ExtensionSpec) -> None:
    if spec.schema_sql_path is None:
        raise RuntimeError(f"Extension '{spec.extension_id}' has no schema SQL path configured.")

    schema_path = Path(spec.schema_sql_path)
    if not schema_path.is_file():
        raise FileNotFoundError(
            f"Schema SQL file for extension '{spec.extension_id}' not found: {schema_path}"
        )

    sql = schema_path.read_text(encoding='utf-8')
    con.executescript(sql)
    con.commit()
