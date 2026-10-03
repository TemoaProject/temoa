import contextlib
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from temoa.utilities.migrate_v4_to_v4_1 import migrate_database, migrate_sql_dump

REPO_ROOT = Path(__file__).parents[1]
UTILITIES_DIR = REPO_ROOT / 'temoa' / 'utilities'
SCHEMA_V4 = REPO_ROOT / 'temoa' / 'db_schema' / 'temoa_schema_v4.sql'
SCHEMA_V4_1 = REPO_ROOT / 'temoa' / 'db_schema' / 'temoa_schema_v4_1.sql'
MOCK_DATA_V4 = REPO_ROOT / 'tests' / 'testing_data' / 'migration_v4_mock.sql'
MIGRATION_SCRIPT = UTILITIES_DIR / 'migrate_v4_to_v4_1.py'


def _make_v4_db(tmp_path: Path) -> Path:
    """Create a v4 SQLite database populated with mock data."""
    db = tmp_path / 'test_v4.sqlite'
    with contextlib.closing(sqlite3.connect(db)) as conn:
        conn.execute('PRAGMA foreign_keys = OFF')
        conn.executescript(SCHEMA_V4.read_text())
        conn.executescript(MOCK_DATA_V4.read_text())
        conn.execute('PRAGMA foreign_keys = ON')
    return db


def _verify_migrated_db(conn: sqlite3.Connection) -> None:
    # Metadata version updated
    major = conn.execute("SELECT value FROM metadata WHERE element='DB_MAJOR'").fetchone()[0]
    minor = conn.execute("SELECT value FROM metadata WHERE element='DB_MINOR'").fetchone()[0]
    assert major == 4
    assert minor == 1

    # planning_reserve_credit: capacity_credit aggregated by (region, tech), period/vintage dropped
    credits = {
        (r[0], r[1]): r[2]
        for r in conn.execute('SELECT region, tech, credit FROM planning_reserve_credit').fetchall()
    }
    # GasTurbine had credit 0.85 (2030) and 0.80 (2040) -> AVG = 0.825
    assert ('R1', 'GasTurbine') in credits
    assert credits[('R1', 'GasTurbine')] == pytest.approx(0.825)
    assert credits[('R1', 'WindFarm')] == pytest.approx(0.25)

    # operating_reserve_derate: reserve_capacity_derate aggregated by (region, season, tech)
    derates = {
        (r[0], r[1], r[2]): r[3]
        for r in conn.execute(
            'SELECT region, season, tech, factor FROM operating_reserve_derate'
        ).fetchall()
    }
    assert ('R1', 'summer', 'GasTurbine') in derates
    assert derates[('R1', 'summer', 'GasTurbine')] == pytest.approx(0.95)
    assert derates[('R1', 'summer', 'WindFarm')] == pytest.approx(0.20)
    assert derates[('R1', 'winter', 'WindFarm')] == pytest.approx(0.10)

    # Removed v4 tables must not be present
    tables = {
        r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    assert 'capacity_credit' not in tables
    assert 'reserve_capacity_derate' not in tables
    assert 'rps_requirement' not in tables

    # planning_reserve_margin: migrated using reserve tech group as tech_or_group
    from temoa.utilities.migrate_v4_to_v4_1 import RESERVE_GROUP_NAME

    margins = conn.execute(
        'SELECT region, tech_or_group, margin FROM planning_reserve_margin'
    ).fetchall()
    assert len(margins) == 1
    assert margins[0] == ('R1', RESERVE_GROUP_NAME, pytest.approx(0.15))

    # reserve tech group must exist with GasTurbine and WindFarm (reserve=1), not CoalPlant
    members = {
        r[0]
        for r in conn.execute(
            'SELECT tech FROM tech_group_member WHERE group_name = ?', (RESERVE_GROUP_NAME,)
        ).fetchall()
    }
    assert 'GasTurbine' in members
    assert 'WindFarm' in members
    assert 'CoalPlant' not in members

    # rps_requirement: migrated to limit_activity_share, one row per period
    activity_shares = {
        (r[0], r[1], r[2]): r[4]
        for r in conn.execute(
            'SELECT region, period, sub_group, super_group, share FROM limit_activity_share'
        ).fetchall()
    }
    assert ('R1', 2030, 'renewables') in activity_shares
    assert activity_shares[('R1', 2030, 'renewables')] == pytest.approx(0.30)
    assert activity_shares[('R1', 2040, 'renewables')] == pytest.approx(0.40)

    # Common table data preserved
    efficiencies = conn.execute('SELECT region, tech, vintage FROM efficiency').fetchall()
    assert len(efficiencies) == 3


def test_v4_1_migration_db(tmp_path: Path) -> None:
    """Test SQLite DB migration from v4 to v4.1."""
    db_v4 = _make_v4_db(tmp_path)
    db_v4_1 = tmp_path / 'test_v4_1.sqlite'

    subprocess.run(
        [
            sys.executable,
            str(MIGRATION_SCRIPT),
            '--type',
            'db',
            '--input',
            str(db_v4),
            '--schema',
            str(SCHEMA_V4_1),
            '--output',
            str(db_v4_1),
        ],
        check=True,
    )

    with contextlib.closing(sqlite3.connect(db_v4_1)) as conn:
        _verify_migrated_db(conn)


def test_v4_1_migration_sql(tmp_path: Path) -> None:
    """Test SQL dump migration from v4 to v4.1."""
    db_v4 = _make_v4_db(tmp_path)

    sql_v4 = tmp_path / 'test_v4.sql'
    with open(sql_v4, 'w') as f:
        with contextlib.closing(sqlite3.connect(db_v4)) as conn:
            for line in conn.iterdump():
                f.write(line + '\n')

    sql_v4_1 = tmp_path / 'test_v4_1.sql'
    subprocess.run(
        [
            sys.executable,
            str(MIGRATION_SCRIPT),
            '--type',
            'sql',
            '--input',
            str(sql_v4),
            '--schema',
            str(SCHEMA_V4_1),
            '--output',
            str(sql_v4_1),
        ],
        check=True,
    )

    with contextlib.closing(sqlite3.connect(':memory:')) as conn:
        conn.executescript(sql_v4_1.read_text())
        _verify_migrated_db(conn)


def test_v4_1_migration_db_inthread(tmp_path: Path) -> None:
    """In-process variant of test_v4_1_migration_db for coverage."""
    db_v4 = _make_v4_db(tmp_path)
    db_v4_1 = tmp_path / 'test_v4_1.sqlite'

    migrate_database(db_v4, SCHEMA_V4_1, db_v4_1)

    with contextlib.closing(sqlite3.connect(db_v4_1)) as conn:
        _verify_migrated_db(conn)


def test_v4_1_migration_sql_inthread(tmp_path: Path) -> None:
    """In-process variant of test_v4_1_migration_sql for coverage."""
    db_v4 = _make_v4_db(tmp_path)

    sql_v4 = tmp_path / 'test_v4.sql'
    with open(sql_v4, 'w') as f:
        with contextlib.closing(sqlite3.connect(db_v4)) as conn:
            for line in conn.iterdump():
                f.write(line + '\n')

    sql_v4_1 = tmp_path / 'test_v4_1.sql'
    migrate_sql_dump(sql_v4, SCHEMA_V4_1, sql_v4_1)

    with contextlib.closing(sqlite3.connect(':memory:')) as conn:
        conn.executescript(sql_v4_1.read_text())
        _verify_migrated_db(conn)
