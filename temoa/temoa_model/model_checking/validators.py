"""
These "validators" are used as validation tools for several elements in the TemoaModel

Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  9/27/23

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

import re
from logging import getLogger
from typing import TYPE_CHECKING

import deprecated
from pyomo.environ import NonNegativeReals

if TYPE_CHECKING:
    from temoa.temoa_model.temoa_model import TemoaModel

logger = getLogger(__name__)


def validate_linked_tech(M: 'TemoaModel') -> bool:
    """
    A validation that for all the linked techs, they have the same lifetime in each possible vintage

    The Constraint that this check supports is indexed by a set that fundamentally expands the (r, t, e)
    index of the LinkedTech data table (where t==driver tech) to include valid vintages.
    The implication is that there is a driven tech in the same region, of
    the same vintage, with the same lifetime as the driver tech.  We should check that.

    We can filter the index down to (r, t_driver, v, e) and then query the lifetime of the driver and driven
    to ensure they are the same

    :param M:
    :return: True if "OK" else False
    """
    logger.debug('Starting to validate linked techs.')

    base_idx = M.LinkedEmissionsTechConstraint_rpsdtve

    drivers = {(r, t, v, e) for r, p, s, d, t, v, e in base_idx}
    for r, t_driver, v, e in drivers:
        # get the linked tech of same region, emission
        t_driven = M.LinkedTechs[r, t_driver, e]

        # check for equality in lifetimes for vintage v
        driver_lifetime = M.LifetimeProcess[r, t_driver, v]
        try:
            driven_lifetime = M.LifetimeProcess[r, t_driven, v]
        except KeyError:
            logger.error(
                'Linked Tech Error:  Driven tech %s does not have a vintage entry %d to match driver %s',
                t_driven,
                v,
                t_driver,
            )
            print('Problem with Linked Tech validation:  See log file')
            return False
        if driven_lifetime != driver_lifetime:
            logger.error(
                'Linked Tech Error:  Driven tech %s has lifetime %d in vintage %d while driver tech %s has lifetime %d',
                t_driven,
                driven_lifetime,
                v,
                t_driver,
                driver_lifetime,
            )
            print('Problem with Linked Tech validation:  See log file')
            return False

    return True


def no_slash_or_pipe(M: 'TemoaModel', element) -> bool:
    """
    No slash character in element
    :param M:
    :param element:
    :return:
    """
    if isinstance(element, int | float):
        return True
    good = '/' not in str(element) and '|' not in str(element)
    if not good:
        logger.error('no slash "/" or pipe "|" character is allowed in: %s', str(element))
        return False
    return True


def region_check(M: 'TemoaModel', region) -> bool:
    """
    Validate the region name (letters + numbers only + underscore)
    """
    # screen against illegal names
    illegal_region_names = {
        'global',
    }
    if region in illegal_region_names:
        return False

    # if this matches, return is true, fail -> false
    if re.match(r'[a-zA-Z0-9_]+\Z', region):  # string that has only letters and numbers
        return True
    return False


def linked_region_check(M: 'TemoaModel', region_pair) -> bool:
    """
    Validate a pair of regions (r-r format where r ∈ M.R )
    """
    linked_regions = re.match(r'([a-zA-Z0-9_]+)\-([a-zA-Z0-9_]+)\Z', region_pair)
    if linked_regions:
        r1 = linked_regions.group(1)
        r2 = linked_regions.group(2)
        if (
            all(r in M.regions for r in (r1, r2)) and r1 != r2
        ):  # both captured regions are in the set of M.R
            return True
    return False


def region_group_check(M: 'TemoaModel', rg) -> bool:
    """
    Validate the region-group name (region or regions separated by '+')
    """
    if '-' in rg:  # it should just be evaluated as a linked_region
        return linked_region_check(M, rg)
    if re.search(r'\A[a-zA-Z0-9\+_]+\Z', rg):
        # it has legal characters only
        if '+' in rg:
            # break up the group
            contained_regions = rg.strip().split('+')
            if all(t in M.regions for t in contained_regions) and len(
                set(contained_regions)
            ) == len(contained_regions):  # no dupes
                return True
        else:  # it is a singleton
            return (rg in M.regions) or rg == 'global'
    return False


@deprecated.deprecated('needs to be updated if re-instated to accommodate group restructuring')
def tech_groups_set_check(M: 'TemoaModel', rg, g, t) -> bool:
    """
    Validate this entry to the tech_groups set
    :param M: the model
    :param rg: region-group index
    :param g: tech group name
    :param t: tech
    :return: True if valid entry, else False
    """
    return all((region_group_check(M, rg), g in M.tech_group_names, t in M.tech_all))


# TODO:  Several of these param checkers below are not in use because the params cannot
#        accept new values for the indexing sets that aren't in an already-constructed set.  Now that we are
#        making the GlobalRegionalIndices, we can probably come back and employ them instead of using
#        the buildAction approach


def activity_param_check(M: 'TemoaModel', val, rg, p, t) -> bool:
    """
    Validate the index and the value for an entry into an activity param indexed with region-groups
    :param M: the model
    :param val: the value of the parameter for this index
    :param rg: region-group
    :param p: time period
    :param t: tech
    :return: True if all OK
    """
    return all(
        (
            val in NonNegativeReals,  # the value should be in this set
            region_group_check(M, rg),
            p in M.time_optimize,
            t in M.tech_all,
        )
    )


def capacity_param_check(M: 'TemoaModel', val, rg, p, t, carrier) -> bool:
    """
    validate entries to capacity params
    :param M: the model
    :param val: the param value at this index
    :param rg: region-group
    :param p: time period
    :param t: tech
    :param carrier: commodity carrier
    :return: True if all OK
    """
    return all(
        (
            val in NonNegativeReals,
            region_group_check(M, rg),
            p in M.time_optimize,
            t in M.tech_all,
            carrier in M.commodity_carrier,
        )
    )


def activity_group_param_check(M: 'TemoaModel', val, rg, p, g) -> bool:
    """
    validate entries into capacity groups
    :param M: the model
    :param val: the value at this index
    :param rg: region-group
    :param p: time period
    :param g: tech group name
    :return: True if all OK
    """
    return all(
        (
            val in NonNegativeReals,
            region_group_check(M, rg),
            p in M.time_optimize,
            g in M.tech_group_names,
        )
    )


def emission_limit_param_check(M: 'TemoaModel', val, rg, p, e) -> bool:
    """
    validate entries into EmissionLimit param
    :param M: the model
    :param val: the value at this index
    :param rg: region-group
    :param p: time period
    :param e: commodity emission
    :return: True if all OK
    """
    return all((region_group_check(M, rg), p in M.time_optimize, e in M.commodity_emissions))


def validate_CapacityFactorProcess(M: 'TemoaModel', val, r, s, d, t, v) -> bool:
    """
    validate the rsdtv index
    :param val: the parameter value
    :param M: the model
    :param r: region
    :param s: season
    :param d: time of day
    :param t: tech
    :param v: vintage
    :return:
    """
    # devnote: CapacityFactorProcess can be a BIG table and most of these seem redundant
    # when they're already enforced by the domain of the parameter
    return all(
        (
            r in M.regions,
            s in M.time_season,
            d in M.time_of_day,
            t in M.tech_with_capacity,
            v in M.vintage_all,
            0 <= val <= 1.0,
        )
    )


def validate_Efficiency(M: 'TemoaModel', val, r, si, t, v, so) -> bool:
    """Handy for troubleshooting problematic entries"""

    if all(
        (
            isinstance(val, float),
            val > 0,
            r in M.regionalIndices,
            si in M.commodity_physical,
            t in M.tech_all,
            so in M.commodity_carrier,
            v in M.vintage_all,
        )
    ):
        return True
    print('Element Validations:')
    print('region', r in M.regionalIndices)
    print('input_commodity', si in M.commodity_physical)
    print('tech', t in M.tech_all)
    print('vintage', v in M.vintage_all)
    print('output_commodity', so in M.commodity_carrier)
    return False


def check_flex_curtail(M: 'TemoaModel'):
    violations = M.tech_flex & M.tech_curtailment
    if violations:
        logger.error(
            'The following technologies are in both flex and curtail, which is not permitted:',
            violations,
        )
        return False
    return True

# Seems unused
def validate_tech_split(M: 'TemoaModel', val, r, p, c, t):
    if all(
        (
            r in M.regions,
            p in M.time_optimize,
            c in M.commodity_physical,
            t in M.tech_all,
        )
    ):
        return True
    print('r', r in M.regions)
    print('p', p in M.time_optimize)
    print('c', c in M.commodity_physical)
    print('t', t in M.tech_all)
    return False

def validate_0to1(M: 'TemoaModel', val, *args):
    return 0.0 <= val <= 1.0