"""
Unit checking module tests for Temoa v4

Tests for the unit checking validation using pint library

"""

import pytest

from temoa.model_checking.unit_checking import ureg
from temoa.model_checking.unit_checking.common import RATIO_ELEMENT, SINGLE_ELEMENT, UnitsFormat
from temoa.model_checking.unit_checking.entry_checker import (
    validate_units_expression,
    validate_units_format,
)

cases = [
    ('PJ', SINGLE_ELEMENT, True),
    ('   kWh', SINGLE_ELEMENT, True),
    ('dog_food   ', SINGLE_ELEMENT, True),
    ('  G * tonne', SINGLE_ELEMENT, True),
    ('Mt.steel ', SINGLE_ELEMENT, False),  # period not allowed
    ('PJ / day', SINGLE_ELEMENT, True),  # SINGLE_ELEMENT regex allows slashes
    ('PJ    / (kT)', RATIO_ELEMENT, True),
    ('(PJ) / (kT)', RATIO_ELEMENT, False),  # numerator with parens doesn't match RATIO regex
    ('PJ / kT', RATIO_ELEMENT, False),  # no parens on denom
    (
        'kWh/day/(cycle)',
        RATIO_ELEMENT,
        True,
    ),  # matches: numerator has slash (allowed), denom in parens
    ('(kWh/day)/(cycle)', RATIO_ELEMENT, False),  # numerator parens not in RATIO regex
]


@pytest.mark.parametrize(
    ('entry', 'units_format', 'expected'),
    cases,
    ids=[f'{t[0]} -> {"valid" if t[2] else "invalid"}' for t in cases],
)
def test_format_validation(entry: str, units_format: UnitsFormat, expected: bool) -> None:
    """Test the regex matching for unit format
    Note:  The unit values here are NOT tested within the Units Registry
    This test is solely to test the regex to grab the units, esp the ratio units"""
    is_valid, _ = validate_units_format(expr=entry, unit_format=units_format)
    assert is_valid is expected


# Test cases: (expression, (is_valid, unit_object))
# These test actual unit registry validation
expression_cases = [
    ('kg', True, ureg.kg),
    ('kg/m^3', True, ureg('kg/(meter*meter*meter)')),
    ('m/s', True, ureg('m/s')),
    ('dog_food', False, None),
    ('ethos', True, ureg.ethos),
    ('passenger', True, ureg.passenger),
    ('seat', True, ureg.seat),
    ('dollar', True, ureg.dollar),
    ('dollars', True, ureg.dollar),
    ('USD', True, ureg.dollar),
    ('EUR', True, ureg.euro),
    ('kWh', True, ureg.kWh),
]


@pytest.mark.parametrize(
    ('expr', 'is_valid', 'expected_unit'),
    expression_cases,
    ids=[f'{t[0]} -> {"valid" if t[1] else "invalid"}' for t in expression_cases],
)
def test_validate_units_expression(expr: str, is_valid: bool, expected_unit: object) -> None:
    """
    Test the validate_units_expression function against various unit expressions.
    """
    valid, result_unit = validate_units_expression(expr)
    assert valid == is_valid
    if is_valid:
        assert result_unit == expected_unit
    else:
        assert result_unit is None


# Time dimension exponents: power units have [time]^-3, energy units have [time]^-2
time_dimension_cases = [('kW', -3), ('kWh', -2), ('PJ', -2), ('PJ/h', -3)]


@pytest.mark.parametrize(
    ('expr', 'location'),
    time_dimension_cases,
    ids=[t[0] for t in time_dimension_cases],
)
def test_time_dimension_locator(expr: str, location: int) -> None:
    valid, test_value = validate_units_expression(expr)
    assert valid, f'Expression {expr} should be valid'
    assert test_value is not None, f'Expected unit object for {expr}'
    found = test_value.dimensionality.get('[time]')
    assert found == location, (
        f'time dimension not found at expected location for units: {test_value}'
    )
