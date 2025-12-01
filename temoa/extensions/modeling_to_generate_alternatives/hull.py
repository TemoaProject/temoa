"""
A thin wrapper on Scipy's ConvexHull to make it more manageable
"""
from logging import getLogger

import numpy as np
import scipy
from scipy.spatial import ConvexHull

logger = getLogger(__name__)


class Hull:
    def __init__(self, points: np.ndarray, **kwargs):
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
        return self.norms_rejected / self.norms_checked

    def update(self):
        """
        Update/rebuild the Hull based on new points.
        :return:
        """
        if self.all_points is None:
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
        except scipy.spatial._qhull.QhullError as e:
            logger.error(
                'Attempt at hull construction from basis vectors failed.'
                '\nMay be non-recoverable.  Possibly try a set of random vectors to initialize the '
                'Hull.'
            )
            logger.error(e)
            raise RuntimeError('Hull construction from vectors failed.  See log file')

        # update the available norms from the new hull
        equations = self.cv_hull.equations[:, 0:-1]
        for norm in equations:
            norm = norm / np.linalg.norm(norm)  # ensure it is a unit vector
            if self.is_new_direction(norm):
                if self._valid_norms is None:
                    self._valid_norms = np.atleast_2d(norm)
                else:
                    self._valid_norms = np.vstack((self._valid_norms, norm))

    def add_point(self, point: np.ndarray):
        if len(point) != self.dim:
            logger.error(
                'Tried adding a point to hull (dim: %d) with wrong dimensions %d. Point: %s',
                self.dim,
                len(point),
                point,
            )
        if self.all_points is None:
            self.all_points = np.atleast_2d(point)
        else:
            self.all_points = np.vstack((self.all_points, point))

    def get_norm(self) -> np.ndarray | None:
        """
        pop a new direction norm from the stack
        :return: a new norm vector
        """
        if self.norm_index < len(self._valid_norms):
            if np.ndim(self._valid_norms) == 1:  # only one on the stack
                res = self._valid_norms
            else:
                res = self._valid_norms[self.norm_index, :]
            self.norm_index += 1
            return res
        return None

    def get_all_norms(self) -> np.ndarray:
        """Get a matrix of all unused new vectors"""
        if self.norms_available > 0:
            res = np.atleast_2d(self._valid_norms)[self.norm_index :, :]
            self.norm_index = len(self._valid_norms)
            return res
        return np.array([])

    def is_new_direction(self, vec: np.ndarray) -> bool:
        """
        compare vector to all directions already processed
        :param vec: the new vector to consider
        :return: True if the new vector is a valid direction, False otherwise"""
        self.norms_checked += 1
        if self.seen_norms is None:
            self.seen_norms = np.atleast_2d(vec)
            return True
        max_similarity = np.max(self.seen_norms.dot(vec))
        if 1 - max_similarity < self.tolerance:
            self.norms_rejected += 1
            return False
        else:
            self.seen_norms = np.vstack((self.seen_norms, vec))
            return True
