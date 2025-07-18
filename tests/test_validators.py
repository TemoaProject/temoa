"""
Tests for the validators for regions, linked regions, and region groups

Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  9/28/23

Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.

"""

import pyomo.environ as pyo
import pytest

from temoa.temoa_model.model_checking.validators import (
    linked_region_check,
    no_slash_or_pipe,
    region_check,
    region_group_check,
)


def test_region_check():
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
    assert all(region_check(None, region=r) for r in good_names)
    for bad_name in bad_names:
        assert not region_check(None, region=bad_name), f'This should fail {bad_name}'


def test_linked_region_check():
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
    assert all(linked_region_check(m, region_pair=rp) for rp in good_names)
    for bad_name in bad_names:
        assert not linked_region_check(m, region_pair=bad_name), f'This should fail {bad_name}'


def test_region_group_check():
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
        assert region_group_check(m, name), f'This name should have been good: {name}'
    for name in bad_names:
        assert not region_group_check(m, name), f'This name should have failed: {name}'


params = [
    ('dogfood', True),
    ('cat/dog', False),
    ('cat|dog', False),
    ('123/45', False),
    (678, True),
]


@pytest.mark.parametrize('value, expected', params)
def test_no_slash(value, expected):
    assert no_slash_or_pipe(M=None, element=value) == expected
