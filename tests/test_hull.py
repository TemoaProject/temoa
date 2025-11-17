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


def test_hull() -> None:
    """Basic build test, just see if it can be built and it rejects bad dimension inputs"""
    hull = Hull(pts)  # noqa F841
    with pytest.raises(ValueError, match='Insufficient points to make hull'):
        # transposed, the points(2) are insufficient for the dimensionality (3)
        hull2 = Hull(pts.T)  # noqa F841


def test_add_point() -> None:
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


def test_get_vector() -> None:
    """Test iteration through the 3 vectors available"""
    hull = Hull(pts)
    for _ in range(3):
        v = hull.get_norm()
        assert v is not None
        assert np.linalg.norm(v) == pytest.approx(1.0)
    # should be no more...
    assert hull.get_norm() is None


def test_is_new_direction() -> None:
    """Test the linear algebra used to see if a new vector is different from an existing vector"""
    hull = Hull(pts)
    # make a new highly similar direction to the [-1, 0] normal
    sim_vec = np.array([-0.99999999999, 0.0])
    sim_vec /= np.linalg.norm(sim_vec)  # normalize
    assert not hull.is_new_direction(sim_vec), 'this should be rejected as a new direction'


def test_valid_directions_available() -> None:
    hull = Hull(pts)
    assert hull.norms_available == 3, '3 basic normals are available'
    hull.add_point(np.array([4, 4]))
    assert hull.norms_available == 3, 'no changes until update'
    hull.update()
    assert hull.norms_available == 5, '5 should be available'


def test_get_vectors() -> None:
    hull = Hull(pts)
    vecs = hull.get_all_norms()
    assert len(vecs) == 3
    hull.add_point(np.array([4, 4]))
    hull.update()
    assert hull.norms_available == 2, '2 new ones were created after 3 were drawn'
    assert len(hull.get_all_norms()) == 2
