"""

The purpose of this module is to provide a ledger for all costs for exchange techs.  The main reason
for the need is that in many cases, the costs need to be apportioned by use ratio so it is helpful to
separately gather all of the costs and then use a usage ratio to generate entries when asked for

"""

from collections import defaultdict
from enum import Enum, unique
from typing import TYPE_CHECKING, Union, cast

from pyomo.common.numeric_types import value

from temoa.core.model import TemoaModel
from temoa.types.core_types import Period, Technology, Vintage

if TYPE_CHECKING:
    from tests.utilities.namespace_mock import Namespace


@unique
class CostType(Enum):
    INVEST = 1
    FIXED = 2
    VARIABLE = 3
    EMISS = 4
    D_INVEST = 5
    D_FIXED = 6
    D_VARIABLE = 7
    D_EMISS = 8


class ExchangeTechCostLedger:
    def __init__(self, model: Union[TemoaModel, 'Namespace']) -> None:
        self.cost_records: dict[CostType, dict[tuple[str, str, str, int, int], float]] = (
            defaultdict(dict)
        )
        # could be a Namespace for testing purposes...  See the related test
        self.M = model

    def add_cost_record(
        self,
        link: str,
        period: Period,
        tech: Technology,
        vintage: Vintage,
        cost: float,
        cost_type: CostType,
    ) -> None:
        """
        add a cost associated with an exchange tech
        :return:
        """
        r1, r2 = link.split('-')
        if not r1 and r2:
            raise ValueError(f'problem splitting region-region: {link}')
        # add to the "seen" records for appropriate cost type
        self.cost_records[cost_type][r1, r2, tech, vintage, period] = cost

    def get_use_ratio(
        self, exporter: str, importer: str, period: Period, tech: Technology, vintage: Vintage
    ) -> float:
        """
        use flow to calculate the use ratio for these 2 entities for cost apportioning purposes
        :param exporter:
        :param importer:
        :param period:
        :param tech:
        :param vintage:
        :return: the proportion to assign to the IMPORTER, or 0.5 if no usage
        """
        # Cast to TemoaModel for type checking - at runtime this will be either TemoaModel or Namespace
        # Both have the same attributes, but mypy doesn't know about Namespace's dynamic attributes
        model = cast(TemoaModel, self.M)
        # need to temporarily reconstitute the names
        rr1 = '-'.join([exporter, importer])
        rr2 = '-'.join([importer, exporter])
        if any(
            (
                period >= vintage + value(model.LifetimeProcess[rr1, tech, vintage]),
                period >= vintage + value(model.LifetimeProcess[rr2, tech, vintage]),
                period < vintage,
            )
        ):
            raise ValueError('received a bogus cost for an illegal period.')
        if tech not in model.tech_annual:
            act_dir1 = value(
                sum(
                    model.V_FlowOut[rr1, period, s, d, S_i, tech, vintage, S_o]
                    for s in model.TimeSeason[period]
                    for d in model.time_of_day
                    for S_i in model.processInputs[rr1, period, tech, vintage]
                    for S_o in model.processOutputsByInput[rr1, period, tech, vintage, S_i]
                )
            )
            act_dir2 = value(
                sum(
                    model.V_FlowOut[rr2, period, s, d, S_i, tech, vintage, S_o]
                    for s in model.TimeSeason[period]
                    for d in model.time_of_day
                    for S_i in model.processInputs[rr2, period, tech, vintage]
                    for S_o in model.processOutputsByInput[rr2, period, tech, vintage, S_i]
                )
            )
        else:
            act_dir1 = value(
                sum(
                    model.V_FlowOutAnnual[rr1, period, S_i, tech, vintage, S_o]
                    for S_i in model.processInputs[rr1, period, tech, vintage]
                    for S_o in model.processOutputsByInput[rr1, period, tech, vintage, S_i]
                )
            )
            act_dir2 = value(
                sum(
                    model.V_FlowOutAnnual[rr2, period, S_i, tech, vintage, S_o]
                    for S_i in model.processInputs[rr2, period, tech, vintage]
                    for S_o in model.processOutputsByInput[rr2, period, tech, vintage, S_i]
                )
            )

        if act_dir1 + act_dir2 > 0:
            return act_dir1 / (act_dir1 + act_dir2)
        return 0.5

    def get_entries(self) -> dict[tuple[str, int, str, int], dict[CostType, float]]:
        region_costs: dict[tuple[str, int, str, int], dict[CostType, float]] = defaultdict(dict)
        # iterate through each region pairing, pull the cost records and decide if/how to split each one
        for cost_type in self.cost_records:
            # make a copy, this will be destructive operation
            records = self.cost_records[cost_type].copy()
            while records:
                (r1, r2, tech, vintage, period), cost = records.popitem()  # pops a random item
                # try to get the partner (reversed regions), if it exists
                partner_cost = records.pop((r2, r1, tech, vintage, period), None)
                if (
                    partner_cost
                ):  # they are both entered, so we just record the costs... no splitting
                    region_costs[r2, period, tech, vintage].update({cost_type: cost})
                    region_costs[r1, period, tech, vintage].update({cost_type: partner_cost})
                else:
                    # only one side had costs: the signal to split based on use
                    use_ratio = self.get_use_ratio(r1, r2, period, tech, vintage)
                    # not r2 is the "importer" and that is the ratio assignment
                    region_costs[r1, period, tech, vintage].update(
                        {cost_type: cost * (1.0 - use_ratio)}
                    )
                    region_costs[r2, period, tech, vintage].update({cost_type: cost * use_ratio})

        return region_costs
