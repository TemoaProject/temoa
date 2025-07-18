"""
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


Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  11/9/24

"""

import pytest

from temoa.extensions.monte_carlo.mc_run import RowData, TweakFactory


@pytest.fixture(scope='module')
def tweak_factory():
    tweak_factory = TweakFactory(
        data_store={'dog': {(1, 2): 3.0, (5, 6): 4.0}, 'cat': {('a', 'b'): 7.0, ('c', 'd'): 8.0}}
    )
    return tweak_factory


good_params = [
    ('1,dog,1|2,a,1.0,some good notes', RowData(1, 'dog', '1|2', 'a', 1.0, 'some good notes'), 1),
    (
        '1  , dog,  1|2  , a , 1.0,',
        RowData(1, 'dog', '1|2', 'a', 1.0, ''),
        1,
    ),  # we should be able to strip lead/trail spaces
    ('22,cat,c|d/e/f|9/10,r,2,', RowData(22, 'cat', 'c|d/e/f|9/10', 'r', 2.0, ''), 6),
]
fail_examples = [
    ('z,dog,1|2,a,1.0,'),  # has 'z' for run, non integer
    ('1,dog,1||2,a,1.0,'),  # has empty index location
    ('2,dog,5|6,x,2.0,'),  # has 'x' not in r/s/a
    ('3,pig,4|5|7,r,2.0,'),  # no pig in data source
]
ids = ['non-int run label', 'empty index', 'non r/s/a', 'no-match param']


@pytest.mark.parametrize('row, expected,_', good_params, ids=range(len(good_params)))
def test__row_parser(row, expected, _, tweak_factory):
    assert tweak_factory.row_parser(0, row=row) == expected


@pytest.mark.parametrize('row', fail_examples, ids=ids)
def test__row_parser_fail(row, tweak_factory):
    with pytest.raises(ValueError):
        tweak_factory.row_parser(0, row=row)


@pytest.mark.parametrize('row, _, num_tweaks', good_params, ids=range(len(good_params)))
def test_make_tweaks(row, _, num_tweaks, tweak_factory):
    _, tweaks = tweak_factory.make_tweaks(0, row=row)
    assert len(tweaks) == num_tweaks
