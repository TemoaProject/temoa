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
Created on:  12/5/24

Objective of this module is to build a lightweight container to hold a selection of model results from a
Worker process with the intent to send this back via multiprocessing queue in lieu of sending the entire
model back (which is giant and slow).  It will probably be a "superset" of data elements required to report
for MC and MGA right now, and maybe others

"""

from temoa.temoa_model.table_data_puller import (
    EI,
    CapData,
    poll_cost_results,
    poll_flow_results,
    poll_emissions,
    poll_objective,
    poll_capacity_results,
)
from temoa.temoa_model.temoa_model import TemoaModel


class DataBrick:
    """
    A utility container for bundling assorted data structures for solved models done by Worker objects.
    """

    def __init__(
        self,
        name,
        emission_costs,
        emission_flows,
        capacity_data,
        flow_data,
        obj_data,
        regular_costs,
        exchange_costs,
    ):
        self._name = name
        self._emission_costs = emission_costs
        self._emission_flows = emission_flows
        self._capacity_data = capacity_data
        self._flow_data = flow_data
        self._obj_data = obj_data
        self._regular_costs = regular_costs
        self._exchange_costs = exchange_costs

    @property
    def name(self) -> str:
        return self._name

    @property
    def emission_flows(self) -> dict[EI, float]:
        return self._emission_flows

    @property
    def capacity_data(self) -> CapData:
        return self._capacity_data

    @property
    def flow_data(self) -> dict:
        return self._flow_data

    @property
    def obj_data(self) -> list:
        return self._obj_data

    @property
    def cost_data(self):
        return self._regular_costs

    @property
    def exchange_cost_data(self):
        return self._exchange_costs

    @property
    def emission_cost_data(self):
        return self._emission_costs


def data_brick_factory(model: TemoaModel) -> DataBrick:
    """
    Build a data brick storage object from a model instance
    :param model: A solved model to pull data from.
    """
    name = model.name
    # process costs
    regular_costs, exchange_costs = poll_cost_results(model, p_0=None)

    # process flows
    flow_data = poll_flow_results(model)

    # process emissions
    emission_costs, emission_flows = poll_emissions(model, p_0=None)

    # poll capacity
    capacity_data = poll_capacity_results(model)

    # process objectives
    obj_data = poll_objective(model)

    db = DataBrick(
        name=name,
        emission_costs=emission_costs,
        emission_flows=emission_flows,
        capacity_data=capacity_data,
        flow_data=flow_data,
        obj_data=obj_data,
        regular_costs=regular_costs,
        exchange_costs=exchange_costs,
    )
    return db
