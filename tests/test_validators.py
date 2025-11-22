"""
Tests for the validators for regions, linked regions, and region groups
"""

from typing import TYPE_CHECKING, cast

import pyomo.environ as pyo
import pytest

from temoa.model_checking.validators import (
    linked_region_check,
    no_slash_or_pipe,
    region_check,
    region_group_check,
)

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types.core_types import Region


def test_region_check() -> None:
    """
    Test good region names
    """
    good_names = {'R3', 'California', 'NY', 'East_US'}
    bad_names = {
        'New York',  # has space
        'R43.2',  # has decimal
        'R3-R4',  # has dash
        '  R12',  # leading spaces
        'global',  # illegal for individual region
    }
    assert all(region_check(cast('TemoaModel', None), region=cast('Region', r)) for r in good_names)
    for bad_name in bad_names:
        assert not region_check(cast('TemoaModel', None), region=cast('Region', bad_name)), (
            f'This should fail {bad_name}'
        )


def test_linked_region_check() -> None:
    """
    Test legal pairings for linked regions
    """
    m = pyo.ConcreteModel()
    m.regions = pyo.Set(initialize=['AZ', 'R2', 'Mexico'])
    good_names = {'AZ-R2', 'Mexico-AZ'}
    bad_names = {
        'AZ R2',  # bad separator
        'AZ',  # not paired
        'R1-R2',  # R1 non in m.R
        'R2-R2',  # dupe
        'R2--AZ',  # dupe separator
        'R2+AZ',  # bad separator
        'AZ - Mexico',  # bad spacing
        'AZ-R2-Mexico',  # triples not allowed
    }
    assert all(linked_region_check(cast('TemoaModel', m), region_pair=rp) for rp in good_names)
    for bad_name in bad_names:
        assert not linked_region_check(cast('TemoaModel', m), region_pair=bad_name), (
            f'This should fail {bad_name}'
        )


def test_region_group_check() -> None:
    """
    Test legal multi-region groupings
    """
    m = pyo.ConcreteModel()
    m.regions = pyo.Set(initialize=['AZ', 'R2', 'Mexico', 'E_US'])
    good_names = {'AZ+R2', 'Mexico+AZ', 'AZ+R2+Mexico', 'R2+E_US', 'global', 'AZ-R2'}
    bad_names = {
        'AZ-R2+Mexico',  # arbitrary grouping of a link + other region not supported
        'AZ+AZ',  # dupe
        'AZ + R2',  # bad spacing
        'AZ+R2+R3',  # R3 is not in m.R
        'Region3',  # singleton not in m.R
    }
    for name in good_names:
        assert region_group_check(cast('TemoaModel', m), rg=name), (
            f'This name should have been good: {name}'
        )
    for name in bad_names:
        assert not region_group_check(cast('TemoaModel', m), rg=name), (
            f'This name should have failed: {name}'
        )


params = [
    ('dogfood', True),
    ('cat/dog', False),
    ('cat|dog', False),
    ('123/45', False),
    (678, True),
]


@pytest.mark.parametrize('value, expected', params)
def test_no_slash(value: str | int, *, expected: bool) -> None:
    assert no_slash_or_pipe(model=cast('TemoaModel', None), element=value) == expected
