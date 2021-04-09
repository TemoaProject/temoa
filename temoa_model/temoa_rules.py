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

# Import below required in Python 2.7 to avoid integer division
# (e.g., 1/2 = 0 instead of 0.5)
from __future__ import division

from temoa_initialize import *

# ---------------------------------------------------------------
# Define the derived variables used in the objective function
# and constraints below.
# ---------------------------------------------------------------

def Capacity_Constraint(M, r, p, s, d, t, v):
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
         \cdot \text{TLF}_{r, p, t, v}
       \right )
       \cdot \textbf{CAP}_{r, t, v}
       =
       \sum_{I, O} \textbf{FO}_{r, p, s, d,i, t, v, o}
       +
       \sum_{I, O} \textbf{CUR}_{r, p,s,d,i,t,v,o}

   \\
   \forall \{r, p, s, d, t, v\} \in \Theta_{\text{FO}}



"""
    if t in M.tech_storage:
        return Constraint.Skip
    # The expressions below are defined in-line to minimize the amount of
    # expression cloning taking place with Pyomo.

    useful_activity = sum(
    M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
    for S_i in M.processInputs[r, p, t, v]
    for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i]
    )

    if t in M.tech_curtailment:
        # If technologies are present in the curtailment set, then enough
        # capacity must be available to cover both activity and curtailment.
        return value(M.CapacityFactorProcess[r, s, d, t, v]) \
            * value(M.CapacityToActivity[r, t]) * value(M.SegFrac[s, d]) \
            * value(M.ProcessLifeFrac[r, p, t, v]) \
            * M.V_Capacity[r, t, v] == useful_activity + sum( \
            M.V_Curtailment[r, p, s, d, S_i, t, v, S_o] \
            for S_i in M.processInputs[r, p, t, v] \
            for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i])
    else:
        return value(M.CapacityFactorProcess[r, s, d, t, v]) \
        * value(M.CapacityToActivity[r, t]) \
        * value(M.SegFrac[s, d]) \
        * value(M.ProcessLifeFrac[r, p, t, v]) \
        * M.V_Capacity[r, t, v] >= useful_activity


def CapacityAnnual_Constraint(M, r, p, t, v):
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
         \cdot \text{TLF}_{r, p, t, v}
       \right )
       \cdot \textbf{CAP}_{r, t, v}
   =
       \sum_{I, O} \textbf{FOA}_{r, p, i, t, v, o}

   \\
   \forall \{r, p, t, v\} \in \Theta_{\text{Activity}}


"""
    CF = 1 #placeholder CF

    activity_rptv = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i]
    )

    return CF \
    * value(M.CapacityToActivity[r, t]) \
    * value(M.ProcessLifeFrac[r, p, t, v]) \
    * M.V_Capacity[r, t, v] >= activity_rptv


def ActivityByTech_Constraint(M, t):
    r"""
This constraint is utilized by the MGA objective function and defines
the total activity of a technology over the planning horizon. The first version
below applies to technologies with variable output at the timeslice level,
and the second version applies to technologies with constant annual output
in the :code:`tech_annual` set.

.. math::
   :label: ActivityByTech

       \textbf{ACT}_{t} = \sum_{R, P, S, D, I, V, O} \textbf{FO}_{r, p, s, d,i, t, v, o}

       \\
       \forall t \not\in T^{a}

       \textbf{ACT}_{t} = \sum_{R, P, I, V, O} \textbf{FOA}_{r, p, i, t, v, o}

       \\
       \forall t \in T^{a}

"""
    if t not in M.tech_annual:
        indices = []
        for s_index in M.FlowVar_rpsditvo:
            if t in s_index:
                indices.append(s_index)
        activity = sum( M.V_FlowOut[s_index]
              for s_index in indices
          )
    else:
        indices = []
        for s_index in M.FlowVarAnnual_rpitvo:
            if t in s_index:
                indices.append(s_index)
        activity = sum( M.V_FlowOutAnnual[s_index]
              for s_index in indices
          )

    if int is type(activity):
        return Constraint.Skip

    expr = M.V_ActivityByTech[t] == activity
    return expr


def CapacityAvailableByPeriodAndTech_Constraint(M, r, p, t):
    r"""

The :math:`\textbf{CAPAVL}` variable is nominally for reporting solution values,
but is also used in the Max and Min constraint calculations.  For any process
with an end-of-life (EOL) on a period boundary, all of its capacity is available
for use in all periods in which it is active (the process' TLF is 1). However,
for any process with an EOL that falls between periods, Temoa makes the
simplifying assumption that the available capacity from the expiring technology
is available through the whole period in proportion to its remaining lifetime.
For example, if a process expires 3 years into an 8-year model time period,
then only :math:`\frac{3}{8}` of the installed capacity is available for use
throughout the period.

.. math::
   :label: CapacityAvailable

   \textbf{CAPAVL}_{r, p, t} = \sum_{V} {TLF}_{r, p, t, v} \cdot \textbf{CAP}

   \\
   \forall p \in \text{P}^o, t \in T, r \in R
"""
    cap_avail = sum(
        value(M.ProcessLifeFrac[r, p, t, S_v]) * M.V_Capacity[r, t, S_v]
        for S_v in M.processVintages[r, p, t]
    )

    expr = M.V_CapacityAvailableByPeriodAndTech[r, p, t] == cap_avail
    return expr

def ExistingCapacity_Constraint(M, r, t, v):
    r"""

Temoa treats existing capacity installed prior to the beginning of the model's
optimization horizon as regular processes that require the same parameter
specification as do new vintage technologies, except for the :code:`CostInvest`
parameter.  This constraint sets the capacity of processes for model periods
that exist prior to the optimization horizon to user-specified values.

.. math::
   :label: ExistingCapacity

   \textbf{CAP}_{r, t, v} = ECAP_{r, t, v}

   \forall \{r, t, v\} \in \Theta_{\text{ExistingCapacity}}
"""
    expr = M.V_Capacity[r, t, v] == M.ExistingCapacity[r, t, v]
    return expr

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
             IC_{r, t, v} \cdot LA_{r, t, v}
             \cdot \frac{(1 + GDR)^{P_0 - v +1} \cdot (1 - (1 + GDR)^{-LLN_{r, t, v}})}{GDR}
             \cdot \frac{ 1-(1+GDR)^{-LPA_{r,t,v}} }{ 1-(1+GDR)^{-LP_{r,t,v}} }
     \right ]
     \cdot \textbf{CAP}_{r, t, v}
     \right )

Note that capital costs (:math:`{IC}_{r,t,v}`) are handled in several steps. First, each capital cost
is amortized using the loan rate (i.e., technology-specific discount rate) and loan
period. Second, the annual stream of payments is converted into a lump sum using
the global discount rate and loan period. Third, the new lump sum is amortized
at the global discount rate and technology lifetime. Fourth, loan payments beyond
the model time horizon are removed and the lump sum recalculated. The terms used
in Steps 3-4 are :math:`\frac{ GDR }{ 1-(1+GDR)^{-LP_{r,t,v} } }\cdot
\frac{ 1-(1+GDR)^{-LPA_{t,v}} }{ GDR }`. The product simplifies to
:math:`\frac{ 1-(1+GDR)^{-LPA_{r,t,v}} }{ 1-(1+GDR)^{-LP_{r,t,v}} }`, where
:math:`LPA_{r,t,v}` represents the active lifetime of process t in region r :math:`(r,t,v)`
before the end of the model horizon, and :math:`LP_{r,t,v}` represents the full
lifetime of a regional process :math:`(r,t,v)`. Fifth, the lump sum is discounted back to the
beginning of the horizon (:math:`P_0`) using the global discount rate. While an
explicit salvage term is not included, this approach properly captures the capital
costs incurred within the model time horizon, accounting for technology-specific
loan rates and periods.

.. math::
   :label: obj_fixed

   C_{fixed} = \sum_{r, p, t, v \in \Theta_{FC}} \left (
     \left [
             FC_{r, p, t, v}
       \cdot \frac{(1 + GDR)^{P_0 - p +1} \cdot (1 - (1 + GDR)^{-{MPL}_{r, t, v}})}{GDR}
     \right ]
     \cdot \textbf{CAP}_{r, t, v}
     \right )

.. math::
   :label: obj_variable

   C_{variable} = \sum_{r, p, t, v \in \Theta_{VC}} \left (
           MC_{r, p, t, v}
     \cdot
     \frac{
       (1 + GDR)^{P_0 - p + 1} \cdot (1 - (1 + GDR)^{-{MPL}_{r,p,t,v}})
     }{
       GDR
     }

     \cdot \sum_{S,D,I, O} \textbf{FO}_{r, p, s, d,i, t, v, o}
     \right )+ \sum_{r, p, t, v \in \Theta_{VC}} \left (
           MC_{r, p, t, v}
     \cdot
     \frac{
       (1 + GDR)^{P_0 - p + 1} \cdot (1 - (1 + GDR)^{-{MPL}_{r,p,t,v}})
     }{
       GDR
     }
     \cdot \sum_{I, O} \textbf{FOA}_{r, p,i, t, v, o}
     \right )

"""
    return sum(PeriodCost_rule(M, p) for p in M.time_optimize)


def PeriodCost_rule(M, p):
    P_0 = min(M.time_optimize)
    P_e = M.time_future.last()  # End point of modeled horizon
    GDR = value(M.GlobalDiscountRate)
    MLL = M.ModelLoanLife
    MPL = M.ModelProcessLife
    x = 1 + GDR  # convenience variable, nothing more.


    if  value(M.MyopicBaseyear) != 0:
      P_0 = value(M.MyopicBaseyear)



    loan_costs = sum(
        M.V_Capacity[r, S_t, S_v]
        * (
            value(M.CostInvest[r, S_t, S_v])
            * value(M.LoanAnnualize[r, S_t, S_v])
            * (
                value(M.LifetimeLoanProcess[r, S_t, S_v])
                if not GDR
                else (
                    x ** (P_0 - S_v + 1)
                    * (1 - x ** (-value(M.LifetimeLoanProcess[r, S_t, S_v])))
                    / GDR
                )
            )
        )
        * (
            (1 - x ** (-min(value(M.LifetimeProcess[r, S_t, S_v]), P_e - S_v)))
            / (1 - x ** (-value(M.LifetimeProcess[r, S_t, S_v])))
        )
        for r, S_t, S_v in M.CostInvest.sparse_iterkeys()
        if S_v == p
    )

    fixed_costs = sum(
        M.V_Capacity[r, S_t, S_v]
        * (
            value(M.CostFixed[r, p, S_t, S_v])
            * (
                value(MPL[r, p, S_t, S_v])
                if not GDR
                else (x ** (P_0 - p + 1) * (1 - x ** (-value(MPL[r, p, S_t, S_v]))) / GDR)
            )
        )
        for r, S_p, S_t, S_v in M.CostFixed.sparse_iterkeys()
        if S_p == p
    )

    variable_costs = sum(
        M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, S_o]
        * (
            value(M.CostVariable[r, p, S_t, S_v])
            * (
                value(MPL[r, p, S_t, S_v])
                if not GDR
                else (x ** (P_0 - p + 1) * (1 - x ** (-value(MPL[r, p, S_t, S_v]))) / GDR)
            )
        )
        for r, S_p, S_t, S_v in M.CostVariable.sparse_iterkeys()
        if S_p == p and S_t not in M.tech_annual
        for S_i in M.processInputs[r, S_p, S_t, S_v]
        for S_o in M.ProcessOutputsByInput[r, S_p, S_t, S_v, S_i]
        for s in M.time_season
        for d in M.time_of_day
    )

    variable_costs_annual = sum(
        M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, S_o]
        * (
            value(M.CostVariable[r, p, S_t, S_v])
            * (
                value(MPL[r, p, S_t, S_v])
                if not GDR
                else (x ** (P_0 - p + 1) * (1 - x ** (-value(MPL[r, p, S_t, S_v]))) / GDR)
            )
        )
        for r, S_p, S_t, S_v in M.CostVariable.sparse_iterkeys()
        if S_p == p and S_t in M.tech_annual
        for S_i in M.processInputs[r, S_p, S_t, S_v]
        for S_o in M.ProcessOutputsByInput[r, S_p, S_t, S_v, S_i]
    )

    period_costs = loan_costs + fixed_costs + variable_costs + variable_costs_annual
    return period_costs


# ---------------------------------------------------------------
# Define the Model Constraints.
# The order of constraint definitions follows the same order as the
# declarations in temoa_model.py.
# ---------------------------------------------------------------


def Demand_Constraint(M, r, p, s, d, dem):
    r"""

The Demand constraint drives the model.  This constraint ensures that supply at
least meets the demand specified by the Demand parameter in all periods and
slices, by ensuring that the sum of all the demand output commodity (:math:`c`)
generated by both commodity flow at the time slice level (:math:`\textbf{FO}`) and
the annual level (:math:`\textbf{FOA}`) must meet the modeler-specified demand
in each time slice.

.. math::
   :label: Demand

       \sum_{I, T^{a}, V} \textbf{FO}_{r, p, s, d, i, t, v, dem} +
       SEG_{s,d} \cdot  \sum_{I, T^{a}, V} \textbf{FOA}_{r, p, i, t, v, dem}
       =
       {DEM}_{p, dem} \cdot {DSD}_{s, d, dem}

Note that the validity of this constraint relies on the fact that the
:math:`C^d` set is distinct from both :math:`C^e` and :math:`C^p`. In other
words, an end-use demand must only be an end-use demand.  Note that if an output
could satisfy both an end-use and internal system demand, then the output from
:math:`\textbf{FO}` and :math:`\textbf{FOA}` would be double counted.
"""
    if (r,s,d,dem) not in M.DemandSpecificDistribution.sparse_keys():
        return Constraint.Skip

    supply = sum(
        M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, dem]
        for S_t, S_v in M.commodityUStreamProcess[r, p, dem] if S_t not in M.tech_annual
        for S_i in M.ProcessInputsByOutput[r, p, S_t, S_v, dem]
    )

    supply_annual = sum(
        M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, dem]
        for S_t, S_v in M.commodityUStreamProcess[r, p, dem] if S_t in M.tech_annual
        for S_i in M.ProcessInputsByOutput[r, p, S_t, S_v, dem]
    ) * value( M.SegFrac[ s, d])

    DemandConstraintErrorCheck(supply + supply_annual, r, p, s, d, dem)

    expr = supply + supply_annual == M.Demand[r, p, dem] * M.DemandSpecificDistribution[r, s, d, dem]
    return expr

def DemandActivity_Constraint(M, r, p, s, d, t, v, dem, s_0, d_0):
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

      DEM_{r, p, s, d, dem} \cdot \sum_{I} \textbf{FO}_{r, p, s_0, d_0, i, t, v, dem}
   =
      DEM_{r, p, s_0, d_0, dem} \cdot \sum_{I} \textbf{FO}_{r, p, s, d, i, t, v, dem}

   \\
   \forall \{r, p, s, d, t, v, dem, s_0, d_0\} \in \Theta_{\text{DemandActivity}}

Note that this constraint is only applied to the demand commodities with diurnal
variations, and therefore the equation above only includes :math:`\textbf{FO}`
and not  :math:`\textbf{FOA}`
"""
    if (r,s,d,dem) not in M.DemandSpecificDistribution.sparse_keys():
        return Constraint.Skip
    DSD = M.DemandSpecificDistribution  # lazy programmer

    act_a = sum(
        M.V_FlowOut[r, p, s_0, d_0, S_i, t, v, dem]
        for S_i in M.ProcessInputsByOutput[r, p, t, v, dem]
    )
    act_b = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, dem]
        for S_i in M.ProcessInputsByOutput[r, p, t, v, dem]
    )

    expr = act_a * DSD[r, s, d, dem] == act_b * DSD[r, s_0, d_0, dem]
    return expr


def CommodityBalance_Constraint(M, r, p, s, d, c):
    r"""
Where the Demand constraint :eq:`Demand` ensures that end-use demands are met,
the CommodityBalance constraint ensures that the endogenous system demands are
met.  This constraint requires the total production of a given commodity
to equal the amount consumed, thus ensuring an energy balance at the system
level. In this most general form of the constraint, the energy commodity being
balanced has variable production at the time slice level. The energy commodity
can then be consumed by three types of processes: storage stechnologies, non-storage
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
(:math:`\textbf{FX}_{r, p, s, d, i, t, v, c})representing
the excess production in the :code:`CommodityBalanceAnnual_Constraint`. Note
that the :code:`tech_flex` set is different from :code:`tech_curtailment` set;
the latter is technology- rather than commodity-focused and is used in the
:code:`Capacity_Constraint` to track output that is used to produce useful
output and the amount curtailed, and to ensure that the installed capacity
covers both.

For commodities that are exclusively produced at a constant annual rate, the
:code:`CommodityBalanceAnnual_Constraint` is used, which is simplified and
reduces computational burden.

*production + imports = consumption + exports + excess*

.. math::
   :label: CommodityBalance

       \sum_{I, T, V} \textbf{FO}_{r, p, s, d, i, t, v, c}
       +
       \sum_{reg} \textbf{FIM}_{reg-r, p, s, d, i, t, v, c} \forall reg\neqr
       =
       \sum_{T^{s}, V, I} \textbf{FIS}_{r, p, s, d, c, t, v, o}
       +
       \sum_{T-T^{s}, V, O} \textbf{FO}_{r, p, s, d, c, t, v, o} /EFF_{r, c,t,v,o}
       +
       SEG_{s,d} \cdot
       \sum_{I, T^{a}, V} \textbf{FOA}_{r, p, c, t, v, o} /EFF_{r, c,t,v,o}
       +
       \sum_{reg} \textbf{FEX}_{r-reg, p, s, d, c, t, v, o} \forall reg\neqr
       +
       \textbf{FX}_{r, p, s, d, i, t, v, c}

       \\
       \forall \{r, p, s, d, c\} \in \Theta_{\text{CommodityBalance}}

"""
    if c in M.commodity_demand:
        return Constraint.Skip

    vflow_in_ToStorage = sum(
        M.V_FlowIn[r, p, s, d, c, S_t, S_v, S_o]
        for S_t, S_v in M.commodityDStreamProcess[r, p, c] if S_t in M.tech_storage
        for S_o in M.ProcessOutputsByInput[r, p, S_t, S_v, c]
    )

    vflow_in_ToNonStorage = sum(
        M.V_FlowOut[r, p, s, d, c, S_t, S_v, S_o] / value(M.Efficiency[r, c, S_t, S_v, S_o])
        for S_t, S_v in M.commodityDStreamProcess[r, p, c] if S_t not in M.tech_storage and S_t not in M.tech_annual
        for S_o in M.ProcessOutputsByInput[r, p, S_t, S_v, c]
    )

    vflow_in_ToNonStorageAnnual = value(M.SegFrac[s, d]) * sum(
        M.V_FlowOutAnnual[r, p, c, S_t, S_v, S_o] / value(M.Efficiency[r, c, S_t, S_v, S_o])
        for S_t, S_v in M.commodityDStreamProcess[r, p, c] if S_t not in M.tech_storage and S_t in M.tech_annual
        for S_o in M.ProcessOutputsByInput[r, p, S_t, S_v, c]
    )

    try:
      vflow_out = sum(
          M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, c]
          for S_t, S_v in M.commodityUStreamProcess[r, p, c]
          for S_i in M.ProcessInputsByOutput[r, p, S_t, S_v, c]
      )

      #export of commodity c from region r to other regions
      interregional_exports = 0
      if (r, p, c) in M.exportRegions:
        interregional_exports = sum(
          M.V_FlowOut[r+"-"+reg, p, s, d, c, S_t, S_v, S_o]
          for reg, S_t, S_v, S_o in M.exportRegions[r, p, c]
          )

      #import of commodity c from other regions into region r
      interregional_imports = 0
      if (r, p, c) in M.importRegions:
        interregional_imports = sum(
          M.V_FlowOut[reg+"-"+r, p, s, d, S_i, S_t, S_v, c]
          for reg, S_t, S_v, S_i in M.importRegions[r, p, c]
          )

      v_out_excess = 0
      if c in M.flex_commodities:
        v_out_excess = sum(
            M.V_Flex[r, p, s, d, S_i, S_t, S_v, c]
            for S_t, S_v in M.commodityUStreamProcess[r, p, c] if S_t not in M.tech_storage and S_t not in M.tech_annual and S_t in M.tech_flex
            for S_i in M.ProcessInputsByOutput[r, p, S_t, S_v, c]
        )

    except:
      raise Exception('The commodity "'+str(c)+'" can be produced \
      by at least one technology in the tech_annual set and one technology \
      not in the tech_annual set. All the producers of the commodity must \
      either be in tech_annual or not in tech_annual')



    CommodityBalanceConstraintErrorCheck(vflow_out + interregional_imports,  vflow_in_ToStorage +  vflow_in_ToNonStorage + vflow_in_ToNonStorageAnnual + interregional_exports + v_out_excess, r, p, s, d, c)

    expr = vflow_out + interregional_imports == vflow_in_ToStorage +  vflow_in_ToNonStorage + vflow_in_ToNonStorageAnnual + interregional_exports + v_out_excess

    return expr

def CommodityBalanceAnnual_Constraint(M, r, p, c):
    r"""
Similar to the CommodityBalance_Constraint, but this version applies only
to commodities produced at a constant annual rate. This version of the
constraint improves computational performance for commodities that do not
need to be balanced at the timeslice level.

While the commodity :math:`c` can only be produced by technologies in the
:code:`tech_annual` set, it can be consumed by any technology in the
:math:`T-T^{s}` set.

*production + imports = consumption + exports + excess*

.. math::
   :label: CommodityBalanceAnnual

       \sum_{I,T, V} \textbf{FOA}_{r, p, i, t, v, c}
        +
       \sum_{reg} \textbf{FIM}_{reg-r, p, i, t, v, c} \forall reg\neqr
        =
       \sum_{S, D, T-T^{s}, V, O} \textbf{FO}_{r, p, s, d, c, t, v, o} /EFF_{r, c,t,v,o}
       +
       \sum_{I, T^{a}, V, O} \textbf{FOA}_{r, p, c, t, v, o} /EFF_{r, c,t,v,o}
       +
       \sum_{reg} \textbf{FEX}_{r-reg, p, c, t, v, o} \forall reg\neqr
       +
       \textbf{FX}_{r, p, i, t, v, c}

       \\
       \forall \{r, p, c\} \in \Theta_{\text{CommodityBalanceAnnual}}

"""
    if c in M.commodity_demand:
        return Constraint.Skip

    vflow_in = sum(
        M.V_FlowOut[r, p, s, d, c, S_t, S_v, S_o] / value(M.Efficiency[r, c, S_t, S_v, S_o])
        for S_t, S_v in M.commodityDStreamProcess[r, p, c] if S_t not in M.tech_annual
        for S_o in M.ProcessOutputsByInput[r, p, S_t, S_v, c]
        for d in M.time_of_day
        for s in M.time_season
    )

    vflow_in_annual = sum(
        M.V_FlowOutAnnual[r, p, c, S_t, S_v, S_o] / value(M.Efficiency[r, c, S_t, S_v, S_o])
        for S_t, S_v in M.commodityDStreamProcess[r, p, c] if S_t in M.tech_annual
        for S_o in M.ProcessOutputsByInput[r, p, S_t, S_v, c]
    )

    vflow_out = sum(
        M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, c]
        for S_t, S_v in M.commodityUStreamProcess[r, p, c]
        for S_i in M.ProcessInputsByOutput[r, p, S_t, S_v, c]
    )

    #export of commodity c from region r to other regions
    interregional_exports = 0
    if (r, p, c) in M.exportRegions:
      interregional_exports = sum(
        M.V_FlowOutAnnual[str(r)+"-"+str(reg), p, c, S_t, S_v, S_o]
        for reg, S_t, S_v, S_o in M.exportRegions[r, p, c]
        )

    #import of commodity c from other regions into region r
    interregional_imports = 0
    if (r, p, c) in M.importRegions:
      interregional_imports = sum(
        M.V_FlowOutAnnual[str(reg)+"-"+str(r), p, S_i, S_t, S_v, c]
        for reg, S_t, S_v, S_i in M.importRegions[r, p, c]
        )

    v_out_excess = 0
    if c in M.flex_commodities:
      v_out_excess = sum(
        M.V_FlexAnnual[r, p, S_i, S_t, S_v, c]
        for S_t, S_v in M.commodityUStreamProcess[r, p, c] if S_t in M.tech_flex and S_t in M.tech_annual
        for S_i in M.ProcessInputsByOutput[r, p, S_t, S_v, c]
    )

    CommodityBalanceConstraintErrorCheckAnnual(vflow_out + interregional_imports,  vflow_in_annual + vflow_in + interregional_exports + v_out_excess, r, p, c)

    expr = vflow_out + interregional_imports ==  vflow_in_annual + vflow_in + interregional_exports + v_out_excess


    return expr

def ResourceExtraction_Constraint(M, reg, p, r):
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
    try:
      collected = sum(
          M.V_FlowOut[reg, p, S_s, S_d, S_i, S_t, S_v, r]
          for S_i, S_t, S_v in M.ProcessByPeriodAndOutput.keys()
          for S_s in M.time_season
          for S_d in M.time_of_day
      )
    except:
      collected = sum(
          M.V_FlowOutAnnual[reg, p, S_i, S_t, S_v, r]
          for S_i, S_t, S_v in M.ProcessByPeriodAndOutput.keys()
      )

    expr = collected <= M.ResourceBound[reg, p, r]
    return expr

def BaseloadDiurnal_Constraint(M, r, p, s, d, t, v):
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
    activity_sd = sum( \
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o] \
        for S_i in M.processInputs[r, p, t, v] \
        for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i] \
    )

    activity_sd_0 = sum( \
        M.V_FlowOut[r, p, s, d_0, S_i, t, v, S_o] \
        for S_i in M.processInputs[r, p, t, v] \
        for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i] \
    )

    expr = (
        activity_sd * M.SegFrac[s, d_0]
        == activity_sd_0 * M.SegFrac[s, d]
    )

    return expr

def RegionalExchangeCapacity_Constraint(M, r_e, r_i, t, v):
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

    expr = M.V_Capacity[r_e+"-"+r_i, t, v] == M.V_Capacity[r_i+"-"+r_e, t, v]

    return expr


def StorageEnergy_Constraint(M, r, p, s, d, t, v):
    r"""

This constraint tracks the storage charge level (:math:`\textbf{SL}_{r, p, s, d, t, v}`)
assuming ordered time slices. The initial storage charge level is optimized
for the first time slice in each period, and then the charge level is updated each time
slice based on the amount of energy stored or discharged. At the end of the last time
slice associated with each period, the charge level must equal the starting charge level.
In the formulation below, note that :math:`\textbf{stored_energy}` is an internal model
decision variable.

First, the amount of stored energy in a given time slice is calculated as the
difference between the amount of energy stored (first term) and the amount of energy
dispatched (second term). Note that the storage device's roundtrip efficiency is applied
on the input side:

.. math::
   :label: StorageEnergy

      \textbf{stored_energy} =
      \sum_{I, O} \textbf{FIS}_{r, p, s, d, i, t, v, o} \cdot
      EFF_{r,i,t,v,o}
      -
      \sum_{I, O} \textbf{FO}_{r, p, s, d, i, t, v, o}

With :math:`\bf{stored\_energy}` calculated, the storage
charge level (:math:`\textbf{SL}_{r,p,s,d,t,v}`) is updated, but the update procedure varies
based on the time slice within each time period. For the first season and time-of-day within
a given period:

.. math::
      \textbf{SL}_{r, p, s, d, t, v} = \textbf{SI}_{r,t,v} + \textbf{stored_energy}

For the first time-of-day slice in any other season except the first:

.. math::
      \textbf{SL}_{r, p, s, d, t, v} =
      \textbf{SL}_{r, p, s_{prev}, d_{last}, t, v} + \textbf{stored_energy}

For the last season and time-of-day in the year, the ending storage charge level
should be equal to the starting charge level:

.. math::
      \textbf{SL}_{r, p, s, d, t, v} + \textbf{stored_energy} = \textbf{SI}_{r,t,v}

For all other time slices not explicitly outlined above:

.. math::
      \textbf{SL}_{r, p, s, d, t, v} = \textbf{SL}_{r, p, s, d_{prev}, t, v} + \textbf{stored_energy}

All equations below are sparsely indexed such that:

.. math::
      \forall \{r, p, s, d, t, v\} \in \Theta_{\text{StorageEnergy}}

"""
    # This is the sum of all input=i sent TO storage tech t of vintage v with
    # output=o in p,s,d
    charge = sum(
        M.V_FlowIn[r, p, s, d, S_i, t, v, S_o] * M.Efficiency[r, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i]
    )

    # This is the sum of all output=o withdrawn FROM storage tech t of vintage v
    # with input=i in p,s,d
    discharge = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for S_o in M.processOutputs[r, p, t, v]
        for S_i in M.ProcessInputsByOutput[r, p, t, v, S_o]
    )

    stored_energy = charge - discharge

    # This storage formulation allows stored energy to carry over through
    # time of day and seasons, but must be zeroed out at the end of each period, i.e.,
    # the last time slice of the last season must zero out
    if d == M.time_of_day.last() and s == M.time_season.last():
        d_prev = M.time_of_day.prev(d)
        expr = M.V_StorageLevel[r, p, s, d_prev, t, v] + stored_energy == M.V_StorageInit[r, t,v]

    # First time slice of the first season (i.e., start of period), starts at StorageInit level
    elif d == M.time_of_day.first() and s == M.time_season.first():
        expr = M.V_StorageLevel[r, p, s, d, t, v] == M.V_StorageInit[r,t,v] + stored_energy

    # First time slice of any season that is NOT the first season
    elif d == M.time_of_day.first():
        d_last = M.time_of_day.last()
        s_prev = M.time_season.prev(s)
        expr = (
            M.V_StorageLevel[r, p, s, d, t, v]
            == M.V_StorageLevel[r, p, s_prev, d_last, t, v] + stored_energy
        )

    # Any time slice that is NOT covered above (i.e., not the time slice ending
    # the period, or the first time slice of any season)
    else:
        d_prev = M.time_of_day.prev(d)
        expr = (
            M.V_StorageLevel[r, p, s, d, t, v]
            == M.V_StorageLevel[r, p, s, d_prev, t, v] + stored_energy
        )

    return expr

def StorageEnergyUpperBound_Constraint(M, r, p, s, d, t, v):
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
        M.V_Capacity[r, t, v]
        * M.CapacityToActivity[r, t]
        * (M.StorageDuration[r, t] / 8760)
        * sum(M.SegFrac[s,S_d] for S_d in M.time_of_day) * 365
        * value(M.ProcessLifeFrac[r, p, t, v])
    )
    expr = M.V_StorageLevel[r, p, s, d, t, v] <= energy_capacity

    return expr


def StorageChargeRate_Constraint(M, r, p, s, d, t, v):
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
        M.V_FlowIn[r, p, s, d, S_i, t, v, S_o] * M.Efficiency[r, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i]
    )

    # Maximum energy charge in each time slice
    max_charge = (
        M.V_Capacity[r, t, v]
        * M.CapacityToActivity[r, t]
        * M.SegFrac[s, d]
        * value(M.ProcessLifeFrac[r, p, t, v])
    )

    # Energy charge cannot exceed the power capacity of the storage unit
    expr = slice_charge <= max_charge

    return expr


def StorageDischargeRate_Constraint(M, r, p, s, d, t, v):
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
        for S_i in M.ProcessInputsByOutput[r, p, t, v, S_o]
    )

    # Maximum energy discharge in each time slice
    max_discharge = (
        M.V_Capacity[r, t, v]
        * M.CapacityToActivity[r, t]
        * M.SegFrac[s, d]
        * value(M.ProcessLifeFrac[r, p, t, v])
    )

    # Energy discharge cannot exceed the capacity of the storage unit
    expr = slice_discharge <= max_discharge

    return expr


def StorageThroughput_Constraint(M, r, p, s, d, t, v):
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
        for S_i in M.ProcessInputsByOutput[r, p, t, v, S_o]
    )

    charge = sum(
        M.V_FlowIn[r, p, s, d, S_i, t, v, S_o] * M.Efficiency[r, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i]
    )

    throughput = charge + discharge
    max_throughput = (
        M.V_Capacity[r, t, v]
        * M.CapacityToActivity[r, t]
        * M.SegFrac[s, d]
        * value(M.ProcessLifeFrac[r, p, t, v])
    )
    expr = throughput <= max_throughput
    return expr


def StorageInit_Constraint( M, r, t, v ):
    r"""

This constraint is used if the users wishes to force a specific initial storage charge level
for certain storage technologies and vintages. In this case, the value of the decision variable
:math:`\textbf{SI}_{r,t,v}` is set by this constraint rather than being optimized.
User-specified initial storage charge levels that are sufficiently different from the optimial
:math:`\textbf{SI}_{r,t,v}` could impact the cost-effectiveness of storage. For example, if the
optimial initial charge level happens to be 50% of the full energy capacity, forced initial
charge levels (specified by parameter :math:`SIF_{r,t,v}`) equal to 10% or 90% of the full energy
capacity could lead to more expensive solutions.


.. math::
   :label: StorageInit

      \textbf{SI}_{r,t, v} \le
      \ SIF_{r,t,v}
      \cdot
      \textbf{CAP}_{r,t,v} \cdot C2A_{r,t} \cdot \frac {SD_{r,t}}{8760 hrs/yr}
      \cdot \sum_{d} SEG_{s_{first},d} \cdot 365 days/yr

      \\
      \forall \{r, t, v\} \in \Theta_{\text{StorageInit}}
"""

    s = M.time_season.first()
    energy_capacity = (
        M.V_Capacity[r, t, v]
        * M.CapacityToActivity[r, t]
        * (M.StorageDuration[r, t] / 8760)
        * sum(M.SegFrac[s,S_d] for S_d in M.time_of_day) * 365
        * value(M.ProcessLifeFrac[r, v, t, v])
    )

    expr = M.V_StorageInit[r, t, v] ==  energy_capacity * M.StorageInitFrac[r, t, v]

    return expr


def RampUpDay_Constraint(M, r, p, s, d, t, v):
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
:math:`\textbf{D} = \{d_i, i=1, 2, \cdots, nd\}`.

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
    if d != M.time_of_day.first():
        d_prev = M.time_of_day.prev(d)
        activity_sd_prev = sum( \
            M.V_FlowOut[r, p, s, d_prev, S_i, t, v, S_o] \
            for S_i in M.processInputs[r, p, t, v] \
            for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i] \
        )

        activity_sd = sum( \
            M.V_FlowOut[r, p, s, d, S_i, t, v, S_o] \
            for S_i in M.processInputs[r, p, t, v] \
            for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i] \
        )

        expr_left = (
            activity_sd / value(M.SegFrac[s, d])
            - activity_sd_prev / value(M.SegFrac[s, d_prev])
        ) / value(M.CapacityToActivity[r,t])
        expr_right = M.V_Capacity[r, t, v] * value(M.RampUp[r, t])
        expr = expr_left <= expr_right
    else:
        return Constraint.Skip

    return expr


def RampDownDay_Constraint(M, r, p, s, d, t, v):
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
    if d != M.time_of_day.first():
        d_prev = M.time_of_day.prev(d)
        activity_sd_prev = sum( \
            M.V_FlowOut[r, p, s, d_prev, S_i, t, v, S_o] \
            for S_i in M.processInputs[r, p, t, v] \
            for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i] \
        )

        activity_sd = sum( \
            M.V_FlowOut[r, p, s, d, S_i, t, v, S_o] \
            for S_i in M.processInputs[r, p, t, v] \
            for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i] \
        )

        expr_left = (
            activity_sd / value(M.SegFrac[s, d])
            - activity_sd_prev / value(M.SegFrac[s, d_prev])
        ) / value(M.CapacityToActivity[r,t])
        expr_right = -(M.V_Capacity[r, t, v] * value(M.RampDown[r, t]))
        expr = expr_left >= expr_right
    else:
        return Constraint.Skip

    return expr


def RampUpSeason_Constraint(M, r, p, s, t, v):
    r"""

Note that :math:`d_1` and :math:`d_{nd}` represent the first and last time-of-day,
respectively.

.. math::
   :label:

      \frac{
          \sum_{I, O} \textbf{FO}_{r, p, s_{i + 1}, d_1, i, t, v, o}
          }{
          SEG_{s_{i + 1}, d_1} \cdot C2A_{r,t}
          }
      -
      \frac{
          \sum_{I, O} \textbf{FO}_{r, p, s_i, d_{nd}, i, t, v, o}
          }{
          SEG_{s_i, d_{nd}} \cdot C2A_{r,t}
          }
      \leq
      r_t \cdot \textbf{CAPAVL}_{r,p,t}
      \\
      \forall \{r, p, s, t, v\} \in \Theta_{\text{RampUpSeason}}
"""
    if s != M.time_season.first():
        s_prev = M.time_season.prev(s)
        d_first = M.time_of_day.first()
        d_last = M.time_of_day.last()

        activity_sd_first = sum( \
            M.V_FlowOut[r, p, s, d_first, S_i, t, v, S_o] \
            for S_i in M.processInputs[r, p, t, v] \
            for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i] \
        )

        activity_s_prev_d_last = sum( \
            M.V_FlowOut[r, p, s_prev, d_last, S_i, t, v, S_o] \
            for S_i in M.processInputs[r, p, t, v] \
            for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i] \
        )

        expr_left = (
            activity_sd_first / M.SegFrac[s, d_first]
            - activity_s_prev_d_last / M.SegFrac[s_prev, d_last]
        ) / value(M.CapacityToActivity[r,t])
        expr_right = M.V_Capacity[r, t, v] * value(M.RampUp[r, t])
        expr = expr_left <= expr_right
    else:
        return Constraint.Skip

    return expr


def RampDownSeason_Constraint(M, r, p, s, t, v):
    r"""

Similar to the :code:`RampUpSeason` constraint, we use the
:code:`RampDownSeason` constraint to limit ramp down rates
between any two adjacent seasons.

.. math::
   :label: RampDownSeason

      \frac{
          \sum_{I, O} \textbf{FO}_{r, p, s_{i + 1}, d_1, i, t, v, o}
          }{
          SEG_{s_{i + 1}, d_1} \cdot C2A_{r,t}
          }
      -
      \frac{
          \sum_{I, O} \textbf{FO}_{r, p, s_i, d_{nd}, i, t, v, o}
          }{
          SEG_{s_i, d_{nd}} \cdot C2A_{r,t}
          }
      \geq
      -r_t \cdot \textbf{CAPAVL}_{r,p,t}
      \\
      \forall \{r, p, s, t, v\} \in \Theta_{\text{RampDownSeason}}
"""
    if s != M.time_season.first():
        s_prev = M.time_season.prev(s)
        d_first = M.time_of_day.first()
        d_last = M.time_of_day.last()

        activity_sd_first = sum( \
            M.V_FlowOut[r, p, s, d_first, S_i, t, v, S_o] \
            for S_i in M.processInputs[r, p, t, v] \
            for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i] \
        )

        activity_s_prev_d_last = sum( \
            M.V_FlowOut[r, p, s_prev, d_last, S_i, t, v, S_o] \
            for S_i in M.processInputs[r, p, t, v] \
            for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i] \
        )

        expr_left = (
            activity_sd_first / value(M.SegFrac[s, d_first])
            - activity_s_prev_d_last / value(M.SegFrac[s_prev, d_last])
        ) / value(M.CapacityToActivity[r,t])
        expr_right = -(M.V_Capacity[r, t, v] * value(M.RampDown[r, t]))
        expr = expr_left >= expr_right
    else:
        return Constraint.Skip

    return expr


def RampUpPeriod_Constraint(M, r, p, t, v):

    # if p != M.time_future.first():
    # 	p_prev  = M.time_future.prev(p)
    # 	s_first = M.time_season.first()
    # 	s_last  = M.time_season.last()
    # 	d_first = M.time_of_day.first()
    # 	d_last  = M.time_of_day.last()
    # 	expr_left = (
    # 		M.V_Activity[ p, s_first, d_first, t, v ] -
    # 		M.V_Activity[ p_prev, s_last, d_last, t, v ]
    # 		)
    # 	expr_right = (
    # 		M.V_Capacity[t, v]*
    # 		value( M.RampUp[t] )*
    # 		value( M.CapacityToActivity[ t ] )*
    # 		value( M.SegFrac[s, d])
    # 		)
    # 	expr = (expr_left <= expr_right)
    # else:
    # 	return Constraint.Skip

    # return expr

    return Constraint.Skip  # We don't need inter-period ramp up/down constraint.


def RampDownPeriod_Constraint(M, r, p, t, v):

    # if p != M.time_future.first():
    # 	p_prev  = M.time_future.prev(p)
    # 	s_first = M.time_season.first()
    # 	s_last  = M.time_season.last()
    # 	d_first = M.time_of_day.first()
    # 	d_last  = M.time_of_day.last()
    # 	expr_left = (
    # 		M.V_Activity[ p, s_first, d_first, t, v ] -
    # 		M.V_Activity[ p_prev, s_last, d_last, t, v ]
    # 		)
    # 	expr_right = (
    # 		-1*
    # 		M.V_Capacity[t, v]*
    # 		value( M.RampDown[t] )*
    # 		value( M.CapacityToActivity[ t ] )*
    # 		value( M.SegFrac[s, d])
    # 		)
    # 	expr = (expr_left >= expr_right)
    # else:
    # 	return Constraint.Skip

    # return expr

    return Constraint.Skip  # We don't need inter-period ramp up/down constraint.


def ReserveMargin_Constraint(M, r, p, s, d):
    r"""

During each period :math:`p`, the sum of the available capacity of all reserve
technologies :math:`\sum_{t \in T^{e}} \textbf{CAPAVL}_{r,p,t}`, which are
defined in the set :math:`\textbf{T}^{r,e}`, should exceed the peak load by
:math:`RES`, the regional reserve margin. Note that the reserve
margin is expressed in percentage of the peak load. Generally speaking, in
a database we may not know the peak demand before running the model, therefore,
we write this equation for all the time-slices defined in the database in each region.

.. math::
   :label: reserve_margin

       \sum_{t \in T^{r,e}} {
       CC_{t,r} \cdot
       \textbf{CAPAVL}_{p,t} \cdot
       SEG_{s^*,d^*} \cdot C2A_{r,t} }
       \geq
       \sum_{ t \in T^{r,e},V,I,O } {
           \textbf{FO}_{r, p, s, d, i, t, v, o}  \cdot (1 + RES_r)
       }

       \\
       \forall \{r, p, s, d\} \in \Theta_{\text{ReserveMargin}}

"""
    if (not M.tech_reserve) or ((r,p) not in M.processReservePeriods.keys()):  # If reserve set empty or if r,p not in M.processReservePeriod.keys(), skip the constraint
        return Constraint.Skip

    cap_avail = sum(
        value(M.CapacityCredit[r, p, t, v])
        * M.ProcessLifeFrac[r, p, t, v]
        * M.V_Capacity[r, t, v]
        * value(M.CapacityToActivity[r, t])
        * value(M.SegFrac[s, d])
        for t in M.tech_reserve
        if (r, p, t) in M.processVintages.keys()
        for v in M.processVintages[r, p, t]
        # Make sure (r,p,t,v) combinations are defined
        if (r,p,t,v) in M.activeCapacityAvailable_rptv


    )

    # In most Temoa input databases, demand is endogenous, so we use electricity
    # generation instead.
    total_generation = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, S_v, S_o]
        for (t,S_v) in M.processReservePeriods[r, p]
        for S_i in M.processInputs[r, p, t, S_v]
        for S_o in M.ProcessOutputsByInput[r, p, t, S_v, S_i]
    )

    cap_target = total_generation * (1 + value(M.PlanningReserveMargin[r]))

    return cap_avail >= cap_target


def EmissionLimit_Constraint(M, r, p, e):
    r"""

A modeler can track emissions through use of the :code:`commodity_emissions`
set and :code:`EmissionActivity` parameter.  The :math:`EAC` parameter is
analogous to the efficiency table, tying emissions to a unit of activity.  The
EmissionLimit constraint allows the modeler to assign an upper bound per period
to each emission commodity. Note that this constraint sums emissions from
technologies with output varying at the time slice and those with constant annual
output in separate terms.

.. math::
   :label: EmissionLimit

       \sum_{S,D,I,T,V,O|{r,e,i,t,v,o} \in EAC} \left (
       EAC_{r, e, i, t, v, o} \cdot \textbf{FO}_{r, p, s, d, i, t, v, o}
       \right )
       +
       \sum_{I,T,V,O|{r,e,i,t \in T^{a},v,o} \in EAC} \left (
       EAC_{r, e, i, t, v, o} \cdot \textbf{FOA}_{r, p, i, t, v, o}
       \right )
       \le
       ELM_{r, p, e}

       \\
       \forall \{r, p, e\} \in \Theta_{\text{EmissionLimit}}

"""
    emission_limit = M.EmissionLimit[r, p, e]

     # r can be an individual region (r='US'), or a combination of regions separated by hyphen (r='Mexico-US-Canada'), or 'global'.
     # Note that regions!=M.regions. We iterate over regions to find actural_emissions and actual_emissions_annual.
    regions = set(r.split("-"))

    # if r == 'global', the constraint is system-wide
    if regions == {'global'}:
      regions = M.regions


    actual_emissions = sum(
        M.V_FlowOut[reg, p, S_s, S_d, S_i, S_t, S_v, S_o]
        * M.EmissionActivity[reg, e, S_i, S_t, S_v, S_o]
        for reg in regions
        for tmp_r, tmp_e, S_i, S_t, S_v, S_o in M.EmissionActivity.sparse_iterkeys()
        if tmp_e == e and tmp_r == reg and S_t not in M.tech_annual
        # EmissionsActivity not indexed by p, so make sure (r,p,t,v) combos valid
        if (reg, p, S_t, S_v) in M.processInputs.keys()
        for S_s in M.time_season
        for S_d in M.time_of_day
    )

    actual_emissions_flex = sum(
        M.V_Flex[reg, p, S_s, S_d, S_i, S_t, S_v, S_o]
        * M.EmissionActivity[reg, e, S_i, S_t, S_v, S_o]
        for reg in regions
        for tmp_r, tmp_e, S_i, S_t, S_v, S_o in M.EmissionActivity.sparse_iterkeys()
        if tmp_e == e and tmp_r == reg and S_t not in M.tech_annual and S_t in M.tech_flex and S_o in M.flex_commodities
        # EmissionsActivity not indexed by p, so make sure (r,p,t,v) combos valid
        if (reg, p, S_t, S_v) in M.processInputs.keys()
        for S_s in M.time_season
        for S_d in M.time_of_day
    )

    actual_emissions_curtail = sum(
        M.V_Curtailment[reg, p, S_s, S_d, S_i, S_t, S_v, S_o]
        * M.EmissionActivity[reg, e, S_i, S_t, S_v, S_o]
        for reg in regions
        for tmp_r, tmp_e, S_i, S_t, S_v, S_o in M.EmissionActivity.sparse_iterkeys()
        if tmp_e == e and tmp_r == reg and S_t not in M.tech_annual and S_t in M.tech_curtailment
        # EmissionsActivity not indexed by p, so make sure (r,p,t,v) combos valid
        if (reg, p, S_t, S_v) in M.processInputs.keys()
        for S_s in M.time_season
        for S_d in M.time_of_day
    )

    actual_emissions_annual = sum(
        M.V_FlowOutAnnual[reg, p, S_i, S_t, S_v, S_o]
        * M.EmissionActivity[reg, e, S_i, S_t, S_v, S_o]
        for reg in regions
        for tmp_r, tmp_e, S_i, S_t, S_v, S_o in M.EmissionActivity.sparse_iterkeys()
        if tmp_e == e and tmp_r == reg and S_t in M.tech_annual
        # EmissionsActivity not indexed by p, so make sure (r,p,t,v) combos valid
        if (reg, p, S_t, S_v) in M.processInputs.keys()
    )

    actual_emissions_flex_annual = sum(
        M.V_FlexAnnual[reg, p, S_i, S_t, S_v, S_o]
        * M.EmissionActivity[reg, e, S_i, S_t, S_v, S_o]
        for reg in regions
        for tmp_r, tmp_e, S_i, S_t, S_v, S_o in M.EmissionActivity.sparse_iterkeys()
        if tmp_e == e and tmp_r == reg and S_t in M.tech_annual and S_t in M.tech_flex and S_o in M.flex_commodities
        # EmissionsActivity not indexed by p, so make sure (r,p,t,v) combos valid
        if (reg, p, S_t, S_v) in M.processInputs.keys()
    )

    if int is type(actual_emissions + actual_emissions_annual + actual_emissions_flex + actual_emissions_curtail + actual_emissions_flex_annual):
        msg = (
            "Warning: No technology produces emission '%s', though limit was "
            "specified as %s.\n"
        )
        SE.write(msg % (e, emission_limit))
        return Constraint.Skip

    expr = actual_emissions + actual_emissions_annual + actual_emissions_flex + actual_emissions_curtail + actual_emissions_flex_annual <= emission_limit
    return expr


def GrowthRateConstraint_rule(M, p, r, t):
    r"""

This constraint sets an upper bound growth rate on technology-specific capacity.

.. math::
   :label: GrowthRate

   CAPAVL_{r, p_{i},t} \le GRM \cdot CAPAVL_{r,p_{i-1},t} + GRS

   \\
   \forall \{r, p, t\} \in \Theta_{\text{GrowthRate}}

where :math:`GRM` is the maximum growth rate, and should be specified as
:math:`(1+r)` and :math:`GRS` is the growth rate seed, which has units of
capacity. Without the seed, any technology with zero capacity in the first time
period would be restricted to zero capacity for the remainder of the time
horizon.
"""
    GRS = value(M.GrowthRateSeed[r, t])
    GRM = value(M.GrowthRateMax[r, t])
    CapPT = M.V_CapacityAvailableByPeriodAndTech

    periods = sorted(set(p_ for r_, p_, t_ in CapPT if t_ == t))

    if p not in periods:
        return Constraint.Skip

    if p == periods[0]:
        expr = CapPT[r, p, t] <= GRS

    else:
        p_prev = periods.index(p)
        p_prev = periods[p_prev - 1]

        expr = CapPT[r, p, t] <= GRM * CapPT[r, p_prev, t] + GRS

    return expr


def MaxActivity_Constraint(M, r, p, t):
    r"""

The MaxActivity sets an upper bound on the activity from a specific technology.
Note that the indices for these constraints are region, period and tech, not tech
and vintage. The first version of the constraint pertains to technologies with
variable output at the time slice level, and the second version pertains to
technologies with constant annual output belonging to the :code:`tech_annual`
set.

.. math::
   :label: MaxActivity

   \sum_{S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o}  \le MAXACT_{r, p, t}

   \forall \{r, p, t\} \in \Theta_{\text{MaxActivity}}

   \sum_{I,V,O} \textbf{FOA}_{r, p, i, t, v, o}  \le MAXACT_{r, p, t}

   \forall \{r, p, t \in T^{a}\} \in \Theta_{\text{MaxActivity}}

"""
    try:
      activity_rpt = sum(
          M.V_FlowOut[r, p, s, d, S_i, t, S_v, S_o]
          for S_v in M.processVintages[r, p, t]
          for S_i in M.processInputs[r, p, t, S_v]
          for S_o in M.ProcessOutputsByInput[r, p, t, S_v, S_i]
          for s in M.time_season
          for d in M.time_of_day
      )
    except:
      activity_rpt = sum(
          M.V_FlowOutAnnual[r, p, S_i, t, S_v, S_o]
          for S_v in M.processVintages[r, p, t]
          for S_i in M.processInputs[r, p, t, S_v]
          for S_o in M.ProcessOutputsByInput[r, p, t, S_v, S_i]
      )

    max_act = value(M.MaxActivity[r, p, t])
    expr = activity_rpt <= max_act
    return expr


def MinActivity_Constraint(M, r, p, t):
    r"""

The MinActivity sets a lower bound on the activity from a specific technology.
Note that the indices for these constraints are region, period and tech, not tech and
vintage. The first version of the constraint pertains to technologies with
variable output at the time slice level, and the second version pertains to
technologies with constant annual output belonging to the :code:`tech_annual`
set.

.. math::
   :label: MinActivity

   \sum_{S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o} \ge MINACT_{r, p, t}

   \forall \{r, p, t\} \in \Theta_{\text{MinActivity}}

   \sum_{I,V,O} \textbf{FOA}_{r, p, i, t, v, o} \ge MINACT_{r, p, t}

   \forall \{r, p, t \in T^{a}\} \in \Theta_{\text{MinActivity}}

"""

    try:
      activity_rpt = sum(
          M.V_FlowOut[r, p, s, d, S_i, t, S_v, S_o]
          for S_v in M.processVintages[r, p, t]
          for S_i in M.processInputs[r, p, t, S_v]
          for S_o in M.ProcessOutputsByInput[r, p, t, S_v, S_i]
          for s in M.time_season
          for d in M.time_of_day
      )
    except:
      activity_rpt = sum(
          M.V_FlowOutAnnual[r, p, S_i, t, S_v, S_o]
          for S_v in M.processVintages[r, p, t]
          for S_i in M.processInputs[r, p, t, S_v]
          for S_o in M.ProcessOutputsByInput[r, p, t, S_v, S_i]
      )

    min_act = value(M.MinActivity[r, p, t])
    expr = activity_rpt >= min_act
    return expr


def MinActivityGroup_Constraint(M, p, g):
    r"""

The MinActivityGroup constraint sets a minimum activity limit for a user-defined
technology group. Each technology within each group is multiplied by a
weighting function, which determines what technology activity share can count
towards the constraint.

.. math::
   :label: MinActivityGroup

       \sum_{S,D,I,T,V,O} \textbf{FO}_{p, s, d, i, t, v, o} \cdot WEIGHT_{t|t \not \in T^{a}}
       + \sum_{I,T,V,O} \textbf{FOA}_{p, i, t, v, o} \cdot WEIGHT_{t \in T^{a}}
       \ge MGGT_{p, g}

       \forall \{p, g\} \in \Theta_{\text{MinActivityGroup}}

where :math:`g` represents the assigned technology group and :math:`MGGT`
refers to the :code:`MinGenGroupTarget` parameter.
"""

    activity_p = sum(
        M.V_FlowOut[r, p, s, d, S_i, S_t, S_v, S_o] * M.MinGenGroupWeight[r, S_t, g]
        for r, p, S_t in M.processVintages.keys() if (S_t in M.tech_groups) & (S_t not in M.tech_annual)
        for S_v in M.processVintages[r, p, S_t]
        for S_i in M.processInputs[r, p, S_t, S_v]
        for S_o in M.ProcessOutputsByInput[r, p, S_t, S_v, S_i]
        for s in M.time_season
        for d in M.time_of_day
    )

    activity_p_annual = sum(
        M.V_FlowOutAnnual[r, p, S_i, S_t, S_v, S_o] * M.MinGenGroupWeight[r, S_t, g]
        for r, p, S_t in M.processVintages.keys() if (S_t in M.tech_groups) & (S_t in M.tech_annual)
        for S_v in M.processVintages[r, p, S_t]
        for S_i in M.processInputs[r, p, S_t, S_v]
        for S_o in M.ProcessOutputsByInput[r, p, S_t, S_v, S_i]
    )


    min_act = value(M.MinGenGroupTarget[p, g])
    expr = activity_p + activity_p_annual >= min_act
    return expr


def MaxCapacity_Constraint(M, r, p, t):
    r"""

The MaxCapacity constraint sets a limit on the maximum available capacity of a
given technology. Note that the indices for these constraints are region, period and
tech, not tech and vintage.

.. math::
   :label: MaxCapacity

   \textbf{CAPAVL}_{r, p, t} \le MAX_{r, p, t}

   \forall \{r, p, t\} \in \Theta_{\text{MaxCapacity}}
"""
    max_cap = value(M.MaxCapacity[r, p, t])
    expr = M.V_CapacityAvailableByPeriodAndTech[r, p, t] <= max_cap
    return expr


def MaxResource_Constraint(M, r, t):
    r"""

The MaxResource constraint sets a limit on the maximum available resource of a
given technology across all model time periods. Note that the indices for these
constraints are region and tech.

.. math::
   :label: MaxResource

   \textbf{CAPAVL}_{r, p, t} \le MAX_{r, p, t}

   \forall \{r, p, t\} \in \Theta_{\text{MaxCapacity}}
"""
    max_resource = value(M.MaxResource[r, t])
    try:
      activity_rt = sum(
          M.V_FlowOut[r, p, s, d, S_i, t, S_v, S_o]
          for p in M.time_optimize
          if (r, p, t) in M.processVintages.keys()
          for S_v in M.processVintages[r, p, t]
          for S_i in M.processInputs[r, p, t, S_v]
          for S_o in M.ProcessOutputsByInput[r, p, t, S_v, S_i]
          for s in M.time_season
          for d in M.time_of_day
      )
    except:
      activity_rt = sum(
          M.V_FlowOutAnnual[r, p, S_i, t, S_v, S_o]
          for p in M.time_optimize
          if (r, p, t) in M.processVintages.keys()
          for S_v in M.processVintages[r, p, t]
          for S_i in M.processInputs[r, p, t, S_v]
          for S_o in M.ProcessOutputsByInput[r, p, t, S_v, S_i]
      )

    expr = activity_rt <= max_resource
    return expr


def MaxCapacitySet_Constraint(M, p):
    r"""
Similar to the :code:`MaxCapacity` constraint, but works on a group of technologies
specified in the :code:`tech_capacity_max` subset.

"""
    max_cap = value(M.MaxCapacitySum[p])
    aggcap = sum(
        M.V_CapacityAvailableByPeriodAndTech[p, t] for t in M.tech_capacity_max
    )
    expr = aggcap <= max_cap
    return expr


def MinCapacity_Constraint(M, r, p, t):
    r"""

The MinCapacity constraint sets a limit on the minimum available capacity of a
given technology. Note that the indices for these constraints are region, period and
tech, not tech and vintage.

.. math::
   :label: MinCapacityCapacityAvailableByPeriodAndTech

   \textbf{CAPAVL}_{r, p, t} \ge MIN_{r, p, t}

   \forall \{r, p, t\} \in \Theta_{\text{MinCapacity}}
"""
    min_cap = value(M.MinCapacity[r, p, t])
    expr = M.V_CapacityAvailableByPeriodAndTech[r, p, t] >= min_cap
    return expr


def MinCapacitySet_Constraint(M, p):
    r"""
Similar to the :code:`MinCapacity` constraint, but works on a group of technologies
specified in the :code:`tech_capacity_min` subset.

"""
    min_cap = value(M.MinCapacitySum[p])
    aggcap = sum(
        M.V_CapacityAvailableByPeriodAndTech[p, t] for t in M.tech_capacity_min
    )
    expr = aggcap >= min_cap
    return expr


def TechInputSplit_Constraint(M, r, p, s, d, i, t, v):
    r"""
Allows users to specify fixed or minimum shares of commodity inputs to a process
producing a single output. These shares can vary by model time period. See
TechOutputSplit_Constraint for an analogous explanation. Under this constraint,
only the technologies with variable output at the timeslice level (i.e.,
NOT in the :code:`tech_annual` set) are considered.
"""
    inp = sum(
        M.V_FlowOut[r, p, s, d, i, t, v, S_o] / value(M.Efficiency[r, i, t, v, S_o])
        for S_o in M.ProcessOutputsByInput[r, p, t, v, i]
    )

    total_inp = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o] / value(M.Efficiency[r, S_i, t, v, S_o])
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.ProcessOutputsByInput[r, p, t, v, i]
    )

    expr = inp >= M.TechInputSplit[r, p, i, t] * total_inp
    return expr

def TechInputSplitAnnual_Constraint(M, r, p, i, t, v):
    r"""
Allows users to specify fixed or minimum shares of commodity inputs to a process
producing a single output. These shares can vary by model time period. See
TechOutputSplitAnnual_Constraint for an analogous explanation. Under this
function, only the technologies with constant annual output (i.e., members
of the :math:`tech_annual` set) are considered.
"""
    inp = sum(
        M.V_FlowOutAnnual[r, p, i, t, v, S_o] / value(M.Efficiency[r, i, t, v, S_o])
        for S_o in M.ProcessOutputsByInput[r, p, t, v, i]
    )

    total_inp = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o] / value(M.Efficiency[r, S_i, t, v, S_o])
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.ProcessOutputsByInput[r, p, t, v, i]
    )

    expr = inp >= M.TechInputSplit[r, p, i, t] * total_inp
    return expr

def TechOutputSplit_Constraint(M, r, p, s, d, t, v, o):
    r"""

Some processes take a single input and make multiple outputs, and the user would like to
specify either a constant or time-varying ratio of outputs per unit input.  The most
canonical example is an oil refinery.  Crude oil is used to produce many different refined
products. In many cases, the modeler would like to specify a minimum share of each refined
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
   :label: TechOutputSplit

     \sum_{I, t \not \in T^{a}} \textbf{FO}_{r, p, s, d, i, t, v, o}
   \geq
     SPL_{r, p, t, o} \cdot \sum_{I, O, t \not \in T^{a}} \textbf{FO}_{r, p, s, d, i, t, v, o}

   \forall \{r, p, s, d, t, v, o\} \in \Theta_{\text{TechOutputSplit}}
"""
    out = sum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, o]
        for S_i in M.ProcessInputsByOutput[r, p, t, v, o]
    )

    total_out = sum(
      M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
      for S_i in M.processInputs[r, p, t, v]
      for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i]
    )

    expr = out >= M.TechOutputSplit[r, p, t, o] * total_out
    return expr

def TechOutputSplitAnnual_Constraint ( M, r, p, t, v, o):
    r"""
This constraint operates similarly to TechOutputSplit_Constraint.
However, under this function, only the technologies with constant annual
output (i.e., members of the :math:`tech_annual` set) are considered.

.. math::
   :label: TechOutputSplitAnnual

     \sum_{I, t \in T^{a}} \textbf{FOA}_{r, p, i, t, v, o}

   \geq

     SPL_{r, p, t, o} \cdot \sum_{I, O, t \in T^{a}} \textbf{FOA}_{r, p, s, d, i, t, v, o}

   \forall \{r, p, t, v, o\} \in \Theta_{\text{TechOutputSplitAnnual}}
"""
    out = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, o]
        for S_i in M.ProcessInputsByOutput[r, p, t, v, o]
    )

    total_out = sum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i]
      )

    expr = out >= M.TechOutputSplit[r, p, t, o] * total_out
    return expr

# ---------------------------------------------------------------
# Define rule-based parameters
# ---------------------------------------------------------------
def ParamModelLoanLife_rule(M, r, t, v):
    loan_length = value(M.LifetimeLoanProcess[r, t, v])
    mll = min(loan_length, max(M.time_future) - v)

    return mll


def ParamModelProcessLife_rule(M, r, p, t, v):
    life_length = value(M.LifetimeProcess[r, t, v])
    tpl = min(v + life_length - p, value(M.PeriodLength[p]))

    return tpl


def ParamPeriodLength(M, p):
    # This specifically does not use time_optimize because this function is
    # called /over/ time_optimize.
    periods = sorted(M.time_future)

    i = periods.index(p)

    # The +1 won't fail, because this rule is called over time_optimize, which
    # lacks the last period in time_future.
    length = periods[i + 1] - periods[i]

    return length


def ParamPeriodRate(M, p):
    """\

The "Period Rate" is a multiplier against the costs incurred within a period to
bring the time-value back to the base year.  The parameter PeriodRate is not
directly specified by the modeler, but is a convenience calculation based on the
GlobalDiscountRate and the length of each period.  One may refer to this
(pseudo) parameter via M.PeriodRate[ a_period ]
"""
    rate_multiplier = sum(
        (1 + M.GlobalDiscountRate) ** (M.time_optimize.first() - p - y)
        for y in range(0, M.PeriodLength[p])
    )

    return value(rate_multiplier)


def ParamProcessLifeFraction_rule(M, r, p, t, v):
    """\

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


def ParamLoanAnnualize_rule(M, r, t, v):
    dr = value(M.DiscountRate[r, t, v])
    lln = value(M.LifetimeLoanProcess[r, t, v])
    if not dr:
        return 1.0 / lln
    annualized_rate = dr / (1.0 - (1.0 + dr) ** (-lln))

    return annualized_rate
