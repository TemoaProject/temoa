"""
Integration tests for unit checking using pre-built test databases.

Uses Utopia database variants with specific unit errors to test the unit checker.
Test databases are created by create_unit_test_dbs() in tests/conftest.py during
pytest setup.
"""

import shutil
from pathlib import Path

import pytest

from temoa.model_checking.unit_checking.screener import screen

# Test database paths
TEST_DB_DIR = Path(__file__).parent / 'testing_outputs'

# Module-level skip condition - all tests require the test databases
DBS_PRESENT = (TEST_DB_DIR / 'utopia_valid_units.sqlite').exists()

pytestmark = pytest.mark.skipif(
    not DBS_PRESENT,
    reason='Test databases not created. Ensure conftest.py setup completed successfully.',
)


def test_valid_units_pass_check() -> None:
    """Test that properly configured Utopia database passes all checks.

    This includes verifying that valid composite units with currency dimensions
    (e.g., 'Mdollar / (PJ^2 / GW)') are accepted.
    """
    db_path = TEST_DB_DIR / 'utopia_valid_units.sqlite'

    result = screen(db_path)

    assert result is True, 'Valid Utopia database should pass all unit checks'


def test_invalid_currency_units_detected() -> None:
    """Test that cost units without currency dimension are detected"""
    db_path = TEST_DB_DIR / 'utopia_invalid_currency.sqlite'
    report_dir = TEST_DB_DIR / 'reports'

    try:
        result = screen(db_path, report_dir=report_dir)
    finally:
        if report_dir.exists():
            shutil.rmtree(report_dir)

    assert result is False, 'Should detect missing currency dimension in cost table'


def test_energy_units_in_capacity_table_detected() -> None:
    """Test that energy units (GWh) in capacity tables are detected"""
    db_path = TEST_DB_DIR / 'utopia_energy_in_capacity.sqlite'

    result = screen(db_path)

    assert result is False, 'Should detect energy units (GWh) in capacity table'


def test_missing_ratio_parentheses_detected() -> None:
    """Test that missing parentheses in ratio format are detected"""
    db_path = TEST_DB_DIR / 'utopia_missing_parentheses.sqlite'

    result = screen(db_path)

    assert result is False, 'Should detect missing parentheses in ratio format'


def test_unknown_units_detected() -> None:
    """Test that unregistered units are detected"""
    db_path = TEST_DB_DIR / 'utopia_unknown_units.sqlite'

    result = screen(db_path)

    assert result is False, 'Should detect unregistered units'


def test_mismatched_tech_output_units_detected() -> None:
    """Test that technologies with mismatched output units are detected"""
    db_path = TEST_DB_DIR / 'utopia_mismatched_outputs.sqlite'

    result = screen(db_path)

    assert result is False, 'Should detect mismatched output units for same tech'


def test_bad_composite_currency_rejected() -> None:
    """Test that nonsensical currency composites (dollar*meter) are caught"""
    db_path = TEST_DB_DIR / 'utopia_bad_composite_currency.sqlite'

    result = screen(db_path)

    assert result is False, 'Should reject nonsensical currency composite (dollar*meter)'
