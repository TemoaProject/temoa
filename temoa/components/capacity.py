# temoa/components/capacity.py
"""
Defines the capacity-related components of the Temoa model.

This module is responsible for:
-  Defining Pyomo index sets for variables.
-  Defining the rules for all capacity-related constraints, such as capacity
    production limits, retirement accounting, and available capacity aggregation.
-  Pre-calculating sparse index sets for capacity, retirement, and material flows.
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
# HELPER FUNCTIONS AND VALIDATORS
# ============================================================================


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
        for r, p, s, d, t, v in unspecified_cfs:
            CFP[r, p, s, d, t, v] = M.CapacityFactorTech[r, p, s, d, t]
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


def get_capacity_factor(M: 'TemoaModel', r, p, s, d, t, v):
    if M.isCapacityFactorProcess[r, p, t, v]:
        return value(M.CapacityFactorProcess[r, p, s, d, t, v])
    else:
        return value(M.CapacityFactorTech[r, p, s, d, t])


# ============================================================================
# PYOMO INDEX SETS
# ============================================================================


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


def RegionalExchangeCapacityConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r_e, r_i, p, t, v)
        for r_e, p, i in M.exportRegions
        for r_i, t, v, o in M.exportRegions[r_e, p, i]
    )

    return indices


def CapacityAnnualConstraintIndices(M: 'TemoaModel'):
    capacity_indices = set(
        (r, p, t, v)
        for r, p, t, v in M.activeActivity_rptv
        if t in M.tech_annual and t not in M.tech_demand
        if t not in M.tech_uncap
    )

    return capacity_indices


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


def CapacityAvailableVariableIndicesVintage(M: 'TemoaModel'):
    return M.activeCapacityAvailable_rptv


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


def AnnualRetirement_Constraint(M: 'TemoaModel', r, p, t, v):
    r"""
    Get the annualised retirement rate for a process in a given period.
    Used to output retirement (including end of life, EOL) and to model end of
    life flows and emissions. Assumes that retirement from the beginning of each period
    is evenly distributed over that model period :math:`\frac{1}{\text{LEN}_p}`
    for the accounting of retirement flows (in the same way we assume capacity is
    deployed evenly over the model period for construction inputs and embodied emissions).
    The factor :math:`\frac{\text{LSC}_{r,p,t,v}}{\text{PLF}_{r,p,t,v}}`
    adjusts the average survival during a period to the survival at the beginning
    of that period.

    .. math::
        :label: Annual Retirement

            \textbf{ART}_{r,p,t,v} =
            \begin{cases}
                \frac{1}{\text{LEN}_p} \cdot
                \frac{\text{LSC}_{r,p,t,v}}{\text{PLF}_{r,p,t,v}} \cdot \textbf{CAP}_{r,p,t,v}
                & \text{if EOL} \\
                \frac{1}{\text{LEN}_p} \cdot
                \left(
                \frac{\text{LSC}_{r,p,t,v}}{\text{PLF}_{r,p,t,v}} \cdot \textbf{CAP}_{r,p,t,v}
                - \frac{\text{LSC}_{r,p_{next},t,v}}{\text{PLF}_{r,p_{next},t,v}} \cdot \textbf{CAP}_{r,p_{next},t,v}
                \right)
                & \text{otherwise} \\
            \end{cases}

            \\\text{where EOL when } p \leq v + LTP_{r,t,v} < p + LEN_p
    """

    ## Get the capacity at the start of this period
    if p == v + value(M.LifetimeProcess[r, t, v]):
        # Exact EOL. No V_Capacity or V_RetiredCapacity for this period.
        if p == M.time_optimize.first():
            # Must be existing capacity. Apply survival curve to existing cap
            cap_begin = M.ExistingCapacity[r, t, v] * M.LifetimeSurvivalCurve[r, p, t, v]
        else:
            # Get previous capacity and continue survival curve
            p_prev = M.time_optimize.prev(p)
            cap_begin = (
                M.V_Capacity[r, p_prev, t, v]
                * value(M.LifetimeSurvivalCurve[r, p, t, v])
                / value(M.ProcessLifeFrac[r, p_prev, t, v])
            )
    else:
        # The capacity at the beginning of the period
        cap_begin = (
            M.V_Capacity[r, p, t, v]
            * value(M.LifetimeSurvivalCurve[r, p, t, v])
            / value(M.ProcessLifeFrac[r, p, t, v])
        )

    ## Get the capacity at the end of this period
    if p <= v + value(M.LifetimeProcess[r, t, v]) < p + value(M.PeriodLength[p]):
        # EOL so capacity ends on zero
        cap_end = 0
    else:
        # Mid-life period, ending capacity is beginning capacity of next period
        p_next = M.time_future.next(p)

        if p == M.time_optimize.last() or p_next == v + value(M.LifetimeProcess[r, t, v]):
            # No V_Capacity or V_RetiredCapacity for next period so just continue down the survival curve
            cap_end = (
                cap_begin
                * value(M.LifetimeSurvivalCurve[r, p_next, t, v])
                / value(M.LifetimeSurvivalCurve[r, p, t, v])
            )
        else:
            # Get the next period's beginning capacity
            cap_end = (
                M.V_Capacity[r, p_next, t, v]
                * value(M.LifetimeSurvivalCurve[r, p_next, t, v])
                / value(M.ProcessLifeFrac[r, p_next, t, v])
            )

    annualised_retirement = (cap_begin - cap_end) / M.PeriodLength[p]
    return M.V_AnnualRetirement[r, p, t, v] == annualised_retirement


def CapacityAvailableByPeriodAndTech_Constraint(M: 'TemoaModel', r, p, t):
    r"""

    The :math:`\textbf{CAPAVL}` variable is nominally for reporting solution values,
    but is also used in the Limit constraint calculations.

    .. math::
        :label: CapacityAvailable

        \textbf{CAPAVL}_{r, p, t} = \sum_{v, p_i \leq p} \textbf{CAP}_{r, p, t, v}

        \\
        \forall p \in \text{P}^o, r \in R, t \in T
    """
    cap_avail = sum(M.V_Capacity[r, p, t, S_v] for S_v in M.processVintages[r, p, t])

    expr = M.V_CapacityAvailableByPeriodAndTech[r, p, t] == cap_avail
    return expr


def CapacityAnnual_Constraint(M: 'TemoaModel', r, p, t, v):
    r"""
    Similar to Capacity_Constraint, but for technologies belonging to the
    :code:`tech_annual`  set. Technologies in the tech_annual set have constant output
    across different timeslices within a year, so we do not need to ensure
    that installed capacity is sufficient across all timeslices, thus saving
    some computational effort. Instead, annual output is sufficient to calculate
    capacity. Hourly capacity factors cannot be defined to annual technologies
    but annual capacity factors can be set using LimitAnnualCapacityFactor,
    which will be implicitly accounted for here.

    .. math::
        :label: CapacityAnnual

            \text{C2A}_{r, t}
            \cdot \textbf{CAP}_{r, t, v}
        =
            \sum_{I, O} \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}

        \\
        \forall \{r, p, t \in T^{a}, v\} \in \Theta_{\text{Activity}}
    """
    activity_rptv = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    return value(M.CapacityToActivity[r, t]) * M.V_Capacity[r, p, t, v] >= activity_rptv


def Capacity_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    r"""
    This constraint ensures that the capacity of a given process is sufficient
    to support its activity across all time periods and time slices. The calculation
    on the left hand side of the equality is the maximum amount of energy a process
    can produce in the timeslice :code:`(s,d)`. Note that the curtailment variable
    shown below only applies to technologies that are members of the curtailment set.
    Curtailment is necessary to track explicitly in scenarios that include a high
    renewable target. Without it, the model can generate more activity than is used
    to meet demand, and have all activity (including the portion curtailed) count
    towards the target. Tracking activity and curtailment separately prevents this
    possibility.

    .. math::
       :label: Capacity

           \left (
                   \text{CFP}_{r, p, s, d, t, v}
             \cdot \text{C2A}_{r, t}
             \cdot \text{SEG}_{s, d}
           \right )
           \cdot \textbf{CAP}_{r, t, v}
           =
           \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o}
           +
           \sum_{I, O} \textbf{CUR}_{r, p, s, d, i, t, v, o}

       \\
       \forall \{r, p, s, d, t, v\} \in \Theta_{\text{FO}}
    """
    # The expressions below are defined in-line to minimize the amount of
    # expression cloning taking place with Pyomo.

    if t in M.tech_annual:
        # Annual demand technology
        useful_activity = sum(
            (
                value(M.DemandSpecificDistribution[r, p, s, d, S_o])
                if S_o in M.commodity_demand
                else value(M.SegFrac[p, s, d])
            )
            * M.V_FlowOutAnnual[r, p, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
    else:
        useful_activity = sum(
            M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )

    if t in M.tech_curtailment:
        # If technologies are present in the curtailment set, then enough
        # capacity must be available to cover both activity and curtailment.
        return get_capacity_factor(M, r, p, s, d, t, v) * value(M.CapacityToActivity[r, t]) * value(
            M.SegFrac[p, s, d]
        ) * M.V_Capacity[r, p, t, v] == useful_activity + sum(
            M.V_Curtailment[r, p, s, d, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
    else:
        return (
            get_capacity_factor(M, r, p, s, d, t, v)
            * value(M.CapacityToActivity[r, t])
            * value(M.SegFrac[p, s, d])
            * M.V_Capacity[r, p, t, v]
            >= useful_activity
        )


def AdjustedCapacity_Constraint(M: 'TemoaModel', r, p, t, v):
    r"""
    This constraint updates the capacity of a process by taking into account retirements
    and end of life. For a given :code:`(r,p,t,v)` index, this constraint sets the capacity
    equal to the amount installed in period :code:`v` and subtracts from it any and all retirements
    that occurred prior to the period in question, :code:`p`, and end of life from the
    survival curve if defined. It finally adjusts for the process life fraction, which
    accounts for a possible mid-period end of life where, for example, EOL 3 years into a 5-year
    period would be treated as :math:`\frac{3}{5}` capacity for all 5 years.

    .. figure:: images/adjusted_capacity_plf.*
        :align: center
        :width: 100%
        :figclass: align-center
        :figwidth: 50%

        For processes reaching end of life mid-period, the process life fraction adjustment is applied,
        distributing the effective capacity over the whole period.

    For processes using survival curves, the yearly survival curve :math:`\text{LSC}_{r,p,t,v}` is
    averaged over the period to get the effective remaining capacity for that period  Because this
    implicitly handles mid-period end of life, :math:`\text{PLF}_{r,p,t,v}` is used to account for both
    phenomena.

    .. figure:: images/adjusted_capacity_sc.*
        :align: center
        :width: 100%
        :figclass: align-center
        :figwidth: 50%

        For processes with a defined survival curve, the surviving capacity is averaged over each
        period to get the adjusted capacity. This implicitly handles mid-period end of life as a
        survival curve will always be zero after the end of life of a process.

    .. math::
        :label: Adjusted Capacity

            \textbf{CAP}_{r,p,t,v} =
            \begin{cases}
                \text{PLF}_{r,p,t,v} \cdot
                \left(
                \text{ECAP}_{r,t,v} - \sum\limits_{v < p' <= p}
                \frac{\textbf{RCAP}_{r,p',t,v}}{\text{LSC}_{r,p',t,v}}
                \right)
                & \text{if } \ v \in T^e \\
                \text{PLF}_{r,p,t,v} \cdot
                \left(
                \textbf{NCAP}_{r,t,v} - \sum\limits_{v < p' <= p}
                \frac{\textbf{RCAP}_{r,p',t,v}}{\text{LSC}_{r,p',t,v}}
                \right)
                & \text{if } \ v \notin T^e
            \end{cases}

            \\\text{where }
            \text{PLF}_{r,p,t,v} =
            \begin{cases}
                \frac{1}{\text{LEN}_p} \cdot \left(
                \sum\limits_{y = p}^{p+\text{LEN}_{p}-1}{\text{LSC}_{r,y,t,v}}
                \right)
                & \text{if } t \in T^{sc} \\
                \frac{1}{\text{LEN}_p} \cdot \left( v + \text{LTP}_{r,t,v} - p \right)
                & \text{if } t \notin T^{sc} \\
            \end{cases}

    We divide :math:`\frac{\textbf{RCAP}_{r,p',t,v}}{\text{LSC}_{r,p',t,v}}`
    because the average survival factor in :math:`\text{PLF}_{r,p,t,v}` is indexed to the vintage
    period (the beginning of the survival curve). So, we adjust for the relative survival from
    the time when that retirement occurred (treated here as at the beginning of each period).
    """

    if v in M.time_exist:
        built_capacity = value(M.ExistingCapacity[r, t, v])
    else:
        built_capacity = M.V_NewCapacity[r, t, v]

    early_retirements = 0
    if t in M.tech_retirement:
        early_retirements = sum(
            M.V_RetiredCapacity[r, S_p, t, v] / value(M.LifetimeSurvivalCurve[r, S_p, t, v])
            for S_p in M.time_optimize
            if v < S_p <= p
            and S_p < v + value(M.LifetimeProcess[r, t, v]) - value(M.PeriodLength[S_p])
        )

    remaining_capacity = (built_capacity - early_retirements) * value(M.ProcessLifeFrac[r, p, t, v])
    return M.V_Capacity[r, p, t, v] == remaining_capacity


# ============================================================================
# PRE-COMPUTATION FUNCTIONS
# ============================================================================


def create_capacity_and_retirement_sets(M: 'TemoaModel'):
    """
    Creates and populates component-specific Python sets and dictionaries on the model object.

    This function is called once during model initialization and is responsible for
    creating the sparse indices related to technology capacity, retirement, and
    construction/end-of-life material flows. These data structures are then
    used by other functions in this module to build Pyomo components.

    Populates:
        - M.retirementPeriods: dict mapping (r, t, v) to a set of periods `p`
          where retirement can occur.
        - M.capacityConsumptionTechs: dict mapping (r, v, i) to a set of techs `t`
          that consume commodity `i` for construction.
        - M.retirementProductionProcesses: dict mapping (r, p, o) to a set of `(t, v)`
          processes that produce commodity `o` at end-of-life.
        - M.newCapacity_rtv: set of (r, t, v) for new capacity investments.
        - M.activeCapacityAvailable_rpt: set of (r, p, t) where capacity is active.
        - M.activeCapacityAvailable_rptv: set of (r, p, t, v) where vintage capacity is active.
    """

    logger.debug('Creating capacity, retirement, and construction/EOL sets.')
    # Calculate retirement periods based on lifetime and survival curves
    for r, _i, t, v, _o in M.Efficiency.sparse_iterkeys():
        lifetime = value(M.LifetimeProcess[r, t, v])
        for p in M.time_optimize:
            is_natural_eol = p <= v + lifetime < p + value(M.PeriodLength[p])
            is_early_retire = t in M.tech_retirement and v < p <= v + lifetime - value(
                M.PeriodLength[p]
            )
            is_survival_curve = M.isSurvivalCurveProcess[r, t, v] and v <= p <= v + lifetime

            if t not in M.tech_uncap and any((is_natural_eol, is_early_retire, is_survival_curve)):
                M.retirementPeriods.setdefault((r, t, v), set()).add(p)

    # Link construction materials to technologies
    for r, i, t, v in M.ConstructionInput.sparse_iterkeys():
        M.capacityConsumptionTechs.setdefault((r, v, i), set()).add(t)

    # Link end-of-life materials to retiring technologies
    for r, t, v, o in M.EndOfLifeOutput.sparse_iterkeys():
        if (r, t, v) in M.retirementPeriods:
            for p in M.retirementPeriods[r, t, v]:
                M.retirementProductionProcesses.setdefault((r, p, o), set()).add((t, v))

    # Create active capacity index sets from the now-populated processVintages
    M.newCapacity_rtv = set(
        (r, t, v)
        for r, p, t in M.processVintages
        for v in M.processVintages[r, p, t]
        if t not in M.tech_uncap and v in M.time_optimize
    )
    M.activeCapacityAvailable_rpt = set(
        (r, p, t)
        for r, p, t in M.processVintages
        if M.processVintages[r, p, t] and t not in M.tech_uncap
    )
    M.activeCapacityAvailable_rptv = set(
        (r, p, t, v)
        for r, p, t in M.processVintages
        for v in M.processVintages[r, p, t]
        if t not in M.tech_uncap
    )
