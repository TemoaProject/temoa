import argparse
import os
import re
import sqlite3

import tempfile
from pathlib import Path
from typing import Any

# Mapping config
CUSTOM_MAP: dict[str, str] = {
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

OPERATOR_ADDED_TABLES = {
    'EmissionLimit': ('limit_emission', 'le'),
    'TechOutputSplit': ('limit_tech_output_split', 'ge'),
    'TechInputSplitAnnual': ('limit_tech_input_split_annual', 'ge'),
    'TechInputSplitAverage': ('limit_tech_input_split_annual', 'ge'),
    'TechInputSplit': ('limit_tech_input_split', 'ge'),
    'MinNewCapacityShare': ('limit_new_capacity_share', 'ge'),
    'MinNewCapacityGroupShare': ('limit_new_capacity_share', 'ge'),
    'MinNewCapacityGroup': ('limit_new_capacity', 'ge'),
    'MinNewCapacity': ('limit_new_capacity', 'ge'),
    'MinCapacityShare': ('limit_capacity_share', 'ge'),
    'MinCapacityGroup': ('limit_capacity', 'ge'),
    'MinCapacity': ('limit_capacity', 'ge'),
    'MinActivityShare': ('limit_activity_share', 'ge'),
    'MinActivityGroup': ('limit_activity', 'ge'),
    'MinActivity': ('limit_activity', 'ge'),
    'MaxNewCapacityShare': ('limit_new_capacity_share', 'le'),
    'MaxNewCapacityGroupShare': ('limit_new_capacity_share', 'le'),
    'MaxNewCapacityGroup': ('limit_new_capacity', 'le'),
    'MaxNewCapacity': ('limit_new_capacity', 'le'),
    'MaxCapacityShare': ('limit_capacity_share', 'le'),
    'MaxCapacityGroup': ('limit_capacity', 'le'),
    'MaxCapacity': ('limit_capacity', 'le'),
    'MaxActivityShare': ('limit_activity_share', 'le'),
    'MaxActivityGroup': ('limit_activity', 'le'),
    'MaxActivity': ('limit_activity', 'le'),
    'MaxResource': ('limit_resource', 'le'),
}

PERIOD_TO_VINTAGE_TABLES = {
    'limit_new_capacity_share',
    'limit_new_capacity',
}


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


def get_table_info(conn: sqlite3.Connection, table: str) -> list[tuple[Any, ...]]:
    try:
        return conn.execute(f'PRAGMA table_info({table});').fetchall()
    except sqlite3.OperationalError:
        return []


def execute_v3_to_v4_migration(con_old: sqlite3.Connection, con_new: sqlite3.Connection) -> None:
    old_tables = [
        r[0]
        for r in con_old.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    ]
    new_tables = [
        r[0]
        for r in con_new.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    ]
    total = 0

    # 1. Handle operator-added tables
    print('--- Migrating max/min tables to operator constraints ---')
    for old_name, (new_name, operator) in OPERATOR_ADDED_TABLES.items():
        try:
            data = con_old.execute(f'SELECT * FROM {old_name}').fetchall()
        except sqlite3.OperationalError:
            continue
        if not data:
            continue

        new_cols = [c[1] for c in get_table_info(con_new, new_name)]
        if 'operator' not in new_cols:
            continue

        op_index = new_cols.index('operator')
        data = [(*row[0:op_index], operator, *row[op_index : len(new_cols) - 1]) for row in data]

        # Move period to vintage if applicable
        if new_name in PERIOD_TO_VINTAGE_TABLES:
            old_cols = [c[1] for c in get_table_info(con_old, old_name)]
            if 'period' in old_cols and 'vintage' in new_cols:
                period_index = old_cols.index('period')
                vintage_index = new_cols.index('vintage')
                data = [
                    (
                        *row[0:period_index],
                        *row[period_index + 1 : vintage_index + 1],
                        row[period_index],
                        *row[vintage_index + 1 :],
                    )
                    for row in data
                ]

        placeholders = ','.join(['?'] * len(data[0]))
        query = f'INSERT OR REPLACE INTO {new_name} VALUES ({placeholders})'
        con_new.executemany(query, data)
        print(f'Migrated {len(data)} rows: {old_name} -> {new_name}')
        total += len(data)

    # 2. Standard directory / copied tables
    custom_handled_old_tables = {
        'MetaData',
        'MetaDataReal',
        'TimeSeason',
        'time_season',
        'time_of_day',
        'time_season_sequential',
        'TimeSeasonSequential',
        'TimeSegmentFraction',
        'LoanLifetimeTech',
        'CapacityFactorProcess',
    }.union(OPERATOR_ADDED_TABLES.keys())

    print('--- Executing standard table migrations ---')
    for old in old_tables:
        if old.lower().startswith('sqlite_') or old in custom_handled_old_tables:
            continue

        new = map_token_no_cascade(old)
        if new not in new_tables:
            candidates = [t for t in new_tables if t == new or t.startswith(new) or new in t]
            if len(candidates) == 1:
                new = candidates[0]
            else:
                continue

        old_cols = [c[1] for c in get_table_info(con_old, old)]
        if not old_cols:
            continue
        new_cols = [c[1] for c in get_table_info(con_new, new)]

        selectable_old_cols, insert_new_cols = [], []
        for oc in old_cols:
            mapped = map_token_no_cascade(oc)
            if mapped == 'seg_frac':
                mapped = 'segment_fraction'
            if mapped in new_cols:
                selectable_old_cols.append(oc)
                insert_new_cols.append(mapped)

        if not selectable_old_cols:
            continue

        sel_clause = ','.join(selectable_old_cols)
        rows = con_old.execute(f'SELECT {sel_clause} FROM {old}').fetchall()
        filtered = [r for r in rows if any(v is not None for v in r)]
        if not filtered:
            continue

        placeholders = ','.join(['?'] * len(insert_new_cols))
        q = f'INSERT OR REPLACE INTO {new} ({",".join(insert_new_cols)}) VALUES ({placeholders})'
        con_new.executemany(q, filtered)
        print(f'Copied {len(filtered)} rows: {old} -> {new}')
        total += len(filtered)

    # 3. Custom specific logics
    print('--- Processing custom migration logic ---')

    # 3.1 LoanLifetimeTech -> loan_lifetime_process
    try:
        data = con_old.execute(
            'SELECT region, tech, lifetime, notes FROM LoanLifetimeTech'
        ).fetchall()
        if data:
            new_data = []
            for row in data:
                vints = [
                    v[0]
                    for v in con_old.execute(
                        'SELECT vintage FROM Efficiency WHERE region=? AND tech=?', (row[0], row[1])
                    ).fetchall()
                ]
                for v in vints:
                    new_data.append((row[0], row[1], v, row[2], row[3]))
            con_new.executemany(
                'INSERT OR REPLACE INTO loan_lifetime_process (region, tech, vintage, lifetime, notes) VALUES (?,?,?,?,?)',
                new_data,
            )
            print(f'Migrated {len(new_data)} rows: LoanLifetimeTech -> loan_lifetime_process')
            total += len(new_data)
    except sqlite3.OperationalError:
        pass

    # 3.2 time_season (aggregate from TimeSegmentFraction)
    try:
        old_data = []
        cols = [c[1] for c in get_table_info(con_old, 'TimeSegmentFraction')]
        if 'period' in cols:
            old_data = con_old.execute(
                'SELECT season, SUM(segfrac) / COUNT(DISTINCT period) FROM TimeSegmentFraction GROUP BY season'
            ).fetchall()
        else:
            old_data = con_old.execute(
                'SELECT season, SUM(segfrac) FROM TimeSegmentFraction GROUP BY season'
            ).fetchall()

        if old_data:
            con_new.executemany(
                'INSERT OR REPLACE INTO time_season (season, segment_fraction) VALUES (?, ?)',
                old_data,
            )
            print(f'Propagated {len(old_data)} seasons to time_season.')
            total += len(old_data)
    except sqlite3.OperationalError:
        pass

    # 3.3 time_of_day (aggregate from TimeSegmentFraction)
    try:
        old_data = []
        cols = [c[1] for c in get_table_info(con_old, 'TimeSegmentFraction')]
        if 'period' in cols:
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
        else:
            old_data = con_old.execute(
                'SELECT tod, SUM(segfrac) FROM TimeSegmentFraction GROUP BY tod'
            ).fetchall()
            if old_data:
                normalized_data = [(r[0], r[1] * 24.0) for r in old_data]
                con_new.executemany(
                    'INSERT OR REPLACE INTO time_of_day (tod, hours) VALUES (?, ?)', normalized_data
                )
                print(f'Propagated {len(normalized_data)} time-of-day slots to time_of_day.')
                total += len(normalized_data)
    except sqlite3.OperationalError:
        pass

    # 3.4 time_season_sequential
    try:
        old_data = []
        cols = [c[1] for c in get_table_info(con_old, 'TimeSeasonSequential')]
        if 'period' in cols:
            first_period = con_old.execute(
                'SELECT MIN(period) FROM TimeSeasonSequential'
            ).fetchone()[0]
            if first_period:
                old_data = con_old.execute(
                    'SELECT seas_seq, season, (num_days / 365.25) FROM TimeSeasonSequential WHERE period = ?',
                    (first_period,),
                ).fetchall()
        else:
            old_data = con_old.execute(
                'SELECT seas_seq, season, (num_days / 365.25) FROM TimeSeasonSequential'
            ).fetchall()

        if old_data:
            con_new.executemany(
                'INSERT OR REPLACE INTO time_season_sequential '
                '(seas_seq, season, segment_fraction) VALUES (?, ?, ?)',
                old_data,
            )
            print(f'Propagated {len(old_data)} sequential seasons to time_season_sequential.')
            total += len(old_data)
    except sqlite3.OperationalError:
        pass

    # 3.5 CapacityFactorProcess
    try:
        old_data = []
        cols = [c[1] for c in get_table_info(con_old, 'CapacityFactorProcess')]
        if cols:
            if 'period' in cols:
                old_data = con_old.execute(
                    'SELECT region, season, tod, tech, vintage, AVG(factor) FROM CapacityFactorProcess '
                    'GROUP BY region, season, tod, tech, vintage'
                ).fetchall()
            else:
                old_data = con_old.execute(
                    'SELECT region, season, tod, tech, vintage, factor FROM CapacityFactorProcess'
                ).fetchall()
            if old_data:
                con_new.executemany(
                    'INSERT OR REPLACE INTO capacity_factor_process (region, season, tod, tech, vintage, factor) VALUES (?,?,?,?,?,?)',
                    old_data,
                )
                print(
                    f'Copied {len(old_data)} rows: CapacityFactorProcess -> capacity_factor_process'
                )
                total += len(old_data)
    except sqlite3.OperationalError:
        pass

    # 4. Final Updates
    con_new.execute("UPDATE technology SET flag='p' WHERE flag='r';")
    con_new.execute("INSERT OR REPLACE INTO metadata VALUES ('DB_MAJOR', 4, '')")
    con_new.execute("INSERT OR REPLACE INTO metadata VALUES ('DB_MINOR', 0, '')")
    print(f'Total rows successfully copied: {total}')


def migrate_database(source_path: Path, schema_path: Path, output_path: Path) -> None:
    fd, temp_path_str = tempfile.mkstemp(suffix='.sqlite', prefix='temp_migration_')
    os.close(fd)
    temp_path = Path(temp_path_str)

    con_old = sqlite3.connect(source_path)
    con_new = sqlite3.connect(temp_path)
    
    try:
        with open(schema_path, encoding='utf-8') as f:
            con_new.executescript(f.read())
    
        con_new.execute('PRAGMA foreign_keys = 0;')
        execute_v3_to_v4_migration(con_old, con_new)
    
        con_new.commit()
        con_new.execute('VACUUM;')
        con_new.execute('PRAGMA foreign_keys = 1;')
    except Exception:
        con_old.close()
        con_new.close()
        if temp_path.exists():
            os.remove(temp_path)
        raise
        
    con_old.close()
    con_new.close()
    os.replace(temp_path, output_path)


def migrate_sql_dump(source_path: Path, schema_path: Path, output_path: Path) -> None:
    con_old_in_memory = sqlite3.connect(':memory:')
    with open(source_path, encoding='utf-8') as f:
        con_old_in_memory.executescript(f.read())

    con_new_in_memory = sqlite3.connect(':memory:')
    with open(schema_path, encoding='utf-8') as f:
        con_new_in_memory.executescript(f.read())

    con_new_in_memory.execute('PRAGMA foreign_keys = 0;')
    execute_v3_to_v4_migration(con_old_in_memory, con_new_in_memory)

    con_new_in_memory.commit()
    con_new_in_memory.execute('PRAGMA foreign_keys = 1;')

    with open(output_path, 'w', encoding='utf-8') as f_out:
        for line in con_new_in_memory.iterdump():
            f_out.write(line + '\n')

    con_old_in_memory.close()
    con_new_in_memory.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Master Migrator for v3 to v4')
    parser.add_argument('--input', '-i', required=True, help='Input DB or SQL file')
    parser.add_argument('--schema', '-s', required=True, help='Path to v4 schema SQL')
    parser.add_argument('--output', '-o', required=True, help='Output DB or SQL file')
    parser.add_argument('--type', choices=['db', 'sql'], required=True, help='Migration type')
    args = parser.parse_args()

    input_path = Path(args.input)
    schema_path = Path(args.schema)
    output_path = Path(args.output)

    if args.type == 'db':
        migrate_database(input_path, schema_path, output_path)
    elif args.type == 'sql':
        migrate_sql_dump(input_path, schema_path, output_path)
