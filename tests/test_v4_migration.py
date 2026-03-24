import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

# Constants
REPO_ROOT = Path(__file__).parents[1]
UTILITIES_DIR = REPO_ROOT / 'temoa' / 'utilities'
SCHEMA_V3_1 = REPO_ROOT / 'temoa' / 'db_schema' / 'temoa_schema_v3_1.sql'
SCHEMA_V4 = REPO_ROOT / 'temoa' / 'db_schema' / 'temoa_schema_v4.sql'
MOCK_DATA = REPO_ROOT / 'tests' / 'testing_data' / 'migration_v3_1_mock.sql'


def test_v4_migrations(tmp_path: Path) -> None:
    """Test both SQL and SQLite v4 migrators."""

    # 1. Create v3.1 SQLite DB
    db_v3_1 = tmp_path / 'test_v3_1.sqlite'
    with sqlite3.connect(db_v3_1) as conn:
        conn.execute('PRAGMA foreign_keys = OFF')
        conn.executescript(SCHEMA_V3_1.read_text())
        conn.executescript(MOCK_DATA.read_text())
        conn.execute('PRAGMA foreign_keys = ON')

    # 2. Dump v3.1 to SQL
    sql_v3_1 = tmp_path / 'test_v3_1.sql'
    with open(sql_v3_1, 'w') as f:
        for line in sqlite3.connect(db_v3_1).iterdump():
            f.write(line + '\n')

    # 3. Verify SQL migration script
    sql_v4_migrated = tmp_path / 'test_v4_migrated.sql'
    subprocess.run(
        [
            sys.executable,
            str(UTILITIES_DIR / 'sql_migration_v3_1_to_v4.py'),
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
    conn_sql = sqlite3.connect(':memory:')
    conn_sql.executescript(sql_v4_migrated.read_text())

    _verify_migrated_data(conn_sql)

    # 4. Verify SQLite direct migration script
    db_v4_migrated = tmp_path / 'test_v4_migrated.sqlite'
    subprocess.run(
        [
            sys.executable,
            str(UTILITIES_DIR / 'db_migration_v3_1_to_v4.py'),
            '--source',
            str(db_v3_1),
            '--schema',
            str(SCHEMA_V4),
            '--out',
            str(db_v4_migrated),
        ],
        check=True,
    )

    with sqlite3.connect(db_v4_migrated) as conn_db:
        _verify_migrated_data(conn_db)


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

    # Check metadata version
    major = conn.execute("SELECT value FROM metadata WHERE element='DB_MAJOR'").fetchone()[0]
    assert int(major) == 4
