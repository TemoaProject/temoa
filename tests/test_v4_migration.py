import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

# Constants
REPO_ROOT = Path(__file__).parents[1]
UTILITIES_DIR = REPO_ROOT / 'temoa' / 'utilities'
SCHEMA_V4 = REPO_ROOT / 'temoa' / 'db_schema' / 'temoa_schema_v4.sql'

SCHEMA_V3 = REPO_ROOT / 'temoa' / 'db_schema' / 'temoa_schema_v3.sql'
SCHEMA_V3_1 = REPO_ROOT / 'temoa' / 'db_schema' / 'temoa_schema_v3_1.sql'
MOCK_DATA_V3 = REPO_ROOT / 'tests' / 'testing_data' / 'migration_v3_mock.sql'
MOCK_DATA_V3_1 = REPO_ROOT / 'tests' / 'testing_data' / 'migration_v3_1_mock.sql'


@pytest.mark.parametrize(
    ('schema_file', 'mock_data_file'),
    [
        (SCHEMA_V3, MOCK_DATA_V3),
        (SCHEMA_V3_1, MOCK_DATA_V3_1),
    ],
)
def test_v4_migrations(tmp_path: Path, schema_file: Path, mock_data_file: Path) -> None:
    """Test both SQL and SQLite master migrators."""

    # 1. Create SQLite DB
    db_v3_1 = tmp_path / 'test_db.sqlite'
    import contextlib

    with contextlib.closing(sqlite3.connect(db_v3_1)) as conn:
        conn.execute('PRAGMA foreign_keys = OFF')
        conn.executescript(schema_file.read_text())
        conn.executescript(mock_data_file.read_text())
        conn.execute('PRAGMA foreign_keys = ON')

    # 2. Dump to SQL
    sql_v3_1 = tmp_path / 'test_v3_1.sql'
    with open(sql_v3_1, 'w') as f:
        with contextlib.closing(sqlite3.connect(db_v3_1)) as con_dump:
            for line in con_dump.iterdump():
                f.write(line + '\n')

    # 3. Verify SQL migration script
    sql_v4_migrated = tmp_path / 'test_v4_migrated.sql'
    subprocess.run(
        [
            sys.executable,
            str(UTILITIES_DIR / 'master_migration.py'),
            '--type',
            'sql',
            '--input',
            str(sql_v3_1),
            '--schema',
            str(SCHEMA_V4),
            '--output',
            str(sql_v4_migrated),
        ],
        check=True,
    )

    # Load SQL result into memory to verify
    with contextlib.closing(sqlite3.connect(':memory:')) as conn_sql:
        conn_sql.executescript(sql_v4_migrated.read_text())
        _verify_migrated_data(conn_sql)

    # 4. Verify SQLite direct migration script
    db_v4_migrated = tmp_path / 'test_v4_migrated.sqlite'
    subprocess.run(
        [
            sys.executable,
            str(UTILITIES_DIR / 'master_migration.py'),
            '--type',
            'db',
            '--input',
            str(db_v3_1),
            '--schema',
            str(SCHEMA_V4),
            '--output',
            str(db_v4_migrated),
        ],
        check=True,
    )

    import contextlib

    with contextlib.closing(sqlite3.connect(db_v4_migrated)) as conn_db:
        _verify_migrated_data(conn_db)


def test_get_annual_techs_source_variants() -> None:
    """_get_annual_techs must read Technology.annual, fall back to a tech_annual
    table (older v3 databases), and return an empty set when neither exists."""
    from temoa.utilities.master_migration import _get_annual_techs

    con = sqlite3.connect(':memory:')
    con.execute('CREATE TABLE Technology (tech TEXT, annual INTEGER)')
    con.executemany('INSERT INTO Technology VALUES (?, ?)', [('T1', 0), ('T2', 1)])
    assert _get_annual_techs(con) == {'T2'}

    con_old = sqlite3.connect(':memory:')
    con_old.execute('CREATE TABLE tech_annual (tech TEXT)')
    con_old.execute("INSERT INTO tech_annual VALUES ('T9')")
    assert _get_annual_techs(con_old) == {'T9'}

    assert _get_annual_techs(sqlite3.connect(':memory:')) == set()


def _verify_migrated_data(conn: sqlite3.Connection) -> None:
    # Check time_season restructuring (aggregated from TimeSegmentFraction)
    # Summer: 0.4 + 0.3 = 0.7
    # Winter: 0.2 + 0.1 = 0.3
    seasons = dict(conn.execute('SELECT season, segment_fraction FROM time_season').fetchall())
    assert seasons['summer'] == pytest.approx(0.7)
    assert seasons['winter'] == pytest.approx(0.3)

    # Check time_of_day restructuring (normalized to 24 hours based on weights)
    # Day weight: 0.2 + 0.4 = 0.6
    # Night weight: 0.1 + 0.3 = 0.4
    # Normalized to 24: Day=0.6*24=14.4, Night=0.4*24=9.6
    tods = dict(conn.execute('SELECT tod, hours FROM time_of_day').fetchall())
    assert tods['day'] == pytest.approx(14.4)
    assert tods['night'] == pytest.approx(9.6)

    # Check period removal from capacity_factor_process
    # Original PK: (region, period, season, tod, tech, vintage)
    # New PK: (region, season, tod, tech, vintage)
    cols = [c[1] for c in conn.execute('PRAGMA table_info(capacity_factor_process)').fetchall()]
    assert 'period' not in cols

    rows = conn.execute(
        'SELECT region, season, tod, tech, vintage, factor FROM capacity_factor_process'
    ).fetchall()
    assert len(rows) == 1
    assert rows[0] == ('R1', 'winter', 'day', 'T1', 2030, pytest.approx(0.6))

    # Check operator-added tables (limit_capacity and limit_emission)
    cap_rows = conn.execute(
        'SELECT region, tech_or_group, period, capacity, operator FROM limit_capacity'
    ).fetchall()
    assert len(cap_rows) == 1
    assert cap_rows[0] == ('R1', 'T1', 2030, 10.0, 'ge')

    # Split-table routing: an annual tech's split must land in the *_annual table —
    # the seasonal split constraints silently skip annual techs, so a mis-routed row
    # disappears from the model without error.
    in_seasonal = conn.execute(
        'SELECT region, period, input_comm, tech, operator, proportion FROM limit_tech_input_split'
    ).fetchall()
    assert in_seasonal == [('R1', 2030, 'In', 'T1', 'ge', pytest.approx(0.3))]
    in_annual = conn.execute(
        'SELECT region, period, input_comm, tech, operator, proportion '
        'FROM limit_tech_input_split_annual'
    ).fetchall()
    assert in_annual == [('R1', 2030, 'In', 'T2', 'ge', pytest.approx(0.4))]
    out_seasonal = conn.execute(
        'SELECT region, period, tech, output_comm, operator, proportion '
        'FROM limit_tech_output_split'
    ).fetchall()
    assert out_seasonal == [('R1', 2030, 'T1', 'Out', 'ge', pytest.approx(0.5))]
    out_annual = conn.execute(
        'SELECT region, period, tech, output_comm, operator, proportion '
        'FROM limit_tech_output_split_annual'
    ).fetchall()
    assert out_annual == [('R1', 2030, 'T2', 'Out', 'ge', pytest.approx(0.6))]

    emis_rows = conn.execute(
        'SELECT region, period, value, operator FROM limit_emission'
    ).fetchall()
    assert len(emis_rows) == 1
    assert emis_rows[0] == ('R1', 2030, 100.0, 'le')

    # Check metadata version
    major = conn.execute("SELECT value FROM metadata WHERE element='DB_MAJOR'").fetchone()[0]
    assert int(major) == 4
    assert (
        int(conn.execute("SELECT value FROM metadata WHERE element='DB_MINOR'").fetchone()[0]) == 0
    )
