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
Created on:  4/15/24

An ABC to serve as a framework for future Vector Managers
"""

import sqlite3
from abc import ABC, abstractmethod
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
    ):
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
    def group_members(self, group) -> list[str]:
        """The members (by string name) in the group"""
        raise NotImplementedError()

    @property
    @abstractmethod
    def expired(self) -> bool:
        """
        Indicator that this manager has no more vectors to generate
        :return: True if expired
        """

    @abstractmethod
    def group_variable_names(self, tech) -> list[str]:
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
    def process_results(self, M: TemoaModel):
        raise NotImplementedError('the manager subclass must implement process_results')

    @abstractmethod
    def finalize_tracker(self):
        """Finalize any tracker employed by the manager"""
        pass
