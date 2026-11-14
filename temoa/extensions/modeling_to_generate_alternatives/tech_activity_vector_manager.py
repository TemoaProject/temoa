from __future__ import annotations

import queue
from collections import defaultdict
from logging import getLogger
from queue import Queue
from typing import TYPE_CHECKING, Any

import numpy as np
from matplotlib import pyplot as plt
from pyomo.core import Var, value

from temoa.extensions.modeling_to_generate_alternatives.hull import HullSet
from temoa.extensions.modeling_to_generate_alternatives.mga_constants import MgaWeighting
from temoa.extensions.modeling_to_generate_alternatives.vector_manager import VectorManager
from temoa.extensions.modeling_to_generate_alternatives.worker import ObjectiveJob

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Iterable, Iterator, Mapping, Sequence

    from temoa.core.config import TemoaConfig
    from temoa.core.model import TemoaModel


logger = getLogger(__name__)


def hull_point(model: TemoaModel, terms: Sequence[Sequence[tuple[str, Any, float]]]) -> list[float]:
    """The coordinates of the hull point of a solved model, from VectorManager.hull_point_terms"""
    variables: dict[str, Any] = {}
    point = []
    for coordinate in terms:
        total = 0.0
        for var_name, idx, coefficient in coordinate:
            if var_name not in variables:
                variables[var_name] = model.find_component(var_name)
            total += coefficient * value(variables[var_name][idx])
        point.append(total)
    return point


class DefaultItem:
    """A dummy class just to hold items that will have a reasonable __str__ and __repr__"""

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


# just a convenience to have something other than a None item for placeholder
# for use in categories listings for categories that are empty in the model
default_cat = DefaultItem('DEFAULT')


class TechActivityVectorManager(VectorManager):
    completed_solves: int
    conn: sqlite3.Connection
    base_model: TemoaModel
    optimal_cost: float
    cost_relaxation: float
    config: TemoaConfig
    generation_index: int
    category_mapping: dict[str | DefaultItem, list[str]]
    technology_size: dict[str, int]
    variable_index_mapping: dict[str, dict[str, list[tuple[Any, ...]]]]
    coefficient_vector_queue: Queue[np.ndarray]
    hull_points: np.ndarray | None
    hull: HullSet | None
    hull_max_dimension: int
    rng: np.random.Generator
    basis_coefficients: Queue[np.ndarray]
    hull_monitor: bool
    perf_data: dict[int, float]
    progress_label: str

    def __init__(
        self,
        conn: sqlite3.Connection,
        base_model: TemoaModel,
        weighting: MgaWeighting,
        optimal_cost: float,
        cost_relaxation: float,
        config: TemoaConfig,
    ) -> None:
        self.completed_solves = 0
        self.conn = conn
        self.base_model = base_model
        self.optimal_cost = optimal_cost
        self.cost_relaxation = cost_relaxation
        self.config = config
        self.generation_index = 1  # index of how many models generated to couple inputs-outputs

        # {category : [technology, ...]}
        # the number of keys in this are the dimension of the hull
        self.category_mapping = defaultdict(list)

        # {technology: [number of associated variables, ...]}
        self.technology_size = defaultdict(int)
        # in order to peel the data out of a solved model, we also need a rollup of the NAME
        # of the variable and indices in order...
        # {tech : {var_name : [indices, ...]}, ...}
        self.variable_index_mapping = {}

        self.coefficient_vector_queue = Queue()

        if weighting != MgaWeighting.HULL_EXPANSION:
            raise NotImplementedError(
                'Tech Activity currently only works with Hull Expansion weighting'
            )
        self.hull_points = None
        self.hull = None
        mga_inputs = getattr(config, 'mga_inputs', None) or {}
        self.hull_max_dimension = int(mga_inputs.get('hull_max_dimension', 8))
        if self.hull_max_dimension < 2:
            raise ValueError('MGA hull_max_dimension must be at least 2')
        self.rng = np.random.default_rng()
        self._regenerated_at = -1

        self.initialize()
        self.basis_coefficients = self._generate_basis_coefficients(
            self.category_mapping, self.technology_size
        )

        # monitor/report the size of the hull for each new point.  May cause some slowdown due to
        # hull re-computes, but it seems quite fast RN.
        self.hull_monitor = True
        self.perf_data = {}
        self.progress_label = 'hull volume'

    def initialize(self) -> None:
        """
        Fill the internal data stores from db and model
        :return:
        """
        # self.basis_coefficients = [] # Removed inconsistent assignment
        techs_implemented = self.base_model.tech_all  # some may have been culled by source tracing
        logger.debug('Initializing Technology Vectors data elements')
        raw = self.conn.execute('SELECT category, tech FROM Technology').fetchall()
        self.category_mapping = defaultdict(list)
        for row in raw:
            cat, tech = row
            if cat in {None, ''}:
                cat = default_cat
            if tech in techs_implemented:
                self.category_mapping[cat].append(tech)
                self.variable_index_mapping[tech] = defaultdict(list)

        for cat in self.category_mapping:
            logger.debug('Category %s members: %d', cat, len(self.category_mapping[cat]))

        # now pull the flow variables and map them
        for idx in self.base_model.active_flow_rpsditvo or set():
            tech = idx[5]
            self.technology_size[tech] += 1
            self.variable_index_mapping[tech][self.base_model.v_flow_out.name].append(idx)
        for idx_annual in self.base_model.active_flow_rpitvo or set():
            tech = idx_annual[3]
            if tech not in self.base_model.tech_annual:
                continue
            self.technology_size[tech] += 1
            self.variable_index_mapping[tech][self.base_model.v_flow_out_annual.name].append(
                idx_annual
            )
        logger.debug('Catalogued %d Technology Variables', sum(self.technology_size.values()))

    @property
    def expired(self) -> bool:
        return False  # this Manager can always generate more...

    def group_variable_names(self, tech: str) -> list[str]:
        return list(self.variable_index_mapping.get(tech, {}).keys())

    def random_input_vector_model(self) -> ObjectiveJob:
        coeffs = np.random.random(sum(self.technology_size[t] for t in self._ordered_techs()))
        coeffs /= sum(coeffs)
        return ObjectiveJob(self.new_model_name(), coeffs)

    def model_generator(self) -> Iterator[ObjectiveJob | None]:
        """
        Generate the objectives to solve, as coefficients of objective_terms().  Start with the
        basis vectors, then ...
        :return: an ObjectiveJob
        """
        # traverse the basis vectors first
        coeffs = self._make_basis_objective_vector()
        while coeffs is not None:
            yield ObjectiveJob(self.new_model_name(), coeffs)
            coeffs = self._make_basis_objective_vector()

        # if asking for more, we *should* have enough data to create a good hull now...
        if len(self.category_mapping) > 0:
            while self.completed_solves <= 2 * len(self.category_mapping):
                # some of the basis vectors must have "crashed" or timed out...
                # supply random vectors until we have sufficient number of
                # solved models to make hull
                logger.info(
                    'Adding random vectors to augment the basis.'
                    'Some basis solves may have crashed...'
                )
                yield self.random_input_vector_model()

        logger.info('Generating hull points')
        self.regenerate_hull()
        # now we can run until told to quit.  None: no new direction until more points arrive
        while True:
            coeffs = self._next_objective_vector()
            yield None if coeffs is None else ObjectiveJob(self.new_model_name(), coeffs)

    def new_model_name(self) -> str:
        """produce a new name with updated index suffix"""
        base_name = self.base_model.name.split('-')[0]
        new_name = '-'.join((base_name, str(self.generation_index)))
        self.generation_index += 1
        return new_name

    def process_results(self, model: TemoaModel) -> list[float]:
        """
        retrieve the necessary variable values to make another hull point
        :param M:
        :return: None
        """
        res = hull_point(model, self.hull_point_terms())
        self.add_hull_point(res)
        return res

    def hull_point_terms(self) -> list[list[tuple[str, Any, float]]]:
        return [
            [term for tech in self.category_mapping[cat] for term in self.tech_terms(tech)]
            for cat in self.category_mapping
        ]

    def tech_terms(self, tech: str) -> list[tuple[str, Any, float]]:
        return [
            (var_name, idx, 1.0)
            for var_name, indices in self.variable_index_mapping[tech].items()
            for idx in indices
        ]

    def add_hull_point(self, point: Sequence[float]) -> None:
        self.completed_solves += 1
        # add it to the hull points
        new_point = np.array(point)
        if self.hull_points is None:
            self.hull_points = np.atleast_2d(new_point)
        else:
            self.hull_points = np.vstack((self.hull_points, new_point))
        if self.hull is not None:
            self.hull.add_point(new_point)
            self.load_normals(self._shuffled(self.hull.get_all_norms()))
            if self.hull_monitor:
                self.tracker()

    def stop_resolving(self) -> bool:
        return False

    @property
    def groups(self) -> Iterable[Any]:
        return self.category_mapping.keys()

    def group_members(self, group: str | DefaultItem) -> list[str]:
        return self.category_mapping.get(group, [])

    def _make_basis_objective_vector(self) -> np.ndarray | None:
        """the next basis vector: the coefficients of the objective terms in a basis solve"""
        if self.basis_coefficients.empty():
            return None
        try:
            coeffs = self.basis_coefficients.get()
        except queue.Empty:
            return None

        # verify a unit vector
        err = abs(abs(sum(coeffs)) - 1)
        assert err < 1e-6, 'unit vector size error'
        return coeffs

    def _next_objective_vector(self) -> np.ndarray | None:
        if (
            self.coefficient_vector_queue.qsize() <= 3
            and self.completed_solves > self._regenerated_at
        ):
            logger.info('running low on input vectors...  refreshing the vectors with new hull')
            self.regenerate_hull()
        if not self.coefficient_vector_queue or self.input_vectors_available() == 0:
            return None
        vector = self.coefficient_vector_queue.get()

        # translate the norm vector into coefficients
        coeffs_list = []
        for idx, cat in enumerate(self.category_mapping):
            for tech in self.category_mapping[cat]:
                reps = self.technology_size[tech]
                element = [
                    vector[idx],
                ] * reps
                coeffs_list.extend(element)
        coeffs = np.array(coeffs_list)
        coeffs /= -np.sum(np.abs(coeffs))  # normalize
        return coeffs

    def _ordered_techs(self) -> list[str]:
        return [tech for cat in self.category_mapping for tech in self.category_mapping[cat]]

    def objective_terms(self) -> list[tuple[str, Any, float]]:
        """The (variable name, index, weight) of each objective coefficient, in order"""
        return [term for tech in self._ordered_techs() for term in self.tech_terms(tech)]

    def var_vector(self, model: TemoaModel) -> list[Any]:
        """Produce a properly sequenced array of variables from the current model for use in obj
        vector"""
        res = []
        for cat in self.category_mapping:
            for tech in self.category_mapping[cat]:
                for var_name in self.variable_index_mapping[tech]:
                    var = model.find_component(var_name)
                    if not isinstance(var, Var):
                        raise RuntimeError(
                            'Failed to retrieve a named variable from the model: %s', var_name
                        )
                    for idx in self.variable_index_mapping[tech][var_name]:
                        res.append(var[idx])
        return res

    def regenerate_hull(self) -> None:
        """make the hull, or draw new axis groups for it, and queue its unused directions"""
        if self.hull_points is None:
            logger.warning('Cannot regenerate hull: no points available')
            return
        self._regenerated_at = self.completed_solves
        if self.hull is None:
            logger.debug('Generating the cvx hull from %d points', len(self.hull_points))
            self.hull = HullSet(self.hull_points, self.hull_max_dimension, self.rng)
        elif self.hull.partitioned:
            self.hull.repartition()
        fresh_vecs = self._shuffled(self.hull.get_all_norms())
        logger.info('Made %d fresh vectors', len(fresh_vecs))
        label, progress = self.hull.progress()
        logger.info('Current %s:  %0.2f', label, progress)
        logger.info(
            'Current new vector rejection rate (for collinearity):  %0.2f',
            self.hull.norm_rejection_proportion,
        )
        self.load_normals(fresh_vecs)

    @staticmethod
    def _shuffled(vectors: np.ndarray) -> np.ndarray:
        np.random.shuffle(vectors)
        return vectors

    def load_normals(self, normals: np.ndarray) -> None:
        for vector in normals:
            self.coefficient_vector_queue.put(vector)

    def input_vectors_available(self) -> int:
        return self.coefficient_vector_queue.qsize()

    @staticmethod
    def _generate_basis_coefficients(
        category_mapping: Mapping[Any, Sequence[str]],
        technology_size: Mapping[str, int],
    ) -> Queue[np.ndarray]:
        # Sequentially build the coefficient vector in the order of the categories and associated
        # techs
        q: Queue[np.ndarray] = Queue()
        for selected_cat in category_mapping:
            res = []
            if selected_cat == default_cat:
                continue
            for cat in category_mapping:
                num_marks = sum(technology_size[tech] for tech in category_mapping[cat])
                if cat == selected_cat:
                    marks = [
                        1,
                    ] * num_marks
                else:
                    marks = [
                        0,
                    ] * num_marks
                res.extend(marks)

            entry = np.array(res)
            entry = entry / np.array(np.sum(entry))
            q.put(entry)  # high value
            q.put(-entry)  # low value

        return q

    def tracker(self) -> None:
        """
        Track the growth of the hull after each new point, from the hull already updated with it:
        its volume, or above hull_max_dimension axes the growth of the axis ranges
        """
        if self.hull is not None and self.hull_points is not None:
            self.progress_label, progress = self.hull.progress()
            logger.info('Tracking %s at %0.2f', self.progress_label, progress)
            self.perf_data.update({len(self.hull_points): progress})

    def finalize_tracker(self) -> None:
        fout = self.config.output_path / 'hull_performance.png'
        pts = sorted(self.perf_data.keys())
        y = [self.perf_data[pt] for pt in pts]
        plt.plot(pts, y)
        plt.xlabel('Iteration')
        plt.ylabel(
            'N-Dimensional Hull Volume'
            if self.progress_label == 'hull volume'
            else 'Geometric mean of the axis ranges (relative)'
        )
        plt.savefig(str(fout))
