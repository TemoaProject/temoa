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
Created on:  4/25/24

"""

import pytest

from temoa.temoa_model.model_checking.element_checker import ViableSet, filter_elements

params = [
    {
        'name': 'group 1',
        'filt': ViableSet(
            [('a', 1), ('b', 2), ('bob+tom', 3)], exception_loc=0, exception_vals=[r'dog', r'\+']
        ),
        'testers': [('a', 1), ('b', 2), ('x', 2), ('dog', 4), ('dog', 1), ('cat+dog', 1)],
        'locs': (0, 1),
        'expected': [('a', 1), ('b', 2), ('dog', 1), ('cat+dog', 1)],
    },
    {
        'name': 'singletons',
        'filt': ViableSet(
            elements=[(1,), (2,), ('dog',), ('pig',)],
            exception_loc=0,
            exception_vals=[r'rhino', r'\+'],
        ),
        'testers': [(1,), ('dog',), ('cat',), ('rhino',)],
        'expected': [(1,), ('dog',), ('rhino',)],
    },
    {
        'name': 'param-like',
        'filt': ViableSet(
            [('a', 1), ('b', 2), ('c+d', 3)], exception_loc=0, exception_vals=[r'^dog\Z', r'\+']
        ),
        'testers': [
            ('a', 1, 0.2),
            ('b', 2, 1.5),
            ('x', 2, 8.22),
            ('dog', 4, 'Bob'),
            ('dog', 1, 55),
            ('cat+dog', 1, 23),
            ('a', 1, None),
            ('a', 2, 44),
            ('bigdog', 1, 99),
        ],
        'locs': (0, 1),
        'expected': [
            ('a', 1, 0.2),
            ('b', 2, 1.5),
            ('dog', 1, 55),
            ('cat+dog', 1, 23),
            ('a', 1, None),
        ],
    },
    {
        'name': 'use of defaults',
        'filt': ViableSet(
            [('a', 1), ('b', 2), ('c+d', 3)],
            exception_loc=0,
            exception_vals=ViableSet.REGION_REGEXES,
        ),
        'testers': [
            ('a', 1, 0.2),
            ('b', 2, 1.5),
            ('x', 2, 8.22),
            ('dog', 4, 'Bob'),  # fail not in REGION_REGEXES
            ('global', 1, 55),
            ('global', 33, 22),  # fail 33 invalid
            ('Global', 1, 23),  # fail cap
            ('a', 1, None),
            ('a', 2, 44),
            ('horse+coat', 1, 99),  # pass, '+' in regexes, and '1' is OK too!
        ],
        'locs': (0, 1),
        'expected': [
            ('a', 1, 0.2),
            ('b', 2, 1.5),
            ('global', 1, 55),
            ('a', 1, None),
            ('horse+coat', 1, 99),
        ],
    },
    {
        'name': 'use of defaults with multi-dim params',
        'filt': ViableSet(
            [('a', 1), ('b', 2)],
            exception_loc=0,
            exception_vals=ViableSet.REGION_REGEXES,
        ),
        'testers': [
            ('a', 'stuff', 1, 0.2),
            ('b', 'stuff', 2, 1.5),
            ('a', 'other', 3, 8.22),
            ('global', 33, 1, 22),
            ('global', 1, 77, 66),  # fail 77
            ('a', 'zz top', 1, None),
            ('horse+coat', 'ugly', 1, 99),  # pass, '+' in regexes, and '1' is OK too!
        ],
        'locs': (0, 2),
        'expected': [
            ('a', 'stuff', 1, 0.2),
            ('b', 'stuff', 2, 1.5),
            ('global', 33, 1, 22),
            ('a', 'zz top', 1, None),
            ('horse+coat', 'ugly', 1, 99),  # pass, '+' in regexes, and '1' is OK too!
        ],
    },
]


@pytest.mark.parametrize('data', params, ids=(param['name'] for param in params))
def test_filter_elements(data):
    # use the 'tester' elements against the filter to ensure we get expected results
    assert (
        filter_elements(
            values=data['testers'], validation=data['filt'], value_locations=data.get('locs', (0,))
        )
        == data['expected']
    )


def test_dimension_measurement():
    """quick test to ensure we are getting the correct dimension esp. when elements are not tuple"""
    elements = [(1, 2), (3, 4)]
    assert ViableSet(elements).dim == 2

    elements = ['dog', 'pig', 'uncle bob']
    assert ViableSet(elements).dim == 1

    elements = [('dog',), ('pig',), ('uncle bob',)]
    assert ViableSet(elements).dim == 1

    elements = [(1991,), (1987,)]
    assert ViableSet(elements).dim == 1

    elements = [2000, 2001]
    vs = ViableSet(elements)
    assert vs.dim == 1
    assert vs.members == {2000, 2001}
    assert vs.member_tuples == {(2000,), (2001,)}

    elements = []
    assert ViableSet(elements).dim == 0
