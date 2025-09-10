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
from collections import defaultdict
from itertools import product as cross_product, product
from operator import itemgetter as iget
from sys import stderr as SE
from typing import TYPE_CHECKING

from deprecated import deprecated
from pyomo.core import Set

if TYPE_CHECKING:
    from temoa.temoa_model.temoa_model import TemoaModel

from io import StringIO

from pyomo.environ import value

from logging import getLogger

logger = getLogger(__name__)


# ---------------------------------------------------------------
# Validation and initialization routines.
# There are a variety of functions in this section that do the following:
# Check valid indices, validate parameter specifications, and set default
# parameter values.
# ---------------------------------------------------------------


def isValidProcess(M: 'TemoaModel', r, p, i, t, v, o):
    """\
Returns a boolean (True or False) indicating whether, in any given period, a
technology can take a specified input carrier and convert it to and specified
output carrier. Not currently used.
"""
    index = (r, p, t, v)
    if index in M.processInputs and index in M.processOutputs:
        if i in M.processInputs[index]:
            if o in M.processOutputs[index]:
                return True

    return False


def get_str_padding(obj):
    return len(str(obj))


def CommodityBalanceConstraintErrorCheck(supplied, demanded, r, p, s, d, c):
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem. How this might come up I do not know
    if isinstance(supplied, int) or isinstance(demanded, int):
        expr = str(supplied == demanded)
        msg = (
            "Unable to balance commodity {} in ({}, {}, {}, {}).\n"
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
            "Unable to balance annual commodity {} in ({}, {}).\n"
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


def DemandConstraintErrorCheck(supply, r, p, s, d, dem):
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem
    if isinstance(supply, int):
        msg = (
            "Error: Demand '{}' for ({}, {}, {}, {}) unable to be met by any "
            'technology.\n\tPossible reasons:\n'
            ' - Is the Efficiency parameter missing an entry for this demand?\n'
            ' - Does a tech that satisfies this demand need a longer '
            'Lifetime?\n'
        )
        logger.error(msg)
        raise Exception(msg.format(dem, r, p, s, d))


def validate_time(M: 'TemoaModel'):
    """
    We check for integer status here, rather than asking Pyomo to do this via
    a 'within=Integers' clause in the definition so that we can have a very
    specific error message.  If we instead use Pyomo's mechanism, the
    python invocation of Temoa throws an error (including a traceback)
    that has proven to be scary and/or impenetrable for the typical modeler.
    """
    logger.debug('Started validating time index')
    for year in M.time_exist:
        if isinstance(year, int):
            continue

        msg = f'Set "time_exist" requires integer-only elements.\n\n  ' f'Invalid element: "{year}"'
        logger.error(msg)
        raise Exception(msg)

    for year in M.time_future:
        if isinstance(year, int):
            continue

        msg = f'Set "time_future" requires integer-only elements.\n\n ' f'invalid element: "{year}"'
        logger.error(msg)
        raise Exception(msg)

    if len(M.time_future) < 2:
        msg = (
            'Set "time_future" needs at least 2 specified years.  \nTemoa '
            'treats the integer numbers specified in this set as boundary years \n'
            'between periods, and uses them to automatically ascertain the length \n'
            '(in years) of each period.  Note that this means that there will be \n'
            'one less optimization period than the number of elements in this set.'
        )

        logger.error(msg)
        raise RuntimeError(msg)

    # Ensure that the time_exist < time_future
    max_exist = max(M.time_exist)
    min_horizon = min(M.time_future)

    if not (max_exist < min_horizon):
        msg = (
            'All items in time_future must be larger than in time_exist.'
            '\ntime_exist max:   {}'
            '\ntime_future min: {}'
        )
        logger.error(msg.format(max_exist, min_horizon))
        raise Exception(msg.format(max_exist, min_horizon))
    logger.debug('Finished validating time')


def validate_SegFrac(M: 'TemoaModel'):
    """Ensure that the segment fractions adds up to 1"""
    total = sum(i for i in M.SegFrac.values())

    if abs(float(total) - 1.0) > 0.001:
        # We can't explicitly test for "!= 1.0" because of incremental rounding
        # errors associated with the specification of SegFrac by time slice,
        # but we check to make sure it is within the specified tolerance.

        key_padding = max(map(get_str_padding, M.SegFrac.sparse_iterkeys()))

        fmt = '%%-%ds = %%s' % key_padding
        # Works out to something like "%-25s = %s"

        items = sorted(M.SegFrac.items())
        items = '\n   '.join(fmt % (str(k), v) for k, v in items)

        msg = (
            'The values of the SegFrac parameter do not sum to 1.  Each item '
            'in SegFrac represents a fraction of a year, so they must total to '
            '1.  Current values:\n   {}\n\tsum = {}'
        )
        logger.error(msg.format(items, total))
        raise Exception(msg.format(items, total))


def CheckEfficiencyIndices(M: 'TemoaModel'):
    """
    Ensure that there are no unused items in any of the Efficiency index sets.
    """
    # TODO:  This could be upgraded to scan for finer resolution
    #        by checking by REGION and PERIOD...  Each region/period is unique.
    c_physical = set(i for r, i, t, v, o in M.Efficiency.sparse_iterkeys())
    techs = set(t for r, i, t, v, o in M.Efficiency.sparse_iterkeys())
    c_outputs = set(o for r, i, t, v, o in M.Efficiency.sparse_iterkeys())

    symdiff = c_physical.symmetric_difference(M.commodity_physical)
    if symdiff:
        msg = (
            'Unused or unspecified physical carriers.  Either add or remove '
            'the following elements to the Set commodity_physical.'
            '\n\n    Element(s): {}'
        )
        symdiff = (str(i) for i in symdiff)
        f_msg = msg.format(', '.join(symdiff))
        logger.error(f_msg)
        raise ValueError(f_msg)

    symdiff = techs.symmetric_difference(M.tech_all)
    if symdiff:
        msg = (
            'Unused or unspecified technologies.  Either add or remove '
            'the following technology(ies) to the tech_resource or '
            'tech_production Sets.\n\n    Technology(ies): {}'
        )
        symdiff = (str(i) for i in symdiff)
        f_msg = msg.format(', '.join(symdiff))
        logger.error(f_msg)
        raise ValueError(f_msg)

    diff = M.commodity_demand - c_outputs
    if diff:
        msg = (
            'Unused or unspecified outputs.  Either add or remove the '
            'following elements to the commodity_demand Set.'
            '\n\n    Element(s): {}'
        )
        diff = (str(i) for i in diff)
        f_msg = msg.format(', '.join(diff))
        logger.error(f_msg)
        raise ValueError(f_msg)


@deprecated('should not be needed.  We are pulling the default on-the-fly where used')
def CreateCapacityFactors(M: 'TemoaModel'):
    """
    Steps to creating capacity factors:
    1. Collect all possible processes
    2. Find the ones _not_ specified in CapacityFactorProcess
    3. Set them, based on CapacityFactorTech.
    """
    # Shorter names, for us lazy programmer types
    CFP = M.CapacityFactorProcess

    # Step 1
    processes = set((r, t, v) for r, i, t, v, o in M.Efficiency.sparse_iterkeys())

    all_cfs = set(
        (r, s, d, t, v)
        for (r, t, v), s, d in cross_product(processes, M.time_season, M.time_of_day)
    )

    # Step 2
    unspecified_cfs = all_cfs.difference(CFP.sparse_iterkeys())

    # Step 3

    # Some hackery: We futz with _constructed because Pyomo thinks that this
    # Param is already constructed.  However, in our view, it is not yet,
    # because we're specifically targeting values that have not yet been
    # constructed, that we know are valid, and that we will need.

    if unspecified_cfs:
        # CFP._constructed = False
        for r, s, d, t, v in unspecified_cfs:
            CFP[r, s, d, t, v] = M.CapacityFactorTech[r, s, d, t]
        logger.debug(
            'Created Capacity Factors for %d processes without an explicit specification',
            len(unspecified_cfs),
        )
    # CFP._constructed = True


def get_default_process_lifetime(M: 'TemoaModel', r, t, v):
    """
    This initializer used to initialize the LifetimeProcess parameter from LifetimeTech where needed

    Priority:
        1.  Specified in LifetimeProcess data (provided as a fill and would not call this function)
        2.  Specified in LifetimeTech data
        3.  The default value from the LifetimeTech param (automatic)
    :param M: generic model reference (not used)
    :param r: region
    :param t: tech
    :param v: vintage
    :return: the final lifetime value
    """
    return M.LifetimeTech[r, t]


def get_default_capacity_factor(M: 'TemoaModel', r, s, d, t, v):
    """
    This initializer is used to fill the CapacityFactorProcess from the CapacityFactorTech where needed.

    Priority:
        1.  As specified in data input (this function not called)
        2.  Here
        3.  The default from CapacityFactorTech param
    :param M: generic model reference
    :param r: region
    :param s: season
    :param d: time-of-day slice
    :param t: tech
    :param v: vintage
    :return: the capacity factor
    """
    return M.CapacityFactorTech[r, s, d, t]


def get_default_loan_rate(M, *_):
    """get the default loan rate from the DefaultLoanRate param"""
    return M.DefaultLoanRate()


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

    # iget(3): 3 = magic number to specify the fourth column.  Currently the
    # demand in the tuple (r, s, d, dem)
    DSD_dem_getter = iget(3)

    # iget(0): 0 = magic number to specify the first column.  Currently the
    # demand in the tuple (r, s, d, dem)
    DSD_region_getter = iget(0)

    # Step 1
    used_dems = set(dem for r, p, dem in M.Demand.sparse_iterkeys())
    unused_dems = sorted(M.commodity_demand.difference(used_dems))
    if unused_dems:
        for dem in unused_dems:
            msg = "Warning: Demand '{}' is unused\n"
            logger.warning(msg.format(dem))
            SE.write(msg.format(dem))

    # Step 2
    DDD = M.DemandDefaultDistribution  # Shorter, for us lazy programmer types
    unset_defaults = set(M.SegFrac.sparse_iterkeys())
    unset_defaults.difference_update(DDD.sparse_iterkeys())
    if unset_defaults:
        # Some hackery because Pyomo thinks that this Param is constructed.
        # However, in our view, it is not yet, because we're specifically
        # targeting values that have not yet been constructed, that we know are
        # valid, and that we will need.
        # DDD._constructed = False
        for tslice in unset_defaults:
            DDD[tslice] = M.SegFrac[tslice]  # DDD._constructed = True

    # Step 3
    total = sum(i for i in DDD.values())
    if abs(value(total) - 1.0) > 0.001:
        # We can't explicitly test for "!= 1.0" because of incremental rounding
        # errors associated with the specification of demand shares by time slice,
        # but we check to make sure it is within the specified tolerance.

        key_padding = max(map(get_str_padding, DDD.sparse_iterkeys()))

        fmt = '%%-%ds = %%s' % key_padding
        # Works out to something like "%-25s = %s"

        items = sorted(DDD.items())
        items = '\n   '.join(fmt % (str(k), v) for k, v in items)

        msg = (
            'The values of the DemandDefaultDistribution parameter do not '
            'sum to 1.  The DemandDefaultDistribution specifies how end-use '
            'demands are distributed among the time slices (i.e., time_season, '
            'time_of_day), so together, the data must total to 1.  Current '
            'values:\n   {}\n\tsum = {}'
        )
        logger.error(msg.format(items, total))
        raise ValueError(msg.format(items, total))

    # Step 4
    DSD = M.DemandSpecificDistribution

    demands_specified = set(map(DSD_dem_getter, (i for i in DSD.sparse_iterkeys())))
    unset_demand_distributions = used_dems.difference(
        demands_specified
    )  # the demands not mentioned in DSD *at all*
    unset_distributions = set(
        cross_product(M.regions, M.time_season, M.time_of_day, unset_demand_distributions)
    )

    if unset_distributions:
        # Some hackery because Pyomo thinks that this Param is constructed.
        # However, in our view, it is not yet, because we're specifically
        # targeting values that have not yet been constructed, that we know are
        # valid, and that we will need.
        # DSD._constructed = False
        for r, s, d, dem in unset_distributions:
            DSD[r, s, d, dem] = DDD[s, d]  # DSD._constructed = True

    # Step 5: A final "sum to 1" check for all DSD members (which now should be everything)
    #         Also check that all keys are made...  The demand distro should be supported
    #         by the full set of (r, p, dem) keys because it is an equality constraint
    #         and we need to ensure even the zeros are passed in
    expected_key_length = len(M.time_season) * len(M.time_of_day)
    used_reg_dems = set((r, dem) for r, p, dem in M.Demand.sparse_iterkeys())
    for r, dem in used_reg_dems:
        keys = [
            k
            for k in DSD.sparse_iterkeys()
            if DSD_dem_getter(k) == dem and DSD_region_getter(k) == r
        ]
        if len(keys) != expected_key_length:
            logger.debug(
                'Missing some keys in this set for creation of Demand Distribution %s: %s',
                dem,
                keys,
            )
        total = sum(DSD[i] for i in keys)
        if abs(value(total) - 1.0) > 0.001:
            # We can't explicitly test for "!= 1.0" because of incremental rounding
            # errors associated with the specification of demand shares by time slice,
            # but we check to make sure it is within the specified tolerance.

            keys = [
                k
                for k in DSD.sparse_iterkeys()
                if DSD_dem_getter(k) == dem and DSD_region_getter(k) == r
            ]
            key_padding = max(map(get_str_padding, keys))

            fmt = '%%-%ds = %%s' % key_padding
            # Works out to something like "%-25s = %s"

            items = sorted((k, DSD[k]) for k in keys)
            items = '\n   '.join(fmt % (str(k), v) for k, v in items)

            msg = (
                'The values of the DemandSpecificDistribution parameter do not '
                'sum to 1.  The DemandSpecificDistribution specifies how end-use '
                'demands are distributed per time-slice (i.e., time_season, '
                'time_of_day).  Within each end-use Demand, then, the distribution '
                'must total to 1.\n\n   Demand-specific distribution in error: '
                ' {}\n\n   {}\n\tsum = {}'
            )
            logger.error(msg.format(dem, items, total))
            raise ValueError(msg.format(dem, items, total))
    logger.debug('Finished creating demand distributions')


@deprecated(reason='vintage defaults are no longer available, so this should not be needed')
def CreateCosts(M: 'TemoaModel'):
    """
    Steps to creating fixed and variable costs:
    1. Collect all possible cost indices (CostFixed, CostVariable)
    2. Find the ones _not_ specified in CostFixed and CostVariable
    3. Set them, based on Cost*VintageDefault
    """
    logger.debug('Started Creating Fixed and Variable costs in CreateCosts()')
    # Shorter names, for us lazy programmer types
    CF = M.CostFixed
    CV = M.CostVariable

    # Step 1
    fixed_indices = set(M.CostFixed_rptv)
    var_indices = set(M.CostVariable_rptv)

    # Step 2
    unspecified_fixed_prices = fixed_indices.difference(CF.sparse_iterkeys())
    unspecified_var_prices = var_indices.difference(CV.sparse_iterkeys())

    # Step 3

    # Some hackery: We futz with _constructed because Pyomo thinks that this
    # Param is already constructed.  However, in our view, it is not yet,
    # because we're specifically targeting values that have not yet been
    # constructed, that we know are valid, and that we will need.

    if unspecified_fixed_prices:
        # CF._constructed = False
        for r, p, t, v in unspecified_fixed_prices:
            if (r, t, v) in M.CostFixedVintageDefault:
                CF[r, p, t, v] = M.CostFixedVintageDefault[r, t, v]  # CF._constructed = True

    if unspecified_var_prices:
        # CV._constructed = False
        for r, p, t, v in unspecified_var_prices:
            if (r, t, v) in M.CostVariableVintageDefault:
                CV[r, p, t, v] = M.CostVariableVintageDefault[r, t, v]
    # CV._constructed = True
    logger.debug('Created M.CostFixed with size: %d', len(M.CostFixed))
    logger.debug('Created M.CostVariable with size: %d', len(M.CostVariable))
    logger.debug('Finished creating Fixed and Variable costs')


def init_set_time_optimize(M: 'TemoaModel'):
    return sorted(M.time_future)[:-1]


def init_set_vintage_exist(M: 'TemoaModel'):
    return sorted(M.time_exist)


def init_set_vintage_optimize(M: 'TemoaModel'):
    return sorted(M.time_optimize)


def CreateRegionalIndices(M: 'TemoaModel'):
    """Create the set of all regions and all region-region pairs"""
    regional_indices = set()
    for r_i in M.regions:
        if '-' in r_i:
            logger.error("Individual region names can not have '-' in their names: %s", str(r_i))
            raise ValueError("Individual region names can not have '-' in their names: " + str(r_i))
        for r_j in M.regions:
            if r_i == r_j:
                regional_indices.add(r_i)
            else:
                regional_indices.add(r_i + '-' + r_j)
    # dev note:  Sorting these passed them to pyomo in an ordered container and prevents warnings
    return sorted(regional_indices)


# ---------------------------------------------------------------
# The functions below perform the sparse matrix indexing, allowing Pyomo to only
# create the necessary parameter, variable, and constraint indices.  This
#  cuts down *tremendously* on memory usage, which decreases time and increases
# the maximum specifiable problem size.
#
# It begins below in CreateSparseDicts, which creates a set of
# dictionaries that serve as the basis of the sparse indices.
# ---------------------------------------------------------------


def CreateSparseDicts(M: 'TemoaModel'):
    """
    This function creates customized dictionaries with only the key / value pairs
    defined in the associated datafile. The dictionaries defined here are used to
    do the sparse matrix indexing for all parameters, variables, and constraints
    in the model. The function works by looping over the sparse indices in the
    Efficiency table. For each iteration of the loop, the appropriate key / value
    pairs are defined as appropriate for each dictionary.
    """
    l_first_period = min(M.time_future)
    l_exist_indices = M.ExistingCapacity.sparse_keys()
    l_used_techs = set()

    # The basis for the dictionaries are the sparse keys defined in the
    # Efficiency table.
    logger.debug(
        'Starting creation of SparseDicts with Efficiency table size: %d', len(M.Efficiency)
    )
    for r, i, t, v, o in M.Efficiency.sparse_iterkeys():
        if '-' in r and t not in M.tech_exchange:
            msg = (
                f'Technology {t} seems to be an exchange technology '
                f'but it is not specified in tech_exchange set'
            )
            logger.error(msg)
            raise ValueError(msg)
        l_process = (r, t, v)
        l_lifetime = value(M.LifetimeProcess[l_process])
        # Do some error checking for the user.
        if v in M.vintage_exist:
            if l_process not in l_exist_indices and t not in M.tech_uncap:
                msg = (
                    'Warning: %s has a specified Efficiency, but does not '
                    'have any existing install base (ExistingCapacity).\n'
                )
                SE.write(msg % str(l_process))
                continue
            if t not in M.tech_uncap and M.ExistingCapacity[l_process] == 0:
                msg = (
                    'Notice: Unnecessary specification of ExistingCapacity '
                    '%s.  If specifying a capacity of zero, you may simply '
                    'omit the declaration.\n'
                )
                logger.info(msg, str(l_process))
                SE.write(msg % str(l_process))
                continue
            if v + l_lifetime <= l_first_period:
                msg = (
                    '\nWarning: %s specified as ExistingCapacity, but its '
                    'LifetimeProcess parameter does not extend past the beginning '
                    'of time_future.  (i.e. useless parameter)'
                    '\n\tLifetime:     %s'
                    '\n\tFirst period: %s\n'
                )
                logger.warning(msg, l_process, l_lifetime, l_first_period)
                SE.write(msg % (l_process, l_lifetime, l_first_period))
                continue

        eindex = (r, i, t, v, o)
        if M.Efficiency[eindex] == 0:
            msg = (
                '\nNotice: Unnecessary specification of Efficiency %s.  If '
                'specifying an efficiency of zero, you may simply omit the '
                'declaration.\n'
            )
            logger.info(msg, str(eindex))
            SE.write(msg % str(eindex))
            continue

        l_used_techs.add(t)

        if t in M.tech_flex:
            M.flex_commodities.add(o)

        # Add in the period (p) index, since it's not included in the efficiency
        # table.
        for p in M.time_optimize:
            # Can't build a vintage before it's been invented
            if p < v:
                continue

            pindex = (r, p, t, v)

            # dev note:  this gathering of processLoans appears to be unused in any meaningful way
            #            it is just plucked later for (r, t, v) combos which aren't needed anyhow.
            # if v in M.time_optimize:
            #     l_loan_life = value(M.LoanLifetimeProcess[l_process])
            #     if v + l_loan_life >= p:
            #         M.processLoans[pindex] = True

            # if tech is no longer active, don't include it
            if v + l_lifetime <= p:
                continue

            # Here we utilize the indices in a given iteration of the loop to
            # create the dictionary keys, and initialize the associated values
            # to an empty set.
            if pindex not in M.processInputs:
                M.processInputs[pindex] = set()
                M.processOutputs[pindex] = set()
            if (r, p, i) not in M.commodityDStreamProcess:
                M.commodityDStreamProcess[r, p, i] = set()
            if (r, p, o) not in M.commodityUStreamProcess:
                M.commodityUStreamProcess[r, p, o] = set()
            if (r, p, t, v, i) not in M.ProcessOutputsByInput:
                M.ProcessOutputsByInput[r, p, t, v, i] = set()
            if (r, p, t, v, o) not in M.ProcessInputsByOutput:
                M.ProcessInputsByOutput[r, p, t, v, o] = set()
            if (r, t) not in M.processTechs:
                M.processTechs[r, t] = set()
            # While the dictionary just above identifies the vintage (v)
            # associated with each (r,p,t) we need to do the same below for various
            # technology subsets.
            if (r, p, t) not in M.processVintages:
                M.processVintages[r, p, t] = set()
            if t in M.tech_curtailment and (r, p, t) not in M.curtailmentVintages:
                M.curtailmentVintages[r, p, t] = set()
            if t in M.tech_baseload and (r, p, t) not in M.baseloadVintages:
                M.baseloadVintages[r, p, t] = set()
            if t in M.tech_storage and (r, p, t) not in M.storageVintages:
                M.storageVintages[r, p, t] = set()
            if t in M.tech_ramping and (r, p, t) not in M.rampVintages:
                M.rampVintages[r, p, t] = set()
            if (r, p, i, t) in M.TechInputSplit.sparse_iterkeys() and (
                r,
                p,
                i,
                t,
            ) not in M.inputsplitVintages:
                M.inputsplitVintages[r, p, i, t] = set()
            if (r, p, i, t) in M.TechInputSplitAnnual.sparse_iterkeys() and (
                r,
                p,
                i,
                t,
            ) not in M.inputsplitannualVintages:
                M.inputsplitannualVintages[r, p, i, t] = set()
            if (r, p, t, o) in M.TechOutputSplit.sparse_iterkeys() and (
                r,
                p,
                t,
                o,
            ) not in M.outputsplitVintages:
                M.outputsplitVintages[r, p, t, o] = set()
            if (r, p, t, o) in M.TechOutputSplitAnnual.sparse_iterkeys() and (
                r,
                p,
                t,
                o,
            ) not in M.outputsplitannualVintages:
                M.outputsplitannualVintages[r, p, t, o] = set()
            if t in M.tech_resource and (r, p, o) not in M.ProcessByPeriodAndOutput:
                M.ProcessByPeriodAndOutput[r, p, o] = set()
            if t in M.tech_reserve and (r, p) not in M.processReservePeriods:
                M.processReservePeriods[r, p] = set()

            # since t is in M.tech_exchange, r here has *-* format (e.g. 'US-Mexico').  # r[
            # :r.find("-")] extracts the region index before the "-".
            if t in M.tech_exchange and (r[: r.find('-')], p, i) not in M.exportRegions:
                M.exportRegions[r[: r.find('-')], p, i] = set()
            if t in M.tech_exchange and (r[r.find('-') + 1 :], p, o) not in M.importRegions:
                M.importRegions[r[r.find('-') + 1 :], p, o] = set()

            # Now that all of the keys have been defined, and values initialized
            # to empty sets, we fill in the appropriate values for each
            # dictionary.
            M.processInputs[pindex].add(i)
            M.processOutputs[pindex].add(o)
            M.commodityDStreamProcess[r, p, i].add((t, v))
            M.commodityUStreamProcess[r, p, o].add((t, v))
            M.ProcessOutputsByInput[r, p, t, v, i].add(o)
            M.ProcessInputsByOutput[r, p, t, v, o].add(i)
            M.processTechs[r, t].add((p, v))
            M.processVintages[r, p, t].add(v)
            if t in M.tech_curtailment:
                M.curtailmentVintages[r, p, t].add(v)
            if t in M.tech_baseload:
                M.baseloadVintages[r, p, t].add(v)
            if t in M.tech_storage:
                M.storageVintages[r, p, t].add(v)
            if t in M.tech_ramping:
                M.rampVintages[r, p, t].add(v)
            if (r, p, i, t) in M.TechInputSplit.sparse_iterkeys():
                M.inputsplitVintages[r, p, i, t].add(v)
            if (r, p, i, t) in M.TechInputSplitAnnual.sparse_iterkeys():
                M.inputsplitannualVintages[r, p, i, t].add(v)
            if (r, p, t, o) in M.TechOutputSplit.sparse_iterkeys():
                M.outputsplitVintages[r, p, t, o].add(v)
            if (r, p, t, o) in M.TechOutputSplitAnnual.sparse_iterkeys():
                M.outputsplitannualVintages[r, p, t, o].add(v)
            if t in M.tech_resource:
                M.ProcessByPeriodAndOutput[r, p, o].add((i, t, v))
            if t in M.tech_reserve:
                M.processReservePeriods[r, p].add((t, v))
            if t in M.tech_exchange:
                M.exportRegions[r[: r.find('-')], p, i].add((r[r.find('-') + 1 :], t, v, o))
            if t in M.tech_exchange:
                M.importRegions[r[r.find('-') + 1 :], p, o].add((r[: r.find('-')], t, v, i))

    for r, i, t, v, o in M.Efficiency.sparse_iterkeys():
        if t in M.tech_exchange:
            reg = r.split('-')[0]
            for r1, i1, t1, v1, o1 in M.Efficiency.sparse_iterkeys():
                if (r1 == reg) & (o1 == i):
                    for p in M.time_optimize:
                        if p >= v and (r1, p, o1) not in M.commodityDStreamProcess:
                            msg = (
                                'The {} process in region {} has no downstream process other '
                                'than a transport ({}) process. This will cause the commodity '
                                'balance constraint to fail. Add a dummy technology downstream '
                                'of the {} process to the Efficiency table to avoid this '
                                'issue.  The dummy technology should have the same region and '
                                'vintage as the {} process, an efficiency of 100%, with the {} '
                                'commodity as the input and output.'
                                'The dummy technology may also need a corresponding row in the '
                                'ExistingCapacity table with capacity values that equal the {} '
                                'technology.'
                            )
                            f_msg = msg.format(t1, r1, t, t1, t1, o1, t1)
                            logger.error(f_msg)
                            raise ValueError(f_msg)

    l_unused_techs = M.tech_all - l_used_techs
    if l_unused_techs:
        msg = (
            "Notice: '{}' specified as technology, but it is not utilized in "
            'the Efficiency parameter.\n'
        )
        for i in sorted(l_unused_techs):
            SE.write(msg.format(i))

    M.activeFlow_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.processVintages.keys()
        if t not in M.tech_annual
        for v in M.processVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.ProcessOutputsByInput[r, p, t, v, i]
        for s in M.time_season
        for d in M.time_of_day
    )

    M.activeFlow_rpitvo = set(
        (r, p, i, t, v, o)
        for r, p, t in M.processVintages.keys()
        if t in M.tech_annual
        for v in M.processVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.ProcessOutputsByInput[r, p, t, v, i]
    )

    M.activeFlex_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.processVintages.keys()
        if (t not in M.tech_annual) and (t in M.tech_flex)
        for v in M.processVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.ProcessOutputsByInput[r, p, t, v, i]
        for s in M.time_season
        for d in M.time_of_day
    )

    M.activeFlex_rpitvo = set(
        (r, p, i, t, v, o)
        for r, p, t in M.processVintages.keys()
        if (t in M.tech_annual) and (t in M.tech_flex)
        for v in M.processVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.ProcessOutputsByInput[r, p, t, v, i]
    )

    M.activeFlowInStorage_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.processVintages.keys()
        if t in M.tech_storage
        for v in M.processVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.ProcessOutputsByInput[r, p, t, v, i]
        for s in M.time_season
        for d in M.time_of_day
    )

    M.activeCurtailment_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.curtailmentVintages.keys()
        for v in M.curtailmentVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.ProcessOutputsByInput[r, p, t, v, i]
        for s in M.time_season
        for d in M.time_of_day
    )

    M.activeActivity_rptv = set(
        (r, p, t, v) for r, p, t in M.processVintages.keys() for v in M.processVintages[r, p, t]
    )

    M.activeRegionsForTech = defaultdict(set)
    for r, p, t, v in M.activeActivity_rptv:
        M.activeRegionsForTech[p, t].add(r)

    M.activeCapacity_rtv = set(
        (r, t, v)
        for r, p, t in M.processVintages.keys()
        for v in M.processVintages[r, p, t]
        if t not in M.tech_uncap
    )

    M.activeCapacityAvailable_rpt = set(
        (r, p, t)
        for r, p, t in M.processVintages.keys()
        if M.processVintages[r, p, t]
        if t not in M.tech_uncap
    )

    M.activeCapacityAvailable_rptv = set(
        (r, p, t, v)
        for r, p, t in M.processVintages.keys()
        for v in M.processVintages[r, p, t]
        if t not in M.tech_uncap
    )
    logger.debug('Completed creation of SparseDicts')


# ---------------------------------------------------------------
# Create sparse parameter indices.
# These functions are called from temoa_model.py and use the sparse keys
# associated with specific parameters.
# ---------------------------------------------------------------


@deprecated('switched over to validator... this set is typically VERY empty')
def CapacityFactorProcessIndices(M: 'TemoaModel'):
    indices = set(
        (r, s, d, t, v)
        for r, i, t, v, o in M.Efficiency.sparse_iterkeys()
        for s in M.time_season
        for d in M.time_of_day
    )

    return indices


def CapacityFactorTechIndices(M: 'TemoaModel'):
    processes = set((r, t, v) for r, i, t, v, o in M.Efficiency.sparse_iterkeys())
    all_cfs = set(
        (r, s, d, t) for (r, t, v), s, d in cross_product(processes, M.time_season, M.time_of_day)
    )
    return all_cfs


def CostFixedIndices(M: 'TemoaModel'):
    # we pull the unlimited capacity techs from this index.  They cannot have fixed costs
    return {(r, p, t, v) for r, p, t, v in M.activeActivity_rptv if t not in M.tech_uncap}


def CostVariableIndices(M: 'TemoaModel'):
    return M.activeActivity_rptv


# dev note:  appears superfluous...
# def CostInvestIndices(M: 'TemoaModel'):
#     indices = set((r, t, v) for r, p, t, v in M.processLoans)
#
#     return indices


@deprecated('No longer used.  See the region_group_check in validators.py')
def RegionalGlobalInitializedIndices(M: 'TemoaModel'):
    from itertools import permutations

    indices = set()
    for n in range(1, len(M.regions) + 1):
        regional_perms = permutations(M.regions, n)
        for i in regional_perms:
            indices.add('+'.join(i))
    indices.add('global')
    indices = indices.union(M.RegionalIndices)

    return indices


def GroupShareIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, g)
        for g in M.tech_group_names
        for r, p, t in M.processVintages.keys()
        if t in M.tech_group_members[g]
    )

    return indices


def EmissionActivityIndices(M: 'TemoaModel'):
    indices = set(
        (r, e, i, t, v, o)
        for r, i, t, v, o in M.Efficiency.sparse_iterkeys()
        for e in M.commodity_emissions
        if r in M.regions  # omit any exchange/groups
    )

    return indices


def EmissionActivityByPeriodAndTechVariableIndices(M: 'TemoaModel'):
    indices = set(
        (e, p, t) for e, i, t, v, o in M.EmissionActivity.sparse_iterkeys() for p in M.time_optimize
    )

    return indices


def ModelProcessLifeIndices(M: 'TemoaModel'):
    """\
Returns the set of sensical (region, period, tech, vintage) tuples.  The tuple indicates
the periods in which a process is active, distinct from TechLifeFracIndices that
returns indices only for processes that EOL mid-period.
"""
    return M.activeActivity_rptv


def LifetimeProcessIndices(M: 'TemoaModel'):
    """\
Based on the Efficiency parameter's indices, this function returns the set of
process indices that may be specified in the LifetimeProcess parameter.
"""
    indices = set((r, t, v) for r, i, t, v, o in M.Efficiency.sparse_iterkeys())

    return indices


def LifetimeLoanProcessIndices(M: 'TemoaModel'):
    """\
Based on the Efficiency parameter's indices and time_future parameter, this
function returns the set of process indices that may be specified in the
CostInvest parameter.
"""
    min_period = min(M.vintage_optimize)

    indices = set((r, t, v) for r, i, t, v, o in M.Efficiency.sparse_iterkeys() if v >= min_period)

    return indices


# ---------------------------------------------------------------
# Create sparse indices for decision variables.
# These functions are called from temoa_model.py and use the dictionaries
# created above in CreateSparseDicts()
# ---------------------------------------------------------------


def CapacityVariableIndices(M: 'TemoaModel'):
    return M.activeCapacity_rtv


def RetiredCapacityVariableIndices(M: 'TemoaModel'):
    return set(
        (r, p, t, v)
        for r, p, t in M.processVintages.keys()
        if t in M.tech_retirement
        for v in M.processVintages[r, p, t]
        if p > v and t not in M.tech_uncap
    )


def CapacityAvailableVariableIndices(M: 'TemoaModel'):
    return M.activeCapacityAvailable_rpt


def CapacityAvailableVariableIndicesVintage(M: 'TemoaModel'):
    return M.activeCapacityAvailable_rptv


def FlowVariableIndices(M: 'TemoaModel'):
    return M.activeFlow_rpsditvo


def FlowVariableAnnualIndices(M: 'TemoaModel'):
    return M.activeFlow_rpitvo


def FlexVariablelIndices(M: 'TemoaModel'):
    return M.activeFlex_rpsditvo


def FlexVariableAnnualIndices(M: 'TemoaModel'):
    return M.activeFlex_rpitvo


def FlowInStorageVariableIndices(M: 'TemoaModel'):
    return M.activeFlowInStorage_rpsditvo


def CurtailmentVariableIndices(M: 'TemoaModel'):
    return M.activeCurtailment_rpsditvo


def CapacityConstraintIndices(M: 'TemoaModel'):
    capacity_indices = set(
        (r, p, s, d, t, v)
        for r, p, t, v in M.activeActivity_rptv
        if t not in M.tech_annual
        if t not in M.tech_uncap
        for s in M.time_season
        for d in M.time_of_day
    )

    return capacity_indices


def LinkedTechConstraintIndices(M: 'TemoaModel'):
    linkedtech_indices = set(
        (r, p, s, d, t, v, e)
        for r, t, e in M.LinkedTechs.sparse_iterkeys()
        for p in M.time_optimize
        if (r, p, t) in M.processVintages.keys()
        for v in M.processVintages[r, p, t]
        if (r, p, t, v) in M.activeActivity_rptv
        for s in M.time_season
        for d in M.time_of_day
    )

    return linkedtech_indices


def CapacityAnnualConstraintIndices(M: 'TemoaModel'):
    capacity_indices = set(
        (r, p, t, v)
        for r, p, t, v in M.activeActivity_rptv
        if t in M.tech_annual
        if t not in M.tech_uncap
    )

    return capacity_indices


# ---------------------------------------------------------------
# Create sparse indices for constraints.
# These functions are called from temoa_model.py and use the dictionaries
# created above in CreateSparseDicts()
# ---------------------------------------------------------------


def DemandActivityConstraintIndices(M: 'TemoaModel'):
    """\
This function returns a set of sparse indices that are used in the
DemandActivity constraint. It returns a tuple of the form:
(p,s,d,t,v,dem,first_s,first_d) where "dem" is a demand commodity, and "first_s"
and "first_d" are the reference season and time-of-day, respectively used to
ensure demand activity remains consistent across time slices.
"""

    # needed data structures...
    # the count of techs that supply a commodity
    suppliers = defaultdict(set)
    # (region, demand): (season, tod)  # the goal of the exercise!
    anchor_season_tod = {}
    # (region, demand): (period, tech, vintage) # the viable tech and vintage per region, demand
    viable_tech_vintage = defaultdict(list)

    # start the loop over possible combos
    for r, p, t, v, dem in M.ProcessInputsByOutput:
        # we aren't concerned with non-demand commodities or annual techs
        if dem not in M.commodity_demand or t in M.tech_annual:
            continue
        # capture the (p, t, v) in case we need to act on it
        viable_tech_vintage[r, dem].append((p, t, v))
        suppliers[dem].add(t)  # one more recognized supplier
        if len(suppliers[dem]) > 1:
            # We need to act on (build) for this region-demand, put in a placeholder
            anchor_season_tod[r, dem] = None

    # Find the first timestep of the year where the demand is appreciably sized:
    #   appreciable = not so small that we get into numerical instability when applying small multipliers
    appreciable_size = 0.0001

    for r, dem in anchor_season_tod:
        found_flag = False
        s0, d0 = None, None
        for s0, d0 in ((ss, dd) for ss in M.time_season for dd in M.time_of_day):
            if (r, s0, d0, dem) in M.DemandSpecificDistribution.sparse_iterkeys():
                if value(M.DemandSpecificDistribution[(r, s0, d0, dem)]) >= appreciable_size:
                    found_flag = True
                    break  # we have one with some value associated
        found = 'found' if found_flag else 'not found'
        # set it.  If nothing was found the first indices should work just fine...
        anchor_season_tod[r, dem] = (s0, d0)
        logger.debug(
            'Using season/tod: %s, %s for commodity %s in region %s which was %s in DSD '
            'to set DemandActivity baseline',
            s0,
            d0,
            dem,
            r,
            found,
        )

    # Start yielding the constraint indices
    for r, dem in anchor_season_tod:
        s0, d0 = anchor_season_tod[r, dem]
        for p, t, v in viable_tech_vintage[r, dem]:
            for s in M.time_season:
                for d in M.time_of_day:
                    if s != s0 or d != d0:
                        yield r, p, s, d, t, v, dem, s0, d0


def DemandConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, dem)
        for r, p, dem in M.Demand.sparse_iterkeys()
        for s in M.time_season
        for d in M.time_of_day
    )

    return indices


def BaseloadDiurnalConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v)
        for r, p, t in M.baseloadVintages.keys()
        for v in M.baseloadVintages[r, p, t]
        for s in M.time_season
        for d in M.time_of_day
    )

    return indices


def RegionalExchangeCapacityConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r_e, r_i, p, t, v)
        for r_e, p, i in M.exportRegions.keys()
        for r_i, t, v, o in M.exportRegions[r_e, p, i]
    )

    return indices


def CommodityBalanceConstraintIndices(M: 'TemoaModel'):
    # Generate indices only for those commodities that are produced by
    # technologies with varying output at the time slice level.
    period_commodity_with_up = set(M.commodityUStreamProcess.keys())
    period_commodity_with_dn = set(M.commodityDStreamProcess.keys())
    balanceable_rpc = period_commodity_with_up.intersection(period_commodity_with_dn)
    indices = set(
        (r, p, s, d, c)
        for r, p, c in balanceable_rpc
        # r in this line includes interregional transfer combinations (not needed).
        if r in M.regions  # this line ensures only the regions are included.
        and c not in M.commodity_annual
        for s in M.time_season
        for d in M.time_of_day
    )

    return indices


def AnnualCommodityBalanceConstraintIndices(M: 'TemoaModel'):
    # Generate indices only for those commodities that are produced by
    # technologies with constant annual output.
    period_commodity_with_up = set(M.commodityUStreamProcess.keys())
    period_commodity_with_dn = set(M.commodityDStreamProcess.keys())
    balanceable_rpc = period_commodity_with_up.intersection(period_commodity_with_dn)
    indices = set(
        (r, p, c)
        for r, p, c in balanceable_rpc
        # r in this line includes interregional transfer combinations (not needed).
        if r in M.regions  # this line ensures only the regions are included.
        and c in M.commodity_annual
    )

    return indices


def StorageVariableIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v)
        for r, p, t in M.storageVintages.keys()
        for s in M.time_season
        for d in M.time_of_day
        for v in M.storageVintages[r, p, t]
    )

    return indices


def StorageInitIndices(M: 'TemoaModel'):
    indices = set(
        (r, t, v) for r, p, t in M.storageVintages.keys() for v in M.storageVintages[r, p, t]
    )

    return indices


def StorageInitConstraintIndices(M: 'TemoaModel'):
    indices = set((r, t, v) for r, t, v in M.StorageInitFrac.sparse_iterkeys())

    return indices


def RampConstraintDayIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v)
        for r, p, t in M.rampVintages.keys()
        for s in M.time_season
        for d in M.time_of_day
        for v in M.rampVintages[r, p, t]
    )

    return indices


def RampConstraintSeasonIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, t, v)
        for r, p, t in M.rampVintages.keys()
        for s in M.time_season
        for v in M.rampVintages[r, p, t]
    )

    return indices


def RampConstraintPeriodIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, v) for r, p, t in M.rampVintages.keys() for v in M.rampVintages[r, p, t]
    )

    return indices


def ReserveMarginIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d)
        for r in M.regions
        for p in M.time_optimize
        for s in M.time_season
        for d in M.time_of_day
    )
    return indices


def TechInputSplitConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, i, t, v)
        for r, p, i, t in M.inputsplitVintages.keys()
        if t not in M.tech_annual
        for v in M.inputsplitVintages[r, p, i, t]
        for s in M.time_season
        for d in M.time_of_day
    )
    ann_indices = set(
        (r, p, i, t)
        for r, p, i, t in M.inputsplitVintages.keys()
        if t in M.tech_annual
    )
    if len(ann_indices) > 0:
        msg = (
            "Warning: Annual technologies included in TechInputSplit table. "
            "Use TechInputSplitAnnual table instead or these constraints will be ignored: {}"
        )
        logger.warning(msg.format(ann_indices))

    return indices


def TechInputSplitAnnualConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, i, t, v)
        for r, p, i, t in M.inputsplitannualVintages.keys()
        if t in M.tech_annual
        for v in M.inputsplitannualVintages[r, p, i, t]
    )

    return indices


def TechInputSplitAverageConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, i, t, v)
        for r, p, i, t in M.inputsplitannualVintages.keys()
        if t not in M.tech_annual
        for v in M.inputsplitannualVintages[r, p, i, t]
    )
    return indices


def TechOutputSplitConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v, o)
        for r, p, t, o in M.outputsplitVintages.keys()
        if t not in M.tech_annual
        for v in M.outputsplitVintages[r, p, t, o]
        for s in M.time_season
        for d in M.time_of_day
    )
    ann_indices = set(
        (r, p, t, o)
        for r, p, t, o in M.outputsplitVintages.keys()
        if t in M.tech_annual
    )
    if len(ann_indices) > 0:
        msg = (
            "Warning: Annual technologies included in TechOutputSplit table. "
            "Use TechOutputSplitAnnual table instead or these constraints will be ignored: {}"
        )
        logger.warning(msg.format(ann_indices))

    return indices


def TechOutputSplitAnnualConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, v, o)
        for r, p, t, o in M.outputsplitannualVintages.keys()
        if t in M.tech_annual
        for v in M.outputsplitannualVintages[r, p, t, o]
    )

    return indices


def TechOutputSplitAverageConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, v, o)
        for r, p, t, o in M.outputsplitannualVintages.keys()
        if t not in M.tech_annual
        for v in M.outputsplitannualVintages[r, p, t, o]
    )
    return indices


def get_loan_life(M, r, t, _):
    return M.LoanLifetimeTech[r, t]


def GrowthRateMax_rtv_initializer(M: 'TemoaModel'):
    # need to do this outside of the model because the elements are not initialized yet for 'product'
    return set(product(M.time_optimize, M.GrowthRateMax.sparse_iterkeys()))


def copy_from(other_set):
    """a cheap reference function to replace the lambdas in orig temoa_model"""
    return Set(other_set.sparse_iterkeys())
