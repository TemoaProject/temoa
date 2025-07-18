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
Created on:  3/10/24

The purpose of this module is to build an Object to hold all of the network data for the entire
model in a usable format for the commodity_network_manager to use in building the individual
network.

"""

import logging
import sqlite3
from collections import defaultdict, namedtuple
from itertools import chain
from typing import Any, Self

import deprecated
from pyomo.core import ConcreteModel

from temoa.extensions.myopic.myopic_index import MyopicIndex
from temoa.temoa_model.temoa_model import TemoaModel

Tech = namedtuple('Tech', ['region', 'ic', 'name', 'vintage', 'oc'])
LinkedTech = namedtuple('LinkedTech', ['region', 'driver', 'emission', 'driven'])

logger = logging.getLogger(__name__)


class NetworkModelData:
    """A simple encapsulation of data needed for the Commodity Network"""

    def __init__(self, **kwargs):
        self.demand_commodities: dict[tuple[str, int | str], set[str]] = kwargs.get(
            'demand_commodities'
        )
        self.source_commodities: set[str] = kwargs.get('source_commodities')
        self.all_commodities: set[str] = kwargs.get('all_commodities')
        # dict of (region, period): {Tech}
        self._available_techs: dict[tuple[str, int | str], set[Tech]] = kwargs.get(
            'available_techs'
        )
        self.available_linked_techs: set[LinkedTech] = kwargs.get('available_linked_techs', set())
        # a catch-all for indicators for techs...growth potential
        # dev note:  this is indexed by tech name, and is blind to vintage.  The intended use is in the
        #            network graph, which is also blind to vintage.  So it is interpreted as "at least one"
        #            tech (and likely all) have/has this characteristic if multi-vintage
        self.tech_data: dict[str, dict[str, Any]] = defaultdict(dict)

    def clone(self) -> Self:
        """create a copy of the current"""
        return NetworkModelData(
            demand_commodities=self.demand_commodities.copy(),
            source_commodities=self.source_commodities.copy(),
            all_commodities=self.all_commodities.copy(),
            available_techs=self.available_techs.copy(),
            available_linked_techs=self.available_linked_techs.copy(),
        )

    @property
    def available_techs(self) -> dict[tuple[str, int | str], set[Tech]]:
        return self._available_techs

    @available_techs.setter
    def available_techs(self, available_techs: dict[tuple[str, int], set[Tech]]) -> None:
        # check for region violations
        for r, p in available_techs.keys():
            for tech in available_techs[r, p]:
                if tech.region != r:
                    raise ValueError(
                        f'Improperly constructed set of techs for region {r}, tech: {tech}'
                    )
        self._available_techs = available_techs

    def update_tech_data(self, tech: str, element: str, value: Any) -> None:
        """
        Update a data element for a tech
        :param tech: the tech
        :param element: the string name of the data element
        :param value: the new value
        :return:
        """
        self.tech_data[tech][element] = value

    def get_driven_techs(self, region, period) -> set[Tech]:
        """identifies all linked techs by name from the linked tech names"""
        driven_tech_names = {linked_tech.driven for linked_tech in self.available_linked_techs}
        driven_techs = {
            tech for tech in self.available_techs[region, period] if tech.name in driven_tech_names
        }
        return driven_techs

    def __str__(self):
        return (
            f'all commodities: {len(self.all_commodities)}, demand commodities: {len(self.demand_commodities)}, '
            f'source commodities: {len(self.source_commodities)},'
            f'available techs: {len(tuple(chain(*self.available_techs.values())))}, '
            f'linked techs: {len(self.available_linked_techs)}'
        )


def build(data, *args, **kwargs) -> NetworkModelData:
    builder = _get_builder(data)
    return builder(data, *args, **kwargs)


def _get_builder(data):
    if isinstance(data, TemoaModel | ConcreteModel):
        # dev note:  The built instance will be a ConcreteModel
        builder = _build_from_model
        return builder
    elif isinstance(data, sqlite3.Connection):
        builder = _build_from_db
        return builder
    else:
        raise NotImplementedError('cannot build from that type of data')


@deprecated.deprecated('no longer supported... build from db connection instead')
def _build_from_model(M: TemoaModel, myopic_index=None) -> NetworkModelData:
    """Build a NetworkModelData from a TemoaModel"""
    if myopic_index is not None:
        raise NotImplementedError('cannot build network data from model using a MyopicIndex')
    res = NetworkModelData()
    res.all_commodities = set(M.commodity_all)
    res.source_commodities = set(M.commodity_source)
    dem_com = defaultdict(set)
    for r, p, d in M.Demand:
        dem_com[r, p].add(d)
    res.demand_commodities = dem_com
    techs = defaultdict(set)
    # scan non-annual techs...
    for r, p, s, d, ic, tech, v, oc in M.activeFlow_rpsditvo:
        techs[r, p].add(Tech(r, ic, tech, v, oc))
    # scan annual techs...
    for r, p, ic, tech, v, oc in M.activeFlow_rpitvo:
        techs[r, p].add(Tech(r, ic, tech, v, oc))
    res.available_techs = techs
    linked_techs = set()
    for r, driver, emission, driven in M.LinkedTechs:
        linked_techs.add(LinkedTech(r, driver, emission, driven))
    res.available_linked_techs = linked_techs
    logger.debug('built network data: %s', res.__str__())
    return res


def _build_from_db(
    con: sqlite3.Connection, myopic_index: MyopicIndex | None = None
) -> NetworkModelData:
    """Build NetworkModelData object from a sqlite database."""
    # dev note:  sadly, this will duplicate some code, I think.  Perhaps a later refactoring can
    #            re-use some of the hybrid loader code in a clear way.  Not too much overlap, though
    res = NetworkModelData()
    cur = con.cursor()
    raw = cur.execute('SELECT Commodity.name FROM Commodity').fetchall()
    res.all_commodities = {t[0] for t in raw}
    raw = cur.execute("SELECT Commodity.name FROM Commodity WHERE flag = 's'").fetchall()
    res.source_commodities = {t[0] for t in raw}
    # use Demand to get the region, period specific demand comms
    raw = cur.execute('SELECT region, period, commodity FROM main.Demand').fetchall()
    demand_dict = defaultdict(set)
    for r, p, d in raw:
        demand_dict[r, p].add(d)
    res.demand_commodities = demand_dict
    # need lifetime to screen techs... :/
    default_lifetime = TemoaModel.default_lifetime_tech
    if not myopic_index:
        query = (
            '  SELECT main.Efficiency.region, input_comm, Efficiency.tech, Efficiency.vintage, output_comm,  '
            f'  coalesce(main.LifetimeProcess.lifetime, main.LifetimeTech.lifetime, {default_lifetime}) AS lifetime '
            '   FROM main.Efficiency '
            '    LEFT JOIN main.LifetimeProcess '
            '       ON main.Efficiency.tech = LifetimeProcess.tech '
            '       AND main.Efficiency.vintage = LifetimeProcess.vintage '
            '       AND main.Efficiency.region = LifetimeProcess.region '
            '    LEFT JOIN main.LifetimeTech '
            '       ON main.Efficiency.tech = main.LifetimeTech.tech '
            '     AND main.Efficiency.region = main.LifeTimeTech.region '
            '   JOIN TimePeriod '
            '   ON Efficiency.vintage = TimePeriod.period '
        )
    else:  # we need to pull from the MyopicEfficiency Table
        query = (
            '  SELECT main.MyopicEfficiency.region, input_comm, MyopicEfficiency.tech, MyopicEfficiency.vintage, output_comm,  '
            f'  coalesce(main.LifetimeProcess.lifetime, main.LifetimeTech.lifetime, {default_lifetime}) AS lifetime '
            '   FROM main.MyopicEfficiency '
            '    LEFT JOIN main.LifetimeProcess '
            '       ON main.MyopicEfficiency.tech = LifetimeProcess.tech '
            '       AND main.MyopicEfficiency.vintage = LifetimeProcess.vintage '
            '       AND main.MyopicEfficiency.region = LifetimeProcess.region '
            '    LEFT JOIN main.LifetimeTech '
            '       ON main.MyopicEfficiency.tech = main.LifetimeTech.tech '
            '     AND main.MyopicEfficiency.region = main.LifeTimeTech.region '
            '   JOIN TimePeriod '
            '   ON MyopicEfficiency.vintage = TimePeriod.period '
            # f'   WHERE main.MyopicEfficiency.vintage <= {myopic_index.last_demand_year}'
        )
    raw = cur.execute(query).fetchall()
    periods = cur.execute('SELECT period FROM TimePeriod').fetchall()
    # need to exclude the final year which is a non-demand year and should have no tech data
    # This ensures that the periods in this will match the periods in the hybrid loader.
    periods = [t[0] for t in sorted(periods)[:-1]]
    # filter further if myopic
    if myopic_index:
        periods = {
            p for p in periods if myopic_index.base_year <= p <= myopic_index.last_demand_year
        }
    techs = defaultdict(set)
    living_techs = set()  # for screening the linked techs below
    # filter out the dead ones...
    for element in raw:
        for p in periods:
            (r, ic, tech, v, oc, lifetime) = element
            if v <= p < v + lifetime:
                techs[r, p].add(Tech(r, ic, tech, v, oc))
                living_techs.add(tech)
    res.available_techs = techs

    # pick up the linked techs...
    raw = cur.execute(
        'SELECT primary_region, primary_tech, emis_comm, driven_tech FROM main.LinkedTech'
    ).fetchall()
    res.available_linked_techs = {
        LinkedTech(region=r, driver=driver, emission=emiss, driven=driven)
        for (r, driver, emiss, driven) in raw
        if driver in living_techs and driven in living_techs
    }

    # pick up negative costs...
    raw = cur.execute('SELECT DISTINCT tech FROM CostVariable where cost < 0').fetchall()
    for row in raw:
        tech = row[0]
        res.update_tech_data(tech=tech, element='neg_cost', value=True)
    logger.debug('built network data: %s', res.__str__())
    return res
