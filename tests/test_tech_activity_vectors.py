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
Created on:  4/16/24

"""

import pytest

from temoa.extensions.modeling_to_generate_alternatives.tech_activity_vector_manager import (
    TechActivityVectorManager,
)


def test__vector_engine():
    """
    Make sure the basis generation algorithm is accurate.  In this test case, there are unequal
    number of members per category and differing variables per member.  We should come up with
    4 orthogonal vectors
    :return:
    """
    cat_map = {
        'A': ['dog', 'pig'],
        'B': [
            'cat',
        ],
    }
    var_map = {'dog': ['red', 'blue'], 'pig': ['yellow', 'green'], 'cat': ['blue', 'gold']}
    tech_sizes = {k: len(v) for k, v in var_map.items()}
    # below is just to show the mapping back to variables.... test just want the coefficients from res_values
    # res = [
    #     {'red': 0.25, 'blue': 0.25, 'yellow': 0.25, 'green': 0.25},
    #     {'red': -0.25, 'blue': -0.25, 'yellow': -0.25, 'green': -0.25},
    #     {'blue': 0.5, 'gold': 0.5},
    #     {'blue': -0.5, 'gold': -0.5},
    # ]
    res_values = [
        [0.25, 0.25, 0.25, 0.25, 0, 0],
        [-0.25, -0.25, -0.25, -0.25, 0, 0],
        [0.5, 0.5, 0, 0, 0, 0],
        [-0.5, -0.5, 0, 0, 0, 0],
    ]
    matrix = TechActivityVectorManager._generate_basis_coefficients(
        category_mapping=cat_map, technology_size=tech_sizes
    )
    rows = []
    if matrix.qsize() > 0:
        rows.append(matrix.get_nowait())
    for idx, row in enumerate(rows):
        assert row == pytest.approx(res_values[idx], abs=1e-2)
