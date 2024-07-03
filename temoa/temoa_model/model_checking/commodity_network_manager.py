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

This module is responsible for running the network analysis and generating the filters
that can be used to filter down the data to valid data.  It uses the NetworkModelData
and subdivides this into regions and periods and analyzes each one.

"""

from collections import defaultdict
from logging import getLogger
from typing import Iterable

from temoa.temoa_model.model_checking.commodity_graph import generate_graph
from temoa.temoa_model.model_checking.commodity_network import CommodityNetwork
from temoa.temoa_model.model_checking.element_checker import ViableSet
from temoa.temoa_model.model_checking.network_model_data import NetworkModelData, Tech
from temoa.temoa_model.temoa_config import TemoaConfig

logger = getLogger(__name__)


class CommodityNetworkManager:
    """Manager to run the network analysis recursively for a region and set of periods"""

    def __init__(self, periods: Iterable[str | int], network_data: NetworkModelData):
        self.regions = None
        self.analyzed = False
        self.periods = sorted(periods)
        self.orig_data = network_data
        self.filtered_data: NetworkModelData | None = None

        # outputs / saves for graphing networks
        # orig_tech is saved copy of the links for graphing purposes
        # this is a quick "deep copy"
        self.orig_tech = {k: v.copy() for k, v in network_data.available_techs.items()}
        self.demand_orphans: dict[tuple[str, str], set[Tech]] = defaultdict(set)
        self.other_orphans: dict[tuple[str, str], set[Tech]] = defaultdict(set)

    def _analyze_region(self, region: str, data: NetworkModelData):
        """
        Iteratively whittle away at the region, within the window until no new invalid techs appear

        Note:  this is done in a "while" loop because actions taken in one particular period *might*
        have repercussions in another period.  For instance, if a tech is deemed an "orphan" in
        period 5 and needs to be removed, but it was alive in periods 1-4, those periods now need to
        be re-analyzed post-removal.  In practice, this seems to work very quickly with few iterations, but some
        datasets with complex lifetime relationships between dependent techs and few alternative
        vintages or such may take a few iterations to clean.
        """
        done = False
        iter_count = 0

        while not done:
            iter_count += 1
            demand_orphans_this_pass: set[Tech] = set()
            other_orphans_this_pass: set[Tech] = set()
            for period in self.periods:
                cn = CommodityNetwork(region=region, period=period, model_data=data)
                cn.analyze_network()

                # check for unsupported demands..
                unsupported_demands = cn.unsupported_demands()
                for commodity in unsupported_demands:
                    logger.error(
                        'Demand %s is not supported back to source commodities in region %s period %d',
                        commodity,
                        cn.region,
                        cn.period,
                    )

                # gather orphans...
                new_demand_orphans = cn.get_demand_side_orphans()
                new_other_orphans = cn.get_other_orphans()

                # add the orphans to the orphanages...
                self.demand_orphans[region, period] |= new_demand_orphans
                self.other_orphans[region, period] |= new_other_orphans

                # add them to the collections for the "pass"
                demand_orphans_this_pass |= new_demand_orphans
                other_orphans_this_pass |= new_other_orphans

            # clean up the good tech listing and decide whether to go again...
            # dev note:  we could clean up the good techs in the loop, before processing next period, but
            #            by doing it this way, we properly capture full set of orphans by period/region
            #            for later use
            for period in self.periods:
                # any orphans need to be removed from all periods where they exist
                data.available_techs[region, period] -= demand_orphans_this_pass
                data.available_techs[region, period] -= other_orphans_this_pass

            done = not demand_orphans_this_pass and not other_orphans_this_pass
            logger.debug(
                'Finished %d pass(es) on region %s during removal of orphan techs',
                iter_count,
                region,
            )
            logger.debug(
                'Removed %d orphans', len(demand_orphans_this_pass) + len(other_orphans_this_pass)
            )
            for orphan in sorted(demand_orphans_this_pass):
                logger.warning('Removed %s as demand-side orphan', orphan)
            for orphan in sorted(other_orphans_this_pass):
                logger.warning('Removed %s as other orphan', orphan)

    def analyze_network(self) -> bool:
        """
        Analyze all regions in the model, excluding exchanges
        :return: True if all regions come back "clean" (no orphans), False otherwise
        """
        # NOTE:  by excluding '-' regions, we are deciding NOT to screen any regional exchange techs,
        #        which would be a whole different level of difficulty to do.

        self.filtered_data = self.orig_data.clone()
        self.regions = {r for (r, p) in self.orig_data.available_techs if '-' not in r}
        for region in self.regions:
            logger.info('starting network analysis for region %s', region)
            self._analyze_region(region, data=self.filtered_data)
        self.analyzed = True
        orphans_found = any(self.demand_orphans.values()) or any(self.other_orphans.values())
        return not orphans_found

    def build_filters(self) -> dict[str, ViableSet]:
        """populate the filters from the data, after network analysis"""
        if not self.analyzed:
            raise RuntimeError('Trying to build filters before network analysis.  Code error')
        valid_ritvo = set()
        valid_rtv = set()
        valid_rt = set()
        valid_rpit = set()
        valid_rpto = set()
        valid_t = set()
        valid_input_commodities = set()
        valid_output_commodities = set()
        valid_vintages = set()
        for r, p in self.filtered_data.available_techs:
            for tech in self.filtered_data.available_techs[r, p]:
                valid_ritvo.add((tech.region, tech.ic, tech.name, tech.vintage, tech.oc))
                valid_rtv.add((tech.region, tech.name, tech.vintage))
                valid_rt.add((tech.region, tech.name))
                valid_rpit.add((tech.region, p, tech.ic, tech.name))
                valid_rpto.add((tech.region, p, tech.name, tech.oc))
                valid_t.add(tech.name)
                valid_input_commodities.add(tech.ic)
                valid_output_commodities.add(tech.oc)
                valid_vintages.add(tech.vintage)

        filts = {
            'ritvo': ViableSet(
                elements=valid_ritvo, exception_loc=0, exception_vals=ViableSet.REGION_REGEXES
            ),
            'rtv': ViableSet(
                elements=valid_rtv, exception_loc=0, exception_vals=ViableSet.REGION_REGEXES
            ),
            'rt': ViableSet(
                elements=valid_rt, exception_loc=0, exception_vals=ViableSet.REGION_REGEXES
            ),
            'rpit': ViableSet(valid_rpit, exception_loc=0, exception_vals=ViableSet.REGION_REGEXES),
            'rpto': ViableSet(valid_rpto, exception_loc=0, exception_vals=ViableSet.REGION_REGEXES),
            't': ViableSet(elements=valid_t),
            'v': ViableSet(elements=valid_vintages),
            'ic': ViableSet(elements=valid_input_commodities),
            'oc': ViableSet(elements=valid_output_commodities),
        }
        return filts

    def analyze_graphs(self, config: TemoaConfig):
        if not self.analyzed:
            raise RuntimeError(
                'Trying to build/analyze graphs before network analysis.  Code error'
            )
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
