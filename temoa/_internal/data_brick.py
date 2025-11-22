"""
Objective of this module is to build a lightweight container to hold a selection of model results
from a Worker process with the intent to send this back via multiprocessing queue in lieu of
sending the entire
model back (which is giant and slow).  It will probably be a "superset" of data elements required
to report for MC and MGA right now, and maybe others

"""

from temoa._internal.exchange_tech_cost_ledger import CostType
from temoa._internal.table_data_puller import (
    poll_capacity_results,
    poll_cost_results,
    poll_emissions,
    poll_flow_results,
    poll_objective,
)
from temoa.core.model import TemoaModel
from temoa.types.core_types import Period, Region, Technology, Vintage
from temoa.types.model_types import EI, FI, CapData, FlowType


class DataBrick:
    """
    A utility container for bundling assorted data structures for solved models done by Worker
    objects.
    """

    def __init__(
        self,
        name: str,
        emission_costs: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]],
        emission_flows: dict[EI, float],
        capacity_data: CapData,
        flow_data: dict[FI, dict[FlowType, float]],
        obj_data: list[tuple[str, float]],
        regular_costs: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]],
        exchange_costs: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]],
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
    def flow_data(self) -> dict[FI, dict[FlowType, float]]:
        return self._flow_data

    @property
    def obj_data(self) -> list[tuple[str, float]]:
        return self._obj_data

    @property
    def cost_data(self) -> dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]]:
        return self._regular_costs

    @property
    def exchange_cost_data(
        self,
    ) -> dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]]:
        return self._exchange_costs

    @property
    def emission_cost_data(
        self,
    ) -> dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]]:
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
