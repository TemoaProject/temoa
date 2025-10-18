# temoa/components/limits.py
"""
Defines the various limit-related components of the Temoa model.

This module contains a wide variety of constraints that enforce
limits on the energy system. These include, but are not limited to:
- Input/Output splits for technologies like refineries.
- Growth and degrowth rates for capacity deployment.
- Shares of capacity or activity for technology groups (e.g., for RPS policies).
- Absolute limits on capacity, new investment, or emissions.
"""

import sys
from logging import getLogger
from typing import TYPE_CHECKING, Any

from pyomo.environ import Constraint, quicksum, value

import temoa.components.geography as geography
import temoa.components.technology as technology
from temoa.components.utils import Operator, get_variable_efficiency, operator_expression
from temoa.types import Period, Region, Technology, Vintage

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

logger = getLogger(__name__)

# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def LimitTechInputSplitConstraintIndices(
    M: 'TemoaModel',
) -> set[tuple[Region, Period, str, str, str, str, Vintage, str]]:
    indices = {
        (r, p, s, d, i, t, v, op)
        for r, p, i, t, op in M.inputSplitVintages
        if t not in M.tech_annual
        for v in M.inputSplitVintages[r, p, i, t, op]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    }
    ann_indices = {
        (r, p, i, t, op) for r, p, i, t, op in M.inputSplitVintages if t in M.tech_annual
    }
    if len(ann_indices) > 0:
        msg = (
            'Warning: Annual technologies included in LimitTechInputSplit table. '
            'Use LimitTechInputSplitAnnual table instead or these constraints will be ignored: {}'
        )
        logger.warning(msg.format(ann_indices))

    return indices


def LimitTechInputSplitAnnualConstraintIndices(
    M: 'TemoaModel',
) -> set[tuple[Region, Period, str, str, Vintage, str]]:
    indices = {
        (r, p, i, t, v, op)
        for r, p, i, t, op in M.inputSplitAnnualVintages
        if t in M.tech_annual
        for v in M.inputSplitAnnualVintages[r, p, i, t, op]
    }

    return indices


def LimitTechInputSplitAverageConstraintIndices(
    M: 'TemoaModel',
) -> set[tuple[Region, Period, str, str, Vintage, str]]:
    indices = {
        (r, p, i, t, v, op)
        for r, p, i, t, op in M.inputSplitAnnualVintages
        if t not in M.tech_annual
        for v in M.inputSplitAnnualVintages[r, p, i, t, op]
    }
    return indices


def LimitTechOutputSplitConstraintIndices(
    M: 'TemoaModel',
) -> set[tuple[Region, Period, str, str, str, Vintage, str, str]]:
    indices = {
        (r, p, s, d, t, v, o, op)
        for r, p, t, o, op in M.outputSplitVintages
        if t not in M.tech_annual
        for v in M.outputSplitVintages[r, p, t, o, op]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    }
    ann_indices = {
        (r, p, t, o, op) for r, p, t, o, op in M.outputSplitVintages if t in M.tech_annual
    }
    if len(ann_indices) > 0:
        msg = (
            'Warning: Annual technologies included in LimitTechOutputSplit table. '
            'Use LimitTechOutputSplitAnnual table instead or these constraints will be ignored: {}'
        )
        logger.warning(msg.format(ann_indices))

    return indices


def LimitTechOutputSplitAnnualConstraintIndices(
    M: 'TemoaModel',
) -> set[tuple[Region, Period, str, Vintage, str, str]]:
    indices = {
        (r, p, t, v, o, op)
        for r, p, t, o, op in M.outputSplitAnnualVintages
        if t in M.tech_annual
        for v in M.outputSplitAnnualVintages[r, p, t, o, op]
    }
    return indices


def LimitTechOutputSplitAverageConstraintIndices(
    M: 'TemoaModel',
) -> set[tuple[Region, Period, str, Vintage, str, str]]:
    indices = {
        (r, p, t, v, o, op)
        for r, p, t, o, op in M.outputSplitAnnualVintages
        if t not in M.tech_annual
        for v in M.outputSplitAnnualVintages[r, p, t, o, op]
    }
    return indices


def LimitGrowthCapacityIndices(M: 'TemoaModel') -> set[tuple[Region, Period, Technology, str]]:
    indices = {
        (r, p, t, op)
        for r, t, op in M.LimitGrowthCapacity.sparse_iterkeys()
        for p in M.time_optimize
    }
    return indices


def LimitDegrowthCapacityIndices(M: 'TemoaModel') -> set[tuple[Region, Period, Technology, str]]:
    indices = {
        (r, p, t, op)
        for r, t, op in M.LimitDegrowthCapacity.sparse_iterkeys()
        for p in M.time_optimize
    }
    return indices


def LimitGrowthNewCapacityIndices(M: 'TemoaModel') -> set[tuple[Region, Period, Technology, str]]:
    indices = {
        (r, p, t, op)
        for r, t, op in M.LimitGrowthNewCapacity.sparse_iterkeys()
        for p in M.time_optimize
    }
    return indices


def LimitDegrowthNewCapacityIndices(M: 'TemoaModel') -> set[tuple[Region, Period, Technology, str]]:
    indices = {
        (r, p, t, op)
        for r, t, op in M.LimitDegrowthNewCapacity.sparse_iterkeys()
        for p in M.time_optimize
    }
    return indices


def LimitGrowthNewCapacityDeltaIndices(
    M: 'TemoaModel',
) -> set[tuple[Region, Period, Technology, str]]:
    indices = {
        (r, p, t, op)
        for r, t, op in M.LimitGrowthNewCapacityDelta.sparse_iterkeys()
        for p in M.time_optimize
    }
    return indices


def LimitDegrowthNewCapacityDeltaIndices(
    M: 'TemoaModel',
) -> set[tuple[Region, Period, Technology, str]]:
    indices = {
        (r, p, t, op)
        for r, t, op in M.LimitDegrowthNewCapacityDelta.sparse_iterkeys()
        for p in M.time_optimize
    }
    return indices


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


# @deprecated('Deprecated. Use LimitActivityGroupShare instead') # doesn't play well with pyomo
def RenewablePortfolioStandard_Constraint(M: 'TemoaModel', r: Region, p: Period, g: str) -> Any:
    r"""
    Allows users to specify the share of electricity generation in a region
    coming from RPS-eligible technologies.
    """
    # devnote: this formulation leans on the reserve set, which is not necessarily
    # the super set we want. We can also generalise this to all groups and so
    # it has been deprecated in favour of the LimitActivityGroupShare constraint.

    inp = quicksum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for t in M.tech_group_members[g]
        for (_t, v) in M.processReservePeriods.get((r, p), [])
        if _t == t
        for s in M.TimeSeason[p]
        for d in M.time_of_day
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    total_inp = quicksum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for (t, v) in M.processReservePeriods[r, p]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = inp >= (value(M.RenewablePortfolioStandard[r, p, g]) * total_inp)
    return expr


def LimitResource_Constraint(M: 'TemoaModel', r: Region, t: Technology, op: str) -> Any:
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

    regions = geography.gather_group_regions(M, r)
    techs = technology.gather_group_techs(M, t)

    activity = quicksum(
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
    activity += quicksum(
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
    expr = operator_expression(activity, Operator(op), resource_lim)
    return expr


def LimitActivityShare_Constraint(
    M: 'TemoaModel', r: Region, p: Period, g1: str, g2: str, op: str
) -> Any:
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

    regions = geography.gather_group_regions(M, r)

    sub_group = technology.gather_group_techs(M, g1)
    sub_activity = quicksum(
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
    sub_activity += quicksum(
        M.V_FlowOutAnnual[_r, p, S_i, S_t, S_v, S_o]
        for S_t in sub_group
        if S_t in M.tech_annual
        for _r in regions
        for S_v in M.processVintages.get((_r, p, S_t), [])
        for S_i in M.processInputs[_r, p, S_t, S_v]
        for S_o in M.processOutputsByInput[_r, p, S_t, S_v, S_i]
    )

    super_group = technology.gather_group_techs(M, g2)
    super_activity = quicksum(
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
    super_activity += quicksum(
        M.V_FlowOutAnnual[_r, p, S_i, S_t, S_v, S_o]
        for S_t in super_group
        if S_t in M.tech_annual
        for _r in regions
        for S_v in M.processVintages.get((_r, p, S_t), [])
        for S_i in M.processInputs[_r, p, S_t, S_v]
        for S_o in M.processOutputsByInput[_r, p, S_t, S_v, S_i]
    )

    share_lim = value(M.LimitActivityShare[r, p, g1, g2, op])
    expr = operator_expression(sub_activity, Operator(op), share_lim * super_activity)
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


def LimitCapacityShare_Constraint(
    M: 'TemoaModel', r: Region, p: Period, g1: str, g2: str, op: str
) -> Any:
    r"""
    The LimitCapacityShare constraint limits the available capacity of a given
    technology or technology group as a fraction of another technology or group.
    """

    regions = geography.gather_group_regions(M, r)

    sub_group = technology.gather_group_techs(M, g1)
    sub_capacity = quicksum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, _t]
        for _t in sub_group
        for _r in regions
        if (_r, p, _t) in M.processVintages
    )

    super_group = technology.gather_group_techs(M, g2)
    super_capacity = quicksum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, _t]
        for _t in super_group
        for _r in regions
        if (_r, p, _t) in M.processVintages
    )
    share_lim = value(M.LimitCapacityShare[r, p, g1, g2, op])

    expr = operator_expression(sub_capacity, Operator(op), share_lim * super_capacity)
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitNewCapacityShare_Constraint(
    M: 'TemoaModel', r: Region, p: Period, g1: str, g2: str, op: str
) -> Any:
    r"""
    The LimitNewCapacityShare constraint limits the share of new capacity
    of a given technology or group as a fraction of another technology or
    group."""

    regions = geography.gather_group_regions(M, r)

    sub_group = technology.gather_group_techs(M, g1)
    sub_new_cap = quicksum(
        M.V_NewCapacity[_r, _t, p]
        for _t in sub_group
        for _r in regions
        if (_r, _t, p) in M.processPeriods
    )

    super_group = technology.gather_group_techs(M, g2)
    super_new_cap = quicksum(
        M.V_NewCapacity[_r, _t, p]
        for _t in super_group
        for _r in regions
        if (_r, _t, p) in M.processPeriods
    )

    share_lim = value(M.LimitNewCapacityShare[r, p, g1, g2, op])
    expr = operator_expression(sub_new_cap, Operator(op), share_lim * super_new_cap)
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitAnnualCapacityFactor_Constraint(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, o: str, op: str
) -> Any:
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
    regions = geography.gather_group_regions(M, r)
    # we need to screen here because it is possible that the restriction extends beyond the
    # lifetime of any vintage of the tech...
    if all((_r, p, t) not in M.V_CapacityAvailableByPeriodAndTech for _r in regions):
        return Constraint.Skip

    if t not in M.tech_annual:
        activity_rpt = quicksum(
            M.V_FlowOut[_r, p, s, d, S_i, t, S_v, o]
            for _r in regions
            for S_v in M.processVintages.get((_r, p, t), [])
            for S_i in M.processInputs[_r, p, t, S_v]
            for s in M.TimeSeason[p]
            for d in M.time_of_day
        )
    else:
        activity_rpt = quicksum(
            M.V_FlowOutAnnual[_r, p, S_i, t, S_v, o]
            for _r in regions
            for S_v in M.processVintages.get((_r, p, t), [])
            for S_i in M.processInputs[_r, p, t, S_v]
        )

    possible_activity_rpt = quicksum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, t] * value(M.CapacityToActivity[_r, t])
        for _r in regions
    )
    annual_cf = value(M.LimitAnnualCapacityFactor[r, p, t, o, op])
    expr = operator_expression(activity_rpt, Operator(op), annual_cf * possible_activity_rpt)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


def LimitSeasonalCapacityFactor_Constraint(
    M: 'TemoaModel', r: Region, p: Period, s: str, t: Technology, op: str
) -> Any:
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
    regions = geography.gather_group_regions(M, r)
    # we need to screen here because it is possible that the restriction extends beyond the
    # lifetime of any vintage of the tech...
    if all((_r, p, t) not in M.V_CapacityAvailableByPeriodAndTech for _r in regions):
        return Constraint.Skip

    if t not in M.tech_annual:
        activity_rpst = quicksum(
            M.V_FlowOut[_r, p, s, d, S_i, t, S_v, S_o]
            for _r in regions
            for S_v in M.processVintages[_r, p, t]
            for S_i in M.processInputs[_r, p, t, S_v]
            for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
            for d in M.time_of_day
        )
    else:
        activity_rpst = quicksum(
            M.V_FlowOutAnnual[_r, p, S_i, t, S_v, S_o] * M.SegFracPerSeason[p, s]
            for _r in regions
            for S_v in M.processVintages[_r, p, t]
            for S_i in M.processInputs[_r, p, t, S_v]
            for S_o in M.processOutputsByInput[_r, p, t, S_v, S_i]
        )

    possible_activity_rpst = quicksum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, t]
        * value(M.CapacityToActivity[_r, t])
        * value(M.SegFracPerSeason[p, s])
        for _r in regions
    )
    seasonal_cf = value(M.LimitSeasonalCapacityFactor[r, p, s, t, op])
    expr = operator_expression(activity_rpst, Operator(op), seasonal_cf * possible_activity_rpst)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


def LimitTechInputSplit_Constraint(
    M: 'TemoaModel',
    r: Region,
    p: Period,
    s: str,
    d: str,
    i: str,
    t: Technology,
    v: Vintage,
    op: str,
) -> Any:
    r"""
    Allows users to limit shares of commodity inputs to a process
    producing a single output. These shares can vary by model time period. See
    LimitTechOutputSplit_Constraint for an analogous explanation. Under this constraint,
    only the technologies with variable output at the timeslice level (i.e.,
    NOT in the :code:`tech_annual` set) are considered."""
    inp = quicksum(
        M.V_FlowOut[r, p, s, d, i, t, v, S_o] / get_variable_efficiency(M, r, p, s, d, i, t, v, S_o)
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    total_inp = quicksum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        / get_variable_efficiency(M, r, p, s, d, S_i, t, v, S_o)
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = operator_expression(
        inp, Operator(op), value(M.LimitTechInputSplit[r, p, i, t, op]) * total_inp
    )
    return expr


def LimitTechInputSplitAnnual_Constraint(
    M: 'TemoaModel', r: Region, p: Period, i: str, t: Technology, v: Vintage, op: str
) -> Any:
    r"""
    Allows users to limit shares of commodity inputs to a process
    producing a single output. These shares can vary by model time period. See
    LimitTechOutputSplitAnnual_Constraint for an analogous explanation. Under this
    function, only the technologies with constant annual output (i.e., members
    of the :code:`tech_annual` set) are considered."""
    inp = quicksum(
        M.V_FlowOutAnnual[r, p, i, t, v, S_o] / value(M.Efficiency[r, i, t, v, S_o])
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    total_inp = quicksum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o] / value(M.Efficiency[r, S_i, t, v, S_o])
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = operator_expression(
        inp, Operator(op), value(M.LimitTechInputSplitAnnual[r, p, i, t, op]) * total_inp
    )
    return expr


def LimitTechInputSplitAverage_Constraint(
    M: 'TemoaModel', r: Region, p: Period, i: str, t: Technology, v: Vintage, op: str
) -> Any:
    r"""
    Allows users to limit shares of commodity inputs to a process
    producing a single output. Under this constraint, only the technologies with variable
    output at the timeslice level (i.e., NOT in the :code:`tech_annual` set) are considered.
    This constraint differs from LimitTechInputSplit as it specifies shares on an annual basis,
    so even though it applies to technologies with variable output at the timeslice level,
    the constraint only fixes the input shares over the course of a year."""

    inp = quicksum(
        M.V_FlowOut[r, p, S_s, S_d, i, t, v, S_o]
        / get_variable_efficiency(M, r, p, S_s, S_d, i, t, v, S_o)
        for S_s in M.TimeSeason[p]
        for S_d in M.time_of_day
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    total_inp = quicksum(
        M.V_FlowOut[r, p, S_s, S_d, S_i, t, v, S_o]
        / get_variable_efficiency(M, r, p, S_s, S_d, i, t, v, S_o)
        for S_s in M.TimeSeason[p]
        for S_d in M.time_of_day
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, i]
    )

    expr = operator_expression(
        inp, Operator(op), value(M.LimitTechInputSplitAnnual[r, p, i, t, op]) * total_inp
    )
    return expr


def LimitTechOutputSplit_Constraint(
    M: 'TemoaModel',
    r: Region,
    p: Period,
    s: str,
    d: str,
    t: Technology,
    v: Vintage,
    o: str,
    op: str,
) -> Any:
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
    out = quicksum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, o] for S_i in M.processInputsByOutput[r, p, t, v, o]
    )

    total_out = quicksum(
        M.V_FlowOut[r, p, s, d, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = operator_expression(
        out, Operator(op), value(M.LimitTechOutputSplit[r, p, t, o, op]) * total_out
    )
    return expr


def LimitTechOutputSplitAnnual_Constraint(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, v: Vintage, o: str, op: str
) -> Any:
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
    out = quicksum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, o] for S_i in M.processInputsByOutput[r, p, t, v, o]
    )

    total_out = quicksum(
        M.V_FlowOutAnnual[r, p, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
    )

    expr = operator_expression(
        out, Operator(op), value(M.LimitTechOutputSplitAnnual[r, p, t, o, op]) * total_out
    )
    return expr


def LimitTechOutputSplitAverage_Constraint(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, v: Vintage, o: str, op: str
) -> Any:
    r"""
    Allows users to limit shares of commodity outputs from a process.
    Under this constraint, only the technologies with variable
    output at the timeslice level (i.e., NOT in the :code:`tech_annual` set) are considered.
    This constraint differs from LimitTechOutputSplit as it specifies shares on an annual basis,
    so even though it applies to technologies with variable output at the timeslice level,
    the constraint only fixes the output shares over the course of a year."""

    out = quicksum(
        M.V_FlowOut[r, p, S_s, S_d, S_i, t, v, o]
        for S_i in M.processInputsByOutput[r, p, t, v, o]
        for S_s in M.TimeSeason[p]
        for S_d in M.time_of_day
    )

    total_out = quicksum(
        M.V_FlowOut[r, p, S_s, S_d, S_i, t, v, S_o]
        for S_i in M.processInputs[r, p, t, v]
        for S_o in M.processOutputsByInput[r, p, t, v, S_i]
        for S_s in M.TimeSeason[p]
        for S_d in M.time_of_day
    )

    expr = operator_expression(
        out, Operator(op), value(M.LimitTechOutputSplitAnnual[r, p, t, o, op]) * total_out
    )
    return expr


def LimitEmission_Constraint(M: 'TemoaModel', r: Region, p: Period, e: str, op: str) -> Any:
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

    regions = geography.gather_group_regions(M, r)

    # ================= Emissions and Flex and Curtailment =================
    # Flex flows are deducted from V_FlowOut, so it is NOT NEEDED to tax them again.  (See commodity balance constr)
    # Curtailment does not draw any inputs, so it seems logical that curtailed flows not be taxed either

    process_emissions = quicksum(
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

    process_emissions_annual = quicksum(
        M.V_FlowOutAnnual[reg, p, S_i, S_t, S_v, S_o]
        * value(M.EmissionActivity[reg, e, S_i, S_t, S_v, S_o])
        for reg in regions
        for tmp_r, tmp_e, S_i, S_t, S_v, S_o in M.EmissionActivity.sparse_iterkeys()
        if tmp_e == e and tmp_r == reg and S_t in M.tech_annual
        # EmissionsActivity not indexed by p, so make sure (r,p,t,v) combos valid
        if (reg, p, S_t, S_v) in M.processInputs
    )

    embodied_emissions = quicksum(
        M.V_NewCapacity[reg, t, v]
        * value(M.EmissionEmbodied[reg, e, t, v])
        / value(M.PeriodLength[v])
        for reg in regions
        for (S_r, S_e, t, v) in M.EmissionEmbodied.sparse_iterkeys()
        if v == p and S_r == reg and S_e == e
    )

    retirement_emissions = quicksum(
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
    expr = operator_expression(lhs, Operator(op), emission_limit)

    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        msg = "Warning: No technology produces emission '%s', though limit was specified as %s.\n"
        logger.warning(msg, (e, emission_limit))
        sys.stderr.write(msg % (e, emission_limit))
        return Constraint.Skip

    return expr


def LimitGrowthCapacityConstraint_rule(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str
) -> Any:
    r"""Constrain ramp up rate of available capacity"""
    return LimitGrowthCapacity(M, r, p, t, op, False)


def LimitDegrowthCapacityConstraint_rule(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str
) -> Any:
    r"""Constrain ramp down rate of available capacity"""
    return LimitGrowthCapacity(M, r, p, t, op, True)


def LimitGrowthCapacity(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str, degrowth: bool = False
) -> Any:
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

    regions = geography.gather_group_regions(M, r)
    techs = technology.gather_group_techs(M, t)

    growth = M.LimitDegrowthCapacity if degrowth else M.LimitGrowthCapacity
    RATE = 1 + value(growth[r, t, op][0])
    SEED = value(growth[r, t, op][1])
    CapRPT = M.V_CapacityAvailableByPeriodAndTech

    # relevant r, p, t indices
    cap_rpt = {(_r, _p, _t) for _r, _p, _t in CapRPT.keys() if _t in techs and _r in regions}
    # periods the technology can have capacity in this region (sorted)
    periods = sorted({_p for _r, _p, _t in cap_rpt})

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
        expr = operator_expression(capacity_prev, Operator(op), SEED + capacity * RATE)
    else:
        expr = operator_expression(capacity, Operator(op), SEED + capacity_prev * RATE)

    # Check if any variables are actually included before returning
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitGrowthNewCapacityConstraint_rule(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str
) -> Any:
    r"""Constrain ramp up rate of new capacity deployment"""
    return LimitGrowthNewCapacity(M, r, p, t, op, False)


def LimitDegrowthNewCapacityConstraint_rule(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str
) -> Any:
    r"""Constrain ramp down rate of new capacity deployment"""
    return LimitGrowthNewCapacity(M, r, p, t, op, True)


def LimitGrowthNewCapacity(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str, degrowth: bool = False
) -> Any:
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

    regions = geography.gather_group_regions(M, r)
    techs = technology.gather_group_techs(M, t)

    growth = M.LimitDegrowthNewCapacity if degrowth else M.LimitGrowthNewCapacity
    RATE = 1 + value(growth[r, t, op][0])
    SEED = value(growth[r, t, op][1])
    NewCapRTV = M.V_NewCapacity

    # relevant r, t, v indices
    cap_rtv = {(_r, _t, _v) for _r, _t, _v in NewCapRTV.keys() if _t in techs and _r in regions}
    # periods the technology can be built in this region (sorted)
    periods = sorted({_v for _r, _t, _v in cap_rtv})

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
        expr = operator_expression(new_cap_prev, Operator(op), SEED + new_cap * RATE)
    else:
        expr = operator_expression(new_cap, Operator(op), SEED + new_cap_prev * RATE)

    # Check if any variables are actually included before returning
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitGrowthNewCapacityDeltaConstraint_rule(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str
) -> Any:
    r"""Constrain ramp up rate of change in new capacity deployment"""
    return LimitGrowthNewCapacityDelta(M, r, p, t, op, False)


def LimitDegrowthNewCapacityDeltaConstraint_rule(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str
) -> Any:
    r"""Constrain ramp down rate of change in new capacity deployment"""
    return LimitGrowthNewCapacityDelta(M, r, p, t, op, True)


def LimitGrowthNewCapacityDelta(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str, degrowth: bool = False
) -> Any:
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

    regions = geography.gather_group_regions(M, r)
    techs = technology.gather_group_techs(M, t)

    growth = M.LimitDegrowthNewCapacityDelta if degrowth else M.LimitGrowthNewCapacityDelta
    RATE = 1 + value(growth[r, t, op][0])
    SEED = value(growth[r, t, op][1])
    NewCapRTV = M.V_NewCapacity

    # relevant r, t, v indices
    cap_rtv = {(_r, _t, _v) for _r, _t, _v in NewCapRTV.keys() if _t in techs and _r in regions}
    # periods the technology can be built in this region (sorted)
    periods = sorted({_v for _r, _t, _v in cap_rtv})

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
        expr = operator_expression(nc_delta_prev, Operator(op), SEED + nc_delta * RATE)
    else:
        expr = operator_expression(nc_delta, Operator(op), SEED + nc_delta_prev * RATE)

    # Check if any variables are actually included before returning
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def LimitActivity_Constraint(M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str) -> Any:
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
    regions = geography.gather_group_regions(M, r)
    techs = technology.gather_group_techs(M, t)

    activity = quicksum(
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
    activity += quicksum(
        M.V_FlowOutAnnual[_r, p, S_i, _t, S_v, S_o]
        for _t in techs
        if _t in M.tech_annual
        for _r in regions
        for S_v in M.processVintages.get((_r, p, _t), [])
        for S_i in M.processInputs[_r, p, _t, S_v]
        for S_o in M.processOutputsByInput[_r, p, _t, S_v, S_i]
    )

    act_lim = value(M.LimitActivity[r, p, t, op])
    expr = operator_expression(activity, Operator(op), act_lim)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


def LimitNewCapacity_Constraint(
    M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str
) -> Any:
    r"""
    The LimitNewCapacity constraint sets a limit on the newly installed capacity of a
    given technology or group in a given year. Note that the indices for these constraints are region,
    period and tech.

    .. math::
        :label: LimitNewCapacity

        \textbf{NCAP}_{r, t, v} \le LNC_{r, p, t}

        \text{where }v=p
    """
    regions = geography.gather_group_regions(M, r)
    techs = technology.gather_group_techs(M, t)
    cap_lim = value(M.LimitNewCapacity[r, p, t, op])
    new_cap = quicksum(M.V_NewCapacity[_r, _t, p] for _t in techs for _r in regions)
    expr = operator_expression(new_cap, Operator(op), cap_lim)
    return expr


def LimitCapacity_Constraint(M: 'TemoaModel', r: Region, p: Period, t: Technology, op: str) -> Any:
    r"""

    The LimitCapacity constraint sets a limit on the available capacity of a
    given technology. Note that the indices for these constraints are region, period and
    tech, not tech and vintage.

    .. math::
       :label: LimitCapacity

       \textbf{CAPAVL}_{r, p, t} \le LC_{r, p, t}

       \forall \{r, p, t\} \in \Theta_{\text{LimitCapacity}}"""
    regions = geography.gather_group_regions(M, r)
    techs = technology.gather_group_techs(M, t)
    cap_lim = value(M.LimitCapacity[r, p, t, op])
    capacity = quicksum(
        M.V_CapacityAvailableByPeriodAndTech[_r, p, _t] for _t in techs for _r in regions
    )
    expr = operator_expression(capacity, Operator(op), cap_lim)
    return expr


# ============================================================================
# PRE-COMPUTATION FUNCTION
# ============================================================================


def create_limit_vintage_sets(M: 'TemoaModel') -> None:
    """
    Populates vintage-specific dictionaries for input/output split limit constraints.

    This function iterates through active processes and identifies which vintages are
    subject to split constraints, populating dictionaries that are then used by
    the index set functions below.

    Populates:
        - M.inputSplitVintages: dict mapping (r, p, i, t, op) to a set of vintages `v`.
        - M.inputSplitAnnualVintages: dict for annual-specific input splits.
        - M.outputSplitVintages: dict mapping (r, p, t, o, op) to a set of vintages `v`.
        - M.outputSplitAnnualVintages: dict for annual-specific output splits.
    """
    logger.debug('Creating vintage sets for split limits.')
    # Assuming M.processVintages is already populated
    for r, p, t in M.processVintages:
        for v in M.processVintages[r, p, t]:
            for i in M.processInputs.get((r, p, t, v), []):
                for op in M.operator:
                    if (r, p, i, t, op) in M.LimitTechInputSplit:
                        M.inputSplitVintages.setdefault((r, p, i, t, op), set()).add(v)
                    if (r, p, i, t, op) in M.LimitTechInputSplitAnnual:
                        M.inputSplitAnnualVintages.setdefault((r, p, i, t, op), set()).add(v)

            for o in M.processOutputs.get((r, p, t, v), []):
                for op in M.operator:
                    if (r, p, t, o, op) in M.LimitTechOutputSplit:
                        M.outputSplitVintages.setdefault((r, p, t, o, op), set()).add(v)
                    if (r, p, t, o, op) in M.LimitTechOutputSplitAnnual:
                        M.outputSplitAnnualVintages.setdefault((r, p, t, o, op), set()).add(v)
