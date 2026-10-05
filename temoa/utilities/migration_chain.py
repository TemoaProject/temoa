#!/usr/bin/env python3
"""
migration_chain.py

Version-aware migration to the current Temoa schema (v4.1). The source version is read
from its metadata and only the required steps are applied:

    v3.x -> v4.0 (master_migration) -> v4.1 (migrate_v4_to_v4_1)
    v4.0 -> v4.1 (migrate_v4_to_v4_1)
    v4.1 -> unchanged

Intermediate databases are held in memory; the output is only written once every step succeeded.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import tempfile
from pathlib import Path

from temoa.__about__ import DB_MAJOR_VERSION, MIN_DB_MINOR_VERSION
from temoa.utilities.master_migration import execute_v3_to_v4_migration
from temoa.utilities.migrate_v4_to_v4_1 import execute_v4_to_v4_1_migration

LATEST_VERSION = (DB_MAJOR_VERSION, MIN_DB_MINOR_VERSION)
# Historical v4.0 schema used as the intermediate target when migrating from v3
V4_SCHEMA_NAME = 'temoa_schema_v4.sql'


def detect_version(con: sqlite3.Connection) -> tuple[int, int]:
    """Return (major, minor) from the metadata table; databases without a version are v3."""

    def _read(element: str) -> int | None:
        try:
            row = con.execute('SELECT value FROM metadata WHERE element = ?', (element,)).fetchone()
        except sqlite3.OperationalError:
            return None
        return int(row[0]) if row else None

    major = _read('DB_MAJOR')
    if major is None:
        return 3, 0
    return major, _read('DB_MINOR') or 0


def _new_db(schema_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(':memory:')
    con.executescript(schema_path.read_text(encoding='utf-8'))
    con.execute('PRAGMA foreign_keys = 0;')
    return con


def migrate_connection(
    con_src: sqlite3.Connection, schema_path: Path, v4_schema_path: Path
) -> sqlite3.Connection:
    """Migrate an open source database to v4.1, returning an in-memory result connection.

    If the source is already current, it is returned as-is.
    """
    version = detect_version(con_src)
    print(f'Detected source database version: {version[0]}.{version[1]}')
    if version > LATEST_VERSION:
        raise ValueError(
            f'Source database version {version[0]}.{version[1]} is newer than the supported '
            f'{LATEST_VERSION[0]}.{LATEST_VERSION[1]}.'
        )
    if version == LATEST_VERSION:
        print('Database is already at the latest version; no migration needed.')
        return con_src

    current = con_src
    if version[0] < 4:
        if not v4_schema_path.is_file():
            raise FileNotFoundError(f'v4.0 schema file not found: {v4_schema_path}')
        print('=== Step: v3 -> v4.0 ===')
        con_v4 = _new_db(v4_schema_path)
        execute_v3_to_v4_migration(current, con_v4)
        con_v4.commit()
        current = con_v4

    print('=== Step: v4.0 -> v4.1 ===')
    con_v41 = _new_db(schema_path)
    execute_v4_to_v4_1_migration(current, con_v41)
    con_v41.commit()
    if current is not con_src:
        current.close()
    return con_v41


def _resolve_v4_schema(schema_path: Path, v4_schema_path: Path | None) -> Path:
    return v4_schema_path if v4_schema_path is not None else schema_path.parent / V4_SCHEMA_NAME


def migrate_database(
    source_path: Path,
    schema_path: Path,
    output_path: Path,
    v4_schema_path: Path | None = None,
) -> None:
    if not source_path.is_file():
        raise FileNotFoundError(f'Input database not found: {source_path}')
    if not schema_path.is_file():
        raise FileNotFoundError(f'Schema file not found: {schema_path}')

    fd, temp_str = tempfile.mkstemp(
        suffix='.sqlite', prefix='temp_migration_', dir=output_path.parent
    )
    os.close(fd)
    temp_path = Path(temp_str)

    con_src = sqlite3.connect(source_path)
    con_out: sqlite3.Connection | None = None
    try:
        con_out = migrate_connection(
            con_src, schema_path, _resolve_v4_schema(schema_path, v4_schema_path)
        )
        con_dest = sqlite3.connect(temp_path)
        try:
            con_out.backup(con_dest)
            con_dest.execute('VACUUM;')
        finally:
            con_dest.close()
        con_src.close()
        if con_out is not con_src:
            con_out.close()
        os.replace(temp_path, output_path)
    except Exception:
        con_src.close()
        if con_out is not None:
            con_out.close()
        if temp_path.exists():
            os.remove(temp_path)
        raise


def migrate_sql_dump(
    source_path: Path,
    schema_path: Path,
    output_path: Path,
    v4_schema_path: Path | None = None,
) -> None:
    if not source_path.is_file():
        raise FileNotFoundError(f'Input SQL dump not found: {source_path}')
    if not schema_path.is_file():
        raise FileNotFoundError(f'Schema file not found: {schema_path}')

    con_src = sqlite3.connect(':memory:')
    con_out: sqlite3.Connection | None = None
    temp_path: Path | None = None
    try:
        con_src.executescript(source_path.read_text(encoding='utf-8'))
        con_out = migrate_connection(
            con_src, schema_path, _resolve_v4_schema(schema_path, v4_schema_path)
        )
        fd, temp_str = tempfile.mkstemp(
            suffix='.sql', prefix='temp_sql_export_', dir=output_path.parent
        )
        temp_path = Path(temp_str)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            for line in con_out.iterdump():
                f.write(line + '\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, output_path)
    except Exception:
        if temp_path is not None and temp_path.exists():
            os.remove(temp_path)
        raise
    finally:
        con_src.close()
        if con_out is not None and con_out is not con_src:
            con_out.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate a Temoa database (v3 or v4) to v4.1')
    parser.add_argument('--input', '-i', required=True, help='Input DB or SQL file')
    parser.add_argument('--schema', '-s', required=True, help='Path to v4.1 schema SQL')
    parser.add_argument(
        '--v4-schema',
        help=f'Path to v4.0 schema SQL (default: {V4_SCHEMA_NAME} next to --schema)',
    )
    parser.add_argument('--output', '-o', required=True, help='Output DB or SQL file')
    parser.add_argument('--type', choices=['db', 'sql'], required=True, help='Migration type')
    args = parser.parse_args()

    v4_schema = Path(args.v4_schema) if args.v4_schema else None
    if args.type == 'db':
        migrate_database(Path(args.input), Path(args.schema), Path(args.output), v4_schema)
    else:
        migrate_sql_dump(Path(args.input), Path(args.schema), Path(args.output), v4_schema)
