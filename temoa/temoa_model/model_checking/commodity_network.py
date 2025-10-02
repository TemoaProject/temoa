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
Created on:  3/11/24

"""

from collections import defaultdict
from itertools import chain
from logging import getLogger

from temoa.temoa_model.model_checking.network_model_data import NetworkModelData, Tech

logger = getLogger(__name__)


class CommodityNetwork:
    """
    class to hold the network for a particular region/period.  Note that the commodity network here is blind
    to vintage.  Determining whether a connection is valid/invalid is independent of vintage or how many
    vintages are represented.  It is the responsibility of the commodity network manager to use these
    determinations correctly across available vintages
    """

    def __init__(self, region, period: int, model_data: NetworkModelData):
        """
        make the network
        :param region: region
        :param period: period
        :param model_data: a NetworkModelData object
        """
        # check the marking of source commodities first, as the db may not be configured for source check...
        self.model_data = model_data
        if not self.model_data.source_commodities:
            logger.error(
                'No source commodities discovered when initializing Commodity Network.  '
                'Have source commodities been identified in commodities '
                "table with 's'?"
            )
            raise ValueError(
                'Attempted to do source trace with no source commodities marked.  '
                'Have source commodities been identified in commodities '
                "table with 's'?"
            )
        self.demand_orphans: set[tuple] = set()
        self.other_orphans: set[tuple] = set()
        self.good_connections: set[tuple] = set()
        self.region = region
        self.period = period
        # the cataloguing of inputs/outputs by tech is needed for implicit links like via emissions in LinkedTech
        self.tech_inputs: dict[str, set[str]] = defaultdict(set)
        self.tech_outputs: dict[str, set[str]] = defaultdict(set)
        self.connections: dict[str, set[tuple[str, str]]] = defaultdict(set)
        """All connections in the model {oc: {(ic, tech), ...}}"""

        self.viable_linked_tech: set[tuple[str, str]] = set()  # name-name pairings

        self.orig_connex: set[tuple] = set()

        if not self.model_data.demand_commodities[self.region, self.period]:
            raise ValueError(
                f'No demand commodities discovered in region {self.region} period {self.period}.  Check '
                f'Demand table data'
            )
        # dev note:  This code was originally designed/tested to run on tuples of (ic, tech_name, oc)
        #            since the implementation of Tech named tuple, we could switch over to that soon,
        #            but it will be work to re-work the tests.  The networks are smaller this way
        #            because of reduced redundant links for multi-vintages, but we will have to
        #            filter the Tech tuples for output generation against the names...

        # scan techs for this r, p
        for tech in self.model_data.available_techs[self.region, self.period]:
            self.connections[tech.oc].add((tech.ic, tech.name))
            self.tech_inputs[tech.name].add(tech.ic)
            self.tech_outputs[tech.name].add(tech.oc)

        # make synthetic connection between linked techs
        self.prescreen_linked_tech()

    def remove_tech_by_name(self, tech_name: str) -> None:
        """
        Remove a tech by name from the network
        :param tech_name: The string name of the tech
        :return:
        """
        # remove from data sources
        self.tech_inputs.pop(tech_name, None)
        self.tech_outputs.pop(tech_name, None)

        removed = set()
        for oc, s in self.connections.items():
            removals = set()
            for ic, name in s:
                if name == tech_name:  # we found a reference
                    removals.add((ic, name))
                    removed.add((ic, tech_name, oc))
            s -= removals  # take out all the removals from the connection
        # add every removed tech to the orphan list, so it can be processed by the manager
        for r in removed:
            self.other_orphans.add(r)
            logger.debug('removed %s with a by-name removal', r)

    def reload(self, connections: set[Tech]):
        """
        reload the network model with a new set of connections and clear existing ones
        :param connections: a set of connections (Techs) to evaluate
        :return: None
        """
        self.tech_inputs.clear()
        self.tech_outputs.clear()
        self.connections.clear()
        self.orig_connex.clear()
        # reload 'em
        for tech in connections:
            self.connections[tech.oc].add((tech.ic, tech.name))
            self.tech_inputs[tech.name].add(tech.ic)
            self.tech_outputs[tech.name].add(tech.oc)

    def get_valid_tech(self) -> set[Tech]:
        return {
            tech
            for tech in self.model_data.available_techs[self.region, self.period]
            if (tech.ic, tech.name, tech.oc) in self.good_connections
        }

    def get_demand_side_orphans(self) -> set[Tech]:
        return {
            tech
            for tech in self.model_data.available_techs[self.region, self.period]
            if (tech.ic, tech.name, tech.oc) in self.demand_orphans
        }

    def get_other_orphans(self) -> set[Tech]:
        return {
            tech
            for tech in self.model_data.available_techs[self.region, self.period]
            if (tech.ic, tech.name, tech.oc) in self.other_orphans
        }

    def prescreen_linked_tech(self):
        """Screen the linked tech to ensure both members of the available link are available.  If not, remove strays"""

        for r, driver, emission, driven in self.model_data.available_linked_techs:
            if r == self.region:
                # check that the driver & driven techs both exist...  we only check by NAME for LinkedTech
                if driver in self.tech_outputs and driven in self.tech_outputs:  # we're gtg.
                    logger.debug(
                        'Both %s and %s are available in region %s, period %s to establish link',
                        driver,
                        driven,
                        self.region,
                        self.period,
                    )
                    self.viable_linked_tech.add((driver, driven))

                # else, document errors in linkage...
                elif driver not in self.tech_outputs and driven not in self.tech_outputs:
                    # neither tech is present, not a problem
                    logger.debug(
                        'Note (no action reqd.):  Neither linked tech %s nor %s are active in region %s, period %s',
                        driver,
                        driven,
                        self.region,
                        self.period,
                    )
                elif driver in self.tech_outputs and driven not in self.tech_outputs:
                    logger.info(
                        'No driven linked tech available for driver %s in region %s, period %d.  '
                        'Driver REMOVED.',
                        driver,
                        self.region,
                        self.period,
                    )
                    self.remove_tech_by_name(driver)
                else:  # ... only the driven tech is present
                    logger.warning(
                        'Driven linked tech %s is not connected to an active or available '
                        'driver in region %s, period %d.  Driven tech REMOVED.',
                        driven,
                        self.region,
                        self.period,
                    )
                    self.remove_tech_by_name(driven)

    def analyze_network(self):
        # Due to fact that each "scan" is static, we may discover that only 1 member of a linked tech
        # is viable.  IF that happens, we need to remove the partner and go again.  In a bizarre situation,
        # this may be an iterative process, so we might as well do it till done...
        done = False
        demand_side_connections = set()
        while not done:
            done = True  # assume the best!
            # dev note:  send a copy of connections...
            # it is consumed by the function.  (easier than managing it in the recursion)
            discovered_sources, demand_side_connections = _visited_dfs(
                self.model_data.demand_commodities[self.region, self.period] | self.model_data.waste_commodities[self.region, self.period],
                self.model_data.source_commodities[self.region, self.period],
                self.connections.copy(),
            )
            self.good_connections = _mark_good_connections(
                good_ic=discovered_sources, connections=demand_side_connections.copy()
            )
            observed_tech = {tech for (ic, tech, oc) in self.good_connections}
            sour_links = set()
            for link in self.viable_linked_tech:
                if not all((link[0] in observed_tech, link[1] in observed_tech)):
                    sour_links.add(link)
                    self.remove_tech_by_name(link[0])
                    self.remove_tech_by_name(link[1])
                    done = False
                    logger.warning(
                        'Both members of link %s are not valid in the network.  Both members REMOVED in region %s, period %s',
                        link,
                        self.region,
                        self.period,
                    )
            self.viable_linked_tech -= sour_links

        logger.debug(
            'Got %d good technologies (possibly multi-vintage) from %d techs in region %s, period %d',
            len(self.good_connections),
            len(tuple(chain(*self.connections.values()))),
            self.region,
            self.period,
        )

        # Sort out the demand-side and supply-side orphans
        # Now we should have:
        # 1.  The original connections
        # 2.  The demand-side connections from the first search (all things backward from Demands)
        # 3.  The "good" connections that have full linkage from source back to demand

        # So we can infer (these are set operations):
        # 4.  demand-side orphans = demand_side_connections - good_connections
        # 5.  other orphans = original_connections - demand_side_connections - good_connections

        # flat lists are easier for comparison, so...
        self.orig_connex: set[tuple] = {
            (ic, tech, oc) for oc in self.connections for (ic, tech) in self.connections[oc]
        }
        # dev note:  recall, the demand connex are inventoried by IC for use in the 2nd search, so we need to poll by IC...
        demand_connex: set[tuple] = {
            (ic, tech, oc)
            for ic in demand_side_connections
            for (oc, tech) in demand_side_connections[ic]
        }

        self.demand_orphans = demand_connex - self.good_connections
        # we may already have some removed things in "other orphans" so add to it...
        self.other_orphans |= self.orig_connex - demand_connex - self.good_connections

        if self.other_orphans:
            logger.info(
                'Source tracing revealed %d "other" (non-demand) orphaned processes in region %s, period %d.',
                len(self.other_orphans),
                self.region,
                self.period,
            )
            for orphan in sorted(self.other_orphans, key=lambda x: x[1]):
                logger.info(
                    'Discovered orphaned process:   %s in region %s, period %d',
                    orphan,
                    self.region,
                    self.period,
                )
        if self.demand_orphans:
            logger.info(
                'Source tracing revealed %d demand-side orphaned processes in region %s, period %d.',
                len(self.demand_orphans),
                self.region,
                self.period,
            )
            for orphan in sorted(self.demand_orphans, key=lambda x: x[1]):
                logger.info(
                    'Discovered orphaned process:   %s in region %s, period %d',
                    orphan,
                    self.region,
                    self.period,
                )

    def unsupported_demands(self) -> set[str]:
        """
        Look for demand commodities that are not connected via a "good connection"
        :return: set of improperly supported demands
        """
        supported_demands = {t[2] for t in self.good_connections}
        bad_demands = {
            d
            for d in self.model_data.demand_commodities[self.region, self.period]
            if d not in supported_demands
        }
        return bad_demands


def _mark_good_connections(
    good_ic: set[str], connections: dict[str, set[tuple]], start: str | None = None
) -> set[tuple]:
    """
    Now that we have ID'ed the good ic that have been discovered, we need to work back up
    the chain of visited nodes to identify the good connections (this is the reverse of the
    previous search where we looked backward from demand.  Here we look up from the Input Commodities
    :param start: The current node to start from
    :param good_ic: The set of Input Commodities that were discovered by the first search
    :param connections:  The set of connections to analyze.  It is consumed by the function via pop()
    :return:
    """

    # end conditions...
    if not good_ic and not start:  # nothing to discover
        return set()
    else:
        good_connections = set()

    if not start:
        for start in good_ic:
            good_connections |= _mark_good_connections(good_ic, connections, start=start)

    # recurse...
    for oc, tech in connections.pop(start, []):  # prevent re-expanding this later by popping
        good_connections.add((start, tech, oc))
        # explore all upstream
        good_connections |= _mark_good_connections(
            good_ic=good_ic, connections=connections, start=oc
        )
    return good_connections


def _visited_dfs(
    start_nodes: set[str],
    end_nodes: set[str],
    connections: dict[str, set[tuple]],
    current_start=None,
) -> tuple[set, dict[str, set[tuple]]]:
    """
    recursive depth-first search to identify discovered source nodes and connections from
    a start point and set of connections
    :param start_nodes: the set of demand commodities (oc ∈ demand)
    :param end_nodes: source nodes, or ones traceable to source nodes
    :param connections: the connections to explore {output: {(ic, tech)}}
    :param current_start: the current node (ic) index
    :return: the set of viable tech tuples (ic, tech, oc)
    """
    # setup...
    discovered_sources = set()
    visited = defaultdict(set)

    # end conditions...
    if not current_start and not start_nodes:  # no more starts, we're done
        return set(), dict()
    if not current_start:  # start from each node in the starts
        for node in start_nodes:
            ds, v = _visited_dfs(
                start_nodes=start_nodes,
                end_nodes=end_nodes,
                connections=connections,
                current_start=node,
            )
            discovered_sources.update(ds)
            for k in v:
                visited[k].update(v[k])
        return discovered_sources, visited

    # we have a start node, dig from here.
    for ic, tech in connections.pop(current_start, []):  # we can pop, no need to re-explore
        visited[ic].add((current_start, tech))
        if ic in end_nodes:  # we have struck gold
            # add the current ic to discoveries
            discovered_sources.add(ic)
        else:
            # explore from here
            ds, v = _visited_dfs(
                start_nodes,
                end_nodes,
                connections,
                current_start=ic,
            )
            discovered_sources.update(ds)
            for k in v:
                visited[k].update(v[k])
    return discovered_sources, visited
