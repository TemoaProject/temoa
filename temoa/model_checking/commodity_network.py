"""
This module provides the CommodityNetwork class, a tool for analyzing and
validating the structure of an energy system model for a specific region
and time period within the Temoa framework.

The primary purpose is to perform a "source trace" analysis to ensure that all
technologies supplying a demand are fully connected back to a designated source
commodity (e.g., crude oil, natural gas, solar radiation). This process
identifies two types of modeling errors:
1.  Demand-Side Orphans: Technologies that are part of a chain serving a demand
    but are not connected to a valid source.
2.  Other Orphans: Technologies that are not connected to any demand chain at all.

The analysis is performed using a depth first search on a directed graph where
commodities are nodes and technologies are edges.
"""

from collections import defaultdict
from logging import getLogger

from temoa.model_checking.network_model_data import EdgeTuple, NetworkModelData
from temoa.types.core_types import Commodity, Period, Region, Technology

logger = getLogger(__name__)

# Represents a technology link: (input_commodity, tech_name)
type TechLink = tuple[Commodity, Technology]
# Represents a pair of linked technologies: (driver_tech, driven_tech)
type LinkedTechPair = tuple[Technology, Technology]
# Represents a full connection: (input_commodity, tech_name, output_commodity)
type TechConnection = tuple[Commodity, Technology, Commodity]
# Adjacency dict mapping: {output_comm: set of (input_comm, tech_name)}
type ForwardConnections = dict[Commodity, set[TechLink]]
# Adjacency dict mapping: {input_comm: set of (output_comm, tech_name)}
type ReverseConnections = dict[Commodity, set[TechLink]]


class CommodityNetwork:
    """
    Holds and analyzes the commodity-technology network for a specific region and period.

    This class is blind to vintage; it determines network validity based on connections
    independent of vintage. It is the responsibility of the manager to apply these
    findings across available vintages.
    """

    def __init__(self, region: Region, period: Period, model_data: NetworkModelData) -> None:
        """
        Initializes and builds the network for a given region and period.

        :param region: The region to analyze.
        :param period: The period to analyze.
        :param model_data: A NetworkModelData object containing all model connections.
        """
        self.region = region
        self.period = period
        self.model_data = model_data

        if not self.model_data.source_commodities:
            msg = (
                "No source commodities found. Have they been marked with 's' "
                'in the commodities table?'
            )
            logger.error(msg)
            raise ValueError(msg)

        if not self.model_data.demand_commodities[self.region, self.period]:
            msg = (
                f'No demand commodities discovered in region {self.region} '
                f'period {self.period}. Ignore this if this was intentional.'
            )
            logger.info(msg)

        # Final results of the analysis
        self.good_connections: set[TechConnection] = set()
        self.demand_orphans: set[TechConnection] = set()
        self.other_orphans: set[TechConnection] = set()

        # Internal state for the analysis
        self.tech_inputs: dict[Technology, set[Commodity]] = defaultdict(set)
        self.tech_outputs: dict[Technology, set[Commodity]] = defaultdict(set)
        self.connections: ForwardConnections = defaultdict(set)
        self.viable_linked_tech: set[LinkedTechPair] = set()

        self._load_connections()
        self.prescreen_linked_tech()

    def _load_connections(self) -> None:
        """Populate internal connection structures from model_data."""
        self.tech_inputs.clear()
        self.tech_outputs.clear()
        self.connections.clear()

        edge_tuples = self.model_data.available_techs[self.region, self.period]
        for edge_tuple in edge_tuples:
            self.connections[edge_tuple.output_comm].add((edge_tuple.input_comm, edge_tuple.tech))
            self.tech_inputs[edge_tuple.tech].add(edge_tuple.input_comm)
            self.tech_outputs[edge_tuple.tech].add(edge_tuple.output_comm)

    def reload(self, connections: set[EdgeTuple]) -> None:
        """
        Reload the network model with a new set of connections.

        :param connections: A set of connections (Tech objects) to evaluate.
        """
        # Overwrite the model data's available techs for this region/period
        self.model_data.available_techs[self.region, self.period] = connections
        # Clear all existing state and reload
        self.good_connections.clear()
        self.demand_orphans.clear()
        self.other_orphans.clear()
        self.viable_linked_tech.clear()
        self._load_connections()

    def remove_tech_by_name(self, tech_name: Technology) -> None:
        """Remove all connections associated with a given technology name."""
        self.tech_inputs.pop(tech_name, None)
        self.tech_outputs.pop(tech_name, None)

        removed_connections: set[TechConnection] = set()
        # Use list() to avoid issues with modifying the dict during iteration
        for oc, links in list(self.connections.items()):
            removals = {link for link in links if link[1] == tech_name}
            if removals:
                links -= removals
                for ic, name in removals:
                    removed_connections.add((ic, name, oc))
            if not links:
                self.connections.pop(oc, None)

        self.other_orphans.update(removed_connections)
        for r in removed_connections:
            logger.debug('Removed %s via by-name removal', r)

    def prescreen_linked_tech(self) -> None:
        """
        Screen linked techs to ensure both members of a pair are available.
        If not, the stray member is removed from the network analysis.
        """
        for r, driver, _, driven in self.model_data.available_linked_techs:
            if r == self.region:
                driver_exists = driver in self.tech_outputs
                driven_exists = driven in self.tech_outputs

                if driver_exists and driven_exists:
                    logger.debug(
                        'Both %s and %s are available in region %s, period %s to establish link',
                        driver,
                        driven,
                        self.region,
                        self.period,
                    )
                    self.viable_linked_tech.add((driver, driven))
                elif driver_exists and not driven_exists:
                    logger.info(
                        'No driven linked tech for driver %s in region %s, period %s. Driver '
                        'REMOVED.',
                        driver,
                        self.region,
                        self.period,
                    )
                    self.remove_tech_by_name(driver)
                elif not driver_exists and driven_exists:
                    logger.warning(
                        'Driven linked tech %s has no active driver in region %s, period %s. '
                        'Driven tech REMOVED.',
                        driven,
                        self.region,
                        self.period,
                    )
                    self.remove_tech_by_name(driven)

    def analyze_network(self) -> None:
        """
        Analyzes the network to find valid and orphaned connections.

        This process may be iterative if linked technologies are found to be invalid,
        as removing one requires removing its partner and re-running the analysis.
        """
        while True:
            demand_nodes = (
                self.model_data.demand_commodities[self.region, self.period]
                | self.model_data.waste_commodities[self.region, self.period]
            )
            source_nodes = self.model_data.source_commodities[self.region, self.period]

            (
                discovered_sources,
                reverse_connex,
            ) = self._trace_backward_from_demands(
                start_nodes=demand_nodes,
                end_nodes=source_nodes,
                connections=self.connections,
            )

            self.good_connections = self._trace_forward_from_sources(
                start_nodes=discovered_sources, connections=reverse_connex
            )

            observed_tech_names = {tech for _, tech, _ in self.good_connections}
            sour_links = {
                link
                for link in self.viable_linked_tech
                if not (link[0] in observed_tech_names and link[1] in observed_tech_names)
            }

            if not sour_links:
                break  # Analysis is stable, exit loop.

            for driver, driven in sour_links:
                logger.warning(
                    'Both members of link (%s, %s) are not valid. Removing both in region %s, '
                    'period %s.',
                    driver,
                    driven,
                    self.region,
                    self.period,
                )
                self.remove_tech_by_name(driver)
                self.remove_tech_by_name(driven)
            self.viable_linked_tech -= sour_links

        all_connections = {
            (ic, name, oc) for oc, links in self.connections.items() for ic, name in links
        }
        demand_reachable_connections = {
            (ic, name, oc) for ic, links in reverse_connex.items() for oc, name in links
        }

        self.demand_orphans = demand_reachable_connections - self.good_connections
        self.other_orphans |= all_connections - demand_reachable_connections

        self._log_orphans()

    def _trace_backward_from_demands(
        self,
        start_nodes: set[Commodity],
        end_nodes: set[Commodity],
        connections: ForwardConnections,
    ) -> tuple[set[Commodity], ReverseConnections]:
        """Iterative DFS tracing backward from demand nodes."""
        stack = list(start_nodes)
        visited_nodes = set()
        discovered_sources = set()
        reachable_subgraph: ReverseConnections = defaultdict(set)

        while stack:
            current_oc = stack.pop()
            if current_oc in visited_nodes:
                continue
            visited_nodes.add(current_oc)

            for ic, tech in connections.get(current_oc, set()):
                reachable_subgraph[ic].add((current_oc, tech))
                if ic in end_nodes:
                    discovered_sources.add(ic)
                if ic not in visited_nodes:
                    stack.append(ic)

        return discovered_sources, reachable_subgraph

    def _trace_forward_from_sources(
        self, start_nodes: set[Commodity], connections: ReverseConnections
    ) -> set[TechConnection]:
        """Iterative DFS tracing forward from discovered source nodes."""
        stack = list(start_nodes)
        visited_nodes = set(start_nodes)
        good_connections: set[TechConnection] = set()

        while stack:
            current_ic = stack.pop()

            for oc, tech in connections.get(current_ic, set()):
                good_connections.add((current_ic, tech, oc))
                if oc not in visited_nodes:
                    visited_nodes.add(oc)
                    stack.append(oc)

        return good_connections

    def _log_orphans(self) -> None:
        """Helper to log discovered orphaned processes."""
        if self.other_orphans:
            logger.info(
                "Source tracing revealed %s 'other' (non-demand) orphaned processes in region %s, "
                'period %s.',
                len(self.other_orphans),
                self.region,
                self.period,
            )
            for orphan in sorted(self.other_orphans, key=lambda x: x[1]):
                logger.info('Discovered orphaned process:   %s', orphan)

        if self.demand_orphans:
            logger.info(
                'Source tracing revealed %s demand-side orphaned processes in region %s, '
                'period %s.',
                len(self.demand_orphans),
                self.region,
                self.period,
            )
            for orphan in sorted(self.demand_orphans, key=lambda x: x[1]):
                logger.info('Discovered orphaned process:   %s', orphan)

    def get_valid_tech(self) -> set[EdgeTuple]:
        """Returns the set of Tech objects that are part of a valid connection."""
        return {
            edge_tuple
            for edge_tuple in self.model_data.available_techs[self.region, self.period]
            if (edge_tuple.input_comm, edge_tuple.tech, edge_tuple.output_comm)
            in self.good_connections
        }

    def get_demand_side_orphans(self) -> set[EdgeTuple]:
        """Returns Tech objects for demand-side orphans."""
        return {
            edge_tuple
            for edge_tuple in self.model_data.available_techs[self.region, self.period]
            if (edge_tuple.input_comm, edge_tuple.tech, edge_tuple.output_comm)
            in self.demand_orphans
        }

    def get_other_orphans(self) -> set[EdgeTuple]:
        """Returns Tech objects for non-demand-side orphans."""
        return {
            edge_tuple
            for edge_tuple in self.model_data.available_techs[self.region, self.period]
            if (edge_tuple.input_comm, edge_tuple.tech, edge_tuple.output_comm)
            in self.other_orphans
        }

    def unsupported_demands(self) -> set[Commodity]:
        """
        Finds demand commodities that are not supplied by any valid connection.

        :return: A set of unsupported demand commodity names.
        """
        supported_demands = {oc for (_, _, oc) in self.good_connections}
        all_demands = self.model_data.demand_commodities[self.region, self.period]
        return all_demands - supported_demands
