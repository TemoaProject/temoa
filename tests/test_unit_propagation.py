"""
Tests for the UnitPropagator class.

Tests unit derivation from input tables for output table population.
"""

import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest

from temoa.model_checking.unit_checking.unit_propagator import UnitPropagator

# Use the utopia_valid_units database which has proper units
TEST_DB_DIR = Path(__file__).parent / 'testing_outputs'
VALID_UNITS_DB = TEST_DB_DIR / 'utopia_valid_units.sqlite'

# Skip if test database doesn't exist
pytestmark = pytest.mark.skipif(
    not VALID_UNITS_DB.exists(),
    reason='Test database not created. Ensure conftest.py setup completed.',
)


@pytest.fixture
def propagator() -> Generator[UnitPropagator, None, None]:
    """Create a UnitPropagator from the valid units database."""
    with sqlite3.connect(VALID_UNITS_DB) as conn:
        yield UnitPropagator(conn)


def test_propagator_has_unit_data(propagator: UnitPropagator) -> None:
    """Verify propagator detects available unit data."""
    assert propagator.has_unit_data is True


def test_get_flow_out_units(propagator: UnitPropagator) -> None:
    """Test flow out units derived from commodity table."""
    # ELC is a commodity in Utopia with units
    units = propagator.get_flow_out_units('ELC')
    assert units is not None
    assert 'joule' in units.lower() or 'pj' in units.lower()


def test_get_flow_in_units(propagator: UnitPropagator) -> None:
    """Test flow in units derived from commodity table."""
    units = propagator.get_flow_in_units('DSL')
    assert units is not None


def test_get_capacity_units(propagator: UnitPropagator) -> None:
    """Test capacity units derived from existing_capacity table."""
    units = propagator.get_capacity_units('E01')
    assert units == 'GW'


def test_get_cost_units(propagator: UnitPropagator) -> None:
    """Test cost units derived from cost tables."""
    units = propagator.get_cost_units()
    # Should be currency-based
    assert units is not None
    assert 'dollar' in units.lower() or 'usd' in units.lower()


def test_missing_commodity_returns_none(propagator: UnitPropagator) -> None:
    """Test that missing commodities return None gracefully."""
    units = propagator.get_flow_out_units('NONEXISTENT_COMMODITY')
    assert units is None


def test_missing_tech_capacity_returns_none(propagator: UnitPropagator) -> None:
    """Test that missing tech returns None for capacity units."""
    units = propagator.get_capacity_units('NONEXISTENT_TECH')
    assert units is None


def test_empty_database_graceful_fallback() -> None:
    """Test that an empty/minimal database doesn't crash the propagator."""
    # Create in-memory database with minimal schema - use context manager to avoid leaks
    with sqlite3.connect(':memory:') as conn:
        conn.execute('CREATE TABLE commodity (name TEXT, flag TEXT, description TEXT, units TEXT)')
        conn.execute('CREATE TABLE metadata (element TEXT, value INT)')
        conn.execute("INSERT INTO metadata VALUES ('DB_MAJOR', 4)")
        conn.commit()

        propagator = UnitPropagator(conn)

        # Should not crash, just return None/empty
        assert propagator.get_flow_out_units('anything') is None
        assert propagator.get_capacity_units('anything') is None
        assert propagator.get_cost_units() is None


# ---------------------------------------------------------------------------
# Integration test for end-to-end unit propagation
# ---------------------------------------------------------------------------


@pytest.fixture(scope='module')
def solved_db_with_units(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    Run a model solve using utopia_valid_units database and return path to results.

    This fixture creates a copy of the valid units database, runs a full model
    solve, and returns the path for verification.
    """
    import shutil

    from temoa._internal.temoa_sequencer import TemoaSequencer
    from temoa.core.config import TemoaConfig

    # Skip if source database or solver doesn't exist
    if not VALID_UNITS_DB.exists():
        pytest.skip('Valid units database not available')

    is_available, _location = TemoaConfig._check_solver_availability('appsi_highs')
    if not is_available:
        pytest.skip('Solver appsi_highs not available')

    # Create working directory and copy database
    tmp_dir = tmp_path_factory.mktemp('unit_propagation')
    working_db = tmp_dir / 'utopia_propagation_test.sqlite'
    shutil.copy(VALID_UNITS_DB, working_db)

    # Create a config file that points to the correct database
    # Use as_posix() to ensure forward slashes, avoiding escape sequence issues on Windows in TOML
    config_content = (
        f'scenario = "unit_test"\n'
        f'scenario_mode = "perfect_foresight"\n'
        f'input_database = "{working_db.as_posix()}"\n'
        f'output_database = "{working_db.as_posix()}"\n'
        f'solver_name = "appsi_highs"\n'
        f'save_excel = false\n'
        f'save_duals = false\n'
        f'time_sequencing = "seasonal_timeslices"\n'
    )
    config_file = tmp_dir / 'config_unit_propagation.toml'
    config_file.write_text(config_content)

    # Build config from our temporary config file
    config = TemoaConfig.build_config(
        config_file=config_file,
        output_path=tmp_dir,
        silent=True,
    )

    # Run the model
    sequencer = TemoaSequencer(config=config)
    sequencer.start()

    return working_db


def test_units_propagated_to_output_flow_tables(solved_db_with_units: Path) -> None:
    """Verify that output flow tables have units populated."""
    with sqlite3.connect(solved_db_with_units) as conn:
        # Check output_flow_out
        row = conn.execute(
            'SELECT COUNT(*), SUM(CASE WHEN units IS NOT NULL THEN 1 ELSE 0 END)'
            ' FROM output_flow_out'
        ).fetchone()
        total, with_units = row
        assert total > 0
        assert with_units > 0, 'No units populated in output_flow_out'
        sample = conn.execute(
            'SELECT output_comm, units FROM output_flow_out WHERE units IS NOT NULL LIMIT 1'
        ).fetchone()
        assert sample is not None

        # Check output_curtailment (same logic)
        row = conn.execute(
            'SELECT COUNT(*), SUM(CASE WHEN units IS NOT NULL THEN 1 ELSE 0 END)'
            ' FROM output_curtailment'
        ).fetchone()
        if row[0] > 0:
            assert row[1] > 0, 'No units populated in output_curtailment'

        # Check output_flow_in
        row = conn.execute(
            'SELECT COUNT(*), SUM(CASE WHEN units IS NOT NULL THEN 1 ELSE 0 END)'
            ' FROM output_flow_in'
        ).fetchone()
        if row[0] > 0:
            assert row[1] > 0, 'No units populated in output_flow_in'


def test_units_propagated_to_capacity_tables(solved_db_with_units: Path) -> None:
    """Verify that capacity output tables have units populated."""
    with sqlite3.connect(solved_db_with_units) as conn:
        for table in ['output_built_capacity', 'output_net_capacity']:
            row = conn.execute(
                f'SELECT COUNT(*), SUM(CASE WHEN units IS NOT NULL THEN 1 ELSE 0 END) FROM {table}'
            ).fetchone()
            total, with_units = row

            if total > 0:  # Some tables may be empty depending on model
                assert with_units > 0, f'No units populated in {table}'
                # Check for GW (standard capacity unit in Utopia)
                sample = conn.execute(
                    f'SELECT tech, units FROM {table} WHERE units IS NOT NULL LIMIT 1'
                ).fetchone()
                assert sample is not None
                assert sample[1] == 'GW', f'Expected GW, got {sample[1]} in {table}'


def test_units_propagated_to_cost_table(solved_db_with_units: Path) -> None:
    """Verify that output_cost table has units populated."""
    with sqlite3.connect(solved_db_with_units) as conn:
        row = conn.execute(
            'SELECT COUNT(*), SUM(CASE WHEN units IS NOT NULL THEN 1 ELSE 0 END) FROM output_cost'
        ).fetchone()
        total, with_units = row
        assert total > 0
        assert with_units > 0, 'No units populated in output_cost'

        sample = conn.execute(
            'SELECT units FROM output_cost WHERE units IS NOT NULL LIMIT 1'
        ).fetchone()
        assert sample is not None
        # Utopia uses 'Mdollar', but simplified check for non-empty string is good baseline
        units = sample[0].lower()
        assert ('dollar' in units) or ('usd' in units) or ('euro' in units) or ('eur' in units)
