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
from pyomo.environ import NonNegativeReals, value

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


def validate_CapacityFactorProcess(M: 'TemoaModel', val, r, p, s, d, t, v) -> bool:
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
    # Doesn't seem worth the compute time
    return all(
        (
            r in M.regions,
            p in M.time_optimize,
            s in M.time_season[p],
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


def validate_SeasonSequential(M: 'TemoaModel'):
    
    if all((
        not M.tech_seasonal_storage,
        not M.RampUpHourly,
        not M.RampDownHourly,
    )):
        # Don't need it anyway
        return

    if not M.TimeSeasonSequential:
        if M.TimeSequencing.first() in ('sequential_days', 'seasonal_timeslices'):
            logger.info(
                'No data in TimeSeasonSequential. By default, assuming sequential seasons '
                'match TimeSeason and TimeSegmentFraction.'
            )
            for p in M.time_season:
                for s in M.time_season[p]:
                    M.ordered_season_sequential.add((p, s, s))
                    M.TimeSeasonSequential[p, s, s] = value(M.SegFracPerSeason[p, s]) * value(M.DaysPerPeriod)

        else:
            msg = (
                f'No data in TimeSeasonSequential but time_sequencing parameter set to {M.TimeSequencing.first()} '
                'and inter-season features used. TimeSeasonSequential must be filled for this type of time ' 
                'sequencing if seasonal storage or inter-season constraints like RampUp/RampDown are used. Check '
                'the config file.'
            )
            logger.error(msg)
            raise ValueError(msg)
            
    sequential = dict()
    for p, s_seq, s in M.TimeSeasonSequential:
        count = value(M.TimeSeasonSequential[p, s_seq, s])
        if M.TimeSequencing.first() == 'sequential_days' and abs(count - 1.0) >= 0.01:
            msg = (
                'TimeSequencing set to sequential_days but a season in the TimeSegmentFraction table does not '
                f'represent exactly one day. This would lead to bad model behaviour: {p, s}, days: {count}. '
                'Check the config file.'
            )
            logger.error(msg)
            raise ValueError(msg)
        if (p, s) not in sequential:
            sequential[p, s] = 0
        sequential[p, s] += count

    # Check that TimeSeasonSequential day counts total to number of days in each period
    for p in M.time_optimize:
        count_total = sum(
            sequential[p, s]
            for _p, s in sequential
            if _p == p
        )
        if abs(count_total - value(M.DaysPerPeriod)) >= 0.001:
            logger.warning(
                f'Sum of day count in TimeSeasonSequential ({sum(sequential.values())}) '
                f'does not sum to days_per_period ({value(M.DaysPerPeriod)}) from the '
                'MetaData table.'
            )

    # Check that seasons using in storage seasons are actual seasons
    for (p, s) in sequential:
        if (p, s) not in M.SegFracPerSeason:
            msg = (
                f'Period-season index {(p, s)} that does not exist in '
                'TimeSegmentFraction referenced in TimeSeasonSequential .'
            )
            logger.error(msg)
            raise ValueError(msg)
    
    for (p, s) in M.SegFracPerSeason:
        if s not in M.time_season[p]:
            continue

        # Check that all seasons are used in sequential seasons
        if (p, s) not in sequential:
            msg = (f'Period-season index {(p, s)} absent from TimeSeasonSequential')
            logger.warning(msg)

        # Check that the two tables agree on the total seasonal composition of each period
        segfrac = value(M.SegFracPerSeason[p, s])
        segfracseq = sequential[p, s] / value(M.DaysPerPeriod)
        if abs(segfrac - segfracseq) >= 0.001:
            msg = (
                'Discrepancy of total period-season composition between ' 
                'TimeSegmentFraction and TimeSeasonSequential. Total fraction of each '
                'period assigned to each season should match: ' 
                f'TimeSegmentFraction: {(p, s, value(M.SegFracPerSeason[p, s]))}'
                f', TimeSeasonSequential: {(p, s, segfracseq)}'
            )
            logger.warning(msg)


def validate_ReserveMargin(M: 'TemoaModel'):
    for r in M.PlanningReserveMargin:
        if all((r, p) not in M.processReservePeriods for p in M.time_optimize):
            logger.warning(
                'Planning reserve margin provided but there are no reserve '
                f'technologies serving this region: {r, M.PlanningReserveMargin[r]}'
            )


def validate_SurvivalCurve(M: 'TemoaModel'):
    rptv = set(
        (r, p, t, v)
        for r, t, v in M.retirementPeriods
        if (r, t, v) in M.tech_survival_curve
        for p in M.retirementPeriods[r, t, v]
    )
    rptv = rptv | M.SurvivalCurve.sparse_iterkeys()
    for r, p, t, v in rptv:
        if (r, t, v) not in M.survivalCurvePeriods:
            M.survivalCurvePeriods[r, t, v] = list()
        M.survivalCurvePeriods[r, t, v].append(p)
        if M.time_exist.first() < p < M.time_future.last() and p not in M.time_exist | M.time_future:
            msg = (
                'A row in the SurvivalCurve table used a period that was within the bounds of '
                'defined periods but was not one of those periods. This value was ignored: '
                f'({r}, >{p}<, {t}, {v})): {M.SurvivalCurve[r, p, t, v]}'
            )
            logger.warning(msg)
    for r, t, v in M.survivalCurvePeriods:
        M.survivalCurvePeriods[r, t, v] = sorted(M.survivalCurvePeriods[r, t, v])
        for i, p in enumerate(M.survivalCurvePeriods[r, t, v]):
            if i == 0:
                continue
            p_prev = M.survivalCurvePeriods[r, t, v][i-1]
            lsc = M.SurvivalCurve[r, p, t, v]
            lsc_prev = M.SurvivalCurve[r, p_prev, t, v]
            if lsc > lsc_prev:
                msg = (
                    'SurvivalCurve fraction increases going forward in time from {} to {}. '
                    'This is not allowed.'
                ).format((r, p_prev, t, v), (r, p, t, v))
                logger.error(msg)
                raise ValueError(msg)
        

def validate_tech_sets(M: 'TemoaModel'):
    """
    Check tech sets for any forbidden intersections
    """
    if not all(
        (
            check_no_intersection(M.tech_annual, M.tech_baseload),
            check_no_intersection(M.tech_annual, M.tech_storage),
            check_no_intersection(M.tech_annual, M.tech_upramping),
            check_no_intersection(M.tech_annual, M.tech_downramping),
            check_no_intersection(M.tech_annual, M.tech_curtailment),
            check_no_intersection(M.tech_curtailment, M.tech_flex),
            check_no_intersection(M.tech_all, M.tech_group_names),
        )
    ):
        raise ValueError("Technology sets failed to validate. Check log file for details.")


def check_no_intersection(set_one, set_two):
    violations = set_one & set_two
    if violations:
        msg = f'The following are in both {set_one} and {set_two}, which is not permitted:\n{list(violations)}'
        logger.error(msg)
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