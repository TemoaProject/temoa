"""
An ABC to serve as a framework for future Vector Managers
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Iterable, Iterator, Sequence

    from temoa.core.model import TemoaModel
    from temoa.extensions.modeling_to_generate_alternatives.worker import ObjectiveJob


class VectorManager(ABC):
    base_model: TemoaModel

    @abstractmethod
    def __init__(
        self,
        conn: sqlite3.Connection,
        base_model: TemoaModel,
        optimal_cost: float,
        cost_relaxation: float,
    ) -> None:
        """
        Initialize a new manager
        :param conn: connection to the current database
        :param base_model: the base model to clone for repetitive solves
        :param optimal_cost: the optimal cost of the primal solve
        :param cost_relaxation: the proportion to relax the optimal cost
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def groups(self) -> Iterable[str]:
        """The main group labels of the axis"""
        raise NotImplementedError()

    @abstractmethod
    def group_members(self, group: str) -> list[str]:
        """The members (by string name) in the group"""
        raise NotImplementedError()

    @property
    @abstractmethod
    def expired(self) -> bool:
        """
        Indicator that this manager has no more vectors to generate
        :return: True if expired
        """
        raise NotImplementedError()

    @abstractmethod
    def group_variable_names(self, tech: str) -> list[str]:
        """The variable NAMES associated with the individual group members"""
        raise NotImplementedError()

    @abstractmethod
    def random_input_vector_model(self) -> ObjectiveJob:
        """Random objective, as coefficients of objective_terms()"""
        raise NotImplementedError()

    @abstractmethod
    def model_generator(self) -> Iterator[ObjectiveJob | None]:
        """
        generator for the objectives to be solved on the base model, as coefficients of
        objective_terms(); None when no new objective is available until more results arrive
        """
        raise NotImplementedError('the manager subclass must implement instance_generator')

    @abstractmethod
    def objective_terms(self) -> list[tuple[str, Any, float]]:
        """The (variable name, index, weight) of each objective coefficient, in order"""
        raise NotImplementedError

    @abstractmethod
    def process_results(self, model: TemoaModel) -> Any:
        raise NotImplementedError('the manager subclass must implement process_results')

    @abstractmethod
    def hull_point_terms(self) -> list[list[tuple[str, Any, float]]]:
        """
        The terms of each coordinate of a hull point, as (variable name, index, coefficient), so
        that worker processes can compute the hull point of the models they solve
        """
        raise NotImplementedError

    @abstractmethod
    def add_hull_point(self, point: Sequence[float]) -> None:
        """Add the hull point of a solved model"""
        raise NotImplementedError

    @abstractmethod
    def finalize_tracker(self) -> None:
        """Finalize any tracker employed by the manager"""
        pass
