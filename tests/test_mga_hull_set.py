"""
Tests of the hulls that supply the MGA search directions: the filter of repeated directions and
the split of many axes into groups of small hulls.
"""

import numpy as np
import pytest

from temoa.extensions.modeling_to_generate_alternatives.hull import Hull, HullSet


def _sequential_filter(vecs: np.ndarray, tolerance: float) -> np.ndarray:
    """The original one-by-one filter of directions within the tolerance of earlier ones"""
    seen: list[np.ndarray] = []
    for vec in vecs:
        if not seen or 1 - max(float(s @ vec) for s in seen) >= tolerance:
            seen.append(vec)
    return np.array(seen)


def test_new_directions_match_sequential_filter() -> None:
    rng = np.random.default_rng(1)
    vecs = rng.normal(size=(400, 3))
    vecs = np.vstack((vecs, vecs[:40] + 1e-4))
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    hull = Hull.__new__(Hull)
    hull.seen_norms = None
    hull.tolerance = 5e-3
    hull.norms_checked = hull.norms_rejected = 0
    found = np.vstack((hull.new_directions(vecs[:200]), hull.new_directions(vecs[200:])))
    np.testing.assert_allclose(found, _sequential_filter(vecs, 5e-3))
    assert hull.norms_rejected == len(vecs) - len(found)


def test_single_hull_up_to_max_dimension() -> None:
    rng = np.random.default_rng(2)
    hulls = HullSet(rng.random((12, 4)), max_dimension=4, rng=rng)
    assert not hulls.partitioned
    assert len(hulls.hulls) == 1
    label, volume = hulls.progress()
    assert label == 'hull volume'
    assert volume == pytest.approx(hulls.hulls[0].cv_hull.volume)


def test_many_axes_are_split_into_small_hulls() -> None:
    rng = np.random.default_rng(3)
    hulls = HullSet(rng.random((20, 11)), max_dimension=4, rng=rng)
    assert hulls.partitioned
    assert sorted(np.concatenate(hulls.groups).tolist()) == list(range(11))
    assert max(len(g) for g in hulls.groups) <= 4
    norms = hulls.get_all_norms()
    assert norms.shape[1] == 11
    for norm in norms:
        nonzero = np.flatnonzero(norm)
        assert any(set(nonzero) <= set(g.tolist()) for g in hulls.groups)
    label, growth = hulls.progress()
    assert label == 'mean range growth'
    assert growth == pytest.approx(1.0)
    hulls.add_point(np.full(11, 2.0))
    assert hulls.progress()[1] > 1.0
