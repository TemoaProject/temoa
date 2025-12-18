import logging
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from _pytest.config import Config
from pyomo.opt import SolverResults

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel

logger = logging.getLogger(__name__)

# set the target folder for output from testing
output_path = Path(__file__).parent / 'testing_log'
if not output_path.exists():
    output_path.mkdir()

# set up logger in conftest.py so that it is properly anchored in the test folder.
filename = 'testing.log'
logging.basicConfig(
    filename=output_path / filename,
    filemode='w',
    format='%(asctime)s | %(module)s | %(levelname)s | %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.DEBUG,  # <-- global change for testing activities is here
)

logging.getLogger('pyomo').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('pyutilib').setLevel(logging.WARNING)


# Central paths
TEST_DATA_PATH = Path(__file__).parent / 'testing_data'
TEST_OUTPUT_PATH = Path(__file__).parent / 'testing_outputs'
SCHEMA_PATH = Path(__file__).parent.parent / 'temoa' / 'db_schema' / 'temoa_schema_v4.sql'


def _build_test_db(
    db_file: Path,
    data_scripts: list[Path],
    modifications: list[tuple[str, tuple[Any, ...]]] | None = None,
) -> None:
    """Helper to build a test database from central schema + data scripts + mods."""
    if db_file.exists():
        db_file.unlink()

    with sqlite3.connect(db_file) as con:
        con.execute('PRAGMA foreign_keys = OFF')
        # 1. Load central schema
        con.executescript(SCHEMA_PATH.read_text(encoding='utf-8'))
        # Force FK OFF again as schema file might turn it on at the end
        con.execute('PRAGMA foreign_keys = OFF')

        # 2. Load data scripts
        for script_path in data_scripts:
            with open(script_path) as f:
                con.executescript(f.read())

        # 3. Apply modifications
        if modifications:
            for sql, params in modifications:
                con.execute(sql, params)

        # 4. Turn foreign keys back on
        con.execute('PRAGMA foreign_keys = ON')
        con.commit()


def refresh_databases() -> None:
    """
    make new databases from source for testing...  removes possibility of contamination by earlier
    runs
    """
    # Map source files to their locations
    databases = [
        # Utopia uses the unit-compliant data-only script
        ('utopia_data.sql', 'utopia.sqlite'),
        ('utopia_data.sql', 'myo_utopia.sqlite'),
        # Other test databases
        ('test_system.sql', 'test_system.sqlite'),
        ('mediumville.sql', 'mediumville.sqlite'),
        ('seasonal_storage.sql', 'seasonal_storage.sqlite'),
        ('survival_curve.sql', 'survival_curve.sqlite'),
        ('annualised_demand.sql', 'annualised_demand.sqlite'),
        # Feature tests (separate for temporal consistency)
        ('emissions.sql', 'emissions.sqlite'),
        ('materials.sql', 'materials.sqlite'),
        ('simple_linked_tech.sql', 'simple_linked_tech.sqlite'),
        ('storageville.sql', 'storageville.sqlite'),
    ]

    for src, db in databases:
        _build_test_db(TEST_OUTPUT_PATH / db, [TEST_DATA_PATH / src])


def create_unit_test_dbs() -> None:
    """Create unit test databases from SQL source for unit checking tests.

    Generates databases from the single SQL source of truth (utopia_data.sql),
    applying modifications for each test case.
    """
    TEST_OUTPUT_PATH.mkdir(exist_ok=True)

    # Define unit test variations with their modifications
    unit_test_variations = [
        # 1. Valid database (baseline) - no modifications
        ('utopia_valid_units.sqlite', []),
        # 2. Invalid currency (no currency dimension in cost table)
        (
            'utopia_invalid_currency.sqlite',
            [
                ("UPDATE cost_invest SET units = 'PJ / (GW)' WHERE ROWID = 1", ()),
            ],
        ),
        # 3. Energy units in capacity table (GWh instead of GW)
        (
            'utopia_energy_in_capacity.sqlite',
            [
                ("UPDATE existing_capacity SET units = 'GWh' WHERE ROWID = 1", ()),
            ],
        ),
        # 4. Missing parentheses in ratio format
        (
            'utopia_missing_parentheses.sqlite',
            [
                ("UPDATE efficiency SET units = 'PJ / Mt' WHERE ROWID = 1", ()),
            ],
        ),
        # 5. Unknown/unregistered units
        (
            'utopia_unknown_units.sqlite',
            [
                ("UPDATE commodity SET units = 'catfood' WHERE name = 'co2'", ()),
            ],
        ),
        # 6. Mismatched tech output units
        (
            'utopia_mismatched_outputs.sqlite',
            [
                (
                    """
                UPDATE efficiency
                SET units = 'GJ / (Mt)'
                WHERE tech = 'E01' AND output_comm = 'ELC' AND ROWID =
                    (SELECT MIN(ROWID) FROM efficiency WHERE tech = 'E01')
                """,
                    (),
                ),
            ],
        ),
        # 7. Composite currency with nonsensical dimensions
        (
            'utopia_bad_composite_currency.sqlite',
            [
                ("UPDATE cost_invest SET units = 'dollar * meter' WHERE ROWID = 1", ()),
            ],
        ),
    ]

    for db_name, modifications in unit_test_variations:
        _build_test_db(
            TEST_OUTPUT_PATH / db_name,
            [TEST_DATA_PATH / 'utopia_data.sql'],
            modifications,
        )
        logger.info('Created unit test DB: %s', db_name)


def pytest_configure(config: Config) -> None:  # noqa: ARG001
    """Setup test databases before test collection."""
    refresh_databases()
    try:
        create_unit_test_dbs()
    except FileNotFoundError as e:
        # Source DB not available; unit tests will be skipped via pytestmark
        logger.warning(
            'Unit test databases not created: source SQL not found. '
            'Unit checking tests will be skipped.'
        )
        logger.debug('DB creation skipped due to: %s', e)


@pytest.fixture()
def system_test_run(
    request: Any, tmp_path: Path
) -> tuple[Any, SolverResults | None, TemoaModel | None, TemoaSequencer]:
    """
    spin up the model, solve it, and hand over the model and result for inspection
    """
    data_name = request.param['name']
    logger.info('Setting up and solving: %s', data_name)
    filename = request.param['filename']
    config_file = Path(__file__).parent / 'testing_configs' / filename

    config = TemoaConfig.build_config(
        config_file=config_file,
        output_path=tmp_path,
        silent=True,
    )

    sequencer = TemoaSequencer(config=config)

    sequencer.start()

    # The rest of the fixture returns the solved instance from the sequencer
    return (
        data_name,
        sequencer.pf_results,
        sequencer.pf_solved_instance,
        sequencer,
    )
