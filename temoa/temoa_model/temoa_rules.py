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

from pyomo.core import Var, Expression
from pyomo.environ import Constraint, value

from temoa.temoa_model.temoa_initialize import (
    DemandConstraintErrorCheck,
    CommodityBalanceConstraintErrorCheck,
    AnnualCommodityBalanceConstraintErrorCheck,
    gather_group_regions,
)

if TYPE_CHECKING:
    from temoa.temoa_model.temoa_model import TemoaModel

logger = getLogger(__name__)
# ---------------------------------------------------------------
# Define the derived variables used in the objective function
# and constraints below.
# ---------------------------------------------------------------


def AdjustedCapacity_Constraint(M: 'TemoaModel', r, p, t, v):
    r"""
    This constraint updates the capacity of a process by taking into account retirements.
    For a given :code:`(r,p,t,v)` index, this constraint sets the capacity equal to
    the amount installed in period :code:`v` and subtracts from it any and all retirements
    that occurred up until the period in question, :code:`p`."""
    if t not in M.tech_retirement:
        if v in M.time_exist:
            return M.V_Capacity[r, p, t, v] == value(M.ExistingCapacity[r, t, v])
        else:
            return M.V_Capacity[r, p, t, v] == M.V_NewCapacity[r, t, v]

    else:
        retired_cap = sum(
            M.V_RetiredCapacity[r, S_p, t, v] for S_p in M.time_optimize if p >= S_p > v
        )
        if v in M.time_exist:
            return M.V_Capacity[r, p, t, v] == value(M.ExistingCapacity[r, t, v]) - retired_cap
        else:
            return M.V_Capacity[r, p, t, v] == M.V_NewCapacity[r, t, v] - retired_cap
    

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
                   \text{CFP}_{r, t, v}
             \cdot \text{C2A}_{r, t}
             \cdot \text{SEG}_{s, d}
             \cdot \text{PLF}_{r, p, t, v}
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

    useful_activity = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )
    capacity = get_capacity_factor(M, r, p, s, d, t, v)
    
    if t in M.tech_curtailment:
        # If technologies are present in the curtailment set, then enough
        # capacity must be available to cover both activity and curtailment.
        return (
            capacity
            * value(M.CapacityToActivity[r, t])
            * value(M.SegFrac[p, s, d])
            * value(M.ProcessLifeFrac[r, p, t, v])
            * M.V_Capacity[r, p, t, v] == useful_activity + sum(
                M.V_Curtailment[r, p, s, d, S_i, t, v, S_o]
                for S_i in M.processInputs[r, p, t, v]
                for S_o in M.processOutputsByInput[r, p, t, v, S_i]
            )
        )
    else:
        return (
            capacity
            * value(M.CapacityToActivity[r, t])
            * value(M.SegFrac[p, s, d])
            * value(M.ProcessLifeFrac[r, p, t, v])
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
capacity.

.. math::
   :label: CapacityAnnual

       \left (
               \text{CFP}_{r, t, v}
         \cdot \text{C2A}_{r, t}
         \cdot \text{PLF}_{r, p, t, v}
       \right )
       \cdot \textbf{CAP}_{r, t, v}
   =
       \sum_{I, O} \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}

   \\
   \forall \{r, p, t \in T^{a}, v\} \in \Theta_{\text{Activity}}


"""
    CF = 1  # placeholder CF

    activity_rptv = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    return (
        CF
        * value(M.CapacityToActivity[r, t])
        * value(M.ProcessLifeFrac[r, p, t, v])
        * M.V_Capacity[r, p, t, v]
        >= activity_rptv
    )


def ActivityByTech_Constraint(M: 'TemoaModel', t):
    r"""
    This constraint is utilized by the MGA objective function and defines
    the total activity of a technology over the planning horizon. The first version
    below applies to technologies with variable output at the timeslice level,
    and the second version applies to technologies with constant annual output
    in the :code:`tech_annual` set.

    .. math::
       :label: ActivityByTech

           \textbf{ACT}_{t} = \sum_{R, P, S, D, I, V, O} \textbf{FO}_{r, p, s, d,i, t, v, o}
           \;
           \forall t \not\in T^{a}

           \textbf{ACT}_{t} = \sum_{R, P, I, V, O} \textbf{FOA}_{r, p, i, t, v, o}
           \;
           \forall t \in T^{a}
    """
    if t not in M.tech_annual:
        indices = []
        for s_index in M.FlowVar_rpsditvo:
            if t in s_index:
                indices.append(s_index)
        activity = sum(M.V_FlowOut[s_index] for s_index in indices)
    else:
        indices = []
        for s_index in M.FlowVarAnnual_rpitvo:
            if t in s_index:
                indices.append(s_index)
        activity = sum(M.V_FlowOutAnnual[s_index] for s_index in indices)

    if int is type(activity):
        return Constraint.Skip

    expr = M.V_ActivityByTech[t] == activity
    return expr


def CapacityAvailableByPeriodAndTech_Constraint(M: 'TemoaModel', r, p, t):
    r"""

The :math:`\textbf{CAPAVL}` variable is nominally for reporting solution values,
but is also used in the Limit constraint calculations.  For any process
with an end-of-life (EOL) on a period boundary, all of its capacity is available
for use in all periods in which it is active (the process' PLF is 1). However,
for any process with an EOL that falls between periods, Temoa makes the
simplifying assumption that the available capacity from the expiring technology
is available through the whole period in proportion to its remaining lifetime.
For example, if a process expires 3 years into an 8-year model time period,
then only :math:`\frac{3}{8}` of the installed capacity is available for use
throughout the period.

.. math::
   :label: CapacityAvailable

   \textbf{CAPAVL}_{r, p, t} = \sum_{v, p_i \leq p} {PLF}_{r, p, t, v} \cdot \left
   ( \textbf{CAP}_{r, t, v} - \textbf{CAPRET}_{r, p_i, t, v} \right )

   \\
   \forall p \in \text{P}^o, r \in R, t \in T
"""
    cap_avail = sum(
        value(M.ProcessLifeFrac[r, p, t, S_v]) * M.V_Capacity[r, p, t, S_v]
        for S_v in M.processVintages[r, p, t]
    )

    expr = M.V_CapacityAvailableByPeriodAndTech[r, p, t] == cap_avail
    return expr


def RetiredCapacity_Constraint(M: 'TemoaModel', r, p, t, v):
    r"""

Temoa allows for the economic retirement of technologies presented in the
:code:`tech_retirement` set. This constraint sets the upper limit of retired
capacity to the total installed capacity.
In the equation below, we set the upper bound of the retired capacity to the
previous period's total installed capacity (CAPAVL)

.. math::
   :label: RetiredCapacity

   \textbf{CAPRET}_{r, p, t, v} \leq \sum_{V} {PLF}_{r, p, t, v} \cdot \textbf{CAP}_{r, t, v}
   \\
   \forall \{r, p, t, v\} \in \Theta_{\text{RetiredCapacity}}
"""
    if p == M.time_optimize.first():
        cap_avail = value(M.ExistingCapacity[r, t, v])
    else:
        cap_avail = M.V_Capacity[r, M.time_optimize.prev(p), t, v]
    expr = M.V_RetiredCapacity[r, p, t, v] <= cap_avail
    return expr


def AnnualRetirement_Constraint(M: 'TemoaModel', r, p, t, v):
    r"""
    Get the annualised retirement rate for a process in a given period. 
    Used to model end of life flows and emissions. Assumes that retirement
    is evenly distributed over the model period, in the same way we assume
    capacity is deployed evenly over the model period.
    """

    # Need to know what already (before period p) retired economically so we don't double count
    already_retired = 0
    if t in M.tech_retirement:
        already_retired = sum(
            M.V_RetiredCapacity[r, S_p, t, v] for S_p in M.time_optimize if v < S_p < p
        )

    # If it naturally retires at the beginning of or during this period, all capacity minus already retired
    l = value(M.LifetimeProcess[r, t, v])
    if v+l == p or value(M.ModelProcessLife[r, p, t, v]) < value(M.PeriodLength[p]):
        if v in M.time_optimize:
            retired = M.V_NewCapacity[r, t, v] - already_retired
        elif v in M.time_exist:
            retired = M.ExistingCapacity[r, t, v] - already_retired
    # Otherwise if not the vintage period then just early (economic) retirement in this period
    elif t in M.tech_retirement and v < p:
        retired = M.V_RetiredCapacity[r, p, t, v]
    # Neither natural retirement nor early economic retirement possible
    else:
        retired = 0.0

    # Distribute retirement evenly over planning period
    retired /= value(M.PeriodLength[p])

    return M.V_AnnualRetirement[r, p, t, v] == retired


# ---------------------------------------------------------------
# Define the Objective Function
# ---------------------------------------------------------------
def TotalCost_rule(M):
    r"""

    Using the :code:`FlowOut` and :code:`Capacity` variables, the Temoa objective
    function calculates the cost of energy supply, under the assumption that capital
    costs are paid through loans. This implementation sums up all the costs incurred,
    and is defined as :math:`C_{tot} = C_{loans} + C_{fixed} + C_{variable}`. Each
    term on the right-hand side represents the cost incurred over the model
    time horizon and discounted to the initial year in the horizon (:math:`{P}_0`).
    The calculation of each term is given below.

    .. math::
       :label: obj_loan

       C_{loans} = \sum_{r, t, v \in \Theta_{IC}} \left (
         \left [
                 CI_{r, t, v} \cdot LA_{r, t, v}
                 \cdot \frac{(1 + GDR)^{P_0 - v +1} \cdot (1 - (1 + GDR)^{-LLP_{r, t, v}})}{GDR} \right. \right.
                 \\ \left. \left. \cdot \frac{ 1-(1+GDR)^{-LPA_{r,t,v}} }{ 1-(1+GDR)^{-LTP_{r,t,v}} }
         \right ]
         \cdot \textbf{CAP}_{r, t, v}
         \right )

    Note that capital costs (:math:`{IC}_{r,t,v}`) are handled in several steps. First, each capital cost
    is amortized using the loan rate (i.e., technology-specific discount rate) and loan
    period. Second, the annual stream of payments is converted into a lump sum using
    the global discount rate and loan period. Third, the new lump sum is amortized
    at the global discount rate and technology lifetime. Fourth, loan payments beyond
    the model time horizon are removed and the lump sum recalculated. The terms used
    in Steps 3-4 are :math:`\frac{ GDR }{ 1-(1+GDR)^{-LTP_{r,t,v} } }\cdot
    \frac{ 1-(1+GDR)^{-LPA_{t,v}} }{ GDR }`. The product simplifies to
    :math:`\frac{ 1-(1+GDR)^{-LPA_{r,t,v}} }{ 1-(1+GDR)^{-LTP_{r,t,v}} }`, where
    :math:`LPA_{r,t,v}` represents the active lifetime of process t in region r :math:`(r,t,v)`
    before the end of the model horizon, and :math:`LTP_{r,t,v}` represents the full
    lifetime of a regional process :math:`(r,t,v)`. Fifth, the lump sum is discounted back to the
    beginning of the horizon (:math:`P_0`) using the global discount rate. While an
    explicit salvage term is not included, this approach properly captures the capital
    costs incurred within the model time horizon, accounting for technology-specific
    loan rates and periods.

    .. math::
       :label: obj_fixed

       C_{fixed} = \sum_{r, p, t, v \in \Theta_{CF}} \left (
         \left [
                 CF_{r, p, t, v}
           \cdot \frac{(1 + GDR)^{P_0 - p +1} \cdot (1 - (1 + GDR)^{-{MPL}_{r, t, v}})}{GDR}
         \right ]
         \cdot \textbf{CAP}_{r, t, v}
         \right )

    .. math::
       :label: obj_variable

        &C_{variable} = \\ &\quad \sum_{r, p, t, v \in \Theta_{CV}} \left (
               CV_{r, p, t, v}
         \cdot
         \frac{
           (1 + GDR)^{P_0 - p + 1} \cdot (1 - (1 + GDR)^{-{MPL}_{r,p,t,v}})
         }{
           GDR
         }\cdot \sum_{S,D,I, O} \textbf{FO}_{r, p, s, d,i, t, v, o}
         \right ) \\ &\quad + \sum_{r, p, t \not \in T^{a}, v \in \Theta_{VC}} \left (
               CV_{r, p, t, v}
         \cdot
         \frac{
           (1 + GDR)^{P_0 - p + 1} \cdot (1 - (1 + GDR)^{-{MPL}_{r,p,t,v}})
         }{
           GDR
         }
         \cdot \sum_{I, O} \textbf{FOA}_{r, p,i, t \in T^{a}, v, o}
         \right )

    .. math::
        :label: obj_emissions

        &C_{emissions} = \\ &\quad \sum_{r, p, t, v \in \Theta_{CV}} \left (
               CE_{r, p, c} \cdot EAC_{r,e,i,t,v,o}
         \cdot
         \frac{
           (1 + GDR)^{P_0 - p + 1} \cdot (1 - (1 + GDR)^{-{MPL}_{r,p,t,v}})
         }{
           GDR
         }\cdot \sum_{S,D,I, O} \textbf{FO}_{r, p, s, d,i, t, v, o}
         \right ) \\ &\quad + \sum_{r, p, t \not \in T^{a}, v \in \Theta_{CE}} \left (
               CE_{r, p, c} \cdot EAC_{r,e,i,t,v,o}
         \cdot
         \frac{
           (1 + GDR)^{P_0 - p + 1} \cdot (1 - (1 + GDR)^{-{MPL}_{r,p,t,v}})
         }{
           GDR
         }
         \cdot \sum_{I, O} \textbf{FOA}_{r, p,i, t \in T^{a}, v, o}
         \right )

    """

    return sum(PeriodCost_rule(M, p) for p in M.time_optimize)


def annuity_to_pv(rate: float, periods: int) -> float | Expression:
    """Multiplication factor to convert an annuity to present value"""
    return ((1 + rate)**periods - 1) / (rate * (1 + rate)**periods)

def pv_to_annuity(rate: float, periods: int) -> float | Expression:
    """Multiplication factor to convert present value to an annuity"""
    return (rate * (1 + rate)**periods) / ((1 + rate)**periods - 1)
    
def fv_to_pv(rate: float, periods: int) -> float | Expression:
    """Multiplication factor to convert a future value to present value"""
    return 1 / (1 + rate)**periods


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

    # calculate the annualised loan repayment (annuity)
    annuity = (
        capacity * invest_cost  # lump investment cost is capacity times CostInvest
        * loan_annualize        # calculate loan annuities for investment cost, if used
    )
    
    if not GDR:
        # Undiscounted result
        res = (
            annuity
            * lifetime_loan_process                 # sum of loan payments over loan period
            / lifetime_process                      # redistributed over lifetime of process
            * min(lifetime_process, P_e - vintage)  # sum of redistributed costs for life of process (within planning horizon)
        )
    else:
        # Discounted result
        res = (
            annuity
            * annuity_to_pv(GDR, lifetime_loan_process)     # PV of all loan payments, discounted to vintage year using GDR
            * pv_to_annuity(GDR, lifetime_process)          # reannualised over lifetime of process using GDR
            * annuity_to_pv(GDR, min(lifetime_process, P_e - vintage)) # PV of all reannualised costs (within planning horizon)
            * fv_to_pv(GDR, vintage - P_0)                  # finally, discounted from vintage year to P_0
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

    annual_cost = cap_or_flow * cost_factor     # annual fixed, variable, or emission cost
    
    if not GDR:
        # Undiscounted result
        return annual_cost * cost_years         # annual cost times years paying that cost
    else:
        # Discounted result
        return (
            annual_cost
            * annuity_to_pv(GDR, cost_years)    # PV of annual costs over this period, discounted to period p
            * fv_to_pv(GDR, p - P_0)            # discounted from p to p_0
        )


def PeriodCost_rule(M: 'TemoaModel', p):
    P_0 = min(M.time_optimize)
    P_e = M.time_future.last()  # End point of modeled horizon
    GDR = value(M.GlobalDiscountRate)
    MPL = M.ModelProcessLife

    if value(M.MyopicBaseyear) != 0:
        P_0 = value(M.MyopicBaseyear)

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
        if S_v == p
    )

    fixed_costs = sum(
        fixed_or_variable_cost(
            M.V_Capacity[r, p, S_t, S_v],
            value(M.CostFixed[r, p, S_t, S_v]),
            value(MPL[r, p, S_t, S_v]),
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
        for s in M.time_season[p]
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
    # result with processInput.keys()

    # ================= Emissions and Flex and Curtailment =================
    # Flex flows are deducted from V_FlowOut, so it is NOT NEEDED to tax them again.  (See commodity balance constr)
    # Curtailment does not draw any inputs, so it seems logical that curtailed flows not be taxed either
    # Earlier versions of this code had accounting for flex & curtailment that have been removed.

    base = [
        (r, p, e, i, t, v, o)
        for (r, e, i, t, v, o) in M.EmissionActivity
        if (r, p, e) in M.CostEmission  # tightest filter first
        and (r, p, t, v) in M.processInputs
    ]

    # then expand the base for the normal (season/tod) set and annual separately:
    normal = [
        (r, p, e, s, d, i, t, v, o)
        for (r, p, e, i, t, v, o) in base
        for s in M.time_season[p]
        for d in M.time_of_day
        if t not in M.tech_annual
    ]

    annual = [(r, p, e, i, t, v, o) for (r, p, e, i, t, v, o) in base if t in M.tech_annual]

    # 1. variable emissions
    var_emissions = sum(
        fixed_or_variable_cost(
            cap_or_flow=M.V_FlowOut[r, p, s, d, i, t, v, o] * value(M.EmissionActivity[r, e, i, t, v, o]),
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
            cap_or_flow=M.V_FlowOutAnnual[r, p, i, t, v, o] * value(M.EmissionActivity[r, e, i, t, v, o]),
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
            cap_or_flow=M.V_NewCapacity[r, t, v] * value(M.EmissionEmbodied[r, e, t, v]) / value(M.PeriodLength[p]),
            cost_factor=value(M.CostEmission[r, p, e]),
            cost_years=M.PeriodLength[v], # We assume the embodied emissions are emitted in the same year as the capacity is installed.
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
            cost_years=M.PeriodLength[p], # We assume the embodied emissions are emitted in the same year as the capacity is installed.
            GDR=GDR,
            P_0=P_0,
            p=p,
        )
        for (r, e, t, v) in M.EmissionEndOfLife.sparse_iterkeys()
        if (r, p, e) in M.CostEmission
        if (r, t, v) in M.retirementPeriods and p in M.retirementPeriods[r, t, v]
    )

    period_emission_cost = var_emissions + var_annual_emissions + embodied_emissions + endoflife_emissions

    period_costs = (
        loan_costs + fixed_costs + variable_costs + variable_costs_annual + period_emission_cost
    )
    return period_costs


# ---------------------------------------------------------------
# Define the Model Constraints.
# The order of constraint definitions follows the same order as the
# declarations in temoa_model.py.
# ---------------------------------------------------------------


def Demand_Constraint(M: 'TemoaModel', r, p, s, d, dem):
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

    supply = sum(
        M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, dem]
        for S_t, S_v in M.commodityUStreamProcess[r, p, dem]
        if S_t not in M.tech_annual
        for S_i in M.processInputsByOutput[r, p, S_t, S_v, dem]
    )

    supply_annual = sum(
        M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, dem]
        for S_t, S_v in M.commodityUStreamProcess[r, p, dem]
        if S_t in M.tech_annual
        for S_i in M.processInputsByOutput[r, p, S_t, S_v, dem]
    ) * value(M.SegFrac[p, s, d])

    DemandConstraintErrorCheck(supply + supply_annual, r, p, s, d, dem)

    expr = (
        supply + supply_annual == value(M.Demand[r, p, dem]) * value(M.DemandSpecificDistribution[r, p, s, d, dem])
    )

    return expr


def DemandActivity_Constraint(M: 'TemoaModel', r, p, s, d, t, v, dem, s_0, d_0):
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

    act_a = sum(
        M.V_FlowOut[r, p, s_0, d_0, S_i, t, v, dem]
        for S_i in M.processInputsByOutput[r, p, t, v, dem]
    )
    act_b = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, dem] for S_i in M.processInputsByOutput[r, p, t, v, dem]
    )

    expr = (
        act_a * value(M.DemandSpecificDistribution[r, p, s, d, dem])
        == act_b * value(M.DemandSpecificDistribution[r, p, s_0, d_0, dem])
    )
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
    like gasoline. Such a situtation can result in the overproduction of other
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
    covers both.

    This constraint also accounts for imports and exports between regions
    when solving multi-regional systems. The import (:math:`\textbf{FIM}`) and export
    (:math:`\textbf{FEX}`) variables are created on-the-fly by summing the
    :math:`\textbf{FO}` variables over the appropriate import and export regions,
    respectively, which are defined in :code:`temoa_initialize.py` by parsing the
    :code:`tech_exchange` processes.

    Finally, for annual commodities, AnnualCommodityBalance is used which balances
    the sum of flows over each year.

    *production + imports = consumption + exports + flex waste*

    .. math::
       :label: CommodityBalance

           \sum_{I, T, V} \textbf{FO}_{r, p, s, d, i, t, v, c}
           +
           &\sum_{reg} \textbf{FIM}_{r-reg, p, s, d, i, t, v, c} \; \forall reg \neq r
           \\
           = &\sum_{T^{s}, V, I} \textbf{FIS}_{r, p, s, d, c, t, v, o}
           \\ &\quad +
           \sum_{T-T^{s}, V, O} \textbf{FO}_{r, p, s, d, c, t, v, o} /EFF_{r, c,t,v,o}
           \\
           &\quad + \; SEG_{s,d} \cdot
           \sum_{I, T^{a}, V} \textbf{FOA}_{r, p, c, t \in T^{a}, v, o} /EFF_{r, c,t,v,o} \\
           &\quad + \sum_{reg} \textbf{FEX}_{r-reg, p, s, d, c, t, v, o} \; \forall reg \neq r
           \\ &\quad + \;
           \textbf{FLX}_{r, p, s, d, i, t, v, c}

           \\
           &\forall \{r, p, s, d, c\} \in \Theta_{\text{CommodityBalance}}

    """
    if c in M.commodity_demand: # Is this necessary? Demand comms have no downstream process no shouldnt be in indices
        return Constraint.Skip

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
            M.V_FlowOut[r, p, s, d, c, S_t, S_v, S_o] / get_variable_efficiency(M, r, p, s, d, c, S_t, S_v, S_o)
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t not in M.tech_storage and S_t not in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        # Into annual flows
        consumed += value(M.SegFrac[p, s, d]) * sum(
            M.V_FlowOutAnnual[r, p, c, S_t, S_v, S_o] / get_variable_efficiency(M, r, p, s, d, c, S_t, S_v, S_o)
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t not in M.tech_storage and S_t in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

    if (r, p, c) in M.capacityConsumptionTechs:
        # Consumed by building capacity
        # Assume evenly distributed over a year
        consumed += value(M.SegFrac[p, s, d]) * sum(
            value(M.ConstructionInput[r, c, S_t, p]) * M.V_NewCapacity[r, S_t, p]
            for S_t in M.capacityConsumptionTechs[r, p, c]
        ) / M.PeriodLength[p]

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
            value(M.SegFrac[p, s, d]) * M.V_FlowOutAnnual[reg + '-' + r, p, c, S_t, S_v, S_o]
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
    at the annual level, summing all flows over the year. Applies only to commodities tagged as annual
    'a' in the Commodity table.
    """

    if c in M.commodity_demand: # Is this necessary? Demand comms have no downstream process no shouldnt be in indices
        return Constraint.Skip
    
    produced = 0
    consumed = 0
    
    if (r, p, c) in M.commodityDStreamProcess:
        # Only storage techs have a flow in variable
        # For other techs, it would be redundant as in = out / eff
        consumed += sum(
            M.V_FlowIn[r, p, S_s, S_d, c, S_t, S_v, S_o]
            for S_s in M.time_season[p]
            for S_d in M.time_of_day
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t in M.tech_storage
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        consumed += sum(
            M.V_FlowOut[r, p, S_s, S_d, c, S_t, S_v, S_o] / get_variable_efficiency(M, r, p, S_s, S_d, c, S_t, S_v, S_o)
            for S_s in M.time_season[p]
            for S_d in M.time_of_day
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t not in M.tech_storage and S_t not in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

        consumed += sum(
            M.V_FlowOutAnnual[r, p, c, S_t, S_v, S_o] / value(M.Efficiency[r, c, S_t, S_v, S_o])
            for S_t, S_v in M.commodityDStreamProcess[r, p, c]
            if S_t not in M.tech_storage and S_t in M.tech_annual
            for S_o in M.processOutputsByInput[r, p, S_t, S_v, c]
        )

    if (r, p, c) in M.capacityConsumptionTechs:
        # Consumed by building capacity
        # Assume evenly distributed over a year
        consumed += sum(
            value(M.ConstructionInput[r, c, S_t, p]) * M.V_NewCapacity[r, S_t, p]
            for S_t in M.capacityConsumptionTechs[r, p, c]
        ) / M.PeriodLength[p]

    if (r, p, c) in M.commodityUStreamProcess:
        # Includes output from storage
        produced += sum(
            M.V_FlowOut[r, p, S_s, S_d, S_i, S_t, S_v, c]
            for S_s in M.time_season[p]
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
                for S_s in M.time_season[p]
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
            for S_s in M.time_season[p]
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
            for S_s in M.time_season[p]
            for S_d in M.time_of_day
            for S_r, S_t, S_v, S_i in M.importRegions[r, p, c]
            if S_t not in M.tech_annual
        )
        produced += sum(
            M.V_FlowOutAnnual[r + '-' + S_r, p, S_i, S_t, S_v, c]
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


def ResourceExtraction_Constraint(M: 'TemoaModel', reg, p, r):
    r"""
    The ResourceExtraction constraint allows a modeler to specify an annual limit on
    the amount of a particular resource Temoa may use in a period. The first version
    of the constraint pertains to technologies with variable output at the time slice
    level, and the second version pertains to technologies with constant annual output
    belonging to the :code:`tech_annual` set.

    .. math::
       :label: ResourceExtraction

       \sum_{S, D, I, t \in T^r \& t \not \in T^{a}, V} \textbf{FO}_{r, p, s, d, i, t, v, c} \le RSC_{r, p, c}

       \forall \{r, p, c\} \in \Theta_{\text{ResourceExtraction}}

       \sum_{I, t \in T^r \& t \in T^{a}, V} \textbf{FOA}_{r, p, i, t, v, c} \le RSC_{r, p, c}

       \forall \{r, p, c\} \in \Theta_{\text{ResourceExtraction}}
    """
    logger.warning(
        'The ResourceBound parameter / ResourceExtraction constraint is not currently supported.  '
        'Recommend removing data from supporting table'
    )
    # dev note:  This constraint does not have a table in the current schema
    #            Additionally, the below (incorrect) construct assumes that a resource cannot be used
    #            by BOTH a non-annual and annual tech.  It should be re-written to add these
    # dev note:  Cant think of a case where this would be needed but cant use LimitActivityGroup
    try:
        collected = sum(
            M.V_FlowOut[reg, p, S_s, S_d, S_i, S_t, S_v, r] # is r the input or the output!?
            for S_i, S_t, S_v in M.processByPeriodAndOutput.keys()
            for S_s in M.time_season[p]
            for S_d in M.time_of_day
        )
    except KeyError:
        collected = sum(
            M.V_FlowOutAnnual[reg, p, S_i, S_t, S_v, r]
            for S_i, S_t, S_v in M.processByPeriodAndOutput.keys()
        )

    expr = collected <= value(M.ResourceBound[reg, p, r])
    return expr


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
    """
    This constraint enforces the continuity of state of charge (StorageLevel) between time slices.
    StorageLevel in the next time slice is equal to current StorageLevel plus net charge in the current time slice.
    """

    # This is the sum of all input=i sent TO storage tech t of vintage v with
    # output=o in p,s,d
    charge = sum(
        M.V_FlowIn[r, p, s, d, S_i, t, v, S_o] * get_variable_efficiency(M, r, p, s, d, S_i, t, v, S_o)
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

    expr = M.V_StorageLevel[r, p, s, d, t, v] + stored_energy == M.V_StorageLevel[r, p, s_next, d_next, t, v]

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
    summed over the time-of-day slices (:math:`d`) multiplied by 365 days / yr yields the
    number of days per season. This step is necessary because conventional time sliced models
    use a single day to represent many days within a given season. Thus, it is necessary to
    scale the storage duration to account for the number of days in each season.

    .. math::
       :label: StorageEnergyUpperBound

          \textbf{SL}_{r, p, s, d, t, v} \le
          \textbf{CAP}_{r,t,v} \cdot C2A_{r,t} \cdot \frac {SD_{r,t}}{8760 hrs/yr}
          \cdot \sum_{d} SEG_{s,d} \cdot 365 days/yr

          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{StorageEnergyUpperBound}}

    """

    energy_capacity = (
        M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * (value(M.StorageDuration[r, t]) / 8760)
        * M.SegFracPerSeason[p, s]
        * 365
        * value(M.ProcessLifeFrac[r, p, t, v])
    )
    
    expr = M.V_StorageLevel[r, p, s, d, t, v] <= energy_capacity

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
        M.V_FlowIn[r, p, s, d, S_i, t, v, S_o] * get_variable_efficiency(M, r, p, s, d, S_i, t, v, S_o)
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    # Maximum energy charge in each time slice
    max_charge = (
        M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * value(M.SegFrac[p, s, d])
        * value(M.ProcessLifeFrac[r, p, t, v])
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
        M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * value(M.SegFrac[p, s, d])
        * value(M.ProcessLifeFrac[r, p, t, v])
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
        M.V_FlowIn[r, p, s, d, S_i, t, v, S_o] * get_variable_efficiency(M, r, p, s, d, S_i, t, v, S_o)
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    throughput = charge + discharge
    max_throughput = (
        M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * value(M.SegFrac[p, s, d])
        * value(M.ProcessLifeFrac[r, p, t, v])
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
          \textbf{CAP}_{r,p,t,v} \cdot C2A_{r,t} \cdot \frac {SD_{r,t}}{8760 hrs/yr}
          \cdot \sum_{d} SEG_{s,d} \cdot 365 days/yr \cdot MPL_{r,p,t,v}

          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{LimitStorageFraction}}
    """

    energy_capacity = (
        M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * (value(M.StorageDuration[r, t]) / 8760)
        * M.SegFracPerSeason[p, s]
        * 365
        * value(M.ProcessLifeFrac[r, p, t, v])
    )

    expr = operator_expression(M.V_StorageLevel[r, p, s, d, t, v], op, energy_capacity * value(M.LimitStorageFraction[r, p, s, d, t, v, op]))

    return expr


def RampUp_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    # M.time_of_day is a sorted set, and M.time_of_day.first() returns the first
    # element in the set, similarly, M.time_of_day.last() returns the last element.
    # M.time_of_day.prev(d) function will return the previous element before s, and
    # M.time_of_day.next(d) function will return the next element after s.

    r"""

    The ramp rate constraint is utilized to limit the rate of electricity generation
    increase and decrease between two adjacent time slices in order to account for
    physical limits associated with thermal power plants. Note that this constraint
    only applies to technologies with ramp capability, which is defined in the set
    :math:`T^{m}`. We assume for simplicity the rate limits for both
    ramp up and down are equal and they do not vary with technology vintage. The
    ramp rate limits (:math:`r_t`) for technology :math:`t` should be expressed in
    percentage of its rated capacity.

    Note that when :math:`d_{nd}` is the last time-of-day, :math:`d_{nd + 1} \not \in
    \textbf{D}`, i.e., if one time slice is the last time-of-day in a season and the
    other time slice is the first time-of-day in the next season, the ramp rate
    limits between these two time slices can not be expressed by :code:`RampUpDay`.
    Therefore, the ramp rate constraints between two adjacent seasons are
    represented in :code:`RampUpSeason`.

    In the :code:`RampUpDay` and :code:`RampUpSeason` constraints, we assume
    :math:`\textbf{S} = \{s_i, i = 1, 2, \cdots, ns\}` and
    :math:`\textbf{D} = \{d_i, i = 1, 2, \cdots, nd\}`.

    .. math::
       :label: RampUpDay

          \frac{
              \sum_{I, O} \textbf{FO}_{r, p, s, d_{i + 1}, i, t, v, o}
              }{
              SEG_{s, d_{i + 1}} \cdot C2A_{r,t}
              }
          -
          \frac{
              \sum_{I, O} \textbf{FO}_{r, p, s, d_i, i, t, v, o}
              }{
              SEG_{s, d_i} \cdot C2A_{r,t}
              }
          \leq
          r_t \cdot \textbf{CAPAVL}_{r,p,t}
          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{RampUpDay}}
    """

    s_next, d_next = M.time_next[p, s, d]

    activity_sd = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    ) / value(M.SegFrac[p, s, d])

    activity_sd_next = sum(
        M.V_FlowOut[r, p, s_next, d_next, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    ) / value(M.SegFrac[p, s_next, d_next])

    hours_elapsed = 8760 * ( value(M.SegFrac[p, s, d]) + value(M.SegFrac[p, s_next, d_next]) ) / 2
    hours_elapsed /= M.SegFracPerSeason[p, s] * 365 # adjust for how many days this season represents
    ramp_fraction = hours_elapsed * value(M.RampUp[r, t])

    if ramp_fraction >= 1:
        msg = (
            "Warning: Hourly ramp up rate ({}, {}) is too large to be constraining from ({}, {}, {}) to ({}, {}, {}). Constraint skipped."
        )
        logger.warning(msg.format(r, t, p, s, d, p, s_next, d_next))
        return Constraint.Skip

    activity_increase = activity_sd_next - activity_sd # opposite sign from rampdown
    rampable_activity = ramp_fraction * M.V_Capacity[r, p, t, v] * value(M.CapacityToActivity[r, t]) * value(M.ProcessLifeFrac[r, p, t, v])
    expr = activity_increase <= rampable_activity

    return expr


def RampDown_Constraint(M: 'TemoaModel', r, p, s, d, t, v):
    r"""

    Similar to the :code`RampUpDay` constraint, we use the :code:`RampDownDay`
    constraint to limit ramp down rates between any two adjacent time slices.

    .. math::
       :label: RampDownDay

          \frac{
              \sum_{I, O} \textbf{FO}_{r, p, s, d_{i + 1}, i, t, v, o}
              }{
              SEG_{s, d_{i + 1}} \cdot C2A_{r,t}
              }
          -
          \frac{
              \sum_{I, O} \textbf{FO}_{r, p, s, d_i, i, t, v, o}
              }{
              SEG_{s, d_i} \cdot C2A_{r,t}
              }
          \geq
          -r_t \cdot \textbf{CAPAVL}_{r,p,t}
          \\
          \forall \{r, p, s, d, t, v\} \in \Theta_{\text{RampDownDay}}
    """

    s_next, d_next = M.time_next[p, s, d]

    activity_sd = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    ) / value(M.SegFrac[p, s, d])

    activity_sd_next = sum(
        M.V_FlowOut[r, p, s_next, d_next, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    ) / value(M.SegFrac[p, s_next, d_next])

    hours_elapsed = 8760 * ( value(M.SegFrac[p, s, d]) + value(M.SegFrac[p, s_next, d_next]) ) / 2
    hours_elapsed /= M.SegFracPerSeason[p, s] * 365 # adjust for how many days this season represents
    ramp_fraction = hours_elapsed * value(M.RampDown[r, t])

    if ramp_fraction >= 1:
        msg = (
            "Warning: Hourly ramp down rate  ({}, {}) is too large to be constraining from ({}, {}, {}) to ({}, {}, {}). Constraint skipped."
        )
        logger.warning(msg.format(r, t, p, s, d, p, s_next, d_next))
        return Constraint.Skip

    activity_decrease = activity_sd - activity_sd_next # opposite sign from rampup
    rampable_activity = ramp_fraction * M.V_Capacity[r, p, t, v] * value(M.CapacityToActivity[r, t]) * value(M.ProcessLifeFrac[r, p, t, v])
    expr = activity_decrease <= rampable_activity

    return expr


def ReserveMargin_Constraint(M: 'TemoaModel', r, p, s, d):
    r"""

    During each period :math:`p`, the sum of the available capacity of all reserve
    technologies :math:`\sum_{t \in T^{e}} \textbf{CAPAVL}_{r,p,t}`, which are
    defined in the set :math:`\textbf{T}^{r,e}`, should exceed the peak load by
    :math:`PRM`, the regional reserve margin. Note that the reserve
    margin is expressed in percentage of the peak load. Generally speaking, in
    a database we may not know the peak demand before running the model, therefore,
    we write this equation for all the time-slices defined in the database in each region.

    .. math::
        :label: reserve_margin

            &\sum_{t \in T^{res} \setminus T^{e}} {CC_{t,r} \cdot \textbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*} \cdot C2A_{r,t} }\\
            &+ \sum_{t \in T^{res} \cap T^{e}} {CC_{t,r_i-r} \cdot \textbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*} \cdot C2A_{r_i-r,t} }\\
            &- \sum_{t \in T^{res} \cap T^{e}} {CC_{t,r-r_i} \cdot \textbf{CAPAVL}_{p,t} \cdot SEG_{s^*,d^*} \cdot C2A_{r_i-r,t} }\\
            &\geq \left [ \sum_{ t \in T^{res} \setminus T^{e},V,I,O } \textbf{FO}_{r, p, s, d, i, t, v, o}\right.\\
            &+ \sum_{ t \in T^{res} \cap T^{e},V,I,O } \textbf{FO}_{r_i-r, p, s, d, i, t, v, o}\\
            &- \sum_{ t \in T^{res} \cap T^{e},V,I,O } \textbf{FI}_{r-r_i, p, s, d, i, t, v, o}\\
            &- \left.\sum_{ t \in T^{res} \cap T^{s},V,I,O } \textbf{FI}_{r, p, s, d, i, t, v, o}  \right]  \cdot (1 + PRM_r)\\
            &\qquad \qquad \forall \{r, p, s, d\} \in \Theta_{\text{ReserveMargin}} \text{and} \forall r_i \in R
    """
    if (not M.tech_reserve) or (
        (r, p) not in M.processReservePeriods
    ):  # If reserve set empty or if r,p not in M.processReservePeriod, skip the constraint
        return Constraint.Skip

    cap_avail = sum(
        value(M.CapacityCredit[r, p, t, v])
        * value(M.ProcessLifeFrac[r, p, t, v])
        * M.V_Capacity[r, p, t, v]
        * value(M.CapacityToActivity[r, t])
        * value(M.SegFrac[p, s, d])
        for t in M.tech_reserve
        if (r, p, t) in M.processVintages
        for v in M.processVintages[r, p, t]
        # Make sure (r,p,t,v) combinations are defined
        if (r, p, t, v) in M.activeCapacityAvailable_rptv
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
        r1, r2 = r1r2.split('-')

        # Only consider the capacity of technologies that import to
        # the region in question -- i.e. for cases where r2 == r.
        if r2 != r:
            continue

        # add the available capacity of the exchange tech.
        cap_avail += sum(
            value(M.CapacityCredit[r1r2, p, t, v])
            * value(M.ProcessLifeFrac[r1r2, p, t, v])
            * M.V_Capacity[r1r2, p, t, v]
            * value(M.CapacityToActivity[r1r2, t])
            * value(M.SegFrac[p, s, d])
            for t in M.tech_reserve
            if (r1r2, p, t) in M.processVintages
            for v in M.processVintages[r1r2, p, t]
            # Make sure (r,p,t,v) combinations are defined
            if (r1r2, p, t, v) in M.activeCapacityAvailable_rptv
        )

    # In most Temoa input databases, demand is endogenous, so we use electricity
    # generation instead as a proxy for electricity demand.
    total_generation = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, S_v, S_o]
        for (t, S_v) in M.processReservePeriods[r, p]
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
        if (r1r2, p) not in M.processReservePeriods:  # ensure the technology in question exists
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
                if (t, S_v) in M.processReservePeriods[r1r2, p]
            )

    cap_target = total_generation * (1 + value(M.PlanningReserveMargin[r]))
    return cap_avail >= cap_target


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
        for S_s in M.time_season[p]
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
        M.V_AnnualRetirement[reg, p, t, v]
        * value(M.EmissionEndOfLife[reg, e, t, v])
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
        msg = (
            "Warning: No technology produces emission '%s', though limit was " 'specified as %s.\n'
        )
        logger.warning(msg, (e, emission_limit))
        SE.write(msg % (e, emission_limit))
        return Constraint.Skip
    
    return expr


def LimitGrowthCapacityConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp down rate of available capacity"""
    return LimitGrowthCapacity(M, r, p, t, op, False)

def LimitDegrowthCapacityConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp up rate of available capacity"""
    return LimitGrowthCapacity(M, r, p, t, op, True)

def LimitGrowthCapacity(M: 'TemoaModel', r, p, t, op, degrowth: bool = False):
    r"""
    Constrain the change of capacity available between periods. 
    Forces the model to ramp up and down the availability of new technologies 
    more smoothly. Has constant (seed) and proportional (rate) terms.
    
    CapacityAvailable_(p) <= SEED + RATE * CapacityAvailable_(p-1)
    """

    regions = gather_group_regions(M, r)

    growth = M.LimitDegrowthCapacity if degrowth else M.LimitGrowthCapacity
    RATE = 1 + value(growth[r, t, op][0])
    SEED = value(growth[r, t, op][1])
    CapRPT = M.V_CapacityAvailableByPeriodAndTech

    # relevant r, p, t indices
    cap_rpt = set((_r, _p, _t) for _r, _p, _t in CapRPT if _t == t and _r in regions)
    # periods the technology can have capacity in this region (sorted)
    periods = sorted(set(_p for _r, _p, _t in cap_rpt))

    if len(periods) == 0:
        if p == M.time_optimize.first():
            msg = (
                'Tried to set {}rowthCapacity constraint {} but there are no periods where this '
                'technology is available in this region. Constraint skipped.'
            ).format("Deg" if degrowth else "G", (r, t))
            logger.warning(msg)
        return Constraint.Skip
    
    # Only warn in p0 so we dont dump multiple warnings
    if p == periods[0]:
        if SEED == 0:
            msg = (
                'No constant term (seed) provided for {}rowthCapacity constraint {}. '
                'No capacity will be built in any period following one with zero capacity.'
            ).format("Deg" if degrowth else "G", (r, t))
            logger.info(msg)
        gaps = [_p for _p in M.time_optimize if _p not in periods and min(periods) < _p < max(periods)]
        if gaps:
            msg = (
                'Constructing {}rowthCapacity constraint {} and there are period gaps in which'
                'capacity cannot exist in this region ({}). Capacity in these periods '
                'will be treated as zero which may cause infeasibility or other problems.'
            ).format("Deg" if degrowth else "G", (r, t), gaps)
            logger.warning(msg)
    
    # sum available capacity in this period
    capacity = sum(CapRPT[_r, _p, _t] for _r, _p, _t in cap_rpt if _p == p)

    if p == M.time_optimize.first():
        # First future period. Grab available capacity in last existing period
        # Adjust in-line for past PLF because we are constraining available capacity
        p_prev = M.time_exist.last()
        capacity_prev = sum(
            value(M.ExistingCapacity[_r, _t, _v]) \
                * min( 1.0, (_v + value(M.LifetimeProcess[_r, _t, _v]) - p_prev)/(p - p_prev) )
            for _r, _t, _v in M.ExistingCapacity
            if _r in regions and _t == t and _v + value(M.LifetimeProcess[_r, _t, _v]) > p_prev
        )
    else:
        # Otherwise, grab previous future period
        p_prev = M.time_optimize.prev(p)
        capacity_prev = sum(
            CapRPT[_r, _p, _t]
            for _r, _p, _t in cap_rpt
            if _p == p_prev
        )

    if degrowth:
        expr = operator_expression(capacity_prev, op, SEED + capacity * RATE)
    else:
        expr = operator_expression(capacity, op, SEED + capacity_prev * RATE)
    
    # Check if any variables are actually included before returning
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitGrowthNewCapacityConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp down rate of new capacity deployment"""
    return LimitGrowthNewCapacity(M, r, p, t, op, False)

def LimitDegrowthNewCapacityConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp up rate of new capacity deployment"""
    return LimitGrowthNewCapacity(M, r, p, t, op, True)

def LimitGrowthNewCapacity(M: 'TemoaModel', r, p, t, op, degrowth: bool = False):
    r"""
    Constrain the change of new capacity deployed between periods. 
    Forces the model to ramp up and down the deployment of new technologies 
    more smoothly. Has constant (seed) and proportional (rate) terms.
    
    NewCapacity_(p) <= SEED + RATE * NewCapacity_(p-1)
    """

    regions = gather_group_regions(M, r)

    growth = M.LimitDegrowthNewCapacity if degrowth else M.LimitGrowthNewCapacity
    RATE = 1 + value(growth[r, t, op][0])
    SEED = value(growth[r, t, op][1])
    NewCapRTV = M.V_NewCapacity

    # relevant r, t, v indices
    cap_rtv = set((_r, _t, _v) for _r, _t, _v in NewCapRTV if _t == t and _r in regions)
    # periods the technology can be built in this region (sorted)
    periods = sorted(set(_v for _r, _t, _v  in NewCapRTV if _v in M.time_optimize))

    if len(periods) == 0:
        if p == M.time_optimize.first():
            msg = (
                'Tried to set {}rowthNewCapacity constraint {} but there are no periods where this '
                'technology can be built in this region. Constraint skipped.'
            ).format("Deg" if degrowth else "G", (r, t))
            logger.warning(msg)
        return Constraint.Skip
    
    # Only warn in p0 so we dont dump multiple warnings
    if p == periods[0]:
        if SEED == 0:
            msg = (
                'No constant term (seed) provided for {}rowthNewCapacity constraint {}. '
                'No capacity will be built in any period following one with zero new capacity.'
            ).format("Deg" if degrowth else "G", (r, t))
            logger.info(msg)
        gaps = [_p for _p in M.time_optimize if _p not in periods and min(periods) < _p < max(periods)]
        if gaps:
            msg = (
                'Constructing {}rowthNewCapacity constraint {} and there are period gaps in which'
                'new capacity cannot be built in this region ({}). New capacity in these periods '
                'will be treated as zero which may cause infeasibility or other problems.'
            ).format("Deg" if degrowth else "G", (r, t), gaps)
            logger.warning(msg)
    
    # sum new capacity in this period
    new_cap = sum(NewCapRTV[_r, _t, _v] for _r, _t, _v in cap_rtv if _v == p)

    if p == M.time_optimize.first():
        # First future period. Grab last existing vintage
        p_prev = M.time_exist.last()
        new_cap_prev = sum(
            value(M.ExistingCapacity[_r, _t, _v])
            for _r, _t, _v in M.ExistingCapacity
            if _r in regions and _t == t and _v == p_prev
        )
    else:
        # Otherwise, grab previous future vintage
        p_prev = M.time_optimize.prev(p)
        new_cap_prev = sum(
            NewCapRTV[_r, _t, _v]
            for _r, _t, _v in cap_rtv
            if _v == p_prev
        )

    if degrowth:
        expr = operator_expression(new_cap_prev, op, SEED + new_cap * RATE)
    else:
        expr = operator_expression(new_cap, op, SEED + new_cap_prev * RATE)

    # Check if any variables are actually included before returning
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr
    

def LimitGrowthNewCapacityDeltaConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp down rate of change in new capacity deployment"""
    return LimitGrowthNewCapacityDelta(M, r, p, t, op, False)

def LimitDegrowthNewCapacityDeltaConstraint_rule(M: 'TemoaModel', r, p, t, op):
    r"""Constrain ramp up rate of change in new capacity deployment"""
    return LimitGrowthNewCapacityDelta(M, r, p, t, op, True)

def LimitGrowthNewCapacityDelta(M: 'TemoaModel', r, p, t, op, degrowth: bool = False):
    r"""
    Constrain the acceleration of new capacity deployed between periods. 
    Forces the model to ramp up and down the change in deployment of new technologies 
    more smoothly. Has constant (seed) and proportional (rate) terms.
    
    (NewCapacity_(p) - NewCapacity_(p-1)) <= SEED + RATE * (NewCapacity_(p-1) - NewCapacity_(p-2))
    """

    regions = gather_group_regions(M, r)

    growth = M.LimitDegrowthNewCapacityDelta if degrowth else M.LimitGrowthNewCapacityDelta
    RATE = 1 + value(growth[r, t, op][0])
    SEED = value(growth[r, t, op][1])
    NewCapRTV = M.V_NewCapacity

    # relevant r, t, v indices
    cap_rtv = set((_r, _t, _v) for _r, _t, _v in NewCapRTV if _t == t and _r in regions)
    # periods the technology can be built in this region (sorted)
    periods = sorted(set(_v for _r, _t, _v  in cap_rtv if _v in M.time_optimize))

    if len(periods) == 0:
        if p == M.time_optimize.first():
            msg = (
                'Tried to set {}rowthNewCapacityDelta constraint {} but there are no periods where this '
                'technology can be built in this region. Constraint skipped.'
            ).format("Deg" if degrowth else "G", (r, t))
            logger.warning(msg)
        return Constraint.Skip

    # Only warn in p0 so we dont dump multiple warnings
    if p == periods[0]:
        if SEED == 0:
            msg = (
                'No constant term (seed) provided for {}rowthNewCapacityDelta constraint {}. '
                'This is not recommended as deployment rates cannot inflect (change from '
                'accelerating to decelerating or vice-versa).'
            ).format("Deg" if degrowth else "G", (r, t))
            logger.warning(msg)
        gaps = [_p for _p in M.time_optimize if _p not in periods and min(periods) < _p < max(periods)]
        if gaps:
            msg = (
                'Constructing {}rowthNewCapacityDelta constraint {} and there are period gaps in which'
                'new capacity cannot be built in this region ({}). New capacity in these periods '
                'will be treated as zero which may cause infeasibility or other problems.'
            ).format("Deg" if degrowth else "G", (r, t), gaps)
            logger.warning(msg)

    # sum new capacity in this period
    new_cap = sum(NewCapRTV[_r, _t, _v] for _r, _t, _v in cap_rtv if _v == p)

    if p == M.time_optimize.first():
        # First planning period, pull last two existing vintages
        p_prev = M.time_exist.last()
        new_cap_prev = sum(
            value(M.ExistingCapacity[_r, _t, _v])
            for _r, _t, _v in M.ExistingCapacity
            if _r in regions and _t == t and _v == p_prev
        )
        p_prev2 = M.time_exist.prev(p_prev)
        new_cap_prev2 = sum(
            value(M.ExistingCapacity[_r, _t, _v])
            for _r, _t, _v in M.ExistingCapacity
            if _r in regions and _t == t and _v == p_prev2
        )
    else:
        # Not the first future period. Grab previous future period
        p_prev = M.time_optimize.prev(p)
        new_cap_prev = sum(
            NewCapRTV[_r, _t, _v]
            for _r, _t, _v in cap_rtv
            if _v == p_prev
        )
        if p == M.time_optimize.at(2): # apparently pyomo sets are indexed 1-based
            # Second future period, grab last existing vintage
            p_prev2 = M.time_exist.last()
            new_cap_prev2 = sum(
                value(M.ExistingCapacity[_r, _t, _v])
                for _r, _t, _v in M.ExistingCapacity
                if _r in regions and _t == t and _v == p_prev2
            )
        else:
            # At least the third future period. Grab last two future vintages
            p_prev2 = M.time_optimize.prev(p_prev)
            new_cap_prev2 = sum(
                NewCapRTV[_r, _t, _v]
                for _r, _t, _v in cap_rtv
                if _v == p_prev2
            )

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

       \sum_{S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o}  \le MAA_{r, p, t}

       \forall \{r, p, t\} \in \Theta_{\text{LimitActivity}}

       \sum_{I,V,O} \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}  \le MAA_{r, p, t}

       \forall \{r, p, t \in T^{a}\} \in \Theta_{\text{LimitActivity}}
    """
    # r can be an individual region (r='US'), or a combination of regions separated by
    # a + (r='Mexico+US+Canada'), or 'global'.
    # if r == 'global', the constraint is system-wide
    regions = gather_group_regions(M=M, region=r)

    if t not in M.tech_annual:
        activity_rpt = sum(
            M.V_FlowOut[_r, p, s, d, S_i, t, S_v, S_o]
            for _r in regions
            for S_v in M.processVintages.get((_r, p, t), [])
            for S_i in M.processInputs[_r, p, t, S_v]
            for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
            for s in M.time_season[p]
            for d in M.time_of_day
            if (_r, p, s, d, S_i, t, S_v, S_o) in M.V_FlowOut
        )
    else:
        activity_rpt = sum(
            M.V_FlowOutAnnual[_r, p, S_i, t, S_v, S_o]
            for _r in regions
            for S_v in M.processVintages.get((_r, p, t), [])
            for S_i in M.processInputs[_r, p, t, S_v]
            for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
            if (_r, p, S_i, t, S_v, S_o) in M.V_FlowOutAnnual
        )

    act_lim = value(M.LimitActivity[r, p, t, op])
    expr = operator_expression(activity_rpt, op, act_lim)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


# def LimitSeasonalCapacityFactor_Constraint(M: 'TemoaModel', r, p, s, t, op):

#     r"""
#     Sets a limit on the capacity factor of a specific technology in a season.
#     Note that the indices for these constraints are region, period, season, and tech.
#     The first component of the constraint pertains to technologies with
#     variable output at the time slice level, and the second component pertains to
#     technologies with constant annual output belonging to the :code:`tech_annual`
#     set.
#     .. math::
#         :label: LimitSeasonalCapacityFactor
#         \sum_{S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o}  \le LIMSSNACT_{r, p, s, t}
#         \forall \{r, p, s, t\} \in \Theta_{\text{LimitSeasonalCapacityFactor}}
#         \sum_{I,V,O} \textbf{FOA}_{r, p, i, t, v, o}  \le LIMSSNACT_{r, p, s, t}
#         \forall \{r, p, s, t \in T^{a}\} \in \Theta_{\text{LimitSeasonalCapacityFactor}}
#     """

#     # Notice that this constraint follows the implementation of the
#     # LimitAnnualCapacityFactor_Constraint(). The difference is that this function is defined
#     # over each "season" as opposed to the entire year, or "period"

#     # The V_FlowOut variable is scaled by the weights of each season.
#     # In order to determine the daily flow, the V_FlowOut variable
#     # must be converted back to its un-scaled value. We do this by dividing the
#     # V_FlowOut value by M.SegFracPerSeason[p, s, d]*365 (how many days are in this season).

#     regions = gather_group_regions(M, r)

#     try:
#         activity_rpst = sum(
#             M.V_FlowOut[_r, p, s, d, S_i, t, S_v, S_o] / (value(M.SegFracPerSeason[p, s, d])*365)
#             for _r in regions
#             for S_v in M.processVintages[_r, p, t]
#             for S_i in M.processInputs[_r, p, t, S_v]
#             for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
#             for d in M.time_of_day
#         )
#     except:
#         msg = (
#         "\nWarning: LimitSeasonalCapacityFactor constraint cannot be defined for "
#         "technologies in \"tech_annual\". Continuing by ignoring the constraint "
#         "for '%s'.\n "
#         )
#         SE.write(msg % (t))
#         return Constraint.Skip
    
#     act_lim = value(M.LimitSeasonalCapacityFactor[r, p, s, t, op])
#     expr = operator_expression(activity_rpst, op, act_lim)

#     # in the case that there is nothing to sum, skip
#     if isinstance(expr, bool):  # an empty list was generated
#         return Constraint.Skip
    
    # return expr


def LimitActivityGroup_Constraint(M: 'TemoaModel', r, p, g, op):
    r"""
    The LimitActivityGroup constraint sets an activity limit for a user-defined
    technology group.
    .. math::
       :label: LimitActivityGroup
           \sum_{R,S,D,I,T,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o} + \sum_{I,T,V,O}
           \textbf{FOA}_{r, p, i, t, v, o}
           \le MxAG_{r, p, g}
           \forall \{r, p, g\} \in \Theta_{\text{LimitActivityGroup}}
    where :math:`g` represents the assigned technology group and :math:`MxAG`
    refers to the :code:`LimitActivityGroup` parameter."""

    regions = gather_group_regions(M, r)

    activity_p = 0
    activity_p_annual = 0
    for _r in regions:
        activity_p += sum(
            M.V_FlowOut[_r, p, s, d, S_i, S_t, S_v, S_o]
            for S_t in M.tech_group_members[g]
            if (_r, p, S_t) in M.processVintages and S_t not in M.tech_annual
            for S_v in M.processVintages[_r, p, S_t]
            for S_i in M.processInputs[_r, p, S_t, S_v]
            for S_o in M.processOutputsByInput[_r, p, S_t, S_v, S_i]
            for s in M.time_season[p]
            for d in M.time_of_day
            if (_r, p, s, d, S_i, S_t, S_v, S_o) in M.V_FlowOut
        )
        activity_p_annual += sum(
            M.V_FlowOutAnnual[_r, p, S_i, S_t, S_v, S_o]
            for S_t in M.tech_group_members[g]
            if (_r, p, S_t) in M.processVintages and S_t in M.tech_annual
            for S_v in M.processVintages[_r, p, S_t]
            for S_i in M.processInputs[_r, p, S_t, S_v]
            for S_o in M.processOutputsByInput[_r, p, S_t, S_v, S_i]
            if (_r, p, S_i, S_t, S_v, S_o) in M.V_FlowOutAnnual
        )

    act_lim = value(M.LimitActivityGroup[r, p, g, op])
    expr = operator_expression(activity_p + activity_p_annual, op, act_lim)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


def LimitNewCapacity_Constraint(M: 'TemoaModel', r, p, t, op):
    r"""
    The LimitNewCapacity constraint sets a limit on the newly installed capacity of a
    given technology in a given year. Note that the indices for these constraints are region,
    period and tech.
    .. math::
       :label: LimitNewCapacity
       \textbf{CAP}_{r, t, p} \le LIM_{r, p, t}"""
    regions = gather_group_regions(M, r)
    cap_lim = value(M.LimitNewCapacity[r, p, t, op])
    new_cap = sum(
        M.V_NewCapacity[_r, t, p]
        for _r in regions
    )
    expr = operator_expression(new_cap, op, cap_lim)
    return expr


def LimitCapacity_Constraint(M: 'TemoaModel', r, p, t, op):
    r"""

    The LimitCapacity constraint sets a limit on the available capacity of a
    given technology. Note that the indices for these constraints are region, period and
    tech, not tech and vintage.

    .. math::
       :label: LimitCapacity

       \textbf{CAPAVL}_{r, p, t} \le MAC_{r, p, t}

       \forall \{r, p, t\} \in \Theta_{\text{LimitCapacity}}"""
    regions = gather_group_regions(M, r)
    cap_lim = value(M.LimitCapacity[r, p, t, op])
    capacity = sum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, t]
        for _r in regions
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

       \sum_{P} \textbf{CAPAVL}_{r, p, t} \le MAR_{r, t}

       \forall \{r, t\} \in \Theta_{\text{LimitCapacity}}"""
    # logger.warning(
    #     'The LimitResource constraint is not currently supported in the model, pending review.  Recommend '
    #     'removing data from the LimitResource Table'
    # )
    # dev note:  this constraint is a misnomer.  It is actually a "global activity constraint on a tech"
    #            regardless of whatever "resources" are consumed.
    # dev note:  this would generally be applied to a "dummy import" technology to restrict something like
    #            oil/mineral extraction across all model periods. Looks fine to me.

    regions = gather_group_regions(M, r)

    if t in M.tech_annual:
        activity_rt = sum(
            M.V_FlowOutAnnual[_r, p, S_i, t, S_v, S_o]
            for p in M.time_optimize
            for _r in regions
            if (_r, p, t) in M.processVintages
            for S_v in M.processVintages[_r, p, t]
            for S_i in M.processInputs[_r, p, t, S_v]
            for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
        )
    else:
        activity_rt = sum(
            M.V_FlowOut[_r, p, s, d, S_i, t, S_v, S_o]
            for p in M.time_optimize
            for _r in regions
            if (_r, p, t) in M.processVintages
            for S_v in M.processVintages[_r, p, t]
            for S_i in M.processInputs[_r, p, t, S_v]
            for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
            for s in M.time_season[p]
            for d in M.time_of_day
        )
    
    resource_lim = value(M.LimitResource[r, t, op])
    expr = operator_expression(activity_rt, op, resource_lim)
    return expr


def LimitCapacityGroup_Constraint(M: 'TemoaModel', r, p, g, op):
    r"""
    Similar to the :code:`LimitCapacity` constraint, but works on a group of technologies.
    """
    regions = gather_group_regions(M, r)

    cap_lim = value(M.LimitCapacityGroup[r, p, g, op])

    cap = sum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, t]
        for t in M.tech_group_members[g]
        for _r in regions
        if (_r, p, t) in M.V_CapacityAvailableByPeriodAndTech
    )

    expr = operator_expression(cap, op, cap_lim)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool): # an empty list was generated
        logger.error(
            'No elements available to support LimitCapacityGroup: %s.'
            ' Check data/log for available/suppressed techs. Constraint ignored.',
            (r, p, g)
        )
        return Constraint.Skip
    return expr


def LimitNewCapacityGroup_Constraint(M: 'TemoaModel', r, p, g, op):
    r"""
    Similar to the :code:`LimitNewCapacity` constraint, but works on a group of technologies."""

    regions = gather_group_regions(M, r)

    new_cap_lim = value(M.LimitNewCapacityGroup[r, p, g, op])
    agg_new_cap = sum(
        M.V_NewCapacity[_r, t, p]
        for t in M.tech_group_members[g]
        for _r in regions
        if (_r, p, t) in M.V_CapacityAvailableByPeriodAndTech
    )
    expr = operator_expression(agg_new_cap, op, new_cap_lim)
    if isinstance(expr, bool):
        logger.error(
            'No elements available to support LimitNewCapacityGroup: (%s, %d, %s).'
            '  Check data/log for available/suppressed techs.  Requirement IGNORED.',
            r,
            p,
            g,
        )
        return Constraint.Skip
    return expr


def LimitActivityShare_Constraint(M: 'TemoaModel', r, p, t, g, op):
    r"""
    The LimitActivityShare constraint limits the activity share for a given
    technology within a technology groups to which it belongs.
    For instance, you might define a tech_group of light-duty vehicles, whose
    members are different types for LDVs. This constraint could be used to enforce
    that no more than 10% of LDVs must be of a certain type."""

    regions = gather_group_regions(M, r)

    if t not in M.tech_annual:
        activity_tech = sum(
            M.V_FlowOut[_r, p, s, d, S_i, t, S_v, S_o]
            for _r in regions
            for S_v in M.processVintages.get((_r, p, t), [])
            for S_i in M.processInputs[_r, p, t, S_v]
            for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
            for s in M.time_season[p]
            for d in M.time_of_day
            if (_r, p, s, d, S_i, t, S_v, S_o) in M.V_FlowOut
        )
    else:
        activity_tech = sum(
            M.V_FlowOutAnnual[_r, p, S_i, t, S_v, S_o]
            for _r in regions
            for S_v in M.processVintages.get((_r, p, t), [])
            for S_i in M.processInputs[_r, p, t, S_v]
            for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
            if (_r, p, S_i, t, S_v, S_o) in M.V_FlowOutAnnual
        )

    activity_group = sum(
        M.V_FlowOut[_r, p, s, d, S_i, S_t, S_v, S_o]
        for S_t in M.tech_group_members[g]
        for _r in regions
        if (_r, p, S_t) in M.processVintages and S_t not in M.tech_annual
        for S_v in M.processVintages[_r, p, S_t]
        for S_i in M.processInputs[_r, p, S_t, S_v]
        for S_o in M.processOutputsByInput[_r, p, S_t, S_v, S_i]
        for s in M.time_season[p]
        for d in M.time_of_day
        if (_r, p, s, d, S_i, S_t, S_v, S_o) in M.V_FlowOut
    )
    activity_group_annual = sum(
        M.V_FlowOutAnnual[_r, p, S_i, S_t, S_v, S_o]
        for S_t in M.tech_group_members[g]
        for _r in regions
        if (_r, p, S_t) in M.processVintages and S_t in M.tech_annual
        for S_v in M.processVintages[_r, p, S_t]
        for S_i in M.processInputs[_r, p, S_t, S_v]
        for S_o in M.processOutputsByInput[_r, p, S_t, S_v, S_i]
        if (_r, p, S_i, S_t, S_v, S_o) in M.V_FlowOutAnnual
    )
    activity_group = activity_group + activity_group_annual

    share_lim = value(M.LimitActivityShare[r, p, t, g, op])
    expr = operator_expression(activity_tech, op, share_lim * activity_group)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    logger.debug(
        'created limit activity share constraint for (%s, %d, %s, %s) of %0.2f',
        r, p, t, g, share_lim,
    )
    return expr


def LimitCapacityShare_Constraint(M: 'TemoaModel', r, p, t, g, op):
    r"""
    The LimitCapacityShare constraint limits the share for a given
    technology within a technology groups to which it belongs.
    For instance, you might define a tech_group of light-duty vehicles, whose
    members are different types for LDVs. This constraint could be used to enforce
    that no more than 10% of LDVs must be of a certain type."""

    regions = gather_group_regions(M, r)

    capacity_t = sum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, t]
        for _r in regions
    )
    capacity_group = sum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, S_t]
        for S_t in M.tech_group_members[g]
        for _r in regions
        if (_r, p, S_t) in M.processVintages
    )
    share_lim = value(M.LimitCapacityShare[r, p, t, g, op])

    expr = operator_expression(capacity_t, op, share_lim * capacity_group)
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitNewCapacityShare_Constraint(M: 'TemoaModel', r, p, t, g, op):
    r"""
    The LimitCapacityShare constraint limits the share for a given
    technology within a technology groups to which it belongs.
    For instance, you might define a tech_group of light-duty vehicles, whose
    members are different types for LDVs. This constraint could be used to enforce
    that no more than 10% of LDV purchases in a given year must be of a certain type."""

    regions = gather_group_regions(M, r)

    new_cap_t = sum(
        M.V_NewCapacity[_r, t, p]
        for _r in regions
    )
    new_cap_group = sum(
        M.V_NewCapacity[_r, S_t, p]
        for S_t in M.tech_group_members[g]
        for _r in regions
        if (_r, S_t, p) in M.V_NewCapacity
    )
    share_lim = value(M.LimitNewCapacityShare[r, p, t, g, op])

    expr = operator_expression(new_cap_t, op, share_lim * new_cap_group)
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitNewCapacityGroupShare_Constraint(M: 'TemoaModel', r, p, g1, g2, op):
    r"""
    Limits the aggregate capacity of one group of technologies as a share of 
    another group of technologies.
    """

    regions = gather_group_regions(M, r)

    share_lim = value(M.LimitNewCapacityGroupShare[r, p, g1, g2, op])
    agg_new_cap_g1 = sum(
        M.V_NewCapacity[_r, t, p]
        for t in M.tech_group_members[g1]
        for _r in regions
        if (_r, p, t) in M.V_CapacityAvailableByPeriodAndTech
    )
    agg_new_cap_g2 = sum(
        M.V_NewCapacity[_r, t, p]
        for t in M.tech_group_members[g2]
        for _r in regions
        if (_r, p, t) in M.V_CapacityAvailableByPeriodAndTech
    )
    expr = operator_expression(agg_new_cap_g1, op, agg_new_cap_g2 * share_lim)

    if isinstance(expr, bool): # one side of expression was empty
        logger.error(
            'Missing group techs to support LimitNewCapacityGroupShare constraint: %s.'
            '  Check data/log for available/suppressed techs. Constraint ignored.',
            (r, p, g1, g2)
        )
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
       \sum_{S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o} \le LIMACF_{r, p, t} * \textbf{CAPAVL}_{r, p, t} * \text{C2A}_{r, t}
       \forall \{r, p, t, o\} \in \Theta_{\text{LimitAnnualCapacityFactor}}
       \sum_{I,V,O} \textbf{FOA}_{r, p, i, t, v, o} \ge LIMACF_{r, p, t} * \textbf{CAPAVL}_{r, p, t} * \text{C2A}_{r, t}
       \forall \{r, p, t, o \in T^{a}\} \in \Theta_{\text{LimitAnnualCapacityFactor}}"""
    # r can be an individual region (r='US'), or a combination of regions separated by plus (r='Mexico+US+Canada'), or 'global'.
    # if r == 'global', the constraint is system-wide
    regions = gather_group_regions(M, r)
    # we need to screen here because it is possible that the restriction extends beyond the
    # lifetime of any vintage of the tech...
    if all(
        (_r, p, t) not in M.V_CapacityAvailableByPeriodAndTech
        for _r in regions
    ):
        return Constraint.Skip

    if t not in M.tech_annual:
        activity_rpt = sum(
            M.V_FlowOut[_r, p, s, d, S_i, t, S_v, o]
            for _r in regions
            for S_v in M.processVintages.get((_r, p, t), [])
            for S_i in M.processInputs[_r, p, t, S_v]
            for s in M.time_season[p]
            for d in M.time_of_day
            if (_r, p, s, d, S_i, t, S_v, o) in M.V_FlowOut
        )
    else:
        activity_rpt = sum(
            M.V_FlowOutAnnual[_r, p, S_i, t, S_v, o]
            for _r in regions
            for S_v in M.processVintages.get((_r, p, t), [])
            for S_i in M.processInputs[_r, p, t, S_v]
            if (_r, p, S_i, t, S_v, o) in M.V_FlowOutAnnual
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
       :label: LimitSeasonalCapacityFactor
       \sum_{S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o} \le LIMACF_{r, p, t} * \textbf{CAPAVL}_{r, p, t} * \text{C2A}_{r, t}
       \forall \{r, p, t, o\} \in \Theta_{\text{LimitSeasonalCapacityFactor}}
       \sum_{I,V,O} \textbf{FOA}_{r, p, i, t, v, o} \ge LIMACF_{r, p, t} * \textbf{CAPAVL}_{r, p, t} * \text{C2A}_{r, t}
       \forall \{r, p, t, o \in T^{a}\} \in \Theta_{\text{LimitSeasonalCapacityFactor}}"""
    # r can be an individual region (r='US'), or a combination of regions separated by plus (r='Mexico+US+Canada'), or 'global'.
    # if r == 'global', the constraint is system-wide
    regions = gather_group_regions(M, r)
    # we need to screen here because it is possible that the restriction extends beyond the
    # lifetime of any vintage of the tech...
    if all(
        (_r, p, t) not in M.V_CapacityAvailableByPeriodAndTech
        for _r in regions
    ):
        return Constraint.Skip

    # The V_FlowOut variable is scaled by the number of days in the season.
    # To adjust for this, we divide by M.SegFracPerSeason[p, s, d]*365, 
    # the number of days this season represents.
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
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o] / get_variable_efficiency(M, r, p, s, d, S_i, t, v, S_o)
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
    of the :math:`tech_annual` set) are considered."""
    inp = sum(
        M.V_FlowOutAnnual[r, p, i, t, v, S_o] / value(M.Efficiency[r, i, t, v, S_o])
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    total_inp = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o] / value(M.Efficiency[r, S_i, t, v, S_o])
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = operator_expression(inp, op, value(M.LimitTechInputSplitAnnual[r, p, i, t, op]) * total_inp)
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
        M.V_FlowOut[r, p, S_s, S_d, i, t, v, S_o] / get_variable_efficiency(M, r, p, S_s, S_d, i, t, v, S_o)
        for S_s in M.time_season[p]
        for S_d in M.time_of_day
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    total_inp = sum(
        M.V_FlowOut[r, p, S_s, S_d, S_i, t, v, S_o] / get_variable_efficiency(M, r, p, S_s, S_d, i, t, v, S_o)
        for S_s in M.time_season[p]
        for S_d in M.time_of_day
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    expr = operator_expression(inp, op, value(M.LimitTechInputSplitAnnual[r, p, i, t, op]) * total_inp)
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
        M.V_FlowOut[r, p, s, d, S_i, t, v, o]
        for S_i in M.processInputsByOutput[r, p, t, v, o]
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
    output (i.e., members of the :math:`tech_annual` set) are considered.

    .. math::
       :label: LimitTechOutputSplitAnnual

         \sum_{I, T^{a}} \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}

       \geq

         TOS_{r, p, t, o} \cdot \sum_{I, O, T^{a}} \textbf{FOA}_{r, p, s, d, i, t \in T^{a}, v, o}

       \forall \{r, p, t \in T^{a}, v, o\} \in \Theta_{\text{LimitTechOutputSplitAnnual}}"""
    out = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, o]
        for S_i in M.processInputsByOutput[r, p, t, v, o]
    )

    total_out = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = operator_expression(out, op, value(M.LimitTechOutputSplitAnnual[r, p, t, o, op]) * total_out)
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
        for S_s in M.time_season[p]
        for S_d in M.time_of_day
    )

    total_out = sum(
        M.V_FlowOut[r, p, S_s, S_d, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        for S_s in M.time_season[p]
        for S_d in M.time_of_day
    )

    expr = operator_expression(out, op, value(M.LimitTechOutputSplitAnnual[r, p, t, o, op]) * total_out)
    return expr


def RenewablePortfolioStandard_Constraint(M: 'TemoaModel', r, p, g):
    r"""
    Allows users to specify the share of electricity generation in a region
    coming from RPS-eligible technologies."""

    inp = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for t in M.tech_group_members[g]
        for (_t, v) in M.processReservePeriods[r, p]
        if _t == t
        for s in M.time_season[p]
        for d in M.time_of_day
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    total_inp = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for (t, v) in M.processReservePeriods[r, p]
        for s in M.time_season[p]
        for d in M.time_of_day
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = inp >= (value(M.RenewablePortfolioStandard[r, p, g]) * total_inp)
    return expr


# ---------------------------------------------------------------
# Define rule-based parameters
# ---------------------------------------------------------------
def ParamModelProcessLife_rule(M: 'TemoaModel', r, p, t, v):
    life_length = value(M.LifetimeProcess[r, t, v])
    mpl = min(v + life_length - p, value(M.PeriodLength[p]))

    return mpl


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

    Calculate the fraction of period p that process :math:`<t, v>` operates.

    For most processes and periods, this will likely be one, but for any process
    that will cease operation (rust out, be decommissioned, etc.) between periods,
    calculate the fraction of the period that the technology is able to
    create useful output.
    """
    eol_year = v + value(M.LifetimeProcess[r, t, v])
    frac = eol_year - p
    period_length = value(M.PeriodLength[p])
    if frac >= period_length:
        # try to avoid floating point round-off errors for the common case.
        return 1

        # number of years into final period loan is complete

    frac /= float(period_length)
    return frac


def loan_annualization_rate(loan_rate: float | None, loan_life: int | float) -> float:
    """
    This calculation is broken out specifically so that it can be used for param creation
    and separately to calculate loan costs rather than rely on fully-built model parameters
    :param loan_rate:
    :param loan_life:

    """
    if not loan_rate:
        # dev note:  this should not be needed as the LoanRate param has a default (see the definition)
        return 1.0 / loan_life
    annualized_rate = loan_rate / (1.0 - (1.0 + loan_rate) ** (-loan_life))
    return annualized_rate


def ParamLoanAnnualize_rule(M: 'TemoaModel', r, t, v):
    dr = value(M.LoanRate[r, t, v])
    lln = value(M.LoanLifetimeProcess[r, t, v])
    annualized_rate = loan_annualization_rate(dr, lln)
    return annualized_rate


def SegFracPerSeason_rule(M: 'TemoaModel', p, s):
    return sum(
        value(M.SegFrac[p, s, S_d])
        for S_d in M.time_of_day
        if (p, s, S_d) in M.SegFrac
    )


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
    linked_t = M.LinkedTechs[r, t, e]

    primary_flow = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o] * value(M.EmissionActivity[r, e, S_i, t, v, S_o])
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    linked_flow = sum(
        M.V_FlowOut[r, p, s, d, S_i, linked_t, v, S_o]
        for S_i in M.processInputs[r, p, linked_t, v]
        for S_o in M.processOutputsByInput[r, p, linked_t, v, S_i]
    )

    return -primary_flow == linked_flow

def operator_expression(lhs: Expression | None, operator: str | None, rhs: Expression | None):
    """Returns an expression, applying a configured operator"""
    if any((lhs is None, operator is None, rhs is None)):
        msg = (
            'Tried to build a constraint using a bad expression or operator: {} {} {}'
        ).format(lhs, operator, rhs)
        logger.error(msg)
        raise ValueError(msg)
    try:
        match operator:
            case "e":
                expr = lhs == rhs
            case "le":
                expr = lhs <= rhs
            case "ge":
                expr = lhs >= rhs
            case _:
                msg = (
                    'Tried to build a constraint using a bad operator. Allowed operators are "e","le", or "ge". Got "{}": {} {} {}'
                ).format(operator, lhs, operator, rhs)
                logger.error(msg)
                raise ValueError(msg)
    except Exception as e:
        print(e)
        msg = (
            'Tried to build a constraint using a bad expression or operator: {} {} {}'
        ).format(lhs, operator, rhs)
        logger.error(msg)
        raise ValueError(msg)
        
    return expr


# To avoid building big many-indexed parameters when they aren't needed - saves memory
# Much faster to build a dictionary and check that than check the parameter
# indices directly every time - saves build time
def get_variable_efficiency(M: 'TemoaModel', r, p, s, d, i, t, v, o):
    if M.efficiencyVariables[r, p, i, t, v, o]:
        return value(M.Efficiency[r, i, t, v, o]) * value(M.EfficiencyVariable[r, p, s, d, i, t, v, o])
    else:
        return value(M.Efficiency[r, i, t, v, o])
    
def get_capacity_factor(M: 'TemoaModel', r, p, s, d, t, v):
    if M.capacityFactorProcesses[r, p, t, v]:
        return value(M.CapacityFactorProcess[r, p, s, d, t, v])
    else:
        return value(M.CapacityFactorTech[r, p, s, d, t])