"""
A thin wrapper on Scipy's ConvexHull to make it more manageable
"""

from __future__ import annotations

from logging import getLogger
from typing import Any

import numpy as np
from scipy.spatial import ConvexHull, cKDTree  # type: ignore[import-untyped]

logger = getLogger(__name__)


class Hull:
    dim: int
    cv_hull: Any
    volume: float
    seen_norms: np.ndarray | None
    _valid_norms: np.ndarray | None
    tolerance: float
    norms_checked: int
    norms_rejected: int
    good_points: np.ndarray | None
    all_points: np.ndarray | None
    norm_index: int

    def __init__(self, points: np.ndarray, **kwargs: Any) -> None:
        """
        Build the initial hull from array of points
        :param points: an array of points [points, hull dimension]
        :param kwargs:
        """
        # the number of columns in the first volley of points sets the dimensions of the hull
        self.dim = points.shape[1]
        if self.dim + 1 > points.shape[0]:
            logger.error(
                'Insufficient points to make hull.  Should have at least hull dimensionality + 1.'
            )
            raise ValueError(
                'Insufficient points to make hull.  Should have at least hull dimensionality + 1.'
                f'  Received {points.shape[0]} points'
            )
        logger.info(
            'Initializing Hull with points: %d and dimensions: %d', points.shape[0], points.shape[1]
        )

        self.cv_hull = None
        self.volume = 0.0

        # containers to manage new and explored directions
        self.seen_norms = None
        self._valid_norms = None

        self.tolerance = 5e-3  # minimum cosine dissimilarity

        # for tracking
        self.norms_checked = 0
        self.norms_rejected = 0

        self.good_points = None  # safe keeping in case we crash later
        self.all_points = points.copy()
        self.norm_index = 0  # pointer to the next new vector from the stack
        self.update()

    @property
    def norms_available(self) -> int:
        if self._valid_norms is None:
            return 0
        else:
            return len(self._valid_norms) - self.norm_index

    @property
    def norm_rejection_proportion(self) -> float:
        if self.norms_checked == 0:
            return 0.0
        return self.norms_rejected / self.norms_checked

    def update(self) -> None:
        """
        Update/rebuild the Hull based on new points.
        :return:
        """
        if self.all_points is None or len(self.all_points) == 0:
            return
        try:
            self.cv_hull = ConvexHull(self.all_points, qhull_options='Q12 QJ')
            # Q12:  Allow "wide" facets, which seems to happen with large disparity in scale in
            #       model
            # QJ:  option to "joggle" inputs if errors arise from singularities, etc.  This seems
            #      to slow things down a moderate amount.
            # Dev Note:  After significant experiments with building new each time or allowing
            #            "incremental" additions to the hull, it appears more ROBUST to just
            #            rebuild.  More frequent abnormal exits when trying to use incremental, and
            #            time difference is negligible for this few pts.
            self.good_points = self.cv_hull.points
            logger.info('Hull updated')
            self.volume = self.cv_hull.volume
        except Exception as e:
            # scipy.spatial._qhull.QhullError may not be easily found by mypy
            logger.error(
                'Attempt at hull construction from basis vectors failed.'
                '\nMay be non-recoverable.  Possibly try a set of random vectors to initialize the '
                'Hull.'
            )
            logger.error(e)
            raise RuntimeError('Hull construction from vectors failed.  See log file') from e

        # update the available norms from the new hull
        equations = self.cv_hull.equations[:, 0:-1]
        norms = equations / np.linalg.norm(equations, axis=1, keepdims=True)
        new_norms = self.new_directions(norms)
        if len(new_norms):
            if self._valid_norms is None:
                self._valid_norms = new_norms
            else:
                self._valid_norms = np.vstack((self._valid_norms, new_norms))

    def add_point(self, point: np.ndarray) -> None:
        if len(point) != self.dim:
            msg = (
                f'Tried adding a point to hull (dim: {self.dim}) with '
                f'wrong dimensions {len(point)}. Point: {point}'
            )
            logger.error(msg)
            raise ValueError(msg)
        if self.all_points is None:
            self.all_points = np.atleast_2d(point)
        else:
            self.all_points = np.vstack((self.all_points, point))

    def get_norm(self) -> np.ndarray | None:
        """
        pop a new direction norm from the stack
        :return: a new norm vector
        """
        if self._valid_norms is not None and self.norm_index < len(self._valid_norms):
            if np.ndim(self._valid_norms) == 1:  # only one on the stack
                res = self._valid_norms
            else:
                res = self._valid_norms[self.norm_index, :]
            self.norm_index += 1
            return res
        return None

    def get_all_norms(self) -> np.ndarray:
        """Get a matrix of all unused new vectors"""
        if self._valid_norms is not None and self.norms_available > 0:
            res = np.atleast_2d(self._valid_norms)[self.norm_index :, :]
            self.norm_index = len(self._valid_norms)
            return res
        return np.array([])

    def is_new_direction(self, vec: np.ndarray) -> bool:
        """
        compare vector to all directions already processed
        :param vec: the new vector to consider
        :return: True if the new vector is a valid direction, False otherwise"""
        return len(self.new_directions(np.atleast_2d(vec))) == 1

    def new_directions(self, vecs: np.ndarray) -> np.ndarray:
        """
        The unit vectors that are not within the tolerance of a direction already seen, nor of an
        earlier vector of the batch, in order.  They are added to the seen directions.
        """
        self.norms_checked += len(vecs)
        # 1 - cos(a, b) < tolerance  <=>  |a - b| < sqrt(2 * tolerance), for unit vectors
        radius = np.sqrt(2 * self.tolerance)
        keep = np.ones(len(vecs), dtype=bool)
        if self.seen_norms is not None and len(vecs):
            dist, _ = cKDTree(self.seen_norms).query(vecs, distance_upper_bound=radius)
            keep &= ~(dist < radius)
        candidates = np.flatnonzero(keep)
        if len(candidates) > 1:
            tree = cKDTree(vecs[candidates])
            for pos in range(len(candidates)):
                if keep[candidates[pos]]:
                    for other in tree.query_ball_point(vecs[candidates[pos]], radius):
                        if other > pos:
                            keep[candidates[other]] = False
        accepted = vecs[keep]
        self.norms_rejected += len(vecs) - len(accepted)
        if len(accepted):
            self.seen_norms = (
                accepted if self.seen_norms is None else np.vstack((self.seen_norms, accepted))
            )
        return accepted


class HullSet:
    """
    The convex hulls that supply the search directions.  Up to max_dimension axes, a single hull
    over all of them.  Above it, the axes are split at random into groups of at most max_dimension
    axes, one hull per group, and the directions of each hull are lifted back to all the axes
    (zero on the other groups).  The groups are drawn again with repartition().
    """

    def __init__(self, points: np.ndarray, max_dimension: int, rng: np.random.Generator) -> None:
        if max_dimension < 2:
            raise ValueError('The hull dimension limit must be at least 2')
        self.dim = points.shape[1]
        self.max_dimension = max_dimension
        self.rng = rng
        self.points = np.atleast_2d(points).copy()
        self._base_range: np.ndarray | None = None
        self.groups: list[np.ndarray] = []
        self.hulls: list[Hull] = []
        self.repartition()

    @property
    def partitioned(self) -> bool:
        return self.dim > self.max_dimension

    def repartition(self) -> None:
        if self.partitioned:
            order = self.rng.permutation(self.dim)
            n_groups = -(-self.dim // self.max_dimension)
            self.groups = [np.sort(g) for g in np.array_split(order, n_groups)]
            logger.info(
                'Hull axes split into %d groups of up to %d axes', n_groups, self.max_dimension
            )
        else:
            self.groups = [np.arange(self.dim)]
        self.hulls = [Hull(self.points[:, g]) for g in self.groups]

    def add_point(self, point: np.ndarray) -> None:
        self.points = np.vstack((self.points, point))
        for g, hull in zip(self.groups, self.hulls, strict=True):
            hull.add_point(np.asarray(point)[g])
            hull.update()

    def get_all_norms(self) -> np.ndarray:
        lifted = []
        for g, hull in zip(self.groups, self.hulls, strict=True):
            norms = hull.get_all_norms()
            if len(norms):
                full = np.zeros((len(norms), self.dim))
                full[:, g] = norms
                lifted.append(full)
        return np.vstack(lifted) if lifted else np.array([])

    @property
    def norm_rejection_proportion(self) -> float:
        checked = sum(h.norms_checked for h in self.hulls)
        return sum(h.norms_rejected for h in self.hulls) / checked if checked else 0.0

    def progress(self) -> tuple[str, float]:
        """
        The hull volume up to max_dimension axes.  Above it, the geometric mean of the ranges of
        the points along each axis, relative to the range of the first hull built, which grows
        as the alternatives spread out and is cheap in any dimension.
        """
        if not self.partitioned:
            return 'hull volume', float(self.hulls[0].volume)
        if self._base_range is None:
            self._base_range = np.ptp(self.points, axis=0)
        ranges = np.ptp(self.points, axis=0)
        scale = np.where(self._base_range > 0, self._base_range, 1.0)
        return 'mean range growth', float(
            np.exp(np.mean(np.log(np.maximum(ranges / scale, 1e-12))))
        )
