import sys
from itertools import product as cross_product
from logging import getLogger
from operator import itemgetter as iget
from typing import TYPE_CHECKING

from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


logger = getLogger(name=__name__)


def CommodityBalanceConstraintErrorCheck(supplied, demanded, r, p, s, d, c):
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem. How this might come up I do not know
    if isinstance(supplied, int) or isinstance(demanded, int):
        expr = str(supplied == demanded)
        msg = (
            'Unable to balance commodity {} in ({}, {}, {}, {}).\n'
            'No flows on one side of constraint expression:\n'
            '   {}\n'
            'Possible reasons:\n'
            " - Is there a missing period in set 'time_future'?\n"
            " - Is there a missing tech in set 'tech_resource'?\n"
            " - Is there a missing tech in set 'tech_production'?\n"
            " - Is there a missing commodity in set 'commodity_physical'?\n"
            ' - Are there missing entries in the Efficiency table?\n'
            ' - Does a process need a longer Lifetime?'
        )
        logger.error(msg.format(c, r, p, s, d, expr))
        raise Exception(msg.format(c, r, p, s, d, expr))


def AnnualCommodityBalanceConstraintErrorCheck(supplied, demanded, r, p, c):
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem. How this might come up I do not know
    if isinstance(supplied, int) or isinstance(demanded, int):
        expr = str(supplied == demanded)
        msg = (
            'Unable to balance annual commodity {} in ({}, {}).\n'
            'No flows on one side of constraint expression:\n'
            '   {}\n'
            'Possible reasons:\n'
            " - Is there a missing period in set 'time_future'?\n"
            " - Is there a missing tech in set 'tech_resource'?\n"
            " - Is there a missing tech in set 'tech_production'?\n"
            " - Is there a missing commodity in set 'commodity_physical'?\n"
            ' - Are there missing entries in the Efficiency table?\n'
            ' - Does a process need a longer Lifetime?'
        )
        logger.error(msg.format(c, r, p, expr))
        raise Exception(msg.format(c, r, p, expr))


def DemandConstraintErrorCheck(supply, r, p, dem):
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem
    if isinstance(supply, int):
        msg = (
            "Error: Demand '{}' for ({}, {}) unable to be met by any "
            'technology.\n\tPossible reasons:\n'
            ' - Is the Efficiency parameter missing an entry for this demand?\n'
            ' - Does a tech that satisfies this demand need a longer '
            'Lifetime?\n'
        )
        logger.error(msg.format(dem, r, p))
        raise Exception(msg.format(dem, r, p))


def DemandActivityConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v, dem)
        for r, p, dem in M.DemandConstraint_rpc
        for t, v in M.commodityUStreamProcess[r, p, dem]
        if t not in M.tech_annual
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )
    return indices


def CreateDemands(M: 'TemoaModel'):
    """
    Steps to create the demand distributions
    1. Use Demand keys to ensure that all demands in commodity_demand are used
    2. Find any slices not set in DemandDefaultDistribution, and set them based
    on the associated SegFrac slice.
    3. Validate that the DemandDefaultDistribution sums to 1.
    4. Find any per-demand DemandSpecificDistribution values not set, and set
    them from DemandDefaultDistribution.  Note that this only sets a
    distribution for an end-use demand if the user has *not* specified _any_
    anything for that end-use demand.  Thus, it is up to the user to fully
    specify the distribution, or not.  No in-between.
     5. Validate that the per-demand distributions sum to 1.
    """
    logger.debug('Started creating demand distributions in CreateDemands()')

    # Step 0: some setup for a couple of reusable items
    # Get the nth element from the tuple (r, p, s, d, dem)
    # So we only have to update these indices in one place if they change
    DSD_region = iget(0)
    DSD_period = iget(1)
    DSD_dem = iget(4)

    # Step 1: Check if any demand commodities are going unused
    used_dems = set(dem for r, p, dem in M.Demand.sparse_iterkeys())
    unused_dems = sorted(M.commodity_demand.difference(used_dems))
    if unused_dems:
        for dem in unused_dems:
            msg = "Warning: Demand '{}' is unused\n"
            logger.warning(msg.format(dem))
            sys.stderr.write(msg.format(dem))

    # devnote: DDD just clones SegFrac. Unless we want to specify it in the database,
    #          makes sense to just use SegFrac directly
    # Step 2: Build the demand default distribution (= segfrac)
    # DDD = M.DemandDefaultDistribution  # Shorter, for us lazy programmer types
    # unset_defaults = set(M.SegFrac.sparse_iterkeys())
    # unset_defaults.difference_update(DDD.sparse_iterkeys())
    # if unset_defaults:
    # Some hackery because Pyomo thinks that this Param is constructed.
    # However, in our view, it is not yet, because we're specifically
    # targeting values that have not yet been constructed, that we know are
    # valid, and that we will need.
    # DDD._constructed = False
    # for tslice in unset_defaults:
    #     DDD[tslice] = M.SegFrac[tslice]  # DDD._constructed = True

    # Step 3: Check that DDD sums to 1
    # devnote: this seems redundant to the SegFrac sum to 1 check.
    # total = sum(i for i in DDD.values())
    # if abs(value(total) - 1.0) > 0.001:
    #     # We can't explicitly test for "!= 1.0" because of incremental rounding
    #     # errors associated with the specification of demand shares by time slice,
    #     # but we check to make sure it is within the specified tolerance.

    #     key_padding = max(map(get_str_padding, DDD.sparse_iterkeys()))

    #     fmt = '%%-%ds = %%s' % key_padding
    #     # Works out to something like "%-25s = %s"

    #     items = sorted(DDD.items())
    #     items = '\n   '.join(fmt % (str(k), v) for k, v in items)

    #     msg = (
    #         'The values of the DemandDefaultDistribution parameter do not '
    #         'sum to 1.  The DemandDefaultDistribution specifies how end-use '
    #         'demands are distributed among the time slices (i.e., time_season, '
    #         'time_of_day), so together, the data must total to 1.  Current '
    #         'values:\n   {}\n\tsum = {}'
    #     )
    #     logger.error(msg.format(items, total))
    #     raise ValueError(msg.format(items, total))

    # Step 4: Fill out demand specific distribution table and check sums to 1 by region and demand
    DSD = M.DemandSpecificDistribution

    demands_specified = set(map(DSD_dem, (i for i in DSD.sparse_iterkeys())))
    unset_demand_distributions = used_dems.difference(
        demands_specified
    )  # the demands not mentioned in DSD *at all*

    if unset_demand_distributions:
        for p in M.time_optimize:
            unset_distributions = set(
                cross_product(
                    M.regions, (p,), M.TimeSeason[p], M.time_of_day, unset_demand_distributions
                )
            )
            for r, p, s, d, dem in unset_distributions:
                DSD[r, p, s, d, dem] = value(M.SegFrac[p, s, d])  # DSD._constructed = True

    # Step 5: A final "sum to 1" check for all DSD members (which now should be everything)
    #         Also check that all keys are made...  The demand distro should be supported
    #         by the full set of (r, p, dem) keys because it is an equality constraint
    #         and we need to ensure even the zeros are passed in
    used_rp_dems = set((r, p, dem) for r, p, dem in M.Demand.sparse_iterkeys())
    for r, p, dem in used_rp_dems:
        expected_key_length = len(M.TimeSeason[p]) * len(M.time_of_day)
        keys = [
            k
            for k in DSD.sparse_iterkeys()
            if DSD_region(k) == r and DSD_period(k) == p and DSD_dem(k) == dem
        ]
        if len(keys) != expected_key_length:
            # this could be very slow but only calls when there's a problem
            missing = set(
                (s, d)
                for s in M.TimeSeason[p]
                for d in M.time_of_day
                if (r, p, s, d, dem) not in keys
            )
            logger.info(
                'Missing some time slices for Demand Specific Distribution %s: %s',
                (r, p, dem),
                missing,
            )
        total = sum(value(DSD[i]) for i in keys)
        if abs(value(total) - 1.0) > 0.001:
            # We can't explicitly test for "!= 1.0" because of incremental rounding
            # errors associated with the specification of demand shares by time slice,
            # but we check to make sure it is within the specified tolerance.
            def get_str_padding(obj):
                return len(str(obj))

            key_padding = max(map(get_str_padding, keys))

            fmt = '%%-%ds = %%s' % key_padding
            # Works out to something like "%-25s = %s"

            items = sorted((k, value(DSD[k])) for k in keys)
            items = '\n   '.join(fmt % (str(k), v) for k, v in items)

            msg = (
                'The values of the DemandSpecificDistribution parameter do not '
                'sum to 1 for {}. The DemandSpecificDistribution specifies how end-use '
                'demands are distributed per time-slice (i.e., time_season, '
                'time_of_day). Within each region, period, end-use demand, then, the distribution '
                'must total to 1.\n\n Demand-specific distribution in error: '
                ' \n   {}\n\tsum = {}'
            )
            logger.error(msg.format((r, p, dem), items, total))
            raise ValueError(msg.format((r, p, dem), items, total))

    logger.debug('Finished creating demand distributions')


def CommodityBalanceConstraintIndices(M: 'TemoaModel'):
    # Generate indices only for those commodities that are produced by
    # technologies with varying output at the time slice level.
    indices = set(
        (r, p, s, d, c)
        for r, p, c in M.commodityBalance_rpc
        # r in this line includes interregional transfer combinations (not needed).
        if r in M.regions  # this line ensures only the regions are included.
        and c not in M.commodity_annual
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    return indices


def AnnualCommodityBalanceConstraintIndices(M: 'TemoaModel'):
    # Generate indices only for those commodities that are produced by
    # technologies with constant annual output.
    indices = set(
        (r, p, c)
        for r, p, c in M.commodityBalance_rpc
        # r in this line includes interregional transfer combinations (not needed).
        if r in M.regions  # this line ensures only the regions are included.
        and c in M.commodity_annual
    )

    return indices
