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

from sys import stderr as SE
from typing import TYPE_CHECKING

from pyomo.core import Set

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


from logging import getLogger

from pyomo.environ import value

logger = getLogger(name=__name__)


# ---------------------------------------------------------------
# Validation and initialization routines.
# There are a variety of functions in this section that do the following:
# Check valid indices, validate parameter specifications, and set default
# parameter values.
# ---------------------------------------------------------------


# ============================================================================
# Public API - Functions intended for external import
# ============================================================================
__all__ = [
    # Index creation functions for constraints and variables
    'CreateSparseDicts',
]


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
                logger.warning(msg, str(l_process))
                # SE.write(msg % str(l_process))
                continue
            if t not in M.tech_uncap and M.ExistingCapacity[l_process] == 0:
                msg = (
                    'Notice: Unnecessary specification of ExistingCapacity '
                    '%s.  If specifying a capacity of zero, you may simply '
                    'omit the declaration.\n'
                )
                logger.warning(msg, str(l_process))
                # SE.write(msg % str(l_process))
                continue
            if v + l_lifetime <= l_first_period:
                msg = (
                    '{} specified as ExistingCapacity, but its '
                    'lifetime ({} years) does not extend past the '
                    'beginning of time_future ({}) so it is never active. This '
                    'may be intentional for use in Growth constraints '
                    'or end of life flows.'
                ).format(l_process, l_lifetime, l_first_period)
                logger.info(msg)
                # Devnote: these are now useful due to end of life flows and
                # Growth constraints growing from existing cap so do not skip
                # SE.write(msg % (l_process, l_lifetime, l_first_period))
                # continue

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

        if t in M.tech_flex and o not in M.commodity_flex:
            M.commodity_flex.add(o)

        # All demand technologies must be annual technologies
        if o in M.commodity_demand and t not in M.tech_demand:
            M.tech_demand.add(t)

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

            # Get all periods where the process can retire
            if t not in M.tech_uncap and any(
                (
                    p <= v + l_lifetime < p + value(M.PeriodLength[p]),  # natural eol this period
                    t in M.tech_retirement
                    and v
                    < p
                    <= v + l_lifetime - value(M.PeriodLength[p]),  # allowed early retirement
                    M.isSurvivalCurveProcess[r, t, v] and v <= p <= v + l_lifetime,
                )
            ):
                if (r, t, v) not in M.retirementPeriods:
                    M.retirementPeriods[r, t, v] = set()
                M.retirementPeriods[r, t, v].add(p)

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
            if (r, p, t, v, i) not in M.processOutputsByInput:
                M.processOutputsByInput[r, p, t, v, i] = set()
            if (r, p, t, v, o) not in M.processInputsByOutput:
                M.processInputsByOutput[r, p, t, v, o] = set()
            if (r, t) not in M.processTechs:
                M.processTechs[r, t] = set()
            # While the dictionary just above identifies the vintage (v)
            # associated with each (r,p,t) we need to do the same below for various
            # technology subsets.
            if (r, p, t) not in M.processVintages:
                M.processVintages[r, p, t] = set()
            if (r, t, v) not in M.processPeriods:
                M.processPeriods[r, t, v] = set()
            if t in M.tech_curtailment and (r, p, t) not in M.curtailmentVintages:
                M.curtailmentVintages[r, p, t] = set()
            if t in M.tech_baseload and (r, p, t) not in M.baseloadVintages:
                M.baseloadVintages[r, p, t] = set()
            if t in M.tech_storage and (r, p, t) not in M.storageVintages:
                M.storageVintages[r, p, t] = set()
            if t in M.tech_upramping and (r, p, t) not in M.rampUpVintages:
                M.rampUpVintages[r, p, t] = set()
            if t in M.tech_downramping and (r, p, t) not in M.rampDownVintages:
                M.rampDownVintages[r, p, t] = set()

            # tech split
            for op in M.operator:
                if (r, p, i, t, op) in M.LimitTechInputSplit:
                    if (r, p, i, t, op) not in M.inputSplitVintages:
                        M.inputSplitVintages[r, p, i, t, op] = set()
                    M.inputSplitVintages[r, p, i, t, op].add(v)
                if (r, p, i, t, op) in M.LimitTechInputSplitAnnual:
                    if (r, p, i, t, op) not in M.inputSplitAnnualVintages:
                        M.inputSplitAnnualVintages[r, p, i, t, op] = set()
                    M.inputSplitAnnualVintages[r, p, i, t, op].add(v)
                if (r, p, t, o, op) in M.LimitTechOutputSplit:
                    if (r, p, t, o, op) not in M.outputSplitVintages:
                        M.outputSplitVintages[r, p, t, o, op] = set()
                    M.outputSplitVintages[r, p, t, o, op].add(v)
                if (r, p, t, o, op) in M.LimitTechOutputSplitAnnual:
                    if (r, p, t, o, op) not in M.outputSplitAnnualVintages:
                        M.outputSplitAnnualVintages[r, p, t, o, op] = set()
                    M.outputSplitAnnualVintages[r, p, t, o, op].add(v)

            # if t in M.tech_resource and (r, p, o) not in M.processByPeriodAndOutput: # not currently used
            #     M.processByPeriodAndOutput[r, p, o] = set()
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
            M.processOutputsByInput[r, p, t, v, i].add(o)
            M.processInputsByOutput[r, p, t, v, o].add(i)
            M.processTechs[r, t].add((p, v))
            M.processVintages[r, p, t].add(v)
            M.processPeriods[r, t, v].add(p)
            if t in M.tech_curtailment:
                M.curtailmentVintages[r, p, t].add(v)
            if t in M.tech_baseload:
                M.baseloadVintages[r, p, t].add(v)
            if t in M.tech_storage:
                M.storageVintages[r, p, t].add(v)
            if t in M.tech_upramping:
                M.rampUpVintages[r, p, t].add(v)
            if t in M.tech_downramping:
                M.rampDownVintages[r, p, t].add(v)

            # if t in M.tech_resource:
            #     M.processByPeriodAndOutput[r, p, o].add((i, t, v)) # not currently used
            if t in M.tech_reserve:
                M.processReservePeriods[r, p].add((t, v))
            if t in M.tech_exchange:
                M.exportRegions[r[: r.find('-')], p, i].add((r[r.find('-') + 1 :], t, v, o))
            if t in M.tech_exchange:
                M.importRegions[r[r.find('-') + 1 :], p, o].add((r[: r.find('-')], t, v, i))

    # devnote: I think this was only necessary because the commodity balance constraint rpc indices
    # weren't accounting for imports/exports. I added them to the set below so this should be fixed
    # for r, i, t, v, o in M.Efficiency.sparse_iterkeys():
    #     if t in M.tech_exchange:
    #         reg = r.split('-')[0]
    #         for r1, i1, t1, v1, o1 in M.Efficiency.sparse_iterkeys():
    #             if (r1 == reg) & (o1 == i):
    #                 for p in M.time_optimize:
    #                     if p >= v and (r1, p, o1) not in M.commodityDStreamProcess:
    #                         msg = (
    #                             'The {} process in region {} has no downstream process other '
    #                             'than a transport ({}) process. This will cause the commodity '
    #                             'balance constraint to fail. Add a dummy technology downstream '
    #                             'of the {} process to the Efficiency table to avoid this '
    #                             'issue.  The dummy technology should have the same region and '
    #                             'vintage as the {} process, an efficiency of 100%, with the {} '
    #                             'commodity as the input and output.'
    #                             'The dummy technology may also need a corresponding row in the '
    #                             'ExistingCapacity table with capacity values that equal the {} '
    #                             'technology.'
    #                         )
    #                         f_msg = msg.format(t1, r1, t, t1, t1, o1, t1)
    #                         logger.error(f_msg)
    #                         raise ValueError(f_msg)

    # Need this here for the commodity balance rpc set
    for r, i, t, v in M.ConstructionInput.sparse_iterkeys():
        if (r, v, i) not in M.capacityConsumptionTechs:
            M.capacityConsumptionTechs[r, v, i] = set()
        M.capacityConsumptionTechs[r, v, i].add(t)
    for r, t, v, o in M.EndOfLifeOutput.sparse_iterkeys():
        if (r, t, v) not in M.retirementPeriods:
            continue  # might be running myopic
        for p in M.retirementPeriods[r, t, v]:
            # What periods can this process retire in, either naturally or economically?
            if (r, p, o) not in M.retirementProductionProcesses:
                M.retirementProductionProcesses[r, p, o] = set()
            M.retirementProductionProcesses[r, p, o].add((t, v))

    l_unused_techs = M.tech_all - l_used_techs
    if l_unused_techs:
        msg = (
            "Notice: '{}' specified as technology, but it is not utilized in "
            'the Efficiency parameter.\n'
        )
        for i in sorted(l_unused_techs):
            SE.write(msg.format(i))

    # valid region-period-commodity sets for commodity balance constraints
    commodityUpstream_rpi = set(
        M.commodityUStreamProcess | M.retirementProductionProcesses | M.importRegions
    )
    commodityDownstream_rpo = set(
        M.commodityDStreamProcess | M.capacityConsumptionTechs | M.exportRegions
    )
    M.commodityBalance_rpc = commodityUpstream_rpi.intersection(commodityDownstream_rpo)

    # A dictionary of whether a storage tech is seasonal, just to speed things up
    for t in M.tech_storage:
        M.isSeasonalStorage[t] = False
    for t in M.tech_seasonal_storage:
        M.isSeasonalStorage[t] = True

    M.activeFlow_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.processVintages
        if t not in M.tech_annual
        for v in M.processVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.processOutputsByInput[r, p, t, v, i]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    M.activeFlow_rpitvo = set(
        (r, p, i, t, v, o)
        for r, p, t in M.processVintages
        for v in M.processVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.processOutputsByInput[r, p, t, v, i]
        if t in M.tech_annual or (t in M.tech_demand and o in M.commodity_demand)
    )

    M.activeFlex_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.processVintages
        if (t not in M.tech_annual) and (t in M.tech_flex)
        for v in M.processVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.processOutputsByInput[r, p, t, v, i]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    M.activeFlex_rpitvo = set(
        (r, p, i, t, v, o)
        for r, p, t in M.processVintages
        if (t in M.tech_annual) and (t in M.tech_flex)
        for v in M.processVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.processOutputsByInput[r, p, t, v, i]
    )

    M.activeFlowInStorage_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.processVintages
        if t in M.tech_storage
        for v in M.processVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.processOutputsByInput[r, p, t, v, i]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    M.activeCurtailment_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.curtailmentVintages
        for v in M.curtailmentVintages[r, p, t]
        for i in M.processInputs[r, p, t, v]
        for o in M.processOutputsByInput[r, p, t, v, i]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    M.activeActivity_rptv = set(
        (r, p, t, v) for r, p, t in M.processVintages for v in M.processVintages[r, p, t]
    )

    # devnote: currently unused
    # M.activeRegionsForTech = defaultdict(set)
    # for r, p, t, v in M.activeActivity_rptv:
    #     M.activeRegionsForTech[p, t].add(r)

    M.newCapacity_rtv = set(
        (r, t, v)
        for r, p, t in M.processVintages
        for v in M.processVintages[r, p, t]
        if t not in M.tech_uncap and v in M.time_optimize
    )

    M.activeCapacityAvailable_rpt = set(
        (r, p, t)
        for r, p, t in M.processVintages
        if M.processVintages[r, p, t]
        if t not in M.tech_uncap
    )

    M.activeCapacityAvailable_rptv = set(
        (r, p, t, v)
        for r, p, t in M.processVintages
        for v in M.processVintages[r, p, t]
        if t not in M.tech_uncap
    )

    # devnote: currently unused
    # M.groupRegionActiveFlow_rpt = set(
    #     (gr, p, t)
    #     for _r, p, t in M.processVintages
    #     for gr in M.regionalGlobalIndices
    #     if _r in gather_group_regions(M, gr)
    # )

    M.storageLevelIndices_rpsdtv = set(
        (r, p, s, d, t, v)
        for r, p, t in M.storageVintages
        for v in M.storageVintages[r, p, t]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    M.seasonalStorageLevelIndices_rpstv = set(
        (r, p, s_stor, t, v)
        for r, p, t in M.storageVintages
        if t in M.tech_seasonal_storage
        for v in M.storageVintages[r, p, t]
        for _p, s_stor in M.sequential_to_season
        if _p == p
    )

    logger.debug('Completed creation of SparseDicts')


# ---------------------------------------------------------------
# Create sparse parameter indices.
# These functions are called from temoa_model.py and use the sparse keys
# associated with specific parameters.
# ---------------------------------------------------------------


# devnote: this does not appear to be used anywhere
# given that it doesnt check if periods are valid, cant think what it would be for
# def EmissionActivityByPeriodAndTechVariableIndices(M: 'TemoaModel'):
#     indices = set(
#         (e, p, t) for e, i, t, v, o in M.EmissionActivity.sparse_iterkeys() for p in M.time_optimize
#     )

#     return indices


# ---------------------------------------------------------------
# Create sparse indices for decision variables.
# These functions are called from temoa_model.py and use the dictionaries
# created above in CreateSparseDicts()
# ---------------------------------------------------------------


def copy_from(other_set):
    """a cheap reference function to replace the lambdas in orig temoa_model"""
    return Set(other_set.sparse_iterkeys())
