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
Created on:  4/18/24

"""
import numpy as np
import pytest

from temoa.extensions.modeling_to_generate_alternatives.hull import Hull

pts = np.array([[2, 2], [2, 4], [4, 2]])
r"""
       |\
   <-- | \  --> (to be viewed at a slightly upward angle. :/ )
       |  \
       |___\
         |
         v
A simple right triangle to start with 
- should have 3 norms from 3 equations as a starter
"""


def test_hull():
    """Basic build test, just see if it can be built and it rejects bad dimension inputs"""
    hull = Hull(pts)
    assert hull.cv_hull
    with pytest.raises(ValueError):
        # transposed, the points(2) are insufficient for the dimensionality (3)
        hull2 = Hull(pts.T)
        print(
            hull2.all_points
        )  # should never get here... just to prevent warning on unused var 'hull'


def test_add_point():
    """
    test adding point to the triangle to make a square and that by doing so
    we get 2 new normals
    """
    hull = Hull(pts)
    # complete the square...
    hull.add_point(np.array([4, 4]))
    hull.update()
    # we should have 5 directions to pull from now, the 4 square sides + the orig triangle face
    count = 0
    v = hull.get_norm()
    while v is not None:
        count += 1
        # print(v)
        v = hull.get_norm()
    assert count == 5, '5 faces were available and should have been added to the available vecs'


def test_get_vector():
    """Test iteration through the 3 vectors available"""
    hull = Hull(pts)
    for _ in range(3):
        v = hull.get_norm()
        assert np.linalg.norm(v) == pytest.approx(1.0)
    # should be no more...
    assert hull.get_norm() is None


def test_is_new_direction():
    """Test the linear algebra used to see if a new vector is different from an existing vector"""
    hull = Hull(pts)
    # make a new highly similar direction to the [-1, 0] normal
    sim_vec = np.array([-0.99999999999, 0.0])
    sim_vec /= np.linalg.norm(sim_vec)  # normalize
    assert not hull.is_new_direction(sim_vec), 'this should be rejected as a new direction'


def test_valid_directions_available():
    hull = Hull(pts)
    assert hull.norms_available == 3, '3 basic normals are available'
    hull.add_point(np.array([4, 4]))
    assert hull.norms_available == 3, 'no changes until update'
    hull.update()
    assert hull.norms_available == 5, '5 should be available'


def test_get_vectors():
    hull = Hull(pts)
    vecs = hull.get_all_norms()
    assert len(vecs) == 3
    hull.add_point(np.array([4, 4]))
    hull.update()
    assert hull.norms_available == 2, '2 new ones were created after 3 were drawn'
    assert len(hull.get_all_norms()) == 2
