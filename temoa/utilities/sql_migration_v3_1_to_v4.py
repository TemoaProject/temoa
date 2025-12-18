#!/usr/bin/env python3
"""
sql_migration_v_3_1_to_v4.py

Converts a v3.1 SQL dump (text) into a valid v4 SQL dump.
This script:
1. Loads the v3.1 SQL dump into a temporary in-memory SQLite database.
2. Applies the v4 schema to a new in-memory SQLite database.
3. Programmatically queries data from the old in-memory DB, maps table/column
   names using the defined rules (non-cascading, case-sensitive-first, etc.),
   and inserts data into the new in-memory v4 DB.
4. Uses SQLite's built-in .dump functionality to generate the final v4 SQL dump.

Usage:
  python sql_migration_v3_1_to_v4.py --input v3_1.sql \
                                     --schema temoa_schema_v4.sql \
                                     --output v4.sql \
                                     [--debug]
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys

# ------------------ Mapping configuration (mirror sqlite migrator) ------------------
CUSTOM_MAP: dict[str, str] = {
    'TimeSeason': 'time_season',
    'time_season': 'time_season',
    'TimeSeasonSequential': 'time_season_sequential',
    'time_season_sequential': 'time_season_sequential',
    'TimeNext': 'time_manual',
    'CommodityDStreamProcess': 'commodity_down_stream_process',
    'commodityUStreamProcess': 'commodity_up_stream_process',
    'SegFrac': 'segment_fraction',
    'segfrac': 'segment_fraction',
    'MetaDataReal': 'metadata_real',
    'MetaData': 'metadata',
    'Myopicefficiency': 'myopic_efficiency',
    'DB_MAJOR': 'db_major',
    'DB_MINOR': 'db_minor',
}
CUSTOM_EXACT_ONLY = {'time_season', 'time_season_sequential'}
CUSTOM_KEYS_SORTED = sorted(
    [k for k in CUSTOM_MAP.keys() if k not in CUSTOM_EXACT_ONLY], key=lambda k: -len(k)
)


# ------------------ Mapping functions (non-cascading) ------------------
def to_snake_case(s: str) -> str:
    if not s:
        return s
    if s == s.lower() and '_' in s:
        return s
    x = s.replace('-', '_').replace(' ', '_')
    x = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', x)
    x = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', x)
    x = re.sub(r'__+', '_', x)
    return x.lower()


def map_token_no_cascade(token: str) -> str:
    if not token:
        return token
    # prevent cascading (already a mapped output)
    mapped_values = {v.lower() for v in CUSTOM_MAP.values()}
    if token.lower() in mapped_values:
        return token.lower()
    # exact case-sensitive
    if token in CUSTOM_MAP:
        return CUSTOM_MAP[token].lower()
    # exact case-insensitive
    tl = token.lower()
    for k, v in CUSTOM_MAP.items():
        if tl == k.lower():
            return v.lower()
    # avoid substring replacements for PascalCase
    if any(c.isupper() for c in token):
        return to_snake_case(token)
    # substring replacements (longest-first)
    orig = token
    orig_lower = orig.lower()
    replacements = [(k, CUSTOM_MAP[k]) for k in CUSTOM_KEYS_SORTED if k.lower() in orig_lower]
    if replacements:
        out = []
        i = 0
        length = len(orig)
        while i < length:
            matched = False
            for key, repl in replacements:
                kl = len(key)
                if i + kl <= length and orig[i : i + kl].lower() == key.lower():
                    out.append(repl)
                    i += kl
                    matched = True
                    break
            if not matched:
                out.append(orig[i])
                i += 1
        mapped_once = ''.join(out)
        mapped_once = re.sub(r'__+', '_', mapped_once).lower()
        return mapped_once
    return to_snake_case(token)


def map_table_name(table: str) -> str:
    return map_token_no_cascade(table)


def map_column_name(col: str) -> str:
    mapped = map_token_no_cascade(col)
    if mapped == 'seg_frac':  # Ensure canonical form for this column
        mapped = 'segment_fraction'
    return mapped


def get_table_info(conn: sqlite3.Connection, table: str) -> list[tuple]:
    try:
        return conn.execute(f'PRAGMA table_info({table});').fetchall()
    except sqlite3.OperationalError:
        return []


def migrate_dump_to_sqlite(args) -> None:
    # --- 1. Load v3.1 SQL dump into a temporary in-memory DB ---
    print(f'Loading v3.1 SQL dump from {args.input} into in-memory DB...')
    con_old_in_memory = sqlite3.connect(':memory:')
    try:
        with open(args.input, encoding='utf-8') as f:
            v3_1_sql_dump = f.read()
        con_old_in_memory.executescript(v3_1_sql_dump)
        print('V3.1 dump loaded.')
    except Exception as e:
        print(f'ERROR: Failed to load v3.1 dump: {e}')
        sys.exit(1)

    # --- 2. Create new in-memory DB and apply v4 schema ---
    print(f'Applying v4 schema from {args.schema} to new in-memory DB...')
    con_new_in_memory = sqlite3.connect(':memory:')
    try:
        with open(args.schema, encoding='utf-8') as f:
            v4_schema_sql = f.read()
        con_new_in_memory.executescript(v4_schema_sql)
        con_new_in_memory.execute('PRAGMA foreign_keys = 0;')  # Temporarily disable for migration
        print('V4 schema applied.')
    except Exception as e:
        print(f'ERROR: Failed to apply v4 schema: {e}')
        sys.exit(1)

    # Get old and new table/column info
    old_tables = [
        r[0]
        for r in con_old_in_memory.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        if not r[0].lower().startswith('sqlite_')
    ]
    new_db_tables = [
        r[0]
        for r in con_new_in_memory.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        if not r[0].lower().startswith('sqlite_')
    ]

    if args.debug:
        print('DEBUG Mapping samples:')
        for t in (
            'TimeSeason',
            'time_season',
            'TimeSeasonSequential',
            'time_season_sequential',
            'SegFrac',
            'segfrac',
        ):
            print(f'  {t} -> {map_token_no_cascade(t)}')
        print('\nDEBUG Old DB tables:', old_tables)
        print('DEBUG New DB tables:', new_db_tables)

    # --- 3. Programmatically copy data ---
    total_rows_copied = 0
    for old_table_name in old_tables:
        mapped_new_table_name = map_table_name(old_table_name)

        if mapped_new_table_name not in new_db_tables:
            # Tolerant fallback: if canonical target table is missing, try candidates
            candidates = [
                t
                for t in new_db_tables
                if t.startswith(mapped_new_table_name)
                or mapped_new_table_name in t
                or mapped_new_table_name.replace('_', '') in t.replace('_', '')
            ]
            if len(candidates) == 1:
                chosen_table = candidates[0]
                print(
                    f'NOTE: Mapped target {mapped_new_table_name} not found for {old_table_name}; '
                    f'using candidate {chosen_table}'
                )
                mapped_new_table_name = chosen_table
            else:
                print(
                    f'SKIP: No target table for {old_table_name} -> {mapped_new_table_name} '
                    f'(candidates: {candidates})'
                )
                continue

        old_cols_info = get_table_info(con_old_in_memory, old_table_name)
        new_cols_info = get_table_info(con_new_in_memory, mapped_new_table_name)

        if not old_cols_info:
            if args.debug:
                print(f'DEBUG: No column info for old table {old_table_name}')
            continue
        if not new_cols_info:
            if args.debug:
                print(f'DEBUG: No column info for new table {mapped_new_table_name}')
            continue

        old_actual_cols = [c[1] for c in old_cols_info]
        new_target_cols = [c[1] for c in new_cols_info]

        selectable_old_cols_for_query = []  # actual column names in old table to select
        insert_target_cols_for_query = []  # mapped column names for new table's INSERT clause

        for oc in old_actual_cols:
            mapped_oc = map_column_name(oc)
            if mapped_oc in new_target_cols:
                selectable_old_cols_for_query.append(oc)
                insert_target_cols_for_query.append(mapped_oc)

        if not selectable_old_cols_for_query:
            if args.debug:
                print(
                    f'DEBUG: No common/mappable columns from {old_table_name} to '
                    f'{mapped_new_table_name}. Skipping data copy.'
                )
            continue

        select_query = f'SELECT {",".join(selectable_old_cols_for_query)} FROM {old_table_name}'
        rows_from_old_table = con_old_in_memory.execute(select_query).fetchall()

        if not rows_from_old_table:
            if args.debug:
                print(f'DEBUG: No data in {old_table_name}. Skipping.')
            continue

        # Filter out rows that are entirely NULL
        filtered_rows_for_insert = [r for r in rows_from_old_table if any(v is not None for v in r)]
        if not filtered_rows_for_insert:
            if args.debug:
                print(f'DEBUG: All rows from {old_table_name} were NULL. Skipping.')
            continue

        placeholders = ','.join(['?'] * len(insert_target_cols_for_query))
        insert_query = (
            f'INSERT OR REPLACE INTO {mapped_new_table_name} '
            f'({",".join(insert_target_cols_for_query)}) VALUES ({placeholders})'
        )

        con_new_in_memory.executemany(insert_query, filtered_rows_for_insert)
        rows_copied_this_table = len(filtered_rows_for_insert)
        print(f'Copied {rows_copied_this_table} rows: {old_table_name} -> {mapped_new_table_name}')
        total_rows_copied += rows_copied_this_table

    # --- Final updates and dump ---
    con_new_in_memory.execute("INSERT OR REPLACE INTO metadata VALUES ('DB_MAJOR', 4, '')")
    con_new_in_memory.execute("INSERT OR REPLACE INTO metadata VALUES ('DB_MINOR', 0, '')")
    con_new_in_memory.commit()
    con_new_in_memory.execute('PRAGMA foreign_keys = 1;')  # Re-enable FKs

    # Generate the v4 SQL dump
    print(f'Generating v4 SQL dump to {args.output}...')
    with open(args.output, 'w', encoding='utf-8') as f_out:
        for line in con_new_in_memory.iterdump():
            # Add back "PRAGMA foreign_keys=OFF;" and "BEGIN TRANSACTION;" at the start if missing
            # And "COMMIT;" at the end.
            # It seems .iterdump() already adds PRAGMA and BEGIN/COMMIT.
            f_out.write(line + '\n')

    con_old_in_memory.close()
    con_new_in_memory.close()
    print(
        f'Conversion complete. Total rows copied: {total_rows_copied}. Output dump: {args.output}'
    )


def parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('--input', '-i', required=True, help='Path to v3.1 SQL dump file')
    p.add_argument('--schema', '-s', required=True, help='Path to v4 schema SQL file')
    p.add_argument('--output', '-o', required=True, help='Path for output v4 SQL dump file')
    p.add_argument('--debug', action='store_true', help='Enable debug output')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_cli()
    migrate_dump_to_sqlite(args)
