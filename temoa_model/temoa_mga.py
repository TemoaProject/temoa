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
"""

from pyomo.environ import *
from temoa_rules import TotalCost_rule


def ActivityObj_rule(M, prev_act_t):
    new_act = 0
    for t in M.V_ActivityByTech:
        if t in prev_act_t:
            new_act += prev_act_t[t] * M.V_ActivityByTech[t]
    return new_act


def SlackedObjective_rule(M, prev_cost, mga_slack):
    # It is important that this function name *not* match its constraint name
    # plus '_rule', else Pyomo will attempt to be too smart.  That is, at the
    # first implementation, the associated constraint name is
    # 'PreviousSlackedObjective', for which Pyomo searches the namespace for
    # 'PreviousSlackedObjective_rule'.  We decidedly do not want Pyomo
    # trying to call this function because it is not aware of the second arg.
    slackcost = (1 + mga_slack) * prev_cost
    oldobjective = TotalCost_rule(M)
    expr = slackcost >= oldobjective
    return expr


def PreviousAct_rule(instance, mga_weight, prev_activity_t):
    #   The version below weights each technology by its previous cumulative
    #   activity. However, different sectors may be tracked in different units and
    #   have activities of very different magnitudes.

    epsilon = 1e-6

    if mga_weight == "integer":
        for t in instance.V_ActivityByTech:
            if t in instance.tech_mga:
                val = value(instance.V_ActivityByTech[t])
                if abs(val) < epsilon:
                    continue
                prev_activity_t[t] += 1.0
        return prev_activity_t

    #   The version below calculates activity by sector and normalized technology-
    #   specific activity by the total activity for the sector. Currently accounts
    #   for electric and transport sectors, but others can be added to the block below.
    elif mga_weight == "normalized":
        sectors = set(
            ["electric", "transport", "industrial", "commercial", "residential"]
        )
        act = dict()
        techs = {
            "electric": instance.tech_electric,
            "transport": instance.tech_transport,
            "industrial": instance.tech_industrial,
            "commercial": instance.tech_commercial,
            "residential": instance.tech_residential,
        }
        for s in sectors:
            if len(techs[s]) > 0:
                act[s] = sum(value(instance.V_ActivityByTech[S_t]) for S_t in techs[s])

        for t in instance.V_ActivityByTech:
            for s in sectors:
                if t in techs[s]:
                    val = value(instance.V_ActivityByTech[t])
                    if abs(val) < epsilon:
                        continue
                    prev_activity_t[t] += val / act[s]
                return prev_activity_t
