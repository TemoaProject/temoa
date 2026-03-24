"""
An ABC to serve as a framework for future Vector Managers
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Iterable, Iterator

    from temoa.core.model import TemoaModel


class VectorManager(ABC):
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
    def random_input_vector_model(self) -> TemoaModel:
        """Random model vector for use as"""
        raise NotImplementedError()

    @abstractmethod
    def model_generator(self) -> Iterator[TemoaModel]:
        """generator for model instances to be solved"""
        raise NotImplementedError('the manager subclass must implement instance_generator')

    @abstractmethod
    def process_results(self, model: TemoaModel) -> Any:
        raise NotImplementedError('the manager subclass must implement process_results')

    @abstractmethod
    def finalize_tracker(self) -> None:
        """Finalize any tracker employed by the manager"""
        pass
