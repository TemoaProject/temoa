# temoa/components/capacity.py
"""
Defines the capacity-related components of the Temoa model.

This includes the core variables for new, retired, and available capacity,
as well as the constraints that govern their relationships and enforce
production limits.
"""

from __future__ import annotations

from itertools import product as cross_product
from logging import getLogger
from typing import TYPE_CHECKING

from deprecated import deprecated
from pyomo.environ import (
    value,
)

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


logger = getLogger(name=__name__)
# ============================================================================
# INDEX GENERATION FUNCTIONS
# (Formerly in temoa/_internal/temoa_initialize.py)
# ============================================================================
# By convention, we can prefix these with an underscore to indicate they are
# internal helpers for this component's construction.


def CapacityVariableIndices(M: 'TemoaModel'):
    return M.newCapacity_rtv


def RetiredCapacityVariableIndices(M: 'TemoaModel'):
    return set(
        (r, p, t, v)
        for r, p, t in M.processVintages
        if t in M.tech_retirement and t not in M.tech_uncap
        for v in M.processVintages[r, p, t]
        if v < p <= v + value(M.LifetimeProcess[r, t, v]) - value(M.PeriodLength[p])
    )


def AnnualRetirementVariableIndices(M: 'TemoaModel'):
    return set(
        (r, p, t, v) for r, t, v in M.retirementPeriods for p in M.retirementPeriods[r, t, v]
    )


def CapacityAvailableVariableIndices(M: 'TemoaModel'):
    return M.activeCapacityAvailable_rpt


def CapacityAvailableVariableIndicesVintage(M: 'TemoaModel'):
    return M.activeCapacityAvailable_rptv


def CheckCapacityFactorProcess(M: 'TemoaModel'):
    count_rptv = dict()
    # Pull CapacityFactorTech by default
    for r, p, _s, _d, t in M.CapacityFactor_rpsdt:
        for v in M.processVintages[r, p, t]:
            M.isCapacityFactorProcess[r, p, t, v] = False
            count_rptv[r, p, t, v] = 0

    # Check for bad values and count up the good ones
    for r, p, _s, _d, t, v in M.CapacityFactorProcess.sparse_iterkeys():
        if v not in M.processVintages[r, p, t]:
            msg = f'Invalid process {p, v} for {r, t} in CapacityFactorProcess table'
            logger.error(msg)
            raise ValueError(msg)

        # Good value, pull from CapacityFactorProcess table
        count_rptv[r, p, t, v] += 1

    # Check if all possible values have been set by process
    # log a warning if some are missing (allowed but maybe accidental)
    for (r, p, t, v), count in count_rptv.items():
        num_seg = len(M.TimeSeason[p]) * len(M.time_of_day)
        if count > 0:
            M.isCapacityFactorProcess[r, p, t, v] = True
            if count < num_seg:
                logger.info(
                    'Some but not all processes were set in CapacityFactorProcess (%i out of a possible %i) for: %s'
                    ' Missing values will default to CapacityFactorTech value or 1 if that is not set either.',
                    count,
                    num_seg,
                    (r, p, t, v),
                )


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
        (r, p, s, d, t, v)
        for (r, t, v) in processes
        for p in M.processPeriods[r, t, v]
        for s, d in cross_product(M.TimeSeason[p], M.time_of_day)
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


def get_default_capacity_factor(M: 'TemoaModel', r, p, s, d, t, v):
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
    return M.CapacityFactorTech[r, p, s, d, t]


@deprecated('switched over to validator... this set is typically VERY empty')
def CapacityFactorProcessIndices(M: 'TemoaModel'):
    indices = set(
        (r, s, d, t, v)
        for r, i, t, v, o in M.Efficiency.sparse_iterkeys()
        for p in M.time_optimize
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )
    return indices


def CapacityFactorTechIndices(M: 'TemoaModel'):
    all_cfs = set(
        (r, p, s, d, t)
        for r, p, t in M.activeCapacityAvailable_rpt
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )
    return all_cfs


def CapacityConstraintIndices(M: 'TemoaModel'):
    capacity_indices = set(
        (r, p, s, d, t, v)
        for r, p, t, v in M.activeActivity_rptv
        if (t not in M.tech_annual or t in M.tech_demand)
        if t not in M.tech_uncap
        if t not in M.tech_storage
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    return capacity_indices


def CapacityAnnualConstraintIndices(M: 'TemoaModel'):
    capacity_indices = set(
        (r, p, t, v)
        for r, p, t, v in M.activeActivity_rptv
        if t in M.tech_annual and t not in M.tech_demand
        if t not in M.tech_uncap
    )

    return capacity_indices


def RegionalExchangeCapacityConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r_e, r_i, p, t, v)
        for r_e, p, i in M.exportRegions
        for r_i, t, v, o in M.exportRegions[r_e, p, i]
    )

    return indices
