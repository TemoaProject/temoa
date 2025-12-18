import logging
import os
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


def refresh_databases() -> None:
    """
    make new databases from source for testing...  removes possibility of contamination by earlier
    runs
    """
    data_output_path = Path(__file__).parent / 'testing_outputs'
    data_source_path = Path(__file__).parent / 'testing_data'
    # utopia.sql is in tutorial_assets (single source of truth for unit-compliant data)
    tutorial_assets_path = Path(__file__).parent.parent / 'temoa' / 'tutorial_assets'

    # Map source files to their locations
    # (source_dir, source_file, output_file)
    databases = [
        # Utopia uses the tutorial_assets source (unit-compliant)
        (tutorial_assets_path, 'utopia.sql', 'utopia.sqlite'),
        (tutorial_assets_path, 'utopia.sql', 'myo_utopia.sqlite'),
        # Other test databases use testing_data
        (data_source_path, 'test_system.sql', 'test_system.sqlite'),
        (data_source_path, 'storageville.sql', 'storageville.sqlite'),
        (data_source_path, 'mediumville.sql', 'mediumville.sqlite'),
        (data_source_path, 'emissions.sql', 'emissions.sqlite'),
        (data_source_path, 'materials.sql', 'materials.sqlite'),
        (data_source_path, 'simple_linked_tech.sql', 'simple_linked_tech.sqlite'),
        (data_source_path, 'seasonal_storage.sql', 'seasonal_storage.sqlite'),
        (data_source_path, 'survival_curve.sql', 'survival_curve.sqlite'),
        (data_source_path, 'annualised_demand.sql', 'annualised_demand.sqlite'),
    ]
    for source_dir, src, db in databases:
        if Path.exists(data_output_path / db):
            os.remove(data_output_path / db)
        # make a new one and fill it
        con = sqlite3.connect(data_output_path / db)
        with open(source_dir / src) as script:
            con.executescript(script.read())
        con.close()


def create_unit_test_db_from_sql(
    source_sql_path: Path, output_db_path: Path, modifications: list[tuple[str, tuple[Any, ...]]]
) -> None:
    """Create a unit test database from SQL source with specific modifications.

    Args:
        source_sql_path: Path to the source SQL file
        output_db_path: Path where the database should be created
        modifications: List of (sql, params) tuples to apply after creation
    """
    if output_db_path.exists():
        output_db_path.unlink()

    # Generate database from SQL source and apply modifications
    with sqlite3.connect(output_db_path) as conn:
        # Execute the SQL source to create the database
        conn.executescript(source_sql_path.read_text(encoding='utf-8'))

        # Apply modifications
        for sql, params in modifications:
            conn.execute(sql, params)
        conn.commit()


def create_unit_test_dbs() -> None:
    """Create unit test databases from SQL source for unit checking tests.

    Generates databases from the single SQL source of truth (tutorial_assets/utopia.sql),
    applying modifications for each test case.
    """
    test_output_dir = Path(__file__).parent / 'testing_outputs'
    test_output_dir.mkdir(exist_ok=True)

    # Source SQL file path (single source of truth)
    source_sql = Path(__file__).parent.parent / 'temoa' / 'tutorial_assets' / 'utopia.sql'

    if not source_sql.exists():
        raise FileNotFoundError(
            f'Source SQL not found at: {source_sql}. Please ensure the Utopia tutorial SQL exists.'
        )

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
        output_path = test_output_dir / db_name
        create_unit_test_db_from_sql(source_sql, output_path, modifications)
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
