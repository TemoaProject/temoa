"""
This module provides the CommodityNetworkManager, which orchestrates the network
analysis across all regions and time periods of a Temoa model.

Its primary responsibility is to identify and filter out "orphaned" technologies—
those that are not part of a valid, complete supply chain from a source commodity
to a demand commodity. It iteratively analyzes the model until a stable, fully-
connected network is achieved, and then generates data filters that can be used
by other parts of the Temoa framework to ensure only valid data is used.
"""

from collections import defaultdict
from collections.abc import Iterable
from logging import getLogger
from typing import Any

from temoa.core.config import TemoaConfig
from temoa.model_checking.commodity_graph import generate_graph
from temoa.model_checking.commodity_network import CommodityNetwork
from temoa.model_checking.element_checker import ViableSet
from temoa.model_checking.network_model_data import NetworkModelData, TechTuple
from temoa.types.core_types import Period, Region

logger = getLogger(__name__)

# Type alias for clarity in dictionary keys
type RegionPeriodKey = tuple[Region, Period]


class CommodityNetworkManager:
    """
    Manages the iterative network analysis for all regions across a set of periods.
    """

    def __init__(self, periods: Iterable[str | int], network_data: NetworkModelData) -> None:
        self.analyzed: bool = False
        self.periods: list[int] = sorted(map(int, periods))
        self.orig_data: NetworkModelData = network_data
        self.filtered_data: NetworkModelData | None = None
        self.regions: set[str] | None = None

        # Store a deep copy of the original connections for graphing purposes
        self.orig_tech = {k: v.copy() for k, v in network_data.available_techs.items()}
        # Final collections of all orphans found, organized by (region, period)
        self.demand_orphans: dict[RegionPeriodKey, set[TechTuple]] = defaultdict(set)
        self.other_orphans: dict[RegionPeriodKey, set[TechTuple]] = defaultdict(set)

    def _analyze_region(self, region: Region, data: NetworkModelData) -> None:
        """
        Iteratively analyzes a region's network until no new orphans are found.

        This process is iterative because removing an orphan technology in one
        period (e.g., its last available vintage) can have cascading effects,
        potentially orphaning dependent technologies in earlier periods. The loop
        continues until a pass over all periods finds no new orphans, signifying
        a stable, valid network.
        """
        for pass_num in range(1, 100):  # Safety break after 100 iterations
            orphans_this_pass: set[TechTuple] = set()

            for period in self.periods:
                cn = CommodityNetwork(region=region, period=period, model_data=data)
                cn.analyze_network()

                # Log any demands that are not fully supported
                for commodity in cn.unsupported_demands():
                    logger.error(
                        'Demand %s is not supported back to a source in region %s, period %d',
                        commodity,
                        region,
                        period,
                    )

                # Collect newly identified orphans from this period's analysis
                new_demand_orphans = cn.get_demand_side_orphans()
                new_other_orphans = cn.get_other_orphans()

                # Add to the main collections, ensuring no duplicates
                self.demand_orphans[region, period].update(new_demand_orphans)
                self.other_orphans[region, period].update(new_other_orphans)

                orphans_this_pass.update(new_demand_orphans)
                orphans_this_pass.update(new_other_orphans)

            if not orphans_this_pass:
                logger.debug(
                    'Region %s analysis stable after %d pass(es).',
                    region,
                    pass_num - 1,
                )
                break  # Exit the loop if the network is stable

            logger.debug(
                'Pass %d for region %s: Found and removed %d orphan(s).',
                pass_num,
                region,
                len(orphans_this_pass),
            )
            for orphan in sorted(orphans_this_pass):
                logger.warning('Removing orphan across all periods: %s', orphan)

            # Remove all orphans found in this pass from all periods in the region
            for period in self.periods:
                data.available_techs[region, period] -= orphans_this_pass
        else:
            logger.error('Region %s analysis did not converge after 100 passes.', region)

    def analyze_network(self) -> bool:
        """
        Analyze all regions in the model.

        Note: By design, this excludes inter-regional exchange technologies,
        which would require a more complex, multi-region analysis.

        :return: True if the model is "clean" (no orphans found), False otherwise.
        """
        self.filtered_data = self.orig_data.clone()
        # Identify regions to analyze (excluding exchange pseudo-regions)
        self.regions = {r for (r, p) in self.orig_data.available_techs if '-' not in r}

        for region in sorted(list(self.regions)):
            logger.info('Starting network analysis for region %s', region)
            self._analyze_region(region, data=self.filtered_data)

        self.analyzed = True
        orphans_found = any(self.demand_orphans.values()) or any(self.other_orphans.values())
        return not orphans_found

    def build_filters(self) -> dict[str, ViableSet]:
        """
        Constructs ViableSet filters based on the valid technologies remaining
        after the network analysis is complete.
        """
        if not self.analyzed or self.filtered_data is None:
            raise RuntimeError('Cannot build filters before calling analyze_network().')

        # Use defaultdicts to easily collect unique elements
        valid_elements: defaultdict[str, set[Any]] = defaultdict(set)  # type: ignore [explicit-any]

        for (_r, p), techs in self.filtered_data.available_techs.items():
            if not techs:
                continue
            for tech in techs:
                valid_elements['ritvo'].add(
                    (tech.region, tech.ic, tech.name, tech.vintage, tech.oc)
                )
                valid_elements['rtv'].add((tech.region, tech.name, tech.vintage))
                valid_elements['rt'].add((tech.region, tech.name))
                valid_elements['rpit'].add((tech.region, p, tech.ic, tech.name))
                valid_elements['rpto'].add((tech.region, p, tech.name, tech.oc))
                valid_elements['t'].add(tech.name)
                valid_elements['v'].add(tech.vintage)
                valid_elements['ic'].add(tech.ic)
                valid_elements['oc'].add(tech.oc)

        return {
            'ritvo': ViableSet(
                elements=valid_elements['ritvo'],
                exception_loc=0,
                exception_vals=ViableSet.REGION_REGEXES,
            ),
            'rtv': ViableSet(
                elements=valid_elements['rtv'],
                exception_loc=0,
                exception_vals=ViableSet.REGION_REGEXES,
            ),
            'rt': ViableSet(
                elements=valid_elements['rt'],
                exception_loc=0,
                exception_vals=ViableSet.REGION_REGEXES,
            ),
            'rpit': ViableSet(
                elements=valid_elements['rpit'],
                exception_loc=0,
                exception_vals=ViableSet.REGION_REGEXES,
            ),
            'rpto': ViableSet(
                elements=valid_elements['rpto'],
                exception_loc=0,
                exception_vals=ViableSet.REGION_REGEXES,
            ),
            't': ViableSet(elements=valid_elements['t']),
            'v': ViableSet(elements=valid_elements['v']),
            'ic': ViableSet(elements=valid_elements['ic']),
            'oc': ViableSet(elements=valid_elements['oc']),
        }

    def analyze_graphs(self, config: TemoaConfig) -> None:
        """
        Generates and saves visual graphs of the network for each region and period.
        """
        if not self.analyzed or self.regions is None:
            raise RuntimeError('Cannot generate graphs before calling analyze_network().')
        for region in self.regions:
            for period in self.periods:
                generate_graph(
                    region,
                    period,
                    network_data=self.orig_data,
                    demand_orphans=self.demand_orphans[region, period],
                    other_orphans=self.other_orphans[region, period],
                    driven_techs=self.orig_data.get_driven_techs(region, period),
                    config=config,
                )
