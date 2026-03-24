from __future__ import annotations

import queue
from collections import defaultdict
from logging import getLogger
from queue import Queue
from typing import TYPE_CHECKING, Any

import numpy as np
from matplotlib import pyplot as plt
from pyomo.core import Expression, Objective, Var, quicksum, value

from temoa.extensions.modeling_to_generate_alternatives.hull import Hull
from temoa.extensions.modeling_to_generate_alternatives.mga_constants import MgaWeighting
from temoa.extensions.modeling_to_generate_alternatives.vector_manager import VectorManager

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Iterable, Iterator, Mapping, Sequence

    from temoa.core.config import TemoaConfig
    from temoa.core.model import TemoaModel


logger = getLogger(__name__)


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
    hull: Hull | None
    basis_coefficients: Queue[np.ndarray]
    hull_monitor: bool
    perf_data: dict[int, float]

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

        self.initialize()
        self.basis_coefficients = self._generate_basis_coefficients(
            self.category_mapping, self.technology_size
        )

        # monitor/report the size of the hull for each new point.  May cause some slowdown due to
        # hull re-computes, but it seems quite fast RN.
        self.hull_monitor = True
        self.perf_data = {}

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
            self.technology_size[tech] += 1
            self.variable_index_mapping[tech][self.base_model.v_flow_out_annual.name].append(idx_annual)
        logger.debug('Catalogued %d Technology Variables', sum(self.technology_size.values()))

    @property
    def expired(self) -> bool:
        return False  # this Manager can always generate more...

    def group_variable_names(self, tech: str) -> list[str]:
        return list(self.variable_index_mapping.get(tech, {}).keys())

    def random_input_vector_model(self) -> TemoaModel:
        new_model = self.base_model.clone()
        new_model.name = self.new_model_name()
        var_vec = self.var_vector(new_model)
        coeffs = np.random.random(len(var_vec))
        coeffs /= sum(coeffs)
        obj_expr = quicksum(c * v for c, v in zip(coeffs, var_vec, strict=False))
        new_model.obj = Objective(expr=obj_expr)
        return new_model

    def model_generator(self) -> Iterator[TemoaModel]:
        """
        Generate instances to solve.  Start with the basis vectors, then ...
        :return: a TemoaModel instance
        """
        # traverse the basis vectors first
        new_model = self.base_model.clone()
        obj_vector = self._make_basis_objective_vector(new_model)
        while obj_vector is not None:
            new_model.obj = Objective(expr=obj_vector)
            new_model.name = self.new_model_name()
            yield new_model
            new_model = self.base_model.clone()
            obj_vector = self._make_basis_objective_vector(new_model)

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
        # now we can run until told to quit or fail to make a new vector
        while True:
            new_model = self.base_model.clone()
            new_model.name = self.new_model_name()
            v = self._next_objective_vector(model=new_model)
            if v is None:
                return
            new_model.obj = Objective(expr=v)
            yield new_model

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
        self.completed_solves += 1
        res: list[float] = []
        for cat in self.category_mapping:
            element = 0
            for tech in self.category_mapping[cat]:
                for var_name in self.variable_index_mapping[tech]:
                    model_var = model.find_component(var_name)
                    if not isinstance(model_var, Var):
                        raise RuntimeError('hooked a bad fish')
                    element += sum(
                        value(model_var[idx]) for idx in self.variable_index_mapping[tech][var_name]
                    )
            res.append(element)

        # add it to the hull points
        hull_point = np.array(res)
        if self.hull_points is None:
            self.hull_points = np.atleast_2d(hull_point)
        else:
            self.hull_points = np.vstack((self.hull_points, hull_point))
        if self.hull_monitor:
            self.tracker()
        return res

    def stop_resolving(self) -> bool:
        return False

    @property
    def groups(self) -> Iterable[Any]:
        return self.category_mapping.keys()

    def group_members(self, group: str | DefaultItem) -> list[str]:
        return self.category_mapping.get(group, [])

    # noinspection PyTypeChecker
    def _make_basis_objective_vector(self, model: TemoaModel) -> Iterable[Expression] | None:
        """generator for basis vectors which will be the coefficients in the obj expression in the
        basis solves"""
        if self.basis_coefficients.empty():
            return None
        try:
            coeffs = self.basis_coefficients.get()
        except queue.Empty:
            return None

        # now we need to roll out a vector of the variables and pair them with coefficients...
        vars = self.var_vector(model)

        # verify a unit vector
        err = abs(abs(sum(coeffs)) - 1)
        assert err < 1e-6, 'unit vector size error'
        expr = sum(c * v for v, c in zip(vars, coeffs, strict=False) if c != 0)
        return expr

    def _next_objective_vector(self, model: TemoaModel) -> Expression | None:
        if self.coefficient_vector_queue.qsize() <= 3:
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
        coeffs /= np.sum(coeffs)  # normalize

        obj_vars = self.var_vector(model)

        assert len(obj_vars) == len(coeffs)
        return quicksum(c * v for v, c in zip(obj_vars, coeffs, strict=False))

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
        """make the hull..."""
        if self.hull_points is None:
            logger.warning('Cannot regenerate hull: no points available')
            return
        logger.debug('Generating the cvx hull from %d points', len(self.hull_points))
        self.hull = Hull(self.hull_points)
        fresh_vecs = self.hull.get_all_norms()
        np.random.shuffle(fresh_vecs)
        logger.info('Made %d fresh vectors', len(fresh_vecs))
        logger.info('Current Hull volume:  %0.2f', self.hull.cv_hull.volume)
        logger.info(
            'Current new vector rejection rate (for collinearity):  %0.2f',
            self.hull.norm_rejection_proportion,
        )
        self.load_normals(fresh_vecs)

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
        A little function to track the size of the hull, after it is built initially
        Note:  This hull is a "throw away" and only used for volume calc, but it is pretty quick
        """
        if self.hull is not None and \
           self.hull_points is not None:  # don't try until after first hull is built
            hull = Hull(self.hull_points)
            volume = hull.volume
            logger.info('Tracking hull at %0.2f', volume)
            self.perf_data.update({len(self.hull_points): volume})

    def finalize_tracker(self) -> None:
        fout = self.config.output_path / 'hull_performance.png'
        pts = sorted(self.perf_data.keys())
        y = [self.perf_data[pt] for pt in pts]
        plt.plot(pts, y)
        plt.xlabel('Iteration')
        plt.ylabel('N-Dimensional Hull Volume')
        plt.savefig(str(fout))
