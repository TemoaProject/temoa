#!/usr/bin/env python3
"""
migrate_v4_to_v4_1.py

Migrates a Temoa v4 database (SQLite or SQL dump) to v4.1 schema format.

Key changes from v4 to v4.1:
  - capacity_credit         -> planning_reserve_credit  (period, vintage dropped; AVG credit)
  - reserve_capacity_derate -> operating_reserve_derate (vintage dropped; AVG factor)
  - planning_reserve_margin -> planning_reserve_margin  (tech_or_group from reserve-flagged techs)
  - rps_requirement         -> limit_activity_share     (tech_group=sub_group, reserve=super_group)
  - operating_reserve_margin is new (no v4 equivalent)
  - DB_MINOR bumped: 0 -> 1
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import tempfile
from pathlib import Path


def get_table_cols(conn: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in conn.execute(f'PRAGMA table_info({table})').fetchall()]


def _migrate_planning_reserve_credit(
    con_old: sqlite3.Connection, con_new: sqlite3.Connection
) -> int:
    """Migrate capacity_credit -> planning_reserve_credit, dropping period and vintage."""
    try:
        rows = con_old.execute(
            'SELECT region, tech, AVG(credit), notes FROM capacity_credit GROUP BY region, tech'
        ).fetchall()
    except sqlite3.OperationalError:
        return 0
    if not rows:
        return 0
    con_new.executemany(
        'INSERT OR REPLACE INTO planning_reserve_credit (region, tech, credit, notes) '
        'VALUES (?, ?, ?, ?)',
        rows,
    )
    print(f'Migrated {len(rows)} rows: capacity_credit -> planning_reserve_credit')
    return len(rows)


def _migrate_operating_reserve_derate(
    con_old: sqlite3.Connection, con_new: sqlite3.Connection
) -> int:
    """Migrate reserve_capacity_derate -> operating_reserve_derate, dropping vintage."""
    try:
        rows = con_old.execute(
            'SELECT region, season, tech, AVG(factor), notes '
            'FROM reserve_capacity_derate GROUP BY region, season, tech'
        ).fetchall()
    except sqlite3.OperationalError:
        return 0
    if not rows:
        return 0
    con_new.executemany(
        'INSERT OR REPLACE INTO operating_reserve_derate (region, season, tech, factor, notes) '
        'VALUES (?, ?, ?, ?, ?)',
        rows,
    )
    print(f'Migrated {len(rows)} rows: reserve_capacity_derate -> operating_reserve_derate')
    return len(rows)


RESERVE_GROUP_NAME = 'migrated_reserve_techs'


def _build_reserve_tech_group(
    con_old: sqlite3.Connection, con_new: sqlite3.Connection
) -> list[str]:
    """Create a tech_group from techs with reserve=1; return the list of reserve tech names."""
    try:
        reserve_techs = [
            r[0]
            for r in con_old.execute('SELECT tech FROM technology WHERE reserve = 1').fetchall()
        ]
    except sqlite3.OperationalError:
        return []
    if not reserve_techs:
        return []
    con_new.execute(
        'INSERT OR IGNORE INTO tech_group (group_name) VALUES (?)', (RESERVE_GROUP_NAME,)
    )
    con_new.executemany(
        'INSERT OR IGNORE INTO tech_group_member (group_name, tech) VALUES (?, ?)',
        [(RESERVE_GROUP_NAME, t) for t in reserve_techs],
    )
    print(f'Built reserve tech group "{RESERVE_GROUP_NAME}" with {len(reserve_techs)} member(s)')
    return reserve_techs


def _migrate_planning_reserve_margin(
    con_old: sqlite3.Connection, con_new: sqlite3.Connection, reserve_group_built: bool
) -> int:
    """Migrate planning_reserve_margin using the reserve tech group as tech_or_group."""
    try:
        rows = con_old.execute(
            'SELECT region, margin, notes FROM planning_reserve_margin'
        ).fetchall()
    except sqlite3.OperationalError:
        return 0
    if not rows:
        return 0
    if not reserve_group_built:
        print(
            f'WARNING: planning_reserve_margin has {len(rows)} row(s) but no reserve-flagged '
            'techs found; skipping migration. Populate planning_reserve_margin manually.'
        )
        return 0
    migrated = [(region, RESERVE_GROUP_NAME, margin, notes) for region, margin, notes in rows]
    con_new.executemany(
        'INSERT OR REPLACE INTO planning_reserve_margin (region, tech_or_group, margin, notes) '
        'VALUES (?, ?, ?, ?)',
        migrated,
    )
    print(
        f'Migrated {len(migrated)} rows: planning_reserve_margin'
        f' (tech_or_group={RESERVE_GROUP_NAME!r})'
    )
    return len(migrated)


def _migrate_rps_requirement(
    con_old: sqlite3.Connection, con_new: sqlite3.Connection, reserve_group_built: bool
) -> int:
    """Migrate rps_requirement -> limit_activity_share.

    sub_group   = tech_group (the RPS-eligible group)
    super_group = RESERVE_GROUP_NAME (all reserve-flagged techs)
    operator    = 'ge' (must meet minimum share)
    """
    try:
        rows = con_old.execute(
            'SELECT region, period, tech_group, requirement, notes FROM rps_requirement'
        ).fetchall()
    except sqlite3.OperationalError:
        return 0
    if not rows:
        return 0
    if not reserve_group_built:
        print(
            'WARNING: rps_requirement has rows but no reserve-flagged techs found to use as '
            'super_group; skipping migration. Populate limit_activity_share manually.'
        )
        return 0
    migrated = [
        (region, period, sub_group, RESERVE_GROUP_NAME, 'ge', requirement, notes)
        for region, period, sub_group, requirement, notes in rows
    ]
    con_new.executemany(
        'INSERT OR REPLACE INTO limit_activity_share '
        '(region, period, sub_group, super_group, operator, share, notes) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        migrated,
    )
    print(f'Migrated {len(migrated)} rows: rps_requirement -> limit_activity_share')
    return len(migrated)


def _migrate_common_tables(con_old: sqlite3.Connection, con_new: sqlite3.Connection) -> int:
    """Copy all tables that exist in both schemas, skipping custom-handled ones."""
    skip = {
        'capacity_credit',
        'reserve_capacity_derate',
        'rps_requirement',
        'planning_reserve_margin',
        'metadata',
        'metadata_real',
        'operator',
        'commodity_type',
    }
    old_tables = {
        r[0]
        for r in con_old.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    new_tables = {
        r[0]
        for r in con_new.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    total = 0
    for table in sorted(old_tables & new_tables):
        if table.startswith('sqlite_') or table in skip:
            continue
        old_cols = set(get_table_cols(con_old, table))
        new_cols = get_table_cols(con_new, table)
        shared = [c for c in new_cols if c in old_cols]
        if not shared:
            continue
        col_list = ', '.join(shared)
        rows = con_old.execute(f'SELECT {col_list} FROM {table}').fetchall()
        if not rows:
            continue
        placeholders = ', '.join(['?'] * len(shared))
        con_new.executemany(
            f'INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({placeholders})', rows
        )
        print(f'Copied {len(rows)} rows: {table}')
        total += len(rows)
    return total


def execute_v4_to_v4_1_migration(con_old: sqlite3.Connection, con_new: sqlite3.Connection) -> None:
    """Run all v4 -> v4.1 migration steps."""
    total = 0
    print('--- Migrating common tables ---')
    total += _migrate_common_tables(con_old, con_new)

    print('--- Migrating restructured tables ---')
    total += _migrate_planning_reserve_credit(con_old, con_new)
    total += _migrate_operating_reserve_derate(con_old, con_new)

    print('--- Building reserve tech group ---')
    reserve_techs = _build_reserve_tech_group(con_old, con_new)
    reserve_group_built = len(reserve_techs) > 0
    total += _migrate_planning_reserve_margin(con_old, con_new, reserve_group_built)
    total += _migrate_rps_requirement(con_old, con_new, reserve_group_built)

    con_new.execute("INSERT OR REPLACE INTO metadata VALUES ('DB_MAJOR', 4, 'DB major version')")
    con_new.execute("INSERT OR REPLACE INTO metadata VALUES ('DB_MINOR', 1, 'DB minor version')")
    print(f'Total rows successfully copied: {total}')


def migrate_database(source_path: Path, schema_path: Path, output_path: Path) -> None:
    if not source_path.is_file():
        raise FileNotFoundError(f'Input database not found: {source_path}')
    if not schema_path.is_file():
        raise FileNotFoundError(f'Schema file not found: {schema_path}')

    fd, temp_str = tempfile.mkstemp(
        suffix='.sqlite', prefix='temp_v4_1_migration_', dir=output_path.parent
    )
    os.close(fd)
    temp_path = Path(temp_str)

    con_old = sqlite3.connect(source_path)
    con_new = sqlite3.connect(temp_path)
    try:
        con_new.executescript(schema_path.read_text(encoding='utf-8'))
        con_new.execute('PRAGMA foreign_keys = 0;')
        execute_v4_to_v4_1_migration(con_old, con_new)
        con_new.commit()
        con_new.execute('PRAGMA foreign_keys = 1;')
        con_old.close()
        con_new.close()
        os.replace(temp_path, output_path)
    except Exception:
        if temp_path.exists():
            os.remove(temp_path)
        raise
    finally:
        con_old.close()
        con_new.close()


def migrate_sql_dump(source_path: Path, schema_path: Path, output_path: Path) -> None:
    if not source_path.is_file():
        raise FileNotFoundError(f'Input SQL dump not found: {source_path}')
    if not schema_path.is_file():
        raise FileNotFoundError(f'Schema file not found: {schema_path}')

    con_old = sqlite3.connect(':memory:')
    con_old.executescript(source_path.read_text(encoding='utf-8'))

    con_new = sqlite3.connect(':memory:')
    con_new.executescript(schema_path.read_text(encoding='utf-8'))

    con_new.execute('PRAGMA foreign_keys = 0;')
    execute_v4_to_v4_1_migration(con_old, con_new)
    con_new.commit()
    con_new.execute('PRAGMA foreign_keys = 1;')

    fd, temp_str = tempfile.mkstemp(suffix='.sql', prefix='temp_v4_1_sql_', dir=output_path.parent)
    temp_path = Path(temp_str)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            for line in con_new.iterdump():
                f.write(line + '\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, output_path)
    except Exception:
        if temp_path.exists():
            os.remove(temp_path)
        raise
    finally:
        con_old.close()
        con_new.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate Temoa database from v4 to v4.1')
    parser.add_argument('--input', '-i', required=True, help='Input DB or SQL file')
    parser.add_argument('--schema', '-s', required=True, help='Path to v4.1 schema SQL')
    parser.add_argument('--output', '-o', required=True, help='Output DB or SQL file')
    parser.add_argument('--type', choices=['db', 'sql'], required=True, help='Migration type')
    args = parser.parse_args()

    input_path = Path(args.input)
    schema_path = Path(args.schema)
    output_path = Path(args.output)

    if args.type == 'db':
        migrate_database(input_path, schema_path, output_path)
    else:
        migrate_sql_dump(input_path, schema_path, output_path)
    print('Migration complete.')
