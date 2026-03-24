#!/usr/bin/env python3
"""
db_migration_v3_1_to_v4.py

Migrate a v3.1 SQLite DB to a v4 SQLite DB using deterministic mapping rules.

Usage:
  python db_migration_v3_1_to_v4.py --source old_v3_1.sqlite \
                                 --schema temoa_schema_v4.sql \
                                 --out new_v4.sqlite
"""

from __future__ import annotations

import argparse
import re
import sqlite3
from pathlib import Path

# ---------- Mapping configuration ----------
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
    mapped_values = {v.lower() for v in CUSTOM_MAP.values()}
    if token.lower() in mapped_values:
        return token.lower()
    if token in CUSTOM_MAP:
        return CUSTOM_MAP[token].lower()
    tl = token.lower()
    for k, v in CUSTOM_MAP.items():
        if tl == k.lower():
            return v.lower()
    if any(c.isupper() for c in token):
        return to_snake_case(token)
    orig = token
    orig_lower = orig.lower()
    replacements: list[tuple[str, str]] = [
        (k, CUSTOM_MAP[k]) for k in CUSTOM_KEYS_SORTED if k.lower() in orig_lower
    ]
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


def get_table_info(conn: sqlite3.Connection, table: str) -> list[tuple]:
    try:
        return conn.execute(f'PRAGMA table_info({table});').fetchall()
    except sqlite3.OperationalError:
        return []


def migrate_direct_table(
    con_old: sqlite3.Connection, con_new: sqlite3.Connection, old_table: str, new_table: str
) -> int:
    old_cols = [c[1] for c in get_table_info(con_old, old_table)]
    if not old_cols:
        return 0
    new_cols = [c[1] for c in get_table_info(con_new, new_table)]
    selectable_old_cols, insert_new_cols = [], []
    for oc in old_cols:
        mapped = map_token_no_cascade(oc)
        if mapped == 'seg_frac':
            mapped = 'segment_fraction'
        if mapped in new_cols:
            selectable_old_cols.append(oc)
            insert_new_cols.append(mapped)
    if not selectable_old_cols:
        return 0
    sel_clause = ','.join(selectable_old_cols)
    rows = con_old.execute(f'SELECT {sel_clause} FROM {old_table}').fetchall()
    if not rows:
        return 0
    # filter out rows that are entirely NULL
    filtered = [r for r in rows if any(v is not None for v in r)]
    if not filtered:
        return 0
    placeholders = ','.join(['?'] * len(insert_new_cols))
    q = f'INSERT OR REPLACE INTO {new_table} ({",".join(insert_new_cols)}) VALUES ({placeholders})'
    con_new.executemany(q, filtered)
    return len(filtered)


def migrate_all(args) -> None:
    src = Path(args.source)
    schema = Path(args.schema)
    out = Path(args.out) if args.out else src.with_suffix('.v4.sqlite')
    con_old = sqlite3.connect(src)
    con_new = sqlite3.connect(out)
    with open(schema, encoding='utf-8') as f:
        sql = f.read()
    con_new.executescript(sql)
    con_new.execute('PRAGMA foreign_keys = 0;')
    old_tables = [
        r[0]
        for r in con_old.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    ]
    new_tables = [
        r[0]
        for r in con_new.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    ]
    total = 0
    for old in old_tables:
        if old.lower().startswith('sqlite_'):
            continue
        if old in (
            'MetaData',
            'MetaDataReal',
            'TimeSeason',
            'time_season',
            'time_of_day',
            'time_season_sequential',
            'TimeSeasonSequential',
        ):
            continue
        if old == 'CapacityFactorProcess':
            # Special case: aggregate across periods
            old_data = con_old.execute(
                'SELECT region, season, tod, tech, vintage, AVG(factor) '
                'FROM CapacityFactorProcess '
                'GROUP BY region, season, tod, tech, vintage'
            ).fetchall()
            if old_data:
                con_new.executemany(
                    'INSERT OR REPLACE INTO capacity_factor_process '
                    '(region, season, tod, tech, vintage, factor) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    old_data,
                )
                print(f'Aggregated {len(old_data)} rows: {old} -> capacity_factor_process')
                total += len(old_data)
            continue

        new = map_token_no_cascade(old)
        if new not in new_tables:
            candidates = [t for t in new_tables if t == new or t.startswith(new) or new in t]
            if len(candidates) == 1:
                new = candidates[0]
            else:
                print(f'SKIP (no target): {old} -> {new}; candidates={candidates}')
                continue
        try:
            n = migrate_direct_table(con_old, con_new, old, new)
            print(f'Copied {n} rows: {old} -> {new}')
            total += n
        except Exception:
            print(f'Error migrating {old} -> {new}')
            raise

    # --- Custom logic for restructured tables (Seasons/TOD) ---
    print('Processing custom migration logic for seasons and time-of-day...')

    # 1. time_season (aggregate from TimeSegmentFraction)
    try:
        old_data = con_old.execute(
            'SELECT season, SUM(segfrac) / COUNT(DISTINCT period) '
            'FROM TimeSegmentFraction GROUP BY season'
        ).fetchall()
        if old_data:
            con_new.executemany(
                'INSERT OR REPLACE INTO time_season (season, segment_fraction) VALUES (?, ?)',
                old_data,
            )
            print(f'Propagated {len(old_data)} seasons to time_season.')
            total += len(old_data)
    except sqlite3.OperationalError:
        print('WARNING: Could not migrate seasons from TimeSegmentFraction.')

    # 2. time_of_day (aggregate from TimeSegmentFraction)
    try:
        old_data = con_old.execute(
            'SELECT tod, SUM(segfrac) FROM TimeSegmentFraction GROUP BY tod'
        ).fetchall()
        if old_data:
            num_periods = (
                con_old.execute(
                    'SELECT COUNT(DISTINCT period) FROM TimeSegmentFraction'
                ).fetchone()[0]
                or 1
            )
            normalized_data = [(r[0], (r[1] / num_periods) * 24.0) for r in old_data]
            con_new.executemany(
                'INSERT OR REPLACE INTO time_of_day (tod, hours) VALUES (?, ?)', normalized_data
            )
            print(f'Propagated {len(normalized_data)} time-of-day slots to time_of_day.')
            total += len(normalized_data)
    except sqlite3.OperationalError:
        print('WARNING: Could not migrate time_of_day from TimeSegmentFraction.')

    # 3. time_season_sequential (aggregate from TimeSeasonSequential)
    try:
        first_period = con_old.execute('SELECT MIN(period) FROM TimeSeasonSequential').fetchone()[0]
        if first_period:
            old_data = con_old.execute(
                'SELECT tss.seas_seq, tss.season, (tss.num_days / 365.25) '
                'FROM TimeSeasonSequential tss '
                'WHERE tss.period = ?',
                (first_period,),
            ).fetchall()
            if old_data:
                con_new.executemany(
                    'INSERT OR REPLACE INTO time_season_sequential '
                    '(seas_seq, season, segment_fraction) VALUES (?, ?, ?)',
                    old_data,
                )
                print(f'Propagated {len(old_data)} sequential seasons to time_season_sequential.')
                total += len(old_data)
    except (sqlite3.OperationalError, TypeError):
        pass

    # ensure metadata version bumped
    cur = con_new.cursor()
    cur.execute("INSERT OR REPLACE INTO metadata VALUES ('DB_MAJOR', 4, '')")
    cur.execute("INSERT OR REPLACE INTO metadata VALUES ('DB_MINOR', 0, '')")
    con_new.commit()
    con_new.execute('VACUUM;')
    con_new.execute('PRAGMA foreign_keys = 1;')
    try:
        fk = con_new.execute('PRAGMA FOREIGN_KEY_CHECK;').fetchall()
        if fk:
            print('FK issues:', fk)
    except sqlite3.OperationalError:
        pass
    con_old.close()
    con_new.close()
    print('Done; approx rows:', total, '->', out)


def parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('--source', required=True)
    p.add_argument('--schema', required=True)
    p.add_argument('--out', required=False)
    return p.parse_args()


if __name__ == '__main__':
    args = parse_cli()
    migrate_all(args)
