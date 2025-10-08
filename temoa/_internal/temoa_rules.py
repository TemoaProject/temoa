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

from logging import getLogger
from sys import stderr as SE
from typing import TYPE_CHECKING

from pyomo.core import Expression, Var
from pyomo.environ import Constraint, value

from temoa._internal.temoa_initialize import (
    AnnualCommodityBalanceConstraintErrorCheck,
    CommodityBalanceConstraintErrorCheck,
    DemandConstraintErrorCheck,
    gather_group_regions,
    gather_group_techs,
)

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

logger = getLogger(__name__)


# ============================================================================
# Public API - Functions intended for external import
# ============================================================================
__all__ = [
    # Core capacity constraints
    'AdjustedCapacity_Constraint',
    'Capacity_Constraint',
    'CapacityAnnual_Constraint',
    'CapacityAvailableByPeriodAndTech_Constraint',
    # Activity and flow constraints
    'Demand_Constraint',
    'DemandActivity_Constraint',
    'CommodityBalance_Constraint',
    'AnnualCommodityBalance_Constraint',
    # Retirement constraints
    'AnnualRetirement_Constraint',
    # Storage constraints
    'StorageEnergy_Constraint',
    'StorageEnergyUpperBound_Constraint',
    'SeasonalStorageEnergy_Constraint',
    'SeasonalStorageEnergyUpperBound_Constraint',
    'StorageChargeRate_Constraint',
    'StorageDischargeRate_Constraint',
    'StorageThroughput_Constraint',
    # Ramping constraints
    'BaseloadDiurnal_Constraint',
    'RampUpDay_Constraint',
    'RampDownDay_Constraint',
    'RampUpSeason_Constraint',
    'RampDownSeason_Constraint',
    # Limit constraints (capacity, activity, emissions, etc.)
    'LimitActivity_Constraint',
    'LimitActivityShare_Constraint',
    'LimitAnnualCapacityFactor_Constraint',
    'LimitCapacity_Constraint',
    'LimitCapacityShare_Constraint',
    'LimitEmission_Constraint',
    'LimitNewCapacity_Constraint',
    'LimitNewCapacityShare_Constraint',
    'LimitResource_Constraint',
    'LimitSeasonalCapacityFactor_Constraint',
    'LimitStorageFraction_Constraint',
    # Technology split constraints
    'LimitTechInputSplit_Constraint',
    'LimitTechInputSplitAnnual_Constraint',
    'LimitTechInputSplitAverage_Constraint',
    'LimitTechOutputSplit_Constraint',
    'LimitTechOutputSplitAnnual_Constraint',
    'LimitTechOutputSplitAverage_Constraint',
    # Growth/degrowth constraints
    'LimitDegrowthCapacityConstraint_rule',
    'LimitDegrowthNewCapacityConstraint_rule',
    'LimitDegrowthNewCapacityDeltaConstraint_rule',
    'LimitGrowthCapacityConstraint_rule',
    'LimitGrowthNewCapacityConstraint_rule',
    'LimitGrowthNewCapacityDeltaConstraint_rule',
    # Regional and special constraints
    'RegionalExchangeCapacity_Constraint',
    'RenewablePortfolioStandard_Constraint',
    'ReserveMargin_Constraint',
    'LinkedEmissionsTech_Constraint',
    # Parameter calculation rules
    'ParamLoanAnnualize_rule',
    'ParamPeriodLength',
    'ParamProcessLifeFraction_rule',
    'SegFracPerSeason_rule',
    # Objective function
    'TotalCost_rule',
]


# ---------------------------------------------------------------
# Define the derived variables used in the objective function
# and constraints below.
# ---------------------------------------------------------------


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


# devnote: long dead
# def ActivityByTech_Constraint(M: 'TemoaModel', t):
#     r"""
#     This constraint is utilized by the MGA objective function and defines
#     the total activity of a technology over the planning horizon. The first version
#     below applies to technologies with variable output at the timeslice level,
#     and the second version applies to technologies with constant annual output
#     in the :code:`tech_annual` set.

#     .. math::
#        :label: ActivityByTech

#            \textbf{ACT}_{t} = \sum_{R, P, S, D, I, V, O} \textbf{FO}_{r, p, s, d,i, t, v, o}
#            \;
#            \forall t \not\in T^{a}

#            \textbf{ACT}_{t} = \sum_{R, P, I, V, O} \textbf{FOA}_{r, p, i, t, v, o}
#            \;
#            \forall t \in T^{a}
#     """
#     if t not in M.tech_annual:
#         indices = []
#         for s_index in M.FlowVar_rpsditvo:
#             if t in s_index:
#                 indices.append(s_index)
#         activity = sum(M.V_FlowOut[s_index] for s_index in indices)
#     else:
#         indices = []
#         for s_index in M.FlowVarAnnual_rpitvo:
#             if t in s_index:
#                 indices.append(s_index)
#         activity = sum(M.V_FlowOutAnnual[s_index] for s_index in indices)

#     if int is type(activity):
#         return Constraint.Skip

#     expr = M.V_ActivityByTech[t] == activity
#     return expr


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


# devnote:  I don't think this constraint is necessary as if this were violated
#           then V_Capacity would be negative, which isn't allowed anyway
# def RetiredCapacity_Constraint(M: 'TemoaModel', r, p, t, v):
#     r"""

# Temoa allows for the economic retirement of technologies presented in the
# :code:`tech_retirement` set. This constraint sets the upper limit of retired
# capacity to the total installed capacity.
# In the equation below, we set the upper bound of the retired capacity to the
# previous period's total installed capacity (CAPAVL)

# .. math::
#    :label: RetiredCapacity

#    \textbf{CAPRET}_{r, p, t, v} \leq \sum_{V} {PLF}_{r, p, t, v} \cdot \textbf{CAP}_{r, t, v}
#    \\
#    \forall \{r, p, t, v\} \in \Theta_{\text{RetiredCapacity}}
# """
#     if p == M.time_optimize.first():
#         cap_avail = value(M.ExistingCapacity[r, t, v])
#     else:
#         cap_avail = M.V_Capacity[r, M.time_optimize.prev(p), t, v]
#     expr = M.V_RetiredCapacity[r, p, t, v] <= cap_avail
#     return expr


# ---------------------------------------------------------------
# Define the Objective Function
# ---------------------------------------------------------------
def TotalCost_rule(M):
    r"""

    Using the :code:`FlowOut` and :code:`Capacity` variables, the Temoa objective
    function calculates the cost of energy supply, under the assumption that capital
    costs are paid through loans. This implementation sums up all the costs incurred,
    and is defined as :math:`C_{tot} = C_{loans} + C_{fixed} + C_{variable} + C_{emissions}`.
    Each term on the right-hand side represents the cost incurred over the model
    time horizon and discounted to the initial year in the horizon (:math:`{P}_0`).
    The calculation of each term is given below.

    .. math::
        :label: obj_invest

        \begin{aligned}
            C_{loans} =& \sum_{r, t, v \in \Theta_{CI}} CI_{r, t, v} \cdot \textbf{NCAP}_{r, t, v}
            && \text{(overnight capital cost)} \\
            &\cdot \frac{A}{P}(i=\text{LR}_{r,t,v}, N=\text{LLP}_{r,t,v})
            && \text{(overnight cost amortised into annual loan payments)} \\
            &\cdot \frac{P}{A}(i=GDR, N=\text{LLP}_{r,t,v})
            && \text{(annual loan payments discounted to NPV in vintage year)} \\
            &\cdot \frac{A}{P}(i=GDR, N=\text{LTP}_{r,t,v})
            && \text{(NPV reamortised over lifetime of process using GDR)} \\
            &\cdot \frac{P}{A}(i=GDR, N=\min(\text{LTP}_{r,t,v}, P_e - v))
            && \text{(costs within planning horizon discounted to NPV in vintage year)} \\
            &\cdot \frac{P}{F}(i=GDR, N=v - P_0)
            && \text{(NPV in vintage year discounted to base year } P_0\text{)} \\
        \end{aligned}

    Note that capital costs (:math:`{CI}_{r,t,v}`) are handled in several steps.

        1. Each capital cost is amortized using the loan rate (i.e., technology-specific discount rate) and loan period.

        2. The annual stream of payments is converted into a lump sum using the global discount rate and loan period.

        3. The new lump sum is amortized at the global discount rate over the process lifetime.

        4. Loan payments beyond the model time horizon are removed and the lump sum recalculated.

        5. Finally, the lump sum is discounted back to the beginning of the horizon (:math:`P_0`) using the global discount rate.

    Steps 3 and 4 serve to correctly balance the cost-benefit of technologies whose useful lives
    would extend beyond the planning horizon. While an explicit salvage term is not included, this approach properly
    captures the capital costs incurred within the model time horizon, accounting for process-specific loan rates
    and periods.

    In the case of processes using survival curves, steps 3 and 4 do not reamortise costs uniformly over the process lifetime.
    Instead, costs are amortised over the life of the process in proportion to the survival fraction in each year.
    Note that, for this calculation, a survival curve :math:`{LSC}_{r,y,t,v}` must be defined out to the year in which the
    surviving fraction is zero, even if that extends beyond the planning horizon. It must also be defined for each integer
    year between model periods and, if not, these gaps will be filled by linear interpolation ahead of this calculation.

    .. math::
        :label: obj_invest_survival_curve

        \begin{aligned}
            C_{loans,LSC} =& \sum_{r, t, v \in \Theta_{CI}} CI_{r, t, v} \cdot \textbf{NCAP}_{r, t, v}
            && \text{(overnight capital cost)} \\
            &\cdot \frac{A}{P}(i=\text{LR}_{r,t,v}, N=\text{LLP}_{r,t,v})
            && \text{(overnight cost amortised into annual loan payments)} \\
            &\cdot \frac{P}{A}(i=GDR, N=\text{LLP}_{r,t,v})
            && \text{(annual loan payments discounted to NPV in vintage year)} \\
            &\cdot \left(
                \sum_{v < Y} LSC_{r,y,t,v} \cdot \frac{P}{F}(i=GDR, N=P - v + 1)
                \right)^{-1}
            && \text{(reamortised over survival curve (normalized)} \\
            &\cdot \sum_{v < Y < P_e} LSC_{r,y,t,v} \cdot \frac{P}{F}(i=GDR, N=P - v + 1)
            && \text{(costs within planning horizon discounted to NPV in vintage year)} \\
            &\cdot \frac{P}{F}(i=GDR, N=v - P_0)
            && \text{(NPV in vintage year discounted to base year } P_0 \text{)}
        \end{aligned}

    Where :math:`Y` is the set of each integer year :math:`y` within the planning horizon.

    .. figure:: images/survival_curve_discounting.*
        :align: center
        :width: 100%
        :figclass: align-center
        :figwidth: 60%

        Steps 3 and 4 for processes with survival curves.

    Fixed, variable, and emissions annual cost factors are determined by:

    .. math::
       :label: annual_fixed_variable_emission

        \begin{aligned}
            C_{fixed} =& \sum_{r, p, t, v \in \Theta_{CF}} CF_{r, p, t, v} \cdot \textbf{CAP}_{r, p, t, v}
            && \text{(annual fixed cost)} \\
            \\
            C_{variable} =& \sum_{r, p, t \notin T^a, v \in \Theta_{CV}}
            CV_{r, p, t, v} \cdot \sum_{S, D, I, O} \mathbf{FO}_{r, p, s, d, i, t, v, o}
            && \text{(annual variable cost on flow)} \\
            & \text{where } t \notin T^a \\
            &+\\
            & \sum_{r, p, t \in T^a,\ v \in \Theta_{VC}} CV_{r, p, t, v}
            \cdot \sum_{I, O} \mathbf{FOA}_{r, p, i, t, v, o}
            && \text{(annual variable cost on annual flows)} \\
            & \text{where } t \in T^a \\
            &+\\
            C_{emissions} =& \sum_{r, p, e \in \Theta_{CE}} CE_{r, p, e}
            \cdot EAC_{r, i, t, v, o, e} \cdot \sum_{S, D, I, O} \mathbf{FO}_{r, p, s, d, i, t, v, o}
            && \text{(annual emission cost on flow)} \\
            & \text{where } t \notin T^a \\
            &+\\
            & \sum_{r, p, e \in \Theta_{CE}} CE_{r, p, e}
            \cdot EAC_{r, i, t, v, o, e} \cdot \sum_{I, O} \mathbf{FOA}_{r, p, i, t, v, o}
            && \text{(annual emission cost on annual flows)} \\
            & \text{where } t \in T^a \\
            &+\\
            & \sum_{r, p, e \in \Theta_{CE}} \frac{CE_{r, p, e}
            \cdot EE_{r, e, t, v} \cdot \mathbf{NCAP}_{r, t, v=p}}{{LEN}_p}
            && \text{(annual embodied emission cost)} \\
            &+\\
            & \sum_{r, p, e \in \Theta_{CE}, v} CE_{r, p, e}
            \cdot EEOL_{r, e, t, v} \cdot \mathbf{ART}_{r, p, t, v}
            && \text{(annual retirement/end of life emission cost)} \\
        \end{aligned}

    Each of these costs are then discounted within each period and then to the base year:

    .. math::
        :label: obj_fixed_variable_emission

        \begin{aligned}
            C_{fix,var,emiss} =& C_{fixed} + C_{variable} + C_{emissions} \\
            &\cdot \frac{P}{A}(i=GDR,\ N=LEN_p)
            && \text{(for each year in period } p \text{ discounted to NPV in } p \text{)}\\
            &\cdot \frac{P}{F}(i=GDR,\ N=p - P_0)
            && \text{(discounted from period } p \text{ to NPV in base year } P_0 \text{)}
        \end{aligned}
    """

    return sum(PeriodCost_rule(M, p) for p in M.time_optimize)


def annuity_to_pv(rate: float, periods: int) -> float | Expression:
    r"""
    Multiplication factor to convert an annuity to net present value

    .. math::
        :label: annuity_to_pv

        \frac{P}{A}(i, N) = \frac{(1 + i)^N - 1}{i (1 + i)^N}

    where:

    - :math:`i` is the interest/discount rate
    - :math:`N` is the number of periods
    """
    if rate == 0:
        return periods
    return ((1 + rate) ** periods - 1) / (rate * (1 + rate) ** periods)


def pv_to_annuity(rate: float, periods: int) -> float | Expression:
    r"""
    Multiplication factor to convert net present value to an annuity

    .. math::
        :label: pv_to_annuity

        \frac{A}{P}(i, N) = \frac{i + (1 + i)^N}{(1 + i)^N - 1}
    """
    if rate == 0:
        return 1 / periods
    return (rate * (1 + rate) ** periods) / ((1 + rate) ** periods - 1)


def fv_to_pv(rate: float, periods: int) -> float | Expression:
    r"""
    Multiplication factor to convert a future value to net present value

    .. math::
        :label: fv_to_pv

        \frac{P}{F}(i, N) = \frac{1}{(1 + i)^N}
    """
    if rate == 0:
        return 1
    return 1 / (1 + rate) ** periods


def loan_cost(
    capacity: float | Var,
    invest_cost: float,
    loan_annualize: float,
    lifetime_loan_process: float | int,
    lifetime_process: int,
    P_0: int,
    P_e: int,
    GDR: float,
    vintage: int,
) -> float | Expression:
    """
    function to calculate the loan cost.  It can be used with fixed values to produce a hard number or
    pyomo variables/params to make a pyomo Expression
    :param capacity: The capacity to use to calculate cost
    :param invest_cost: the cost/capacity
    :param loan_annualize: parameter
    :param lifetime_loan_process: lifetime of the loan
    :param P_0: the year to discount the costs back to
    :param P_e: the 'end year' or cutoff year for loan payments
    :param GDR: Global Discount Rate
    :param vintage: the base year of the loan
    :return: fixed number or pyomo expression based on input types
    """

    # calculate the amortised loan repayment (annuity)
    annuity = (
        capacity
        * invest_cost  # lump investment cost is capacity times CostInvest
        * loan_annualize  # calculate loan annuities for investment cost, if used
    )

    if not GDR:
        # Undiscounted result
        res = (
            annuity
            * lifetime_loan_process  # sum of loan payments over loan period
            / lifetime_process  # redistributed over lifetime of process
            * min(
                lifetime_process, P_e - vintage
            )  # sum of redistributed costs for life of process (within planning horizon)
        )
    else:
        # Discounted result
        res = (
            annuity
            * annuity_to_pv(
                GDR, lifetime_loan_process
            )  # PV of all loan payments, discounted to vintage year using GDR
            * pv_to_annuity(GDR, lifetime_process)  # reamortised over lifetime of process using GDR
            * annuity_to_pv(
                GDR, min(lifetime_process, P_e - vintage)
            )  # PV of all reamortised costs (within planning horizon)
            * fv_to_pv(GDR, vintage - P_0)  # finally, discounted from vintage year to P_0
        )
    return res


def loan_cost_survival_curve(
    M: 'TemoaModel',
    r: str,
    t: str,
    v: str,
    capacity: float | Var,
    invest_cost: float,
    loan_annualize: float,
    lifetime_loan_process: float | int,
    P_0: int,
    P_e: int,
    GDR: float,
) -> float | Expression:
    """
    function to calculate the loan cost only in the case of processes :math:`(r, t, v)` using
    survival curves. It can be used with fixed values to produce a hard number or pyomo
    variables/params to make a pyomo Expression
    :param capacity: The capacity to use to calculate cost
    :param invest_cost: the cost/capacity
    :param loan_annualize: parameter
    :param lifetime_loan_process: lifetime of the loan
    :param P_0: the year to discount the costs back to
    :param P_e: the 'end year' or cutoff year for loan payments
    :param GDR: Global Discount Rate
    :return: fixed number or pyomo expression based on input types
    """

    # calculate the amortised loan repayment (annuity)
    annuity = (
        capacity
        * invest_cost  # lump investment cost is capacity times CostInvest
        * loan_annualize  # calculate loan annuities for investment cost, if used
    )

    if not GDR:
        # Undiscounted result
        res = (
            annuity
            * lifetime_loan_process  # sum of loan payments over loan period
            / sum(  # redistributed over survival curve within horizon
                value(M.LifetimeSurvivalCurve[r, p, t, v])
                for p in M.survivalCurvePeriods[r, t, v]
                if v <= p
            )
            * sum(  # summed over survival curve within horizon
                value(M.LifetimeSurvivalCurve[r, p, t, v])
                for p in M.survivalCurvePeriods[r, t, v]
                if v <= p < P_e
            )
        )
    else:
        # Discounted result
        res = (
            annuity
            * annuity_to_pv(
                GDR, lifetime_loan_process
            )  # PV of all loan payments, discounted to vintage year using GDR
            / sum(  # redistributed over survival curve within horizon
                value(
                    M.LifetimeSurvivalCurve[r, p, t, v]
                )  # reamortised over survival curve of process using GDR
                * fv_to_pv(GDR, p - v + 1)  # +1 because LSC is indexed to start of p not end of p
                for p in M.survivalCurvePeriods[r, t, v]
                if v <= p  # this shouldnt be possible but play it safe
            )
            * sum(  # PV of all reamortised costs (within planning horizon)
                value(M.LifetimeSurvivalCurve[r, p, t, v]) * fv_to_pv(GDR, p - v + 1)
                for p in M.survivalCurvePeriods[r, t, v]
                if v <= p < P_e
            )
            * fv_to_pv(GDR, v - P_0)  # finally, discounted from vintage year to P_0
        )
    return res


def fixed_or_variable_cost(
    cap_or_flow: float | Var,
    cost_factor: float,
    cost_years: float,
    GDR: float | None,
    P_0: float,
    p: int,
) -> float | Expression:
    """
    Extraction of the fixed and var cost formulation.  (It is same for both with either capacity or
    flow as the driving variable.)
    :param cap_or_flow: Capacity if fixed cost / flow out if variable
    :param cost_factor: the cost (either fixed or variable) of the cap/flow variable
    :param cost_years: for how many years is this cost incurred
    :param GDR: discount rate or None
    :param P_0: the period to discount this back to
    :param p: the period under evaluation
    :return:
    """

    annual_cost = cap_or_flow * cost_factor  # annual fixed, variable, or emission cost

    if not GDR:
        # Undiscounted result
        return annual_cost * cost_years  # annual cost times years paying that cost
    else:
        # Discounted result
        return (
            annual_cost
            * annuity_to_pv(
                GDR, cost_years
            )  # PV of annual costs over this period, discounted to period p
            * fv_to_pv(GDR, p - P_0)  # discounted from p to p_0
        )


def PeriodCost_rule(M: 'TemoaModel', p):
    P_0 = min(M.time_optimize)
    P_e = M.time_future.last()  # End point of modeled horizon
    GDR = value(M.GlobalDiscountRate)
    # MPL = M.ModelProcessLife

    if value(M.MyopicDiscountingYear) != 0:
        P_0 = value(M.MyopicDiscountingYear)

    loan_costs = sum(
        loan_cost(
            M.V_NewCapacity[r, S_t, S_v],
            value(M.CostInvest[r, S_t, S_v]),
            value(M.LoanAnnualize[r, S_t, S_v]),
            value(M.LoanLifetimeProcess[r, S_t, S_v]),
            value(M.LifetimeProcess[r, S_t, S_v]),
            P_0,
            P_e,
            GDR,
            vintage=S_v,
        )
        for r, S_t, S_v in M.CostInvest.sparse_iterkeys()
        if S_v == p and not M.isSurvivalCurveProcess[r, S_t, S_v]
    )
    loan_costs += sum(
        loan_cost_survival_curve(
            M,
            r,
            S_t,
            S_v,
            M.V_NewCapacity[r, S_t, S_v],
            value(M.CostInvest[r, S_t, S_v]),
            value(M.LoanAnnualize[r, S_t, S_v]),
            value(M.LoanLifetimeProcess[r, S_t, S_v]),
            P_0,
            P_e,
            GDR,
        )
        for r, S_t, S_v in M.CostInvest.sparse_iterkeys()
        if S_v == p and M.isSurvivalCurveProcess[r, S_t, S_v]
    )

    fixed_costs = sum(
        fixed_or_variable_cost(
            M.V_Capacity[r, p, S_t, S_v],
            value(M.CostFixed[r, p, S_t, S_v]),
            value(M.PeriodLength[p]),
            GDR,
            P_0,
            p=p,
        )
        for r, S_p, S_t, S_v in M.CostFixed.sparse_iterkeys()
        if S_p == p
    )

    variable_costs = sum(
        fixed_or_variable_cost(
            M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, S_o],
            value(M.CostVariable[r, p, S_t, S_v]),
            value(M.PeriodLength[p]),
            GDR,
            P_0,
            p,
        )
        for r, S_p, S_t, S_v in M.CostVariable.sparse_iterkeys()
        if S_p == p and S_t not in M.tech_annual
        for S_i in M.processInputs[r, S_p, S_t, S_v]
        for S_o in M.processOutputsByInput[r, S_p, S_t, S_v, S_i]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    variable_costs_annual = sum(
        fixed_or_variable_cost(
            M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, S_o],
            value(M.CostVariable[r, p, S_t, S_v]),
            value(M.PeriodLength[p]),
            GDR,
            P_0,
            p,
        )
        for r, S_p, S_t, S_v in M.CostVariable.sparse_iterkeys()
        if S_p == p and S_t in M.tech_annual
        for S_i in M.processInputs[r, S_p, S_t, S_v]
        for S_o in M.processOutputsByInput[r, S_p, S_t, S_v, S_i]
    )

    # The emissions costs occur over the five possible emission sources.
    # to do any/all of them we need 2 baseline sets:  The regular and annual sets
    # of indices that are valid which is basically the filter of:
    #     EmissionActivty by CostEmission
    # and to ensure that the techology is active we need to filter that
    # result with processInput

    # ================= Emissions and Flex and Curtailment =================
    # Flex flows are deducted from V_FlowOut, so it is NOT NEEDED to tax them again.  (See commodity balance constr)
    # Curtailment does not draw any inputs, so it seems logical that curtailed flows not be taxed either
    # Earlier versions of this code had accounting for flex & curtailment that have been removed.

    base = [
        (r, p, e, i, t, v, o)
        for (r, e, i, t, v, o) in M.EmissionActivity.sparse_iterkeys()
        if (r, p, e) in M.CostEmission  # tightest filter first
        and (r, p, t, v) in M.processInputs
    ]

    # then expand the base for the normal (season/tod) set and annual separately:
    normal = [
        (r, p, e, s, d, i, t, v, o)
        for (r, p, e, i, t, v, o) in base
        for s in M.TimeSeason[p]
        for d in M.time_of_day
        if t not in M.tech_annual
    ]

    annual = [(r, p, e, i, t, v, o) for (r, p, e, i, t, v, o) in base if t in M.tech_annual]

    # 1. variable emissions
    var_emissions = sum(
        fixed_or_variable_cost(
            cap_or_flow=M.V_FlowOut[r, p, s, d, i, t, v, o]
            * value(M.EmissionActivity[r, e, i, t, v, o]),
            cost_factor=value(M.CostEmission[r, p, e]),
            cost_years=value(M.PeriodLength[p]),
            GDR=GDR,
            P_0=P_0,
            p=p,
        )
        for (r, p, e, s, d, i, t, v, o) in normal
    )

    # 2. flex emissions -- removed (double counting, flex wastes are SUBTRACTIVE from flowout)

    # 3. curtailment emissions -- removed (curtailment is no-flow, for accounting only, so no emissions)

    # 4. annual emissions
    var_annual_emissions = sum(
        fixed_or_variable_cost(
            cap_or_flow=M.V_FlowOutAnnual[r, p, i, t, v, o]
            * value(M.EmissionActivity[r, e, i, t, v, o]),
            cost_factor=value(M.CostEmission[r, p, e]),
            cost_years=value(M.PeriodLength[p]),
            GDR=GDR,
            P_0=P_0,
            p=p,
        )
        for (r, p, e, i, t, v, o) in annual
        if t not in M.tech_flex
    )

    # 5. flex annual emissions -- removed (double counting, flex wastes are SUBTRACTIVE from flowout)

    # 6. embodied - treated as a fixed cost distributed over the deployment period (vintage)
    embodied_emissions = sum(
        fixed_or_variable_cost(
            cap_or_flow=M.V_NewCapacity[r, t, v]
            * value(M.EmissionEmbodied[r, e, t, v])
            / value(M.PeriodLength[p]),
            cost_factor=value(M.CostEmission[r, p, e]),
            cost_years=M.PeriodLength[
                v
            ],  # We assume the embodied emissions are emitted in the same year as the capacity is installed.
            GDR=GDR,
            P_0=P_0,
            p=p,
        )
        for (r, e, t, v) in M.EmissionEmbodied.sparse_iterkeys()
        if (r, p, e) in M.CostEmission
        if v == p
    )

    # 6. endoflife - treated as a fixed cost distributed over the retirement period
    endoflife_emissions = sum(
        fixed_or_variable_cost(
            cap_or_flow=M.V_AnnualRetirement[r, p, t, v] * value(M.EmissionEndOfLife[r, e, t, v]),
            cost_factor=value(M.CostEmission[r, p, e]),
            cost_years=M.PeriodLength[
                p
            ],  # We assume the embodied emissions are emitted in the same year as the capacity is installed.
            GDR=GDR,
            P_0=P_0,
            p=p,
        )
        for (r, e, t, v) in M.EmissionEndOfLife.sparse_iterkeys()
        if (r, p, e) in M.CostEmission
        if (r, t, v) in M.retirementPeriods and p in M.retirementPeriods[r, t, v]
    )

    period_emission_cost = (
        var_emissions + var_annual_emissions + embodied_emissions + endoflife_emissions
    )

    period_costs = (
        loan_costs + fixed_costs + variable_costs + variable_costs_annual + period_emission_cost
    )
    return period_costs


# ---------------------------------------------------------------
# Define the Model Constraints.
# The order of constraint definitions follows the same order as the
# declarations in temoa_model.py.
# ---------------------------------------------------------------


def Demand_Constraint(M: 'TemoaModel', r, p, dem):
    r"""

    The Demand constraint drives the model.  This constraint ensures that supply at
    least meets the demand specified by the Demand parameter in all periods and
    slices, by ensuring that the sum of all the demand output commodity (:math:`c`)
    generated by both commodity flow at the time slice level (:math:`\textbf{FO}`) and
    the annual level (:math:`\textbf{FOA}`) must meet the modeler-specified demand
    in each time slice.

    .. math::
       :label: Demand

           \sum_{I, T-T^{a}, V} \textbf{FO}_{r, p, s, d, i, t \not \in T^{a}, v, dem} +
           SEG_{s,d} \cdot  \sum_{I, T^{a}, V} \textbf{FOA}_{r, p, i, t \in T^{a}, v, dem}
           =
           {DEM}_{r, p, dem} \cdot {DSD}_{r, s, d, dem}

    Note that the validity of this constraint relies on the fact that the
    :math:`C^d` set is distinct from both :math:`C^e` and :math:`C^p`. In other
    words, an end-use demand must only be an end-use demand.  Note that if an output
    could satisfy both an end-use and internal system demand, then the output from
    :math:`\textbf{FO}` and :math:`\textbf{FOA}` would be double counted."""

    # All demand techs are annual now
    # supply = sum(
    #     M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, dem]
    #     for S_t, S_v in M.commodityUStreamProcess[r, p, dem]
    #     if S_t not in M.tech_annual
    #     for S_i in M.processInputsByOutput[r, p, S_t, S_v, dem]
    # )

    supply_annual = sum(
        M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, dem]
        for S_t, S_v in M.commodityUStreamProcess[r, p, dem]
        for S_i in M.processInputsByOutput[r, p, S_t, S_v, dem]
    )

    DemandConstraintErrorCheck(supply_annual, r, p, dem)

    expr = supply_annual == value(M.Demand[r, p, dem])

    return expr


# devnote: no longer needed
def DemandActivity_Constraint(M: 'TemoaModel', r, p, s, d, t, v, dem):
    r"""

    For end-use demands, it is unreasonable to let the model arbitrarily shift the
    use of demand technologies across time slices. For instance, if household A buys
    a natural gas furnace while household B buys an electric furnace, then both units
    should be used throughout the year.  Without this constraint, the model might choose
    to only use the electric furnace during the day, and the natural gas furnace during the
    night.

    This constraint ensures that the ratio of a process activity to demand is
    constant for all time slices.  Note that if a demand is not specified in a given
    time slice, or is zero, then this constraint will not be considered for that
    slice and demand.  This is transparently handled by the :math:`\Theta` superset.

    .. math::
       :label: DemandActivity

          DEM_{r, p, s, d, dem} \cdot \sum_{I} \textbf{FO}_{r, p, s_0, d_0, i, t \not \in T^{a}, v, dem}
       =
          DEM_{r, p, s_0, d_0, dem} \cdot \sum_{I} \textbf{FO}_{r, p, s, d, i, t \not \in T^{a}, v, dem}

       \\
       \forall \{r, p, s, d, t, v, dem, s_0, d_0\} \in \Theta_{\text{DemandActivity}}

    Note that this constraint is only applied to the demand commodities with diurnal
    variations, and therefore the equation above only includes :math:`\textbf{FO}`
    and not  :math:`\textbf{FOA}`
    """

    activity = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, dem] for S_i in M.processInputsByOutput[r, p, t, v, dem]
    )

    annual_activity = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, dem] for S_i in M.processInputsByOutput[r, p, t, v, dem]
    )

    expr = annual_activity * value(M.DemandSpecificDistribution[r, p, s, d, dem]) == activity
    return expr


def CommodityBalance_Constraint(M: 'TemoaModel', r, p, s, d, c):
    r"""
    Where the Demand constraint :eq:`Demand` ensures that end-use demands are met,
    the CommodityBalance constraint ensures that the endogenous system demands are
    met.  This constraint requires the total production of a given commodity
    to equal the amount consumed, thus ensuring an energy balance at the system
    level. In this most general form of the constraint, the energy commodity being
    balanced has variable production at the time slice level. The energy commodity
    can then be consumed by three types of processes: storage technologies, non-storage
    technologies with output that varies at the time slice level, and non-storage
    technologies with constant annual output.

    Separate expressions are required in order to account for the consumption of
    commodity :math:`c` by downstream processes. For the commodity flow into storage
    technologies, we use :math:`\textbf{FI}_{r, p, s, d, i, t, v, c}`. Note that the FlowIn
    variable is defined only for storage technologies, and is required because storage
    technologies balance production and consumption across time slices rather than
    within a single time slice. For commodity flows into non-storage processes with time
    varying output, we use :math:`\textbf{FO}_{r, p, s, d, i, t, v, c}/EFF_{r, i,t,v,o}`.
    The division by :math:`EFF_{r, c,t,v,o}` is applied to the output flows that consume
    commodity :math:`c` to determine input flows. Finally, we need to account
    for the consumption of commodity :math:`c` by the processes in
    :code:`tech_annual`. Since the commodity flow of these processes is on an
    annual basis, we use :math:`SEG_{s,d}` to calculate the consumption of
    commodity :math:`c` in time-slice :math:`(s,d)` from the annual flows.
    Formulating an expression for the production of commodity :math:`c` is
    more straightforward, and is simply calculated by
    :math:`\textbf{FO}_{r, p, s, d, i, t, v, c}`.

    In some cases, the overproduction of a commodity may be required, such
    that the supply exceeds the endogenous demand. Refineries represent a
    common example, where the share of different refined products are governed
    by TechOutputSplit, but total production is driven by a particular commodity
    like gasoline. Such a situation can result in the overproduction of other
    refined products, such as diesel or kerosene. In such cases, we need to
    track the excess production of these commodities. To do so, the technology
    producing the excess commodity should be added to the :code:`tech_flex` set.
    This flexible technology designation will activate a slack variable
    (:math:`\textbf{FLX}_{r, p, s, d, i, t, v, c}`) representing
    the excess production in the :code:`CommodityBalanceAnnual_Constraint`. Note
    that the :code:`tech_flex` set is different from :code:`tech_curtailment` set;
    the latter is technology- rather than commodity-focused and is used in the
    :code:`Capacity_Constraint` to track output that is used to produce useful
    output and the amount curtailed, and to ensure that the installed capacity
    covers both. Alternatively, the commodity can be added to the
    :code:`commodity_waste` set, for which this equality constraint becomes an
    inequality constraint, allowing production to exceed consumption for a single
    commodity.

    This constraint also accounts for imports and exports between regions
    when solving multi-regional systems. The import (:math:`\textbf{FIM}`) and export
    (:math:`\textbf{FEX}`) variables are created on-the-fly by summing the
    :math:`\textbf{FO}` variables over the appropriate import and export regions,
    respectively, which are defined in :code:`temoa_initialize.py` by parsing the
    :code:`tech_exchange` processes.

    Consumption of the commodity by construction inputs is annualised using the period
    length. Production of the commodity by end-of-life outputs uses the AnnualRetirement
    variable, which is already annualised.

    Finally, for annual commodities, AnnualCommodityBalance is used which balances
    the sum of flows over each year.

    *process outputs + imports + end of life outputs = process inputs + construction inputs + exports + flex waste*

    .. math::
       :label: CommodityBalance

            \begin{aligned}
            &\sum_{I, t \notin T^a, V} \mathbf{FO}_{r, p, s, d, i, t, v, c}
            && \text{(processes outputting commodity)} \\
            &+ SEG_{s,d} \cdot \sum_{I, t \in T^a, V} \frac{\mathbf{FOA}_{r, p, i, t, v, c}}{EFF_{r, i, t, v, c}}
            && \text{(annual processes outputting commodity)} \\
            &+ \sum_{\text{reg} \neq r, I, t \in T^x, V} \mathbf{FIM}_{r - \text{reg}, p, s, d, i, t, v, c}
            && \text{(inter-regional imports of commodity)} \\
            &+ SEG_{s,d} \sum_{T, V} \left ( EOLO_{r, t, v, c} \cdot \textbf{ART}_{r, p, t, v} \right )
            && \text{(end-of-life outputs of commodity)} \\
            &\begin{cases}
            &= \text{if } c \notin C^w \\
            &\geq \text{if } c \in C^w \end{cases} \\
            &\sum_{t \in T^s, V, O} \mathbf{FIS}_{r, p, s, d, c, t, v, o}
            && \text{(commodity stored)} \\
            &+ \sum_{t \notin T^s, V, O} \frac{\mathbf{FO}_{r, p, s, d, c, t, v, o}}{EFF_{r, c, t, v, o}}
            && \text{(commodity consumed by processes)} \\
            &+ SEG_{s,d} \cdot \sum_{t \in T^a, V, O} \frac{\mathbf{FOA}_{r, p, c, t, v, o}}{EFF_{r, c, t, v, o}}
            && \text{(commodity consumed by annual processes)} \\
            &+ \sum_{\text{reg} \neq r, t \in T^x, V, O} \mathbf{FEX}_{r - \text{reg}, p, s, d, c, t, v, o}
            && \text{(inter-regional exports of commodity)} \\
            &+ \sum_{I, t \in T^f, V} \mathbf{FLX}_{r, p, s, d, i, t, v, c}
            && \text{(flex wastes of commodity)} \\
            &+ SEG_{s,d} \cdot \sum_{T, V} \left ( CON_{r, c, t, v} \cdot \frac{\textbf{NCAP}_{r, t, v}}{LEN_p} \right )
            && \text{(consumed annually by construction inputs)}
            \end{aligned}

            \qquad \forall \{r, p, s, d, c\} \in \Theta_{\text{CommodityBalance}}

    """

    produced = 0
    consumed = 0

    if (r, p, c) in M.commodityDStreamProcess:
        # Only storage techs have a flow in variable
        # For other techs, it would be redundant as in = out / eff
        consumed += sum(
            M.V_FlowIn[r, p, s, d, c, S_t, S_v, S_o]
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t in M.tech_storage
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        # Into flows
        consumed += sum(
            M.V_FlowOut[r, p, s, d, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r, p, s, d, c, S_t, S_v, S_o)
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t not in M.tech_storage and S_t not in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        # Into annual flows
        consumed += sum(
            (
                value(M.DemandSpecificDistribution[r, p, s, d, S_o])
                if S_o in M.commodity_demand
                else value(M.SegFrac[p, s, d])
            )
            * M.V_FlowOutAnnual[r, p, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r, p, s, d, c, S_t, S_v, S_o)
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

    if (r, p, c) in M.capacityConsumptionTechs:
        # Consumed by building capacity
        # Assume evenly distributed over a year
        consumed += (
            value(M.SegFrac[p, s, d])
            * sum(
                value(M.ConstructionInput[r, c, S_t, p]) * M.V_NewCapacity[r, S_t, p]
                for S_t in M.capacityConsumptionTechs[r, p, c]
            )
            / M.PeriodLength[p]
        )

    if (r, p, c) in M.commodityUStreamProcess:
        # From flows including output from storage
        produced += sum(
            M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, c]
            for S_t, S_v in M.commodityUStreamProcess[r, p, c]
            if S_t not in M.tech_annual
            for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
        )

        # From annual flows
        produced += value(M.SegFrac[p, s, d]) * sum(
            M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, c]
            for S_t, S_v in M.commodityUStreamProcess[r, p, c]
            if S_t in M.tech_annual
            for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
        )

        if c in M.commodity_flex:
            # Wasted by flex flows
            consumed += sum(
                M.V_Flex[r, p, s, d, S_i, S_t, S_v, c]
                for S_t, S_v in M.commodityUStreamProcess[r, p, c]
                if S_t not in M.tech_annual and S_t in M.tech_flex
                for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
            )
            # Wasted by annual flex flows
            consumed += value(M.SegFrac[p, s, d]) * sum(
                M.V_FlexAnnual[r, p, S_i, S_t, S_v, c]
                for S_t, S_v in M.commodityUStreamProcess[r, p, c]
                if S_t in M.tech_annual and S_t in M.tech_flex
                for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
            )

    if (r, p, c) in M.retirementProductionProcesses:
        # Produced by retiring capacity
        # Assume evenly distributed over a year
        produced += value(M.SegFrac[p, s, d]) * sum(
            value(M.EndOfLifeOutput[r, S_t, S_v, c]) * M.V_AnnualRetirement[r, p, S_t, S_v]
            for S_t, S_v in M.retirementProductionProcesses[r, p, c]
        )

    # export of commodity c from region r to other regions
    if (r, p, c) in M.exportRegions:
        consumed += sum(
            M.V_FlowOut[r + '-' + reg, p, s, d, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r + '-' + reg, p, s, d, c, S_t, S_v, S_o)
            for reg, S_t, S_v, S_o in M.exportRegions[r, p, c]
            if S_t not in M.tech_annual
        )
        consumed += sum(
            value(M.SegFrac[p, s, d])
            * M.V_FlowOutAnnual[r + '-' + reg, p, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r + '-' + reg, p, s, d, c, S_t, S_v, S_o)
            for reg, S_t, S_v, S_o in M.exportRegions[r, p, c]
            if S_t in M.tech_annual
        )

    # import of commodity c from other regions into region r
    if (r, p, c) in M.importRegions:
        produced += sum(
            M.V_FlowOut[reg + '-' + r, p, s, d, S_i, S_t, S_v, c]
            for reg, S_t, S_v, S_i in M.importRegions[r, p, c]
            if S_t not in M.tech_annual
        )
        produced += sum(
            value(M.SegFrac[p, s, d]) * M.V_FlowOutAnnual[reg + '-' + r, p, S_i, S_t, S_v, c]
            for reg, S_t, S_v, S_i in M.importRegions[r, p, c]
            if S_t in M.tech_annual
        )

    CommodityBalanceConstraintErrorCheck(
        produced,
        consumed,
        r,
        p,
        s,
        d,
        c,
    )

    if c in M.commodity_waste:
        expr = produced >= consumed
    else:
        expr = produced == consumed

    return expr


def AnnualCommodityBalance_Constraint(M: 'TemoaModel', r, p, c):
    r"""
    Similar to CommodityBalance_Constraint but only balances the supply and demand of the commodity
    at the period level, summing all flows over the period but allowing imbalances at the time slice
    or seasonal level. Applies only to commodities in the :code:`commodity_annual` set.
    """

    produced = 0
    consumed = 0

    if (r, p, c) in M.commodityDStreamProcess:
        # Only storage techs have a flow in variable
        # For other techs, it would be redundant as in = out / eff
        consumed += sum(
            M.V_FlowIn[r, p, S_s, S_d, c, S_t, S_v, S_o]
            for S_s in M.TimeSeason[p]
            for S_d in M.time_of_day
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t in M.tech_storage
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        consumed += sum(
            M.V_FlowOut[r, p, S_s, S_d, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r, p, S_s, S_d, c, S_t, S_v, S_o)
            for S_s in M.TimeSeason[p]
            for S_d in M.time_of_day
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t not in M.tech_storage and S_t not in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        consumed += sum(
            M.V_FlowOutAnnual[r, p, c, S_t, S_v, S_o] / value(M.Efficiency[r, c, S_t, S_v, S_o])
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

    if (r, p, c) in M.capacityConsumptionTechs:
        # Consumed by building capacity
        # Assume evenly distributed over a year
        consumed += (
            sum(
                value(M.ConstructionInput[r, c, S_t, p]) * M.V_NewCapacity[r, S_t, p]
                for S_t in M.capacityConsumptionTechs[r, p, c]
            )
            / M.PeriodLength[p]
        )

    if (r, p, c) in M.commodityUStreamProcess:
        # Includes output from storage
        produced += sum(
            M.V_FlowOut[r, p, S_s, S_d, S_i, S_t, S_v, c]
            for S_s in M.TimeSeason[p]
            for S_d in M.time_of_day
            for S_t, S_v in M.commodityUStreamProcess[r, p, c]
            if S_t not in M.tech_annual
            for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
        )

        produced += sum(
            M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, c]
            for S_t, S_v in M.commodityUStreamProcess[r, p, c]
            if S_t in M.tech_annual
            for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
        )

        if c in M.commodity_flex:
            consumed += sum(
                M.V_Flex[r, p, S_s, S_d, S_i, S_t, S_v, c]
                for S_s in M.TimeSeason[p]
                for S_d in M.time_of_day
                for S_t, S_v in M.commodityUStreamProcess[r, p, c]
                if S_t not in M.tech_annual and S_t in M.tech_flex
                for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
            )
            consumed += sum(
                M.V_FlexAnnual[r, p, S_i, S_t, S_v, c]
                for S_t, S_v in M.commodityUStreamProcess[r, p, c]
                if S_t in M.tech_flex and S_t in M.tech_annual
                for S_i in M.processInputsByOutput[r, p, S_t, S_v, c]
            )

    if (r, p, c) in M.retirementProductionProcesses:
        # Produced by retiring capacity
        # Assume evenly distributed over a year
        produced += sum(
            value(M.EndOfLifeOutput[r, S_t, S_v, c]) * M.V_AnnualRetirement[r, p, S_t, S_v]
            for S_t, S_v in M.retirementProductionProcesses[r, p, c]
        )

    # export of commodity c from region r to other regions
    if (r, p, c) in M.exportRegions:
        consumed += sum(
            M.V_FlowOut[r + '-' + S_r, p, S_s, S_d, c, S_t, S_v, S_o]
            / get_variable_efficiency(M, r + '-' + S_r, p, S_s, S_d, c, S_t, S_v, S_o)
            for S_s in M.TimeSeason[p]
            for S_d in M.time_of_day
            for S_r, S_t, S_v, S_o in M.exportRegions[r, p, c]
            if S_t not in M.tech_annual
        )
        consumed += sum(
            M.V_FlowOutAnnual[r + '-' + S_r, p, c, S_t, S_v, S_o]
            / M.Efficiency[r + '-' + S_r, c, S_t, S_v, S_o]
            for S_r, S_t, S_v, S_o in M.exportRegions[r, p, c]
            if S_t in M.tech_annual
        )

    # import of commodity c from other regions into region r
    if (r, p, c) in M.importRegions:
        produced += sum(
            M.V_FlowOut[S_r + '-' + r, p, S_s, S_d, S_i, S_t, S_v, c]
            for S_s in M.TimeSeason[p]
            for S_d in M.time_of_day
            for S_r, S_t, S_v, S_i in M.importRegions[r, p, c]
            if S_t not in M.tech_annual
        )
        produced += sum(
            M.V_FlowOutAnnual[S_r + '-' + r, p, S_i, S_t, S_v, c]
            for S_r, S_t, S_v, S_i in M.importRegions[r, p, c]
            if S_t in M.tech_annual
        )

    AnnualCommodityBalanceConstraintErrorCheck(
        produced,
        consumed,
        r,
        p,
        c,
    )

    if c in M.commodity_waste:
        expr = produced >= consumed
    else:
        expr = produced == consumed

    return expr


# Devnote: Not currently active
# def ResourceExtraction_Constraint(M: 'TemoaModel', reg, p, r):
#     r"""
#     The ResourceExtraction constraint allows a modeler to specify an annual limit on
#     the amount of a particular resource Temoa may use in a period. The first version
#     of the constraint pertains to technologies with variable output at the time slice
#     level, and the second version pertains to technologies with constant annual output
#     belonging to the :code:`tech_annual` set.

#     .. math::
#        :label: ResourceExtraction

#        \sum_{S, D, I, t \in T^r \& t \not \in T^{a}, V} \textbf{FO}_{r, p, s, d, i, t, v, c} \le RSC_{r, p, c}

#        \forall \{r, p, c\} \in \Theta_{\text{ResourceExtraction}}

#        \sum_{I, t \in T^r \& t \in T^{a}, V} \textbf{FOA}_{r, p, i, t, v, c} \le RSC_{r, p, c}

#        \forall \{r, p, c\} \in \Theta_{\text{ResourceExtraction}}
#     """
#     logger.warning(
#         'The ResourceBound parameter / ResourceExtraction constraint is not currently supported.  '
#         'Recommend removing data from supporting table'
#     )
#     # dev note:  This constraint does not have a table in the current schema
#     #            Additionally, the below (incorrect) construct assumes that a resource cannot be used
#     #            by BOTH a non-annual and annual tech.  It should be re-written to add these
#     # dev note:  Cant think of a case where this would be needed but cant use LimitActivityGroup
#     try:
#         collected = sum(
#             M.V_FlowOut[reg, p, S_s, S_d, S_i, S_t, S_v, r] # is r the input or the output!?
#             for S_i, S_t, S_v in M.processByPeriodAndOutput
#             for S_s in M.TimeSeason[p]
#             for S_d in M.time_of_day
#         )
#     except KeyError:
#         collected = sum(
#             M.V_FlowOutAnnual[reg, p, S_i, S_t, S_v, r]
#             for S_i, S_t, S_v in M.processByPeriodAndOutput
#         )

#     expr = collected <= value(M.ResourceBound[reg, p, r])
#     return expr


def BaseloadDiurnal_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    r"""

    Some electric generators cannot ramp output over a short period of time (e.g.,
    hourly or daily). Temoa models this behavior by forcing technologies in the
    :code:`tech_baseload` set to maintain a constant output across all times-of-day
    within the same season. Note that the output of a baseload process can vary
    between seasons.

    Ideally, this constraint would not be necessary, and baseload processes would
    simply not have a :math:`d` index.  However, implementing the more efficient
    functionality is currently on the Temoa TODO list.

    .. math::
       :label: BaseloadDaily

             SEG_{s, D_0}
       \cdot \sum_{I, O} \textbf{FO}_{r, p, s, d,i, t, v, o}
       =
             SEG_{s, d}
       \cdot \sum_{I, O} \textbf{FO}_{r, p, s, D_0,i, t, v, o}

       \\
       \forall \{r, p, s, d, t, v\} \in \Theta_{\text{BaseloadDiurnal}}
    """
    # Question: How to set the different times of day equal to each other?

    # Step 1: Acquire a "canonical" representation of the times of day
    l_times = sorted(M.time_of_day)  # i.e. a sorted Python list.
    # This is the commonality between invocations of this method.

    index = l_times.index(d)
    if 0 == index:
        # When index is 0, it means that we've reached the beginning of the array
        # For the algorithm, this is a terminating condition: do not create
        # an effectively useless constraint
        return Constraint.Skip

    # Step 2: Set the rest of the times of day equal in output to the first.
    # i.e. create a set of constraints that look something like:
    # tod[ 2 ] == tod[ 1 ]
    # tod[ 3 ] == tod[ 1 ]
    # tod[ 4 ] == tod[ 1 ]
    # and so on ...
    d_0 = l_times[0]

    # Step 3: the actual expression.  For baseload, must compute the /average/
    # activity over the segment.  By definition, average is
    #     (segment activity) / (segment length)
    # So:   (ActA / SegA) == (ActB / SegB)
    #   computationally, however, multiplication is cheaper than division, so:
    #       (ActA * SegB) == (ActB * SegA)
    activity_sd = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    activity_sd_0 = sum(
        M.V_FlowOut[r, p, s, d_0, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = activity_sd * value(M.SegFrac[p, s, d_0]) == activity_sd_0 * value(M.SegFrac[p, s, d])

    return expr


def RegionalExchangeCapacity_Constraint(M: 'TemoaModel', r_e, r_i, p, t, v):
    r"""

    This constraint ensures that the process (t,v) connecting regions
    r_e and r_i is handled by one capacity variables.

    .. math::
       :label: RegionalExchangeCapacity

          \textbf{CAP}_{r_e,t,v}
          =
          \textbf{CAP}_{r_i,t,v}

          \\
          \forall \{r_e, r_i, t, v\} \in \Theta_{\text{RegionalExchangeCapacity}}
    """

    expr = M.V_Capacity[r_e + '-' + r_i, p, t, v] == M.V_Capacity[r_i + '-' + r_e, p, t, v]

    return expr


def StorageEnergy_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    r"""
    This constraint enforces the continuity of storage level between time slices.
    storage level in the next time slice (:math:`s_{next}, d_{next}`) is equal to
    current storage level plus net charge in the current time slice.

    .. math::
        :label: Storage Energy

            {SL}_{r,p,s,d,t,v}
            + \sum\limits_{I,O} \mathbf{FIS}_{r,p,s,d,i,t,v,o} \cdot {EFF}_{r,i,t,v,o}
            - \sum\limits_{I,O} \mathbf{FO}_{r,p,s,d,i,t,v,o}
            = {SL}_{r,p,s_{{next}},d_{{next}},t,v}

    Note that for all seasonal representations except consecutive_days, the last time slice
    of each season will loop back to the first time slice of the same season, preventing
    seasonal deltas for non-seasonal storage (see SeasonalStorageEnergyUpperBound).
    """

    # We allow a non-zero daily delta only in the case of seasonal storage
    if M.isSeasonalStorage[t] and d == M.time_of_day.last():
        return Constraint.Skip  # handled by SeasonalStorageEnergy_Constraint

    # This is the sum of all input=i sent TO storage tech t of vintage v with
    # output=o in p,s,d
    charge = sum(
        M.V_FlowIn[r, p, s, d, S_i, t, v, S_o]
        * get_variable_efficiency(M, r, p, s, d, S_i, t, v, S_o)
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    # This is the sum of all output=o withdrawn FROM storage tech t of vintage v
    # with input=i in p,s,d
    discharge = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for S_o in M.processOutputs[r, p, t, v]
        for S_i in M.processInputsByOutput[r, p, t, v, S_o]
    )

    stored_energy = charge - discharge

    s_next, d_next = M.time_next[p, s, d]

    expr = (
        M.V_StorageLevel[r, p, s, d, t, v] + stored_energy
        == M.V_StorageLevel[r, p, s_next, d_next, t, v]
    )

    return expr


def SeasonalStorageEnergy_Constraint(M: 'TemoaModel', r, p, s_seq, t, v):
    r"""
    This constraint enforces the continuity of state of charge between seasons for seasonal
    storage. Sequential season storage level increases by the matched season's net charge
    over that entire day, adjusted for number of days represented by sequential vs non-sequential
    seasons. Only applies to storage technologies in the :code:`tech_seasonal_storage` set.
    :math:`s^*` represents the matching non-sequential season for the sequential season
    :math:`s^{seq}`.

    .. math::
        :label: Storage Energy (Sequential Seasons)

        \mathbf{SSL}_{r,p,s^{seq},t,v}
        + DA_{r,p,s^{seq}} \cdot \left(\mathbf{SL}_{r,p,s^*,d_{last},t,v} +
        \sum_{I,O} \mathbf{FI}_{r,p,s^*,d_{last},i,t,v,o} \cdot EFF_{r,i,t,v,o}
        - \sum_{I,O} \mathbf{FO}_{r,p,s^*,d_{last},i,t,v,o}
        \right)

        = DA_{r,p,s^{seq}_{next}} \cdot \mathbf{SL}_{r,p,s_{next}^*,d_{first},t,v}
        + \mathbf{SSL}_{r,p,s^{seq}_{next},t,v}

        \\
        \text{where } DA_{r,p,s^{seq}} = \frac{\#days_{s^{seq}}}{SEG_{r,p,s^*} \cdot DPP}

    .. figure:: images/ldes_chain.*
        :align: center
        :width: 100%
        :figclass: align-center
        :figwidth: 60%

        How sequential seasons chain together for seasonal storage. Hatched area is
        SeasonalStorageLevel :math:`SSL_{r,p,s^{seq},t,v}`. Vertical lines are
        StorageLevel :math:`SL_{r,p,s^*,d,t,v}`. Green line is net seasonal storage
        level :math:`SSL_{r,p,s^{seq},t,v} + SL_{r,p,s^*,d,t,v}`. Background grey
        lines show how storage levels from non-sequential seasons are combined
        in sequential seasons. Dashed line is SeasonalStorageEnergyUpperBound.
        Sequential seasons two and four here are each two days while one and three
        are each one day.
    """

    s = M.sequential_to_season[p, s_seq]

    # This is the sum of all input=i sent TO storage tech t of vintage v with
    # output=o in p,s
    charge = sum(
        M.V_FlowIn[r, p, s, M.time_of_day.last(), S_i, t, v, S_o]
        * get_variable_efficiency(M, r, p, s, M.time_of_day.last(), S_i, t, v, S_o)
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    # This is the sum of all output=o withdrawn FROM storage tech t of vintage v
    # with input=i in p,s
    discharge = sum(
        M.V_FlowOut[r, p, s, M.time_of_day.last(), S_i, t, v, S_o]
        for S_o in M.processOutputs[r, p, t, v]
        for S_i in M.processInputsByOutput[r, p, t, v, S_o]
    )

    s_seq_next = M.time_next_sequential[p, s_seq]
    s_next = M.sequential_to_season[p, s_seq_next]

    # Flows and StorageLevel are normalised to the number of days in the non-sequential season, so must
    # be adjusted to the number of days in the sequential season
    days_adjust = value(M.TimeSeasonSequential[p, s_seq, s]) / (
        value(M.SegFracPerSeason[p, s]) * value(M.DaysPerPeriod)
    )
    days_adjust_next = value(M.TimeSeasonSequential[p, s_seq_next, s_next]) / (
        value(M.SegFracPerSeason[p, s_next]) * value(M.DaysPerPeriod)
    )

    stored_energy = (charge - discharge) * days_adjust

    start = (
        M.V_SeasonalStorageLevel[r, p, s_seq, t, v]
        + M.V_StorageLevel[r, p, s, M.time_of_day.last(), t, v] * days_adjust
    )
    end = (
        M.V_SeasonalStorageLevel[r, p, s_seq_next, t, v]
        + M.V_StorageLevel[r, p, s_next, M.time_of_day.first(), t, v] * days_adjust_next
    )

    expr = start + stored_energy == end
    return expr


def StorageEnergyUpperBound_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    r"""
    This constraint ensures that the amount of energy stored does not exceed
    the upper bound set by the energy capacity of the storage device, as calculated
    on the right-hand side.

    Because the number and duration of time slices are user-defined, we need to adjust
    the storage duration, which is specified in hours. First, the hourly duration is divided
    by the number of hours in a year to obtain the duration as a fraction of the year.
    Since the :math:`C2A` parameter assumes the conversion of capacity to annual activity,
    we need to express the storage duration as fraction of a year. Then, :math:`SEG_{s,d}`
    summed over the time-of-day slices (:math:`d`) multiplied by :math:`DPP` yields the
    number of days per season. This step is necessary because conventional time sliced models
    use a single day to represent many days within a given season. Thus, it is necessary to
    scale the storage duration to account for the number of days in each season.

    .. math::
       :label: StorageEnergyUpperBound

          \textbf{SL}_{r, p, s, d, t, v} \le
          \textbf{CAP}_{r,t,v} \cdot C2A_{r,t} \cdot \frac {SD_{r,t}}{24 \cdot DPP}
          \cdot \sum_{d} SEG_{s,d} \cdot DPP

          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{StorageEnergyUpperBound}}

    A season can represent many days. Within each season, flows are multiplied by the
    number of days each season represents and, so, the upper bound needs to be adjusted
    to allow day-scale flows (e.g., charge in the morning, discharge in the afternoon).

    .. figure:: images/daily_storage_representation.*
        :align: center
        :width: 100%
        :figclass: center
        :figwidth: 40%

        Representation of a 3-day season for non-seasonal (daily) storage.
    """

    if M.isSeasonalStorage[t]:
        return Constraint.Skip  # redundant on SeasonalStorageEnergyUpperBound

    energy_capacity = (
        M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * (value(M.StorageDuration[r, t]) / (24 * value(M.DaysPerPeriod)))
        * value(M.SegFracPerSeason[p, s])
        * M.DaysPerPeriod  # adjust for days in season
    )

    expr = M.V_StorageLevel[r, p, s, d, t, v] <= energy_capacity

    return expr


def SeasonalStorageEnergyUpperBound_Constraint(M: 'TemoaModel', r, p, s_seq, d, t, v):
    r"""
    Builds off of StorageEnergyUpperBound_Constraint. Enforces the max charge capacity
    of seasonal storage, summing the real storage level with the superimposed sequential
    seasonal storage level. :math:`s^*` represents the matching non-sequential season for
    the sequential season :math:`s^{seq}`.

    .. math::
        :label: Seasonal Storage Energy Capacity

        \mathbf{SSL}_{r,p,s^{seq},t,v}
        + \mathbf{SL}_{r,p,s^*,d,t,v} \cdot DA_{r,p,s^{seq}}
        \leq \mathbf{CAP}_{r,p,t,v} \cdot C2A_{r,t} \cdot \frac{SD_{r,t}}{24 \cdot DPP}

        \\

        \text{where } DA_{r,p,s^{seq}} = \frac{\#days_{s^{seq}}}{SEG_{r,p,s^*} \cdot DPP}



    Unlike non-seasonal (daily) storage, seasonal storage is allowed to carry energy
    between seasons. However, through seasons representing multiple days, many days'
    charge deltas have accumulated, multiplied by the number of days the season
    represents. If we allowed these stacked deltas to carry between seasons then we would
    be multiplying the effective energy capacity of the storage. We could just constrain
    the seasonal delta to the unadjusted energy capacity, but then the final day in the
    season would sit atop a season's worth of deltas, possibly exceeding our upper or
    lower bound by a factor of :math:`\frac{N-1}{N}` where :math:`N` is the number of
    days the sequential season represents.

    .. figure:: images/ldes_delta_problem.*
        :align: center
        :width: 100%
        :figclass: center
        :figwidth: 100%

        The energy upper bound or non-negative lower bound could be violated in a
        season representing multiple days if we both adjusted the upper bound to
        the number of days and allowed a seasonal delta.

    So, we do not adjust the upper energy bound for seasonal storage. This limits the
    ability of seasonal storage to perform arbitrage within each season, but allows it to
    carry energy between seasons realistically.

    .. figure:: images/ldes_delta_representation.*
        :align: center
        :width: 100%
        :figclass: center
        :figwidth: 40%

        Unadjusted energy upper bound constraint for seasonal storage.
    """

    s = M.sequential_to_season[p, s_seq]

    energy_capacity = (
        M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * (value(M.StorageDuration[r, t]) / (24 * value(M.DaysPerPeriod)))
    )

    # Flows and StorageLevel are normalised to the number of days in the non-sequential season, so must
    # be adjusted to the number of days in the sequential season
    days_adjust = value(M.TimeSeasonSequential[p, s_seq, s]) / (
        value(M.SegFracPerSeason[p, s]) * value(M.DaysPerPeriod)
    )

    # V_StorageLevel tracks the running cumulative delta in the non-sequential season, so must be adjusted
    # to the size of the sequential season
    running_day_delta = M.V_StorageLevel[r, p, s, d, t, v] * days_adjust

    expr = M.V_SeasonalStorageLevel[r, p, s_seq, t, v] + running_day_delta <= energy_capacity

    return expr


def StorageChargeRate_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    r"""

    This constraint ensures that the charge rate of the storage unit is
    limited by the power capacity (typically GW) of the storage unit.

    .. math::
       :label: StorageChargeRate

          \sum_{I, O} \textbf{FIS}_{r, p, s, d, i, t, v, o} \cdot EFF_{r,i,t,v,o}
          \le
          \textbf{CAP}_{r,t,v} \cdot C2A_{r,t} \cdot SEG_{s,d}

          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{StorageChargeRate}}

    """
    # Calculate energy charge in each time slice
    slice_charge = sum(
        M.V_FlowIn[r, p, s, d, S_i, t, v, S_o]
        * get_variable_efficiency(M, r, p, s, d, S_i, t, v, S_o)
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    # Maximum energy charge in each time slice
    max_charge = (
        M.V_Capacity[r, p, t, v] * value(M.CapacityToActivity[r, t]) * value(M.SegFrac[p, s, d])
    )

    # Energy charge cannot exceed the power capacity of the storage unit
    expr = slice_charge <= max_charge

    return expr


def StorageDischargeRate_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    r"""

    This constraint ensures that the discharge rate of the storage unit
    is limited by the power capacity (typically GW) of the storage unit.

    .. math::
       :label: StorageDischargeRate

          \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o}
          \le
          \textbf{CAP}_{r,t,v} \cdot C2A_{r,t} \cdot SEG_{s,d}

          \\
          \forall \{r,p, s, d, t, v\} \in \Theta_{\text{StorageDischargeRate}}
    """
    # Calculate energy discharge in each time slice
    slice_discharge = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for S_o in M.processOutputs[r, p, t, v]
        for S_i in M.processInputsByOutput[r, p, t, v, S_o]
    )

    # Maximum energy discharge in each time slice
    max_discharge = (
        M.V_Capacity[r, p, t, v] * value(M.CapacityToActivity[r, t]) * value(M.SegFrac[p, s, d])
    )

    # Energy discharge cannot exceed the capacity of the storage unit
    expr = slice_discharge <= max_discharge

    return expr


def StorageThroughput_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    r"""

    It is not enough to only limit the charge and discharge rate separately. We also
    need to ensure that the maximum throughput (charge + discharge) does not exceed
    the capacity (typically GW) of the storage unit.

    .. math::
       :label: StorageThroughput

          \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o}
          +
          \sum_{I, O} \textbf{FIS}_{r, p, s, d, i, t, v, o} \cdot EFF_{r,i,t,v,o}
          \le
          \textbf{CAP}_{r,t,v} \cdot C2A_{r,t} \cdot SEG_{s,d}

          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{StorageThroughput}}
    """
    discharge = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for S_o in M.processOutputs[r, p, t, v]
        for S_i in M.processInputsByOutput[r, p, t, v, S_o]
    )

    charge = sum(
        M.V_FlowIn[r, p, s, d, S_i, t, v, S_o]
        * get_variable_efficiency(M, r, p, s, d, S_i, t, v, S_o)
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    throughput = charge + discharge
    max_throughput = (
        M.V_Capacity[r, p, t, v] * value(M.CapacityToActivity[r, t]) * value(M.SegFrac[p, s, d])
    )
    expr = throughput <= max_throughput
    return expr


def LimitStorageFraction_Constraint(M: 'TemoaModel', r, p, s, d, t, v, op):
    r"""

    This constraint is used if the users wishes to force a specific storage charge level
    for certain storage technologies and vintages at a certain time slice.
    In this case, the value of the decision variable :math:`\textbf{SI}_{r,t,v}` is set by
    this constraint rather than being optimized. User-specified storage charge levels that are
    sufficiently different from the optimal :math:`\textbf{SI}_{r,t,v}` could impact the
    cost-effectiveness of storage. For example, if the optimal charge level happens to be
    50% of the full energy capacity, forced charge levels (specified by parameter
    :math:`SIF_{r,t,v}`) equal to 10% or 90% of the full energycapacity could lead to
    more expensive solutions.


    .. math::
       :label: LimitStorageFraction

          \textbf{SF}_{r,p,s,d,t,v} \le
          \ SF_{r,p,s,d,t,v}
          \cdot
          \textbf{CAP}_{r,p,t,v} \cdot C2A_{r,t} \cdot \frac {SD_{r,t}}{(24 \cdot DPP hrs/yr}
          \cdot \sum_{d} SEG_{s,d} \cdot M.DaysPerPeriod days/yr \cdot MPL_{r,p,t,v}

          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{LimitStorageFraction}}
    """

    energy_limit = (
        M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * (value(M.StorageDuration[r, t]) / (24 * value(M.DaysPerPeriod)))
        * value(M.LimitStorageFraction[r, p, s, d, t, v, op])
    )

    if M.isSeasonalStorage[t]:
        s_seq = s  # sequential season
        s = M.sequential_to_season[p, s_seq]  # non-sequential season

    # adjust the storage level to the individual-day level
    energy_level = M.V_StorageLevel[r, p, s, d, t, v] / (
        value(M.SegFracPerSeason[p, s]) * value(M.DaysPerPeriod)
    )

    if M.isSeasonalStorage[t]:
        # seasonal storage upper energy limit is absolute
        energy_level = M.V_SeasonalStorageLevel[r, p, s_seq, t, v] + energy_level * value(
            M.TimeSeasonSequential[p, s_seq, s]
        )

    expr = operator_expression(energy_level, op, energy_limit)

    return expr


def RampUpDay_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    r"""
    One of two constraints built from the RampUpHourly table, along with the
    RampUpSeason_Constraint. RampUpDay constrains ramp rates between time slices
    within each season and RampUpSeason constrains ramp rates between sequential
    seasons. If the :code:`time_sequencing` parameter is set to :code:`consecutive_days`
    then the RampUpSeason constraint is skipped as seasons already connect together.

    The ramp rate constraint is utilized to limit the rate of electricity generation
    increase and decrease between two adjacent time slices in order to account for
    physical limits associated with thermal power plants. This constraint is only
    applied to technologies in the set :code:`tech_upramping`. We assume for
    simplicity the rate limits do not vary with technology vintage. The ramp rate
    limits for a technology should be expressed in percentage of its rated capacity
    per hour.

    In a representative periods or seasonal time slices model, the next time slice,
    :math:`(s_{next},d_{next})`, from the end of each season, :math:`(s,d_{last})`
    is the beginning of the same season, :math:`(s,d_{first})`

    .. math::
       :label: RampUpDay

            \frac{
                \sum_{I,O} \mathbf{FO}_{r,p,s_{next},d_{next},i,t,v,o}
            }{
                SEG_{r,p,s_{next},d_{next}} \cdot 24 \cdot DPP
            }
            -
            \frac{
                \sum_{I,O} \mathbf{FO}_{r,p,s,d,i,t,v,o}
            }{
                SEG_{r,p,s,d} \cdot 24 \cdot DPP
            }
            \leq
            R_{r,t} \cdot \Delta H_{r,p,s,d,s_{next},d_{next}} \cdot CAP_{r,p,t,v} \cdot C2A_{r,t}
            \\
            \forall \{r, p, s, d, t, v\} \in \Theta_{\text{RampUpDay}}
            \\
            \text{where: } \Delta H_{r,p,s,d,s_{next},d_{next}} = \frac{24}{2}
            \left ( \frac{SEG_{r,p,s,d}}{\sum_{D} SEG_{r,p,s,d'}} +
            \frac{SEG_{r,p,s_{next},d_{next}}}{\sum_{D} SEG_{r,p,s_{next},d'}} \right )

    where:

    - :math:`SEG_{r,p,s,d}` is the fraction of the period in time slice :math:`(s,d)`
    - :math:`DPP` is the number of days in each period
    - :math:`R_{r,t}` is the ramp rate per hour
    - :math:`\Delta H_{r,p,s,d,s_{next},d_{next}}` is the number of elapsed hours between midpoints of time slices
    - :math:`CAP \cdot C2A` gives the maximum hourly change in activity
    """

    s_next, d_next = M.time_next[p, s, d]

    # How many hours does this time slice represent
    hours_adjust = value(M.SegFrac[p, s, d]) * value(M.DaysPerPeriod) * 24

    hourly_activity_sd = (
        sum(
            M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    hourly_activity_sd_next = (
        sum(
            M.V_FlowOut[r, p, s_next, d_next, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    # elapsed hours from middle of this time slice to middle of next time slice
    hours_elapsed = (
        24
        / 2
        * (
            value(M.SegFrac[p, s, d]) / value(M.SegFracPerSeason[p, s])
            + value(M.SegFrac[p, s_next, d_next]) / value(M.SegFracPerSeason[p, s_next])
        )
    )
    ramp_fraction = hours_elapsed * value(M.RampUpHourly[r, t])

    if ramp_fraction >= 1:
        msg = (
            'Warning: Hourly ramp up rate ({}, {}) is too large to be constraining from ({}, {}, {}) to ({}, {}, {}). '
            f'Should be less than {1 / hours_elapsed:.4f}. Constraint skipped.'
        )
        logger.warning(msg.format(r, t, p, s, d, p, s_next, d_next))
        return Constraint.Skip

    activity_increase = hourly_activity_sd_next - hourly_activity_sd  # opposite sign from rampdown
    rampable_activity = ramp_fraction * M.V_Capacity[r, p, t, v] * value(M.CapacityToActivity[r, t])
    expr = activity_increase <= rampable_activity

    return expr


def RampDownDay_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    r"""

    Similar to the :code`RampUpDay` constraint, we use the :code:`RampDownDay`
    constraint to limit ramp down rates between any two adjacent time slices.

    .. math::
       :label: RampDownDay

            \frac{
                \sum_{I,O} \mathbf{FO}_{r,p,s,d,i,t,v,o}
            }{
                SEG_{r,p,s,d} \cdot 24 \cdot DPP
            }
            -
            \frac{
                \sum_{I,O} \mathbf{FO}_{r,p,s_{next},d_{next},i,t,v,o}
            }{
                SEG_{r,p,s_{next},d_{next}} \cdot 24 \cdot DPP
            }
            \leq
            R_{r,t} \cdot \Delta H_{r,p,s,d,s_{next},d_{next}} \cdot CAP_{r,p,t,v} \cdot C2A_{r,t}
            \\
            \forall \{r, p, s, d, t, v\} \in \Theta_{\text{RampDownDay}}
    """

    s_next, d_next = M.time_next[p, s, d]

    # How many hours does this time slice represent
    hours_adjust = value(M.SegFrac[p, s, d]) * value(M.DaysPerPeriod) * 24

    hourly_activity_sd = (
        sum(
            M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    hourly_activity_sd_next = (
        sum(
            M.V_FlowOut[r, p, s_next, d_next, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    # elapsed hours from middle of this time slice to middle of next time slice
    hours_elapsed = (
        24
        / 2
        * (
            value(M.SegFrac[p, s, d]) / value(M.SegFracPerSeason[p, s])
            + value(M.SegFrac[p, s_next, d_next]) / value(M.SegFracPerSeason[p, s_next])
        )
    )
    ramp_fraction = hours_elapsed * value(M.RampDownHourly[r, t])

    if ramp_fraction >= 1:
        msg = (
            'Warning: Hourly ramp down rate  ({}, {}) is too large to be constraining from ({}, {}, {}) to ({}, {}, {}). '
            f'Should be less than {1 / hours_elapsed:.4f}. Constraint skipped.'
        )
        logger.warning(msg.format(r, t, p, s, d, p, s_next, d_next))
        return Constraint.Skip

    activity_decrease = hourly_activity_sd - hourly_activity_sd_next  # opposite sign from rampup
    rampable_activity = ramp_fraction * M.V_Capacity[r, p, t, v] * value(M.CapacityToActivity[r, t])
    expr = activity_decrease <= rampable_activity

    return expr


def RampUpSeason_Constraint(M: 'TemoaModel', r, p, s, s_next, t, v):
    r"""
    Constrains the ramp up rate of activity between time slices at the boundary
    of sequential seasons. Same as RampUpDay but only applies to the boundary
    between sequential seasons, i.e., :math:`(s^{seq},d_{last})` to :math:`(s^{seq}_{next},d_{first})`
    and :math:`s^{seq}_{next}` is based on the TimeSequential table rather than the
    TimeSeason table.
    """

    d = M.time_of_day.last()
    d_next = M.time_of_day.first()

    # How many hours does this time slice represent
    hours_adjust = value(M.SegFrac[p, s, d]) * value(M.DaysPerPeriod) * 24

    hourly_activity_sd = (
        sum(
            M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    hourly_activity_sd_next = (
        sum(
            M.V_FlowOut[r, p, s_next, d_next, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    # elapsed hours from middle of this time slice to middle of next time slice
    hours_elapsed = (
        24
        / 2
        * (
            value(M.SegFrac[p, s, d]) / value(M.SegFracPerSeason[p, s])
            + value(M.SegFrac[p, s_next, d_next]) / value(M.SegFracPerSeason[p, s_next])
        )
    )
    ramp_fraction = hours_elapsed * value(M.RampUpHourly[r, t])

    if ramp_fraction >= 1:
        msg = (
            'Warning: Hourly ramp up rate ({}, {}) is too large to be constraining from ({}, {}, {}) to ({}, {}, {}). '
            f'Should be less than {1 / hours_elapsed:.4f}. Constraint skipped.'
        )
        logger.warning(msg.format(r, t, p, s, d, p, s_next, d_next))
        return Constraint.Skip

    activity_increase = hourly_activity_sd_next - hourly_activity_sd  # opposite sign from rampdown
    rampable_activity = ramp_fraction * M.V_Capacity[r, p, t, v] * value(M.CapacityToActivity[r, t])
    expr = activity_increase <= rampable_activity

    return expr


def RampDownSeason_Constraint(M: 'TemoaModel', r, p, s, s_next, t, v):
    r"""
    Constrains the ramp down rate of activity between time slices at the boundary
    of sequential seasons. Same as RampDownDay but only applies to the boundary
    between sequential seasons, i.e., :math:`(s^{seq},d_{last})` to :math:`(s^{seq}_{next},d_{first})`
    and :math:`s^{seq}_{next}` is based on the TimeSequential table rather than the
    TimeSeason table.
    """

    d = M.time_of_day.last()
    d_next = M.time_of_day.first()

    # How many hours does this time slice represent
    hours_adjust = value(M.SegFrac[p, s, d]) * value(M.DaysPerPeriod) * 24

    hourly_activity_sd = (
        sum(
            M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    hourly_activity_sd_next = (
        sum(
            M.V_FlowOut[r, p, s_next, d_next, S_i, t, v, S_o]
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    # elapsed hours from middle of this time slice to middle of next time slice
    hours_elapsed = (
        24
        / 2
        * (
            value(M.SegFrac[p, s, d]) / value(M.SegFracPerSeason[p, s])
            + value(M.SegFrac[p, s_next, d_next]) / value(M.SegFracPerSeason[p, s_next])
        )
    )
    ramp_fraction = hours_elapsed * value(M.RampDownHourly[r, t])

    if ramp_fraction >= 1:
        msg = (
            'Warning: Hourly ramp down rate ({}, {}) is too large to be constraining from ({}, {}, {}) to ({}, {}, {}). '
            f'Should be less than {1 / hours_elapsed:.4f}. Constraint skipped.'
        )
        logger.warning(msg.format(r, t, p, s, d, p, s_next, d_next))
        return Constraint.Skip

    activity_decrease = hourly_activity_sd - hourly_activity_sd_next  # opposite sign from rampup
    rampable_activity = ramp_fraction * M.V_Capacity[r, p, t, v] * value(M.CapacityToActivity[r, t])
    expr = activity_decrease <= rampable_activity

    return expr


def ReserveMargin_Constraint(M: 'TemoaModel', r, p, s, d):
    # Get available generation in this time slice depending on method specified in config file
    match M.ReserveMarginMethod.first():
        case 'static':
            available = ReserveMarginStatic(M, r, p, s, d)
        case 'dynamic':
            available = ReserveMarginDynamic(M, r, p, s, d)
        case _:
            msg = f"Invalid reserve margin parameter '{M.ReserveMarginMethod.first()}'. Check the config file."
            logger.error(msg)
            raise ValueError(msg)

    # In most Temoa input databases, demand is endogenous, so we use electricity
    # generation instead as a proxy for electricity demand.
    # Non-annual generation
    total_generation = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, S_v, S_o]
        for (t, S_v) in M.processReservePeriods[r, p]
        if t not in M.tech_annual
        for S_i in M.processInputs[r, p, t, S_v]
        for S_o in M.processOutputsByInput[r, p, t, S_v, S_i]
    )

    # Generators might serve demands directly
    # Annual generation
    total_generation += sum(
        (
            value(M.DemandSpecificDistribution[r, p, s, d, S_o])
            if S_o in M.commodity_demand
            else value(M.SegFrac[p, s, d])
        )
        * M.V_FlowOutAnnual[r, p, s, d, S_i, t, S_v, S_o]
        for (t, S_v) in M.processReservePeriods[r, p]
        if t in M.tech_annual
        for S_i in M.processInputs[r, p, t, S_v]
        for S_o in M.processOutputsByInput[r, p, t, S_v, S_i]
    )

    # We must take into account flows into storage technologies.
    # Flows into storage technologies need to be subtracted from the
    # load calculation.
    total_generation -= sum(
        M.V_FlowIn[r, p, s, d, S_i, t, S_v, S_o]
        for (t, S_v) in M.processReservePeriods[r, p]
        if t in M.tech_storage
        for S_i in M.processInputs[r, p, t, S_v]
        for S_o in M.processOutputsByInput[r, p, t, S_v, S_i]
    )

    # Electricity imports and exports via exchange techs are accounted
    # for below:
    for r1r2 in M.regionalIndices:  # ensure the region is of the form r1-r2
        if '-' not in r1r2:
            continue
        if (r1r2, p) not in M.processReservePeriods:  # ensure r1r2 is a valid reserve provider in p
            continue
        r1, r2 = r1r2.split('-')
        # First, determine the exports, and subtract this value from the
        # total generation.
        if r1 == r:
            total_generation -= sum(
                M.V_FlowOut[r1r2, p, s, d, S_i, t, S_v, S_o]
                / get_variable_efficiency(M, r1r2, p, s, d, S_i, t, S_v, S_o)
                for (t, S_v) in M.processReservePeriods[r1r2, p]
                for S_i in M.processInputs[r1r2, p, t, S_v]
                for S_o in M.processOutputsByInput[r1r2, p, t, S_v, S_i]
            )
        # Second, determine the imports, and add this value from the
        # total generation.
        elif r2 == r:
            total_generation += sum(
                M.V_FlowOut[r1r2, p, s, d, S_i, t, S_v, S_o]
                for (t, S_v) in M.processReservePeriods[r1r2, p]
                for S_i in M.processInputs[r1r2, p, t, S_v]
                for S_o in M.processOutputsByInput[r1r2, p, t, S_v, S_i]
            )

    requirement = total_generation * (1 + value(M.PlanningReserveMargin[r]))
    return available >= requirement


def ReserveMarginStatic(M: 'TemoaModel', r, p, s, d):
    r"""

    During each period :math:`p`, the sum of capacity values of all reserve
    technologies :math:`\sum_{t \in T^{res}} \textbf{CAPAVL}_{r,p,t}`, which are
    defined in the set :math:`\textbf{T}^{res}`, should exceed the peak load by
    :math:`PRM`, the regional reserve margin. Note that the reserve
    margin is expressed in percentage of the peak load. Generally speaking, in
    a database we may not know the peak demand before running the model, therefore,
    we write this equation for all the time-slices defined in the database in each region.
    Each generator is allowed to contribute its available capacity times a pre-defined
    capacity credit, :math:`CC_{t,r}`

    .. math::
        :label: reserve_margin_static

            &\sum_{t \in T^{res} \setminus T^{x}} {CC_{t,r} \cdot \textbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*} \cdot C2A_{r,t} }\\
            &+ \sum_{t \in T^{res} \cap T^{x}} {CC_{t,r_i-r} \cdot \textbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*} \cdot C2A_{r_i-r,t} }\\
            &- \sum_{t \in T^{res} \cap T^{x}} {CC_{t,r-r_i} \cdot \textbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*} \cdot C2A_{r-r_i,t} }\\
            &\geq \left [ \sum_{ t \in T^{res} \setminus T^{x},V,I,O } \textbf{FO}_{r, p, s, d, i, t, v, o}\right.\\
            &+ \sum_{ t \in T^{res} \cap T^{x},V,I,O } \textbf{FO}_{r_i-r, p, s, d, i, t, v, o}\\
            &- \sum_{ t \in T^{res} \cap T^{x},V,I,O } \textbf{FI}_{r-r_i, p, s, d, i, t, v, o}\\
            &- \left.\sum_{ t \in T^{res} \cap T^{s},V,I,O } \textbf{FI}_{r, p, s, d, i, t, v, o}  \right]  \cdot (1 + PRM_r)\\

            \\
            &\qquad\qquad\forall \{r, p, s, d\} \in \Theta_{\text{ReserveMargin}} \text{and} \forall r_i \in R
    """
    if (not M.tech_reserve) or (
        (r, p) not in M.processReservePeriods
    ):  # If reserve set empty or if r,p not in M.processReservePeriod, skip the constraint
        return Constraint.Skip

    available = sum(
        value(M.CapacityCredit[r, p, t, v])
        * M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * value(M.SegFrac[p, s, d])
        for (t, v) in M.processReservePeriods[r, p]
        if t not in M.tech_uncap
    )

    # The above code does not consider exchange techs, e.g. electricity
    # transmission between two distinct regions.
    # We take exchange takes into account below.
    # Note that a single exchange tech linking regions Ri and Rj is twice
    # defined: once for region "Ri-Rj" and once for region "Rj-Ri".

    # First, determine the amount of firm capacity each exchange tech
    # contributes.
    for r1r2 in M.regionalIndices:
        if '-' not in r1r2:
            continue
        if (r1r2, p) not in M.processReservePeriods:  # ensure r1r2 is a valid reserve provider in p
            continue
        r1, r2 = r1r2.split('-')

        # Only consider the capacity of technologies that import to
        # the region in question -- i.e. for cases where r2 == r.
        if r2 != r:
            continue

        # add the available capacity of the exchange tech.
        available += sum(
            value(M.CapacityCredit[r1r2, p, t, v])
            * M.V_Capacity[r1r2, p, t, v]
            * value(M.CapacityToActivity[r1r2, t])
            * value(M.SegFrac[p, s, d])
            for (t, v) in M.processReservePeriods[r1r2, p]
            for t in M.tech_reserve
        )

    return available


def ReserveMarginDynamic(M: 'TemoaModel', r, p, s, d):
    r"""
    A dynamic alternative to the traditional, static reserve margin constraint. Capacity values
    are calculated from availability of generation in each hour—like an operating reserve margin—\
    accounting for a capacity derate factor subtracting, for example, forced outage due to icing.

    .. math::
        :label: reserve_margin_dynamic

            &\sum_{t \in T^{res} \setminus T^{x} \setminus T^s,\ V} CFP_{r,p,s^*,d^*,t,v}\
                \cdot RCD_{r,p,s^*,t,v}\
                \cdot \mathbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*}\
                \cdot C2A_{r,t} \\
            &+ \sum_{t \in T^{res} \cap T^{x} \setminus T^s,\ V} CFP_{r_i - r, p, s^*, d^*, t, v}\
                \cdot RCD_{r_i - r, p, s^*, t, v}\
                \cdot \mathbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*}\
                \cdot C2A_{r_i - r, t} \\
            &- \sum_{t \in T^{res} \cap T^{x} \setminus T^s,\ V} CFP_{r - r_i, p, s^*, d^*, t, v}\
                \cdot RCD_{r - r_i, p, s^*, t, v}\
                \cdot \mathbf{CAPAVL}_{p,t}\
                \cdot SEG_{s^*,d^*} \cdot C2A_{r - r_i, t} \\
            &+ \sum_{t \in (T^s \cap T^{res}), V, I, O} \
                \left(\
                \mathbf{FO}_{r,p,s,d,i,t,v,o} - \mathbf{FI}_{r,p,s,d,i,t,v,o}\
                \right)\
                \cdot RCD_{r,p,s,t,v} \\
            &\geq\
                \left[\
                \sum_{t \in T^{res} \setminus T^{x}, V, I, O}\
                \mathbf{FO}_{r, p, s, d, i, t, v, o}\
                \right. \\
            &+ \sum_{t \in T^{res} \cap T^{x}, V, I, O} \
                \mathbf{FO}_{r_i - r, p, s, d, i, t, v, o} \\
            &- \sum_{t \in T^{res} \cap T^{x}, V, I, O} \
                \mathbf{FI}_{r - r_i, p, s, d, i, t, v, o} \\
            &- \left. \sum_{t \in T^{res} \cap T^{s}, V, I, O} \
                \mathbf{FI}_{r, p, s, d, i, t, v, o} \right] \cdot (1 + PRM_r) \\
            \\
            &\qquad \qquad \forall \{r, p, s, d\} \in \
            \Theta_{\text{ReserveMargin}} \text{ and } \forall r_i \in R
    """
    if (not M.tech_reserve) or (
        (r, p) not in M.processReservePeriods
    ):  # If reserve set empty or if r,p not in M.processReservePeriod, skip the constraint
        return Constraint.Skip

    # Everything but storage and exchange techs
    # Derated available generation
    available = sum(
        M.V_Capacity[r, p, t, v]
        * value(M.ReserveCapacityDerate[r, p, s, t, v])
        * value(M.CapacityFactorProcess[r, p, s, d, t, v])
        * value(M.CapacityToActivity[r, t])
        * value(M.SegFrac[p, s, d])
        for (t, v) in M.processReservePeriods[r, p]
        if t not in M.tech_uncap and t not in M.tech_storage
    )

    # Storage
    # Derated net output flow
    available += sum(
        M.V_FlowOut[r, p, s, d, i, t, v, o] * value(M.ReserveCapacityDerate[r, p, s, t, v])
        for (t, v) in M.processReservePeriods[r, p]
        if t in M.tech_storage
        for i in M.processInputs[r, p, t, v]
        for o in M.processOutputsByInput[r, p, t, v, i]
    )
    available -= sum(
        M.V_FlowIn[r, p, s, d, i, t, v, o] * value(M.ReserveCapacityDerate[r, p, s, t, v])
        for (t, v) in M.processReservePeriods[r, p]
        if t in M.tech_storage
        for i in M.processInputs[r, p, t, v]
        for o in M.processOutputsByInput[r, p, t, v, i]
    )

    # The above code does not consider exchange techs, e.g. electricity
    # transmission between two distinct regions.
    # We take exchange takes into account below.
    # Note that a single exchange tech linking regions Ri and Rj is twice
    # defined: once for region "Ri-Rj" and once for region "Rj-Ri".

    # First, determine the amount of firm capacity each exchange tech
    # contributes.
    for r1r2 in M.regionalIndices:
        if '-' not in r1r2:
            continue
        if (r1r2, p) not in M.processReservePeriods:  # ensure r1r2 is a valid reserve provider in p
            continue
        r1, r2 = r1r2.split('-')

        # Only consider the capacity of technologies that import to
        # the region in question -- i.e. for cases where r2 == r.
        if r2 != r:
            continue

        # add the available output of the exchange tech.
        available += sum(
            M.V_Capacity[r1r2, p, t, v]
            * value(M.ReserveCapacityDerate[r, p, s, t, v])
            * value(M.CapacityFactorProcess[r, p, s, d, t, v])
            * value(M.CapacityToActivity[r1r2, t])
            * value(M.SegFrac[p, s, d])
            for (t, v) in M.processReservePeriods[r1r2, p]
            for t in M.tech_reserve
        )

    return available


def LimitEmission_Constraint(M: 'TemoaModel', r, p, e, op):
    r"""

    A modeler can track emissions through use of the :code:`commodity_emissions`
    set and :code:`EmissionActivity` parameter.  The :math:`EAC` parameter is
    analogous to the efficiency table, tying emissions to a unit of activity.  The
    LimitEmission constraint allows the modeler to assign an upper bound per period
    to each emission commodity. Note that this constraint sums emissions from
    technologies with output varying at the time slice and those with constant annual
    output in separate terms.

    .. math::
       :label: LimitEmission

           \sum_{S,D,I,T,V,O|{r,e,i,t,v,o} \in EAC} \left (
           EAC_{r, e, i, t, v, o} \cdot \textbf{FO}_{r, p, s, d, i, t, v, o}
           \right ) & \\
           +
           \sum_{I,T,V,O|{r,e,i,t \in T^{a},v,o} \in EAC} (
           EAC_{r, e, i, t, v, o} \cdot & \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}
            )
           \le
           ELM_{r, p, e}

           \\
           & \forall \{r, p, e\} \in \Theta_{\text{LimitEmission}}

    """
    emission_limit = value(M.LimitEmission[r, p, e, op])

    # r can be an individual region (r='US'), or a combination of regions separated by a + (r='Mexico+US+Canada'),
    # or 'global'.  Note that regions!=M.regions. We iterate over regions to find actual_emissions
    # and actual_emissions_annual.

    # if r == 'global', the constraint is system-wide

    regions = gather_group_regions(M, r)

    # ================= Emissions and Flex and Curtailment =================
    # Flex flows are deducted from V_FlowOut, so it is NOT NEEDED to tax them again.  (See commodity balance constr)
    # Curtailment does not draw any inputs, so it seems logical that curtailed flows not be taxed either

    process_emissions = sum(
        M.V_FlowOut[reg, p, S_s, S_d, S_i, S_t, S_v, S_o]
        * value(M.EmissionActivity[reg, e, S_i, S_t, S_v, S_o])
        for reg in regions
        for tmp_r, tmp_e, S_i, S_t, S_v, S_o in M.EmissionActivity.sparse_iterkeys()
        if tmp_e == e and tmp_r == reg and S_t not in M.tech_annual
        # EmissionsActivity not indexed by p, so make sure (r,p,t,v) combos valid
        if (reg, p, S_t, S_v) in M.processInputs
        for S_s in M.TimeSeason[p]
        for S_d in M.time_of_day
    )

    process_emissions_annual = sum(
        M.V_FlowOutAnnual[reg, p, S_i, S_t, S_v, S_o]
        * value(M.EmissionActivity[reg, e, S_i, S_t, S_v, S_o])
        for reg in regions
        for tmp_r, tmp_e, S_i, S_t, S_v, S_o in M.EmissionActivity.sparse_iterkeys()
        if tmp_e == e and tmp_r == reg and S_t in M.tech_annual
        # EmissionsActivity not indexed by p, so make sure (r,p,t,v) combos valid
        if (reg, p, S_t, S_v) in M.processInputs
    )

    embodied_emissions = sum(
        M.V_NewCapacity[reg, t, v]
        * value(M.EmissionEmbodied[reg, e, t, v])
        / value(M.PeriodLength[v])
        for reg in regions
        for (S_r, S_e, t, v) in M.EmissionEmbodied.sparse_iterkeys()
        if v == p and S_r == reg and S_e == e
    )

    retirement_emissions = sum(
        M.V_AnnualRetirement[reg, p, t, v] * value(M.EmissionEndOfLife[reg, e, t, v])
        for reg in regions
        for (S_r, S_e, t, v) in M.EmissionEndOfLife.sparse_iterkeys()
        if (r, t, v) in M.retirementPeriods and p in M.retirementPeriods[r, t, v]
        if S_r == reg and S_e == e
    )

    lhs = (
        process_emissions + process_emissions_annual + embodied_emissions + retirement_emissions
        # + emissions_flex # NO! flex is subtracted from flowout, already accounted by flowout
        # + emissions_curtail # NO! curtailed flows are not actual flows, just an accounting tool
        # + emissions_flex_annual # NO! flexannual is subtracted from flowoutannual, already accounted
    )
    expr = operator_expression(lhs, op, emission_limit)

    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        msg = "Warning: No technology produces emission '%s', though limit was specified as %s.\n"
        logger.warning(msg, (e, emission_limit))
        SE.write(msg % (e, emission_limit))
        return Constraint.Skip

    return expr


def LimitGrowthCapacityConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp up rate of available capacity"""
    return LimitGrowthCapacity(M, r, p, t, op, False)


def LimitDegrowthCapacityConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp down rate of available capacity"""
    return LimitGrowthCapacity(M, r, p, t, op, True)


def LimitGrowthCapacity(M: 'TemoaModel', r, p, t, op, degrowth: bool = False):
    r"""
    Constrain the change of capacity available between periods.
    Forces the model to ramp up and down the availability of new technologies
    more smoothly. Has constant (seed, :math:`S_{r,t}`) and proportional
    (rate, :math:`R_{r,t}`) terms. This can be defined for a technology group
    instead of one technology, in which case, capacity available is summed over
    all technologies in the group. In the first period, previous available
    capacity :math:`\mathbf{CAPAVL}_{r,p,t}` is replaced by previous existing
    capacity, if any can be found.

    .. math::
        :label: Limit (De)Growth Capacity

            \begin{aligned}\text{Growth:}\\
            &\mathbf{CAPAVL}_{r,p,t}
            \leq S_{r,t} + (1+R_{r,t}) \cdot \mathbf{CAPAVL}_{r,p_{prev},t}
            \end{aligned}

            \qquad \forall \{r, p, t\} \in \Theta_{\text{LimitGrowthCapacity}}


            \begin{aligned}\text{Degrowth:}\\
            &\mathbf{CAPAVL}_{r,p_{prev},t}
            \leq S_{r,t} + (1+R_{r,t}) \cdot \mathbf{CAPAVL}_{r,p,t}
            \end{aligned}

            \qquad \forall \{r, p, t\} \in \Theta_{\text{LimitDegrowthCapacity}}
    """

    regions = gather_group_regions(M, r)
    techs = gather_group_techs(M, t)

    growth = M.LimitDegrowthCapacity if degrowth else M.LimitGrowthCapacity
    RATE = 1 + value(growth[r, t, op][0])
    SEED = value(growth[r, t, op][1])
    CapRPT = M.V_CapacityAvailableByPeriodAndTech

    # relevant r, p, t indices
    cap_rpt = set((_r, _p, _t) for _r, _p, _t in CapRPT.keys() if _t in techs and _r in regions)
    # periods the technology can have capacity in this region (sorted)
    periods = sorted(set(_p for _r, _p, _t in cap_rpt))

    if len(periods) == 0:
        if p == M.time_optimize.first():
            msg = (
                'Tried to set {}rowthCapacity constraint {} but there are no periods where this '
                'technology is available in this region. Constraint skipped.'
            ).format('Deg' if degrowth else 'G', (r, t))
            logger.warning(msg)
        return Constraint.Skip

    # Only warn in p0 so we dont dump multiple warnings
    if p == periods[0]:
        if SEED == 0:
            msg = (
                'No constant term (seed) provided for {}rowthCapacity constraint {}. '
                'No capacity will be built in any period following one with zero capacity.'
            ).format('Deg' if degrowth else 'G', (r, t))
            logger.info(msg)
        gaps = [
            _p for _p in M.time_optimize if _p not in periods and min(periods) < _p < max(periods)
        ]
        if gaps:
            msg = (
                'Constructing {}rowthCapacity constraint {} and there are period gaps in which'
                'capacity cannot exist in this region ({}). Capacity in these periods '
                'will be treated as zero which may cause infeasibility or other problems.'
            ).format('Deg' if degrowth else 'G', (r, t), gaps)
            logger.warning(msg)

    # sum available capacity in this period
    capacity = sum(CapRPT[_r, _p, _t] for _r, _p, _t in cap_rpt if _p == p)

    if p == M.time_optimize.first():
        # First future period. Grab available capacity in last existing period
        # Adjust in-line for past PLF because we are constraining available capacity
        p_prev = M.time_exist.last()
        capacity_prev = sum(
            value(M.ExistingCapacity[_r, _t, _v])
            * min(1.0, (_v + value(M.LifetimeProcess[_r, _t, _v]) - p_prev) / (p - p_prev))
            for _r, _t, _v in M.ExistingCapacity.sparse_iterkeys()
            if _r in regions and _t in techs and _v + value(M.LifetimeProcess[_r, _t, _v]) > p_prev
        )
    else:
        # Otherwise, grab previous future period
        p_prev = M.time_optimize.prev(p)
        capacity_prev = sum(CapRPT[_r, _p, _t] for _r, _p, _t in cap_rpt if _p == p_prev)

    if degrowth:
        expr = operator_expression(capacity_prev, op, SEED + capacity * RATE)
    else:
        expr = operator_expression(capacity, op, SEED + capacity_prev * RATE)

    # Check if any variables are actually included before returning
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitGrowthNewCapacityConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp up rate of new capacity deployment"""
    return LimitGrowthNewCapacity(M, r, p, t, op, False)


def LimitDegrowthNewCapacityConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp down rate of new capacity deployment"""
    return LimitGrowthNewCapacity(M, r, p, t, op, True)


def LimitGrowthNewCapacity(M: 'TemoaModel', r, p, t, op, degrowth: bool = False):
    r"""
    Constrain the change of new capacity deployed between periods.
    Forces the model to ramp up and down the deployment of new technologies
    more smoothly. Has constant (seed, :math:`S_{r,t}`) and proportional
    (rate, :math:`R_{r,t}`) terms. This can be defined for a technology group
    instead of one technology, in which case, new capacity is summed over
    all technologies in the group. In the first period, previous new capacity
    :math:`\mathbf{NCAP}_{r,t,v_prev}` is replaced by previous existing capacity,
    if any can be found.

    .. math::
        :label: Limit (De)Growth New Capacity

            \begin{aligned}\text{Growth:}\\
            &\mathbf{NCAP}_{r,t,v}
            \leq S_{r,t} + (1+R_{r,t}) \cdot \mathbf{NCAP}_{r,t,v_{prev}}
            \text{ where } v=p
            \end{aligned}

            \qquad \forall \{r, p, t\} \in \Theta_{\text{LimitGrowthCapacity}}

            \begin{aligned}\text{Degrowth:}\\
            &\mathbf{NCAP}_{r,t,v_{prev}}
            \leq S_{r,t} + (1+R_{r,t}) \cdot \mathbf{NCAP}_{r,t,v}
            \text{ where } v=p
            \end{aligned}

            \qquad \forall \{r, p, t\} \in \Theta_{\text{LimitDegrowthCapacity}}
    """

    regions = gather_group_regions(M, r)
    techs = gather_group_techs(M, t)

    growth = M.LimitDegrowthNewCapacity if degrowth else M.LimitGrowthNewCapacity
    RATE = 1 + value(growth[r, t, op][0])
    SEED = value(growth[r, t, op][1])
    NewCapRTV = M.V_NewCapacity

    # relevant r, t, v indices
    cap_rtv = set((_r, _t, _v) for _r, _t, _v in NewCapRTV.keys() if _t in techs and _r in regions)
    # periods the technology can be built in this region (sorted)
    periods = sorted(set(_v for _r, _t, _v in cap_rtv))

    if len(periods) == 0:
        if p == M.time_optimize.first():
            msg = (
                'Tried to set {}rowthNewCapacity constraint {} but there are no periods where this '
                'technology can be built in this region. Constraint skipped.'
            ).format('Deg' if degrowth else 'G', (r, t))
            logger.warning(msg)
        return Constraint.Skip

    # Only warn in p0 so we dont dump multiple warnings
    if p == periods[0]:
        if SEED == 0:
            msg = (
                'No constant term (seed) provided for {}rowthNewCapacity constraint {}. '
                'No capacity will be built in any period following one with zero new capacity.'
            ).format('Deg' if degrowth else 'G', (r, t))
            logger.info(msg)
        gaps = [
            _p for _p in M.time_optimize if _p not in periods and min(periods) < _p < max(periods)
        ]
        if gaps:
            msg = (
                'Constructing {}rowthNewCapacity constraint {} and there are period gaps in which'
                'new capacity cannot be built in this region ({}). New capacity in these periods '
                'will be treated as zero which may cause infeasibility or other problems.'
            ).format('Deg' if degrowth else 'G', (r, t), gaps)
            logger.warning(msg)

    # sum new capacity in this period
    new_cap = sum(NewCapRTV[_r, _t, _v] for _r, _t, _v in cap_rtv if _v == p)

    if p == M.time_optimize.first():
        # First future period. Grab last existing vintage
        p_prev = M.time_exist.last()
        new_cap_prev = sum(
            value(M.ExistingCapacity[_r, _t, _v])
            for _r, _t, _v in M.ExistingCapacity.sparse_iterkeys()
            if _r in regions and _t in techs and _v == p_prev
        )
    else:
        # Otherwise, grab previous future vintage
        p_prev = M.time_optimize.prev(p)
        new_cap_prev = sum(NewCapRTV[_r, _t, _v] for _r, _t, _v in cap_rtv if _v == p_prev)

    if degrowth:
        expr = operator_expression(new_cap_prev, op, SEED + new_cap * RATE)
    else:
        expr = operator_expression(new_cap, op, SEED + new_cap_prev * RATE)

    # Check if any variables are actually included before returning
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitGrowthNewCapacityDeltaConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp up rate of change in new capacity deployment"""
    return LimitGrowthNewCapacityDelta(M, r, p, t, op, False)


def LimitDegrowthNewCapacityDeltaConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp down rate of change in new capacity deployment"""
    return LimitGrowthNewCapacityDelta(M, r, p, t, op, True)


def LimitGrowthNewCapacityDelta(M: 'TemoaModel', r, p, t, op, degrowth: bool = False):
    r"""
    Constrain the acceleration of new capacity deployed between periods.
    Forces the model to ramp up and down the change in deployment of new technologies
    more smoothly. Has constant (seed, :math:`S_{r,t}`) and proportional
    (rate, :math:`R_{r,t}`) terms. It is recommended to leave the rate term empty
    as it would prevent the possibility of inflection in the rate of deployment.
    This constraint can be defined for a technology group instead of one technology,
    in which case, new capacity is summed over all technologies in the group. In the
    first period, previous new capacities are replaced by previous existing capacities,
    if any can be found.

    .. math::
        :label: Limit (De)Growth New Capacity Delta

            \begin{aligned}\text{Growth:}\\
            &\mathbf{NCAP}_{r,t,v_i} - \mathbf{NCAP}_{r,t,v_{i-1}}
            \leq S_{r,t} + (1+R_{r,t}) \cdot (\mathbf{NCAP}_{r,t,v_{i-1}} - \mathbf{NCAP}_{r,t,v_{i-2}})
            \end{aligned}

            \text{ where } v_i=p

            \qquad \forall \{r, p, t\} \in \Theta_{\text{LimitGrowthCapacityDelta}}

            \begin{aligned}\text{Degrowth:}\\
            &\mathbf{NCAP}_{r,t,v_{i-1}} - \mathbf{NCAP}_{r,t,v_{i-2}}
            \leq S_{r,t} + (1+R_{r,t}) \cdot (\mathbf{NCAP}_{r,t,v_i} - \mathbf{NCAP}_{r,t,v_{i-1}})
            \end{aligned}

            \text{ where } v_i=p

            \qquad \forall \{r, p, t\} \in \Theta_{\text{LimitDegrowthCapacityDelta}}
    """

    regions = gather_group_regions(M, r)
    techs = gather_group_techs(M, t)

    growth = M.LimitDegrowthNewCapacityDelta if degrowth else M.LimitGrowthNewCapacityDelta
    RATE = 1 + value(growth[r, t, op][0])
    SEED = value(growth[r, t, op][1])
    NewCapRTV = M.V_NewCapacity

    # relevant r, t, v indices
    cap_rtv = set((_r, _t, _v) for _r, _t, _v in NewCapRTV.keys() if _t in techs and _r in regions)
    # periods the technology can be built in this region (sorted)
    periods = sorted(set(_v for _r, _t, _v in cap_rtv))

    if len(periods) == 0:
        if p == M.time_optimize.first():
            msg = (
                'Tried to set {}rowthNewCapacityDelta constraint {} but there are no periods where this '
                'technology can be built in this region. Constraint skipped.'
            ).format('Deg' if degrowth else 'G', (r, t))
            logger.warning(msg)
        return Constraint.Skip

    # Only warn in p0 so we dont dump multiple warnings
    if p == periods[0]:
        if SEED == 0:
            msg = (
                'No constant term (seed) provided for {}rowthNewCapacityDelta constraint {}. '
                'This is not recommended as deployment rates cannot inflect (change from '
                'accelerating to decelerating or vice-versa).'
            ).format('Deg' if degrowth else 'G', (r, t))
            logger.warning(msg)
        gaps = [
            _p for _p in M.time_optimize if _p not in periods and min(periods) < _p < max(periods)
        ]
        if gaps:
            msg = (
                'Constructing {}rowthNewCapacityDelta constraint {} and there are period gaps in which'
                'new capacity cannot be built in this region ({}). New capacity in these periods '
                'will be treated as zero which may cause infeasibility or other problems.'
            ).format('Deg' if degrowth else 'G', (r, t), gaps)
            logger.warning(msg)

    # sum new capacity in this period
    new_cap = sum(NewCapRTV[_r, _t, _v] for _r, _t, _v in cap_rtv if _v == p)

    if p == M.time_optimize.first():
        # First planning period, pull last two existing vintages
        p_prev = M.time_exist.last()
        new_cap_prev = sum(
            value(M.ExistingCapacity[_r, _t, _v])
            for _r, _t, _v in M.ExistingCapacity.sparse_iterkeys()
            if _r in regions and _t in techs and _v == p_prev
        )
        p_prev2 = M.time_exist.prev(p_prev)
        new_cap_prev2 = sum(
            value(M.ExistingCapacity[_r, _t, _v])
            for _r, _t, _v in M.ExistingCapacity.sparse_iterkeys()
            if _r in regions and _t in techs and _v == p_prev2
        )
    else:
        # Not the first future period. Grab previous future period
        p_prev = M.time_optimize.prev(p)
        new_cap_prev = sum(NewCapRTV[_r, _t, _v] for _r, _t, _v in cap_rtv if _v == p_prev)
        if p == M.time_optimize.at(2):  # apparently pyomo sets are indexed 1-based
            # Second future period, grab last existing vintage
            p_prev2 = M.time_exist.last()
            new_cap_prev2 = sum(
                value(M.ExistingCapacity[_r, _t, _v])
                for _r, _t, _v in M.ExistingCapacity.sparse_iterkeys()
                if _r in regions and _t in techs and _v == p_prev2
            )
        else:
            # At least the third future period. Grab last two future vintages
            p_prev2 = M.time_optimize.prev(p_prev)
            new_cap_prev2 = sum(NewCapRTV[_r, _t, _v] for _r, _t, _v in cap_rtv if _v == p_prev2)

    nc_delta_prev = new_cap_prev - new_cap_prev2
    nc_delta = new_cap - new_cap_prev

    if degrowth:
        expr = operator_expression(nc_delta_prev, op, SEED + nc_delta * RATE)
    else:
        expr = operator_expression(nc_delta, op, SEED + nc_delta_prev * RATE)

    # Check if any variables are actually included before returning
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitActivity_Constraint(M: 'TemoaModel', r, p, t, op):
    r"""

    Sets a limit on the activity from a specific technology.
    Note that the indices for these constraints are region, period and tech, not tech
    and vintage. The first version of the constraint pertains to technologies with
    variable output at the time slice level, and the second version pertains to
    technologies with constant annual output belonging to the :code:`tech_annual`
    set.

    .. math::
       :label: LimitActivity

       \sum_{S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o}

       \forall \{r, p, t \notin T^{a}\} \in \Theta_{\text{LimitActivity}}

       +\sum_{I,V,O} \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}

       \forall \{r, p, t \in T^{a}\} \in \Theta_{\text{LimitActivity}}

       \le LA_{r, p, t}
    """
    # r can be an individual region (r='US'), or a combination of regions separated by
    # a + (r='Mexico+US+Canada'), or 'global'.
    # if r == 'global', the constraint is system-wide
    regions = gather_group_regions(M, r)
    techs = gather_group_techs(M, t)

    activity = sum(
        M.V_FlowOut[_r, p, s, d, S_i, _t, S_v, S_o]
        for _t in techs
        if _t not in M.tech_annual
        for _r in regions
        for S_v in M.processVintages.get((_r, p, _t), [])
        for S_i in M.processInputs[_r, p, _t, S_v]
        for S_o in M.processOutputsByInput[_r, p, _t, S_v, S_i]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )
    activity += sum(
        M.V_FlowOutAnnual[_r, p, S_i, _t, S_v, S_o]
        for _t in techs
        if _t in M.tech_annual
        for _r in regions
        for S_v in M.processVintages.get((_r, p, _t), [])
        for S_i in M.processInputs[_r, p, _t, S_v]
        for S_o in M.processOutputsByInput[_r, p, _t, S_v, S_i]
    )

    act_lim = value(M.LimitActivity[r, p, t, op])
    expr = operator_expression(activity, op, act_lim)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


def LimitNewCapacity_Constraint(M: 'TemoaModel', r, p, t, op):
    r"""
    The LimitNewCapacity constraint sets a limit on the newly installed capacity of a
    given technology or group in a given year. Note that the indices for these constraints are region,
    period and tech.

    .. math::
        :label: LimitNewCapacity

        \textbf{NCAP}_{r, t, v} \le LNC_{r, p, t}

        \text{where }v=p
    """
    regions = gather_group_regions(M, r)
    techs = gather_group_techs(M, t)
    cap_lim = value(M.LimitNewCapacity[r, p, t, op])
    new_cap = sum(M.V_NewCapacity[_r, _t, p] for _t in techs for _r in regions)
    expr = operator_expression(new_cap, op, cap_lim)
    return expr


def LimitCapacity_Constraint(M: 'TemoaModel', r, p, t, op):
    r"""

    The LimitCapacity constraint sets a limit on the available capacity of a
    given technology. Note that the indices for these constraints are region, period and
    tech, not tech and vintage.

    .. math::
       :label: LimitCapacity

       \textbf{CAPAVL}_{r, p, t} \le LC_{r, p, t}

       \forall \{r, p, t\} \in \Theta_{\text{LimitCapacity}}"""
    regions = gather_group_regions(M, r)
    techs = gather_group_techs(M, t)
    cap_lim = value(M.LimitCapacity[r, p, t, op])
    capacity = sum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, _t] for _t in techs for _r in regions
    )
    expr = operator_expression(capacity, op, cap_lim)
    return expr


def LimitResource_Constraint(M: 'TemoaModel', r, t, op):
    r"""

    The LimitResource constraint sets a limit on the available resource of a
    given technology across all model time periods. Note that the indices for these
    constraints are region and tech.

    .. math::
       :label: LimitResource

       \sum_{P,S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t \notin T^a, v, o}

       +\sum_{P,I,V,O} \textbf{FO}_{r, p, i, t \in T^a, v, o}

       \le LR_{r, t}

       \forall \{r, t\} \in \Theta_{\text{LimitResource}}"""
    # dev note:  this constraint is a misnomer.  It is actually a "global activity constraint on a tech"
    #            regardless of whatever "resources" are consumed.
    # dev note:  this would generally be applied to a "dummy import" technology to restrict something like
    #            oil/mineral extraction across all model periods. Looks fine to me.

    regions = gather_group_regions(M, r)
    techs = gather_group_techs(M, t)

    activity = sum(
        M.V_FlowOutAnnual[_r, p, S_i, _t, S_v, S_o]
        for _t in techs
        if _t in M.tech_annual
        for p in M.time_optimize
        for _r in regions
        if (_r, p, _t) in M.processVintages
        for S_v in M.processVintages[_r, p, _t]
        for S_i in M.processInputs[_r, p, _t, S_v]
        for S_o in M.processOutputsByInput[_r, p, _t, S_v, S_i]
    )
    activity += sum(
        M.V_FlowOut[_r, p, s, d, S_i, _t, S_v, S_o]
        for _t in techs
        if _t not in M.tech_annual
        for p in M.time_optimize
        for _r in regions
        if (_r, p, _t) in M.processVintages
        for S_v in M.processVintages[_r, p, _t]
        for S_i in M.processInputs[_r, p, _t, S_v]
        for S_o in M.processOutputsByInput[_r, p, _t, S_v, S_i]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    resource_lim = value(M.LimitResource[r, t, op])
    expr = operator_expression(activity, op, resource_lim)
    return expr


def LimitActivityShare_Constraint(M: 'TemoaModel', r, p, g1, g2, op):
    r"""
    Limits the activity of a given technology or group as a fraction of another
    technology or group, summed over a period. This can be used to set, for example,
    a renewable portfolio scheme constraint.

    .. math::
        :label: Limit Activity Share

        \sum_{R_g \subseteq R,\ S,\ D,\ I,\ T^{g_1} \subseteq T,\ V,\ O} \mathbf{FO}_{r,p,s,d,i,t,v,o}
        \leq LAS_{r,p,g_1,g_2} \cdot
        \sum_{R_g \subseteq R,\ S,\ D,\ I,\ T^{g_2} \subseteq T,\ V,\ O} \mathbf{FO}_{r,p,s,d,i,t,v,o}

        \qquad \forall \{r, p, g_1, g_2\} \in \Theta_{\text{LimitActivityShare}}
    """

    regions = gather_group_regions(M, r)

    sub_group = gather_group_techs(M, g1)
    sub_activity = sum(
        M.V_FlowOut[_r, p, s, d, S_i, S_t, S_v, S_o]
        for S_t in sub_group
        if S_t not in M.tech_annual
        for _r in regions
        for S_v in M.processVintages.get((_r, p, S_t), [])
        for S_i in M.processInputs[_r, p, S_t, S_v]
        for S_o in M.processOutputsByInput[_r, p, S_t, S_v, S_i]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )
    sub_activity += sum(
        M.V_FlowOutAnnual[_r, p, S_i, S_t, S_v, S_o]
        for S_t in sub_group
        if S_t in M.tech_annual
        for _r in regions
        for S_v in M.processVintages.get((_r, p, S_t), [])
        for S_i in M.processInputs[_r, p, S_t, S_v]
        for S_o in M.processOutputsByInput[_r, p, S_t, S_v, S_i]
    )

    super_group = gather_group_techs(M, g2)
    super_activity = sum(
        M.V_FlowOut[_r, p, s, d, S_i, S_t, S_v, S_o]
        for S_t in super_group
        if S_t not in M.tech_annual
        for _r in regions
        for S_v in M.processVintages.get((_r, p, S_t), [])
        for S_i in M.processInputs[_r, p, S_t, S_v]
        for S_o in M.processOutputsByInput[_r, p, S_t, S_v, S_i]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )
    super_activity += sum(
        M.V_FlowOutAnnual[_r, p, S_i, S_t, S_v, S_o]
        for S_t in super_group
        if S_t in M.tech_annual
        for _r in regions
        for S_v in M.processVintages.get((_r, p, S_t), [])
        for S_i in M.processInputs[_r, p, S_t, S_v]
        for S_o in M.processOutputsByInput[_r, p, S_t, S_v, S_i]
    )

    share_lim = value(M.LimitActivityShare[r, p, g1, g2, op])
    expr = operator_expression(sub_activity, op, share_lim * super_activity)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    logger.debug(
        'created limit activity share constraint for (%s, %d, %s, %s) of %0.2f',
        r,
        p,
        g1,
        g2,
        share_lim,
    )
    return expr


def LimitCapacityShare_Constraint(M: 'TemoaModel', r, p, g1, g2, op):
    r"""
    The LimitCapacityShare constraint limits the available capacity of a given
    technology or technology group as a fraction of another technology or group.
    """

    regions = gather_group_regions(M, r)

    sub_group = gather_group_techs(M, g1)
    sub_capacity = sum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, _t]
        for _t in sub_group
        for _r in regions
        if (_r, p, _t) in M.processVintages
    )

    super_group = gather_group_techs(M, g2)
    super_capacity = sum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, _t]
        for _t in super_group
        for _r in regions
        if (_r, p, _t) in M.processVintages
    )
    share_lim = value(M.LimitCapacityShare[r, p, g1, g2, op])

    expr = operator_expression(sub_capacity, op, share_lim * super_capacity)
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitNewCapacityShare_Constraint(M: 'TemoaModel', r, p, g1, g2, op):
    r"""
    The LimitNewCapacityShare constraint limits the share of new capacity
    of a given technology or group as a fraction of another technology or
    group."""

    regions = gather_group_regions(M, r)

    sub_group = gather_group_techs(M, g1)
    sub_new_cap = sum(
        M.V_NewCapacity[_r, _t, p]
        for _t in sub_group
        for _r in regions
        if (_r, _t, p) in M.processPeriods
    )

    super_group = gather_group_techs(M, g2)
    super_new_cap = sum(
        M.V_NewCapacity[_r, _t, p]
        for _t in super_group
        for _r in regions
        if (_r, _t, p) in M.processPeriods
    )

    share_lim = value(M.LimitNewCapacityShare[r, p, g1, g2, op])
    expr = operator_expression(sub_new_cap, op, share_lim * super_new_cap)
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitAnnualCapacityFactor_Constraint(M: 'TemoaModel', r, p, t, o, op):
    r"""
    The LimitAnnualCapacityFactor sets an upper bound on the annual capacity factor
    from a specific technology. The first portion of the constraint pertains to
    technologies with variable output at the time slice level, and the second portion
    pertains to technologies with constant annual output belonging to the
    :code:`tech_annual` set.

    .. math::
        :label: LimitAnnualCapacityFactor

            \sum_{S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o} \le LIMACF_{r, p, t} \cdot \textbf{CAPAVL}_{r, p, t} \cdot \text{C2A}_{r, t}

            \forall \{r, p, t \notin T^{a}, o\} \in \Theta_{\text{LimitAnnualCapacityFactor}}

            \\\sum_{I,V,O} \textbf{FOA}_{r, p, i, t, v, o} \ge LIMACF_{r, p, t} \cdot \textbf{CAPAVL}_{r, p, t} \cdot \text{C2A}_{r, t}

            \forall \{r, p, t \in T^{a}, o\} \in \Theta_{\text{LimitAnnualCapacityFactor}}
    """
    # r can be an individual region (r='US'), or a combination of regions separated by plus (r='Mexico+US+Canada'), or 'global'.
    # if r == 'global', the constraint is system-wide
    regions = gather_group_regions(M, r)
    # we need to screen here because it is possible that the restriction extends beyond the
    # lifetime of any vintage of the tech...
    if all((_r, p, t) not in M.V_CapacityAvailableByPeriodAndTech for _r in regions):
        return Constraint.Skip

    if t not in M.tech_annual:
        activity_rpt = sum(
            M.V_FlowOut[_r, p, s, d, S_i, t, S_v, o]
            for _r in regions
            for S_v in M.processVintages.get((_r, p, t), [])
            for S_i in M.processInputs[_r, p, t, S_v]
            for s in M.TimeSeason[p]
            for d in M.time_of_day
        )
    else:
        activity_rpt = sum(
            M.V_FlowOutAnnual[_r, p, S_i, t, S_v, o]
            for _r in regions
            for S_v in M.processVintages.get((_r, p, t), [])
            for S_i in M.processInputs[_r, p, t, S_v]
        )

    possible_activity_rpt = sum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, t] * value(M.CapacityToActivity[_r, t])
        for _r in regions
    )
    annual_cf = value(M.LimitAnnualCapacityFactor[r, p, t, o, op])
    expr = operator_expression(activity_rpt, op, annual_cf * possible_activity_rpt)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


def LimitSeasonalCapacityFactor_Constraint(M: 'TemoaModel', r, p, s, t, op):
    r"""
    The LimitSeasonalCapacityFactor sets an upper bound on the seasonal capacity factor
    from a specific technology. The first portion of the constraint pertains to
    technologies with variable output at the time slice level, and the second portion
    pertains to technologies with constant annual output belonging to the
    :code:`tech_annual` set.

    .. math::
        :label: Limit Seasonal Capacity Factor

        \sum_{D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o} \le LIMSCF_{r, p, s, t} \cdot \textbf{CAPAVL}_{r, p, t} \cdot \text{C2A}_{r, t}

        \forall \{r, p, t \notin T^{a}, o\} \in \Theta_{\text{LimitSeasonalCapacityFactor}}

        \\\sum_{I,V,O} \textbf{FOA}_{r, p, i, t, v, o} \cdot \sum_{D} SEG_{s,d} \le LIMSCF_{r, p, s, t} \cdot \textbf{CAPAVL}_{r, p, t} \cdot \text{C2A}_{r, t}

        \forall \{r, p, t \in T^{a}, o\} \in \Theta_{\text{LimitSeasonalCapacityFactor}}
    """
    # r can be an individual region (r='US'), or a combination of regions separated by plus (r='Mexico+US+Canada'), or 'global'.
    # if r == 'global', the constraint is system-wide
    regions = gather_group_regions(M, r)
    # we need to screen here because it is possible that the restriction extends beyond the
    # lifetime of any vintage of the tech...
    if all((_r, p, t) not in M.V_CapacityAvailableByPeriodAndTech for _r in regions):
        return Constraint.Skip

    if t not in M.tech_annual:
        activity_rpst = sum(
            M.V_FlowOut[_r, p, s, d, S_i, t, S_v, S_o]
            for _r in regions
            for S_v in M.processVintages[_r, p, t]
            for S_i in M.processInputs[_r, p, t, S_v]
            for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
            for d in M.time_of_day
        )
    else:
        activity_rpst = sum(
            M.V_FlowOutAnnual[_r, p, S_i, t, S_v, S_o] * M.SegFracPerSeason[p, s]
            for _r in regions
            for S_v in M.processVintages[_r, p, t]
            for S_i in M.processInputs[_r, p, t, S_v]
            for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
        )

    possible_activity_rpst = sum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, t]
        * value(M.CapacityToActivity[_r, t])
        * value(M.SegFracPerSeason[p, s])
        for _r in regions
    )
    seasonal_cf = value(M.LimitSeasonalCapacityFactor[r, p, s, t, op])
    expr = operator_expression(activity_rpst, op, seasonal_cf * possible_activity_rpst)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


def LimitTechInputSplit_Constraint(M: 'TemoaModel', r, p, s, d, i, t, v, op):
    r"""
    Allows users to limit shares of commodity inputs to a process
    producing a single output. These shares can vary by model time period. See
    LimitTechOutputSplit_Constraint for an analogous explanation. Under this constraint,
    only the technologies with variable output at the timeslice level (i.e.,
    NOT in the :code:`tech_annual` set) are considered."""
    inp = sum(
        M.V_FlowOut[r, p, s, d, i, t, v, S_o] / get_variable_efficiency(M, r, p, s, d, i, t, v, S_o)
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    total_inp = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        / get_variable_efficiency(M, r, p, s, d, S_i, t, v, S_o)
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = operator_expression(inp, op, value(M.LimitTechInputSplit[r, p, i, t, op]) * total_inp)
    return expr


def LimitTechInputSplitAnnual_Constraint(M: 'TemoaModel', r, p, i, t, v, op):
    r"""
    Allows users to limit shares of commodity inputs to a process
    producing a single output. These shares can vary by model time period. See
    LimitTechOutputSplitAnnual_Constraint for an analogous explanation. Under this
    function, only the technologies with constant annual output (i.e., members
    of the :code:`tech_annual` set) are considered."""
    inp = sum(
        M.V_FlowOutAnnual[r, p, i, t, v, S_o] / value(M.Efficiency[r, i, t, v, S_o])
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    total_inp = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o] / value(M.Efficiency[r, S_i, t, v, S_o])
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = operator_expression(
        inp, op, value(M.LimitTechInputSplitAnnual[r, p, i, t, op]) * total_inp
    )
    return expr


def LimitTechInputSplitAverage_Constraint(M: 'TemoaModel', r, p, i, t, v, op):
    r"""
    Allows users to limit shares of commodity inputs to a process
    producing a single output. Under this constraint, only the technologies with variable
    output at the timeslice level (i.e., NOT in the :code:`tech_annual` set) are considered.
    This constraint differs from LimitTechInputSplit as it specifies shares on an annual basis,
    so even though it applies to technologies with variable output at the timeslice level,
    the constraint only fixes the input shares over the course of a year."""

    inp = sum(
        M.V_FlowOut[r, p, S_s, S_d, i, t, v, S_o]
        / get_variable_efficiency(M, r, p, S_s, S_d, i, t, v, S_o)
        for S_s in M.TimeSeason[p]
        for S_d in M.time_of_day
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    total_inp = sum(
        M.V_FlowOut[r, p, S_s, S_d, S_i, t, v, S_o]
        / get_variable_efficiency(M, r, p, S_s, S_d, i, t, v, S_o)
        for S_s in M.TimeSeason[p]
        for S_d in M.time_of_day
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    expr = operator_expression(
        inp, op, value(M.LimitTechInputSplitAnnual[r, p, i, t, op]) * total_inp
    )
    return expr


def LimitTechOutputSplit_Constraint(M: 'TemoaModel', r, p, s, d, t, v, o, op):
    r"""

    Some processes take a single input and make multiple outputs, and the user would like to
    specify either a constant or time-varying ratio of outputs per unit input.  The most
    canonical example is an oil refinery.  Crude oil is used to produce many different refined
    products. In many cases, the modeler would like to limit the share of each refined
    product produced by the refinery.

    For example, a hypothetical (and highly simplified) refinery might have a crude oil input
    that produces 4 parts diesel, 3 parts gasoline, and 2 parts kerosene.  The relative
    ratios to the output then are:

    .. math::

       d = \tfrac{4}{9} \cdot \text{total output}, \qquad
       g = \tfrac{3}{9} \cdot \text{total output}, \qquad
       k = \tfrac{2}{9} \cdot \text{total output}

    Note that it is possible to specify output shares that sum to less than unity. In such
    cases, the model optimizes the remaining share. In addition, it is possible to change the
    specified shares by model time period. Under this constraint, only the
    technologies with variable output at the timeslice level (i.e., NOT in the
    :code:`tech_annual` set) are considered.

    The constraint is formulated as follows:

    .. math::
       :label: LimitTechOutputSplit

         \sum_{I, t \not \in T^{a}} \textbf{FO}_{r, p, s, d, i, t, v, o}
       \geq
         TOS_{r, p, t, o} \cdot \sum_{I, O, t \not \in T^{a}} \textbf{FO}_{r, p, s, d, i, t, v, o}

       \forall \{r, p, s, d, t, v, o\} \in \Theta_{\text{LimitTechOutputSplit}}"""
    out = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, o] for S_i in M.processInputsByOutput[r, p, t, v, o]
    )

    total_out = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = operator_expression(out, op, value(M.LimitTechOutputSplit[r, p, t, o, op]) * total_out)
    return expr


def LimitTechOutputSplitAnnual_Constraint(M: 'TemoaModel', r, p, t, v, o, op):
    r"""
    This constraint operates similarly to LimitTechOutputSplit_Constraint.
    However, under this function, only the technologies with constant annual
    output (i.e., members of the :code:`tech_annual` set) are considered.

    .. math::
       :label: LimitTechOutputSplitAnnual

            \sum_{I, T^{a}} \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}
            \geq
            TOS_{r, p, t, o} \cdot \sum_{I, O, T^{a}} \textbf{FOA}_{r, p, s, d, i, t \in T^{a}, v, o}

            \forall \{r, p, t \in T^{a}, v, o\} \in \Theta_{\text{LimitTechOutputSplitAnnual}}"""
    out = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, o] for S_i in M.processInputsByOutput[r, p, t, v, o]
    )

    total_out = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = operator_expression(
        out, op, value(M.LimitTechOutputSplitAnnual[r, p, t, o, op]) * total_out
    )
    return expr


def LimitTechOutputSplitAverage_Constraint(M: 'TemoaModel', r, p, t, v, o, op):
    r"""
    Allows users to limit shares of commodity outputs from a process.
    Under this constraint, only the technologies with variable
    output at the timeslice level (i.e., NOT in the :code:`tech_annual` set) are considered.
    This constraint differs from LimitTechOutputSplit as it specifies shares on an annual basis,
    so even though it applies to technologies with variable output at the timeslice level,
    the constraint only fixes the output shares over the course of a year."""

    out = sum(
        M.V_FlowOut[r, p, S_s, S_d, S_i, t, v, o]
        for S_i in M.processInputsByOutput[r, p, t, v, o]
        for S_s in M.TimeSeason[p]
        for S_d in M.time_of_day
    )

    total_out = sum(
        M.V_FlowOut[r, p, S_s, S_d, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        for S_s in M.TimeSeason[p]
        for S_d in M.time_of_day
    )

    expr = operator_expression(
        out, op, value(M.LimitTechOutputSplitAnnual[r, p, t, o, op]) * total_out
    )
    return expr


# @deprecated('Deprecated. Use LimitActivityGroupShare instead') # doesn't play well with pyomo
def RenewablePortfolioStandard_Constraint(M: 'TemoaModel', r, p, g):
    r"""
    Allows users to specify the share of electricity generation in a region
    coming from RPS-eligible technologies.
    """
    # devnote: this formulation leans on the reserve set, which is not necessarily
    # the super set we want. We can also generalise this to all groups and so
    # it has been deprecated in favour of the LimitActivityGroupShare constraint.

    inp = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for t in M.tech_group_members[g]
        for (_t, v) in M.processReservePeriods[r, p]
        if _t == t
        for s in M.TimeSeason[p]
        for d in M.time_of_day
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    total_inp = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for (t, v) in M.processReservePeriods[r, p]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = inp >= (value(M.RenewablePortfolioStandard[r, p, g]) * total_inp)
    return expr


# ---------------------------------------------------------------
# Define rule-based parameters
# ---------------------------------------------------------------
# devnote: MPL no longer used. Instead, use adjusted capacity * period length
# def ParamModelProcessLife_rule(M: 'TemoaModel', r, p, t, v):
#     life_length = value(M.LifetimeProcess[r, t, v])
#     mpl = min(v + life_length - p, value(M.PeriodLength[p]))

#     return mpl


def ParamPeriodLength(M: 'TemoaModel', p):
    # This specifically does not use time_optimize because this function is
    # called /over/ time_optimize.
    periods = sorted(M.time_future)

    i = periods.index(p)

    # The +1 won't fail, because this rule is called over time_optimize, which
    # lacks the last period in time_future.
    length = periods[i + 1] - periods[i]

    return length


def ParamProcessLifeFraction_rule(M: 'TemoaModel', r, p, t, v):
    r"""
    Get the effective capacity of a process :math:`<r, t, v>` in a period :math:`p`.

    Accounts for mid-period end of life or average survival over the period
    for processes using survival curves.
    """

    period_length = value(M.PeriodLength[p])

    if M.isSurvivalCurveProcess[r, t, v]:
        # Sum survival fraction over the period
        years_remaining = sum(
            value(M.LifetimeSurvivalCurve[r, _p, t, v]) for _p in range(p, p + period_length, 1)
        )
    else:
        # Remaining life years within the EOL period
        years_remaining = v + value(M.LifetimeProcess[r, t, v]) - p

    if years_remaining >= period_length:
        # try to avoid floating point round-off errors for the common case.
        return 1

    frac = years_remaining / float(period_length)
    return frac


# devnote: made redundant by time-value equations for objective function
# def loan_annualization_rate(loan_rate: float | None, loan_life: int | float) -> float:
#     """
#     This calculation is broken out specifically so that it can be used for param creation
#     and separately to calculate loan costs rather than rely on fully-built model parameters
#     :param loan_rate:
#     :param loan_life:

#     """
#     if not loan_rate:
#         # dev note:  this should not be needed as the LoanRate param has a default (see the definition)
#         return 1.0 / loan_life
#     annualized_rate = loan_rate / (1.0 - (1.0 + loan_rate) ** (-loan_life))
#     return annualized_rate


def ParamLoanAnnualize_rule(M: 'TemoaModel', r, t, v):
    dr = value(M.LoanRate[r, t, v])
    lln = value(M.LoanLifetimeProcess[r, t, v])
    annualized_rate = pv_to_annuity(dr, lln)
    return annualized_rate


def SegFracPerSeason_rule(M: 'TemoaModel', p, s):
    return sum(value(M.SegFrac[p, s, S_d]) for S_d in M.time_of_day if (p, s, S_d) in M.SegFrac)


def LinkedEmissionsTech_Constraint(M: 'TemoaModel', r, p, s, d, t, v, e):
    r"""
    This constraint is necessary for carbon capture technologies that produce
    CO2 as an emissions commodity, but the CO2 also serves as a physical
    input commodity to a downstream process, such as synthetic fuel production.
    To accomplish this, a dummy technology is linked to the CO2-producing
    technology, converting the emissions activity into a physical commodity
    amount as follows:

    .. math::
       :label: LinkedEmissionsTech

         - \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o} \cdot EAC_{r, e, i, t, v, o}
         = \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o}

        \forall \{r, p, s, d, t, v, e\} \in \Theta_{\text{LinkedTechs}}

    The relationship between the primary and linked technologies is given
    in the :code:`LinkedTechs` table. Note that the primary and linked
    technologies cannot be part of the :code:`tech_annual` set. It is implicit that
    the primary region corresponds to the linked technology as well. The lifetimes
    of the primary and linked technologies should be specified and identical.
    """

    if t in M.tech_annual:
        primary_flow = sum(
            (
                value(M.DemandSpecificDistribution[r, p, s, d, S_o])
                if S_o in M.commodity_demand
                else value(M.SegFrac[p, s, d])
            )
            * M.V_FlowOutAnnual[r, p, S_i, t, v, S_o]
            * value(M.EmissionActivity[r, e, S_i, t, v, S_o])
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )
    else:
        primary_flow = sum(
            M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
            * value(M.EmissionActivity[r, e, S_i, t, v, S_o])
            for S_i in M.processInputs[r, p, t, v]
            for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        )

    linked_t = M.LinkedTechs[r, t, e]

    # linked_flow = sum(
    #     M.V_FlowOut[r, p, s, d, S_i, linked_t, v, S_o]
    #     for S_i in M.processInputs[r, p, linked_t, v]
    #     for S_o in M.processOutputsByInput[r, p, linked_t, v, S_i]
    # )

    if linked_t in M.tech_annual:
        linked_flow = sum(
            (
                value(M.DemandSpecificDistribution[r, p, s, d, S_o])
                if S_o in M.commodity_demand
                else value(M.SegFrac[p, s, d])
            )
            * M.V_FlowOutAnnual[r, p, S_i, linked_t, v, S_o]
            for S_i in M.processInputs[r, p, linked_t, v]
            for S_o in M.processOutputsByInput[r, p, linked_t, v, S_i]
        )
    else:
        linked_flow = sum(
            M.V_FlowOut[r, p, s, d, S_i, linked_t, v, S_o]
            for S_i in M.processInputs[r, p, linked_t, v]
            for S_o in M.processOutputsByInput[r, p, linked_t, v, S_i]
        )

    return -primary_flow == linked_flow


def operator_expression(lhs: Expression | None, operator: str | None, rhs: Expression | None):
    """Returns an expression, applying a configured operator"""
    if any((lhs is None, operator is None, rhs is None)):
        msg = ('Tried to build a constraint using a bad expression or operator: {} {} {}').format(
            lhs, operator, rhs
        )
        logger.error(msg)
        raise ValueError(msg)
    try:
        match operator:
            case 'e':
                expr = lhs == rhs
            case 'le':
                expr = lhs <= rhs
            case 'ge':
                expr = lhs >= rhs
            case _:
                msg = (
                    'Tried to build a constraint using a bad operator. Allowed operators are "e","le", or "ge". Got "{}": {} {} {}'
                ).format(operator, lhs, operator, rhs)
                logger.error(msg)
                raise ValueError(msg)
    except Exception as e:
        print(e)
        msg = ('Tried to build a constraint using a bad expression or operator: {} {} {}').format(
            lhs, operator, rhs
        )
        logger.error(msg)
        raise ValueError(msg)

    return expr


# To avoid building big many-indexed parameters when they aren't needed - saves memory
# Much faster to build a dictionary and check that than check the parameter
# indices directly every time - saves build time
def get_variable_efficiency(M: 'TemoaModel', r, p, s, d, i, t, v, o):
    if M.isEfficiencyVariable[r, p, i, t, v, o]:
        return value(M.Efficiency[r, i, t, v, o]) * value(
            M.EfficiencyVariable[r, p, s, d, i, t, v, o]
        )
    else:
        return value(M.Efficiency[r, i, t, v, o])


def get_capacity_factor(M: 'TemoaModel', r, p, s, d, t, v):
    if M.isCapacityFactorProcess[r, p, t, v]:
        return value(M.CapacityFactorProcess[r, p, s, d, t, v])
    else:
        return value(M.CapacityFactorTech[r, p, s, d, t])
