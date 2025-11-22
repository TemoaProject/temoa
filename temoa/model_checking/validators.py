"""
These "validators" are used as validation tools for several elements in the TemoaModel

"""

from __future__ import annotations

import re
from logging import getLogger
from typing import TYPE_CHECKING

import deprecated
from pyomo.environ import NonNegativeReals

if TYPE_CHECKING:
    from pyomo.core import Set

    from temoa.core.model import TemoaModel
    from temoa.types.core_types import (
        Commodity,
        Period,
        Region,
        Season,
        Technology,
        TimeOfDay,
        Vintage,
    )

logger = getLogger(__name__)


# ============================================================================
# Public API - Functions intended for external import
# ============================================================================
__all__ = [
    'no_slash_or_pipe',
    'region_check',
    'region_group_check',
    'validate_0to1',
    'validate_efficiency',
    'validate_linked_tech',
    'validate_reserve_margin',
    'validate_tech_sets',
]


def validate_linked_tech(model: TemoaModel) -> bool:
    """
    A validation that for all the linked techs, they have the same lifetime in each possible vintage

    The Constraint that this check supports is indexed by a set that fundamentally expands the
    (r, t, e)
    index of the LinkedTech data table (where t==driver tech) to include valid vintages.
    The implication is that there is a driven tech in the same region, of
    the same vintage, with the same lifetime as the driver tech.  We should check that.

    We can filter the index down to (r, t_driver, v, e) and then query the lifetime of the driver
    and driven
    to ensure they are the same

    :param M:
    :return: True if "OK" else False
    """
    logger.debug('Starting to validate linked techs.')

    base_idx = model.linked_emissions_tech_constraint_rpsdtve

    drivers = {(r, t, v, e) for r, p, s, d, t, v, e in base_idx}
    for r, t_driver, v, e in drivers:
        # get the linked tech of same region, emission
        t_driven = model.linked_techs[r, t_driver, e]

        # check for equality in lifetimes for vintage v
        driver_lifetime = model.lifetime_process[r, t_driver, v]
        try:
            driven_lifetime = model.lifetime_process[r, t_driven, v]
        except KeyError:
            logger.error(
                'Linked Tech Error:  Driven tech %s does not have a vintage entry %d to match '
                'driver %s',
                t_driven,
                v,
                t_driver,
            )
            print('Problem with Linked Tech validation:  See log file')
            return False
        if driven_lifetime != driver_lifetime:
            logger.error(
                'Linked Tech Error:  Driven tech %s has lifetime %d in vintage %d while driver '
                'tech %s has lifetime %d',
                t_driven,
                driven_lifetime,
                v,
                t_driver,
                driver_lifetime,
            )
            print('Problem with Linked Tech validation:  See log file')
            return False

    return True


def no_slash_or_pipe(model: TemoaModel, element: object) -> bool:
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


def region_check(model: TemoaModel, region: Region) -> bool:
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


def linked_region_check(model: TemoaModel, region_pair: str) -> bool:
    """
    Validate a pair of regions (r-r format where r ∈ M.R )
    """
    linked_regions = re.match(r'([a-zA-Z0-9_]+)\-([a-zA-Z0-9_]+)\Z', region_pair)
    if linked_regions:
        r1 = linked_regions.group(1)
        r2 = linked_regions.group(2)
        if (
            all(r in model.regions for r in (r1, r2)) and r1 != r2
        ):  # both captured regions are in the set of M.R
            return True
    return False


def region_group_check(model: TemoaModel, rg: str) -> bool:
    """
    Validate the region-group name (region or regions separated by '+')
    """
    if '-' in rg:  # it should just be evaluated as a linked_region
        return linked_region_check(model, rg)
    if re.search(r'\A[a-zA-Z0-9\+_]+\Z', rg):
        # it has legal characters only
        if '+' in rg:
            # break up the group
            contained_regions = rg.strip().split('+')
            if all(t in model.regions for t in contained_regions) and len(
                set(contained_regions)
            ) == len(contained_regions):  # no dupes
                return True
        else:  # it is a singleton
            return (rg in model.regions) or rg == 'global'
    return False


@deprecated.deprecated('needs to be updated if re-instated to accommodate group restructuring')
def tech_groups_set_check(model: TemoaModel, rg: str, g: str, t: str) -> bool:
    """
    Validate this entry to the tech_groups set
    :param M: the model
    :param rg: region-group index
    :param g: tech group name
    :param t: tech
    :return: True if valid entry, else False
    """
    return all((region_group_check(model, rg), g in model.tech_group_names, t in model.tech_all))


# TODO:  Several of these param checkers below are not in use because the params cannot
#        accept new values for the indexing sets that aren't in an already-constructed set.  Now
#        that we are
#        making the GlobalRegionalIndices, we can probably come back and employ them instead of
#        using
#        the buildAction approach


def activity_param_check(model: TemoaModel, val: float, rg: str, p: Period, t: Technology) -> bool:
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
            region_group_check(model, rg),
            p in model.time_optimize,
            t in model.tech_all,
        )
    )


def capacity_param_check(
    model: TemoaModel, val: float, rg: str, p: Period, t: Technology, carrier: Commodity
) -> bool:
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
            region_group_check(model, rg),
            p in model.time_optimize,
            t in model.tech_all,
            carrier in model.commodity_carrier,
        )
    )


def activity_group_param_check(model: TemoaModel, val: float, rg: str, p: Period, g: str) -> bool:
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
            region_group_check(model, rg),
            p in model.time_optimize,
            g in model.tech_group_names,
        )
    )


def emission_limit_param_check(
    model: TemoaModel, val: float, rg: str, p: Period, e: Commodity
) -> bool:
    """
    validate entries into EmissionLimit param
    :param M: the model
    :param val: the value at this index
    :param rg: region-group
    :param p: time period
    :param e: commodity emission
    :return: True if all OK
    """
    return all(
        (region_group_check(model, rg), p in model.time_optimize, e in model.commodity_emissions)
    )


def validate_capacity_factor_process(
    model: TemoaModel,
    val: float,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> bool:
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
    # devnote: capacity_factor_process can be a BIG table and most of these seem redundant
    # when they're already enforced by the domain of the parameter
    # Doesn't seem worth the compute time
    return all(
        (
            r in model.regions,
            p in model.time_optimize,
            s in model.time_season[p],
            d in model.time_of_day,
            t in model.tech_with_capacity,
            v in model.vintage_all,
            0 <= val <= 1.0,
        )
    )


def validate_efficiency(
    model: TemoaModel,
    val: float,
    r: Region,
    si: Commodity,
    t: Technology,
    v: Vintage,
    so: Commodity,
) -> bool:
    """Handy for troubleshooting problematic entries"""

    if all(
        (
            isinstance(val, float),
            val > 0,
            r in model.regional_indices,
            si in model.commodity_physical,
            t in model.tech_all,
            so in model.commodity_carrier,
            v in model.vintage_all,
        )
    ):
        return True
    print('Element Validations:')
    print('region', r in model.regional_indices)
    print('input_commodity', si in model.commodity_physical)
    print('tech', t in model.tech_all)
    print('vintage', v in model.vintage_all)
    print('output_commodity', so in model.commodity_carrier)
    return False


def validate_reserve_margin(model: TemoaModel) -> None:
    for r in model.planning_reserve_margin.sparse_iterkeys():
        if all((r, p) not in model.process_reserve_periods for p in model.time_optimize):
            logger.warning(
                'Planning reserve margin provided but there are no reserve technologies serving '
                'this '
                'region: %s',
                (r, model.planning_reserve_margin[r]),
            )


def validate_tech_sets(model: TemoaModel) -> None:
    """
    Check tech sets for any forbidden intersections
    """
    if not all(
        (
            check_no_intersection(model.tech_annual, model.tech_baseload),
            check_no_intersection(model.tech_annual, model.tech_storage),
            check_no_intersection(model.tech_annual, model.tech_upramping),
            check_no_intersection(model.tech_annual, model.tech_downramping),
            check_no_intersection(model.tech_annual, model.tech_curtailment),
            check_no_intersection(model.tech_curtailment, model.tech_flex),
            check_no_intersection(model.tech_all, model.tech_group_names),
            check_no_intersection(model.tech_uncap, model.tech_reserve),
        )
    ):
        raise ValueError('Technology sets failed to validate. Check log file for details.')


def check_no_intersection(set_one: Set, set_two: Set) -> bool:
    violations = set_one & set_two
    if violations:
        msg = (
            f'The following are in both {set_one} and {set_two}, which is not permitted:\n'
            f'{list(violations)}'
        )
        logger.error(msg)
        return False
    return True


# Seems unused
def validate_tech_split(
    model: TemoaModel, val: float, r: Region, p: Period, c: Commodity, t: Technology
) -> bool:
    if all(
        (
            r in model.regions,
            p in model.time_optimize,
            c in model.commodity_physical,
            t in model.tech_all,
        )
    ):
        return True
    print('r', r in model.regions)
    print('p', p in model.time_optimize)
    print('c', c in model.commodity_physical)
    print('t', t in model.tech_all)
    return False


def validate_0to1(model: TemoaModel, val: float, *args: object) -> bool:
    return 0.0 <= val <= 1.0
