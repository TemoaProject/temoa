import contextlib
import sqlite3
from pathlib import Path

from temoa.utilities import migration_chain

REPO_ROOT = Path(__file__).parents[1]
SCHEMA_DIR = REPO_ROOT / 'temoa' / 'db_schema'
SCHEMA_V4 = SCHEMA_DIR / 'temoa_schema_v4.sql'
SCHEMA_V4_1 = SCHEMA_DIR / 'temoa_schema_v4_1.sql'
MOCK_V3 = REPO_ROOT / 'tests' / 'testing_data' / 'migration_v3_mock.sql'
SCHEMA_V3 = SCHEMA_DIR / 'temoa_schema_v3.sql'


def _make_v3_db(path: Path) -> Path:
    with contextlib.closing(sqlite3.connect(path)) as conn:
        conn.execute('PRAGMA foreign_keys = OFF')
        conn.executescript(SCHEMA_V3.read_text())
        conn.executescript(MOCK_V3.read_text())
    return path


MOCK_V4 = REPO_ROOT / 'tests' / 'testing_data' / 'migration_v4_mock.sql'


def _version(conn: sqlite3.Connection) -> tuple[int, int]:
    return migration_chain.detect_version(conn)


def test_chain_v3_sql_to_v4_1(tmp_path: Path) -> None:
    sql_src = tmp_path / 'v3.sql'
    with contextlib.closing(sqlite3.connect(_make_v3_db(tmp_path / 'v3_src.sqlite'))) as conn:
        sql_src.write_text('\n'.join(conn.iterdump()))
    out = tmp_path / 'out.sql'
    migration_chain.migrate_sql_dump(sql_src, SCHEMA_V4_1, out)
    with contextlib.closing(sqlite3.connect(':memory:')) as conn:
        conn.executescript(out.read_text())
        assert _version(conn) == (4, 1)
        assert conn.execute('SELECT COUNT(*) FROM efficiency').fetchone()[0] > 0


def test_chain_v3_db_to_v4_1(tmp_path: Path) -> None:
    src = _make_v3_db(tmp_path / 'v3.sqlite')
    out = tmp_path / 'out.sqlite'
    migration_chain.migrate_database(src, SCHEMA_V4_1, out)
    with contextlib.closing(sqlite3.connect(out)) as conn:
        assert _version(conn) == (4, 1)


def test_chain_v4_db_to_v4_1_and_idempotent(tmp_path: Path) -> None:
    src = tmp_path / 'v4.sqlite'
    with contextlib.closing(sqlite3.connect(src)) as conn:
        conn.execute('PRAGMA foreign_keys = OFF')
        conn.executescript(SCHEMA_V4.read_text())
        conn.executescript(MOCK_V4.read_text())
    out = tmp_path / 'v4_1.sqlite'
    migration_chain.migrate_database(src, SCHEMA_V4_1, out)
    again = tmp_path / 'again.sqlite'
    migration_chain.migrate_database(out, SCHEMA_V4_1, again)
    for path in (out, again):
        with contextlib.closing(sqlite3.connect(path)) as conn:
            assert _version(conn) == (4, 1)
