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

from __future__ import annotations

import sys
from logging import getLogger
from typing import TYPE_CHECKING, cast

from pyomo.environ import Constraint, quicksum, value

import temoa.components.geography as geography
import temoa.components.technology as technology
from temoa.components.utils import (
    Operator,
    get_variable_efficiency,
    operator_expression,
)

if TYPE_CHECKING:
    from pyomo.core import Expression

    from temoa.core.model import TemoaModel
    from temoa.types import ExprLike, Period, Region, Technology, Vintage
    from temoa.types.core_types import Commodity, Season, TimeOfDay

logger = getLogger(__name__)

# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def limit_tech_input_split_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, str]]:
    indices = {
        (r, p, s, d, i, t, v, op)
        for r, p, i, t, op in model.input_split_vintages
        if t not in model.tech_annual
        for v in model.input_split_vintages[r, p, i, t, op]
        for s in model.time_season
        for d in model.time_of_day
    }
    ann_indices = {
        (r, p, i, t, op) for r, p, i, t, op in model.input_split_vintages if t in model.tech_annual
    }
    if len(ann_indices) > 0:
        msg = (
            'Warning: Annual technologies included in limit_tech_input_split table. '
            'Use limit_tech_input_split_annual table instead or these constraints will '
            'be ignored: {}'
        )
        logger.warning(msg.format(ann_indices))

    return indices


def limit_tech_input_split_annual_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Commodity, Technology, Vintage, str]]:
    return {
        (r, p, i, t, v, op)
        for r, p, i, t, op in model.input_split_annual_vintages
        if t in model.tech_annual
        for v in model.input_split_annual_vintages[r, p, i, t, op]
    }


def limit_tech_input_split_average_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Commodity, Technology, Vintage, str]]:
    return {
        (r, p, i, t, v, op)
        for r, p, i, t, op in model.input_split_annual_vintages
        if t not in model.tech_annual
        for v in model.input_split_annual_vintages[r, p, i, t, op]
    }


def limit_tech_output_split_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage, Commodity, str]]:
    indices = {
        (r, p, s, d, t, v, o, op)
        for r, p, t, o, op in model.output_split_vintages
        if t not in model.tech_annual
        for v in model.output_split_vintages[r, p, t, o, op]
        for s in model.time_season
        for d in model.time_of_day
    }
    ann_indices = {
        (r, p, t, o, op) for r, p, t, o, op in model.output_split_vintages if t in model.tech_annual
    }
    if len(ann_indices) > 0:
        msg = (
            'Warning: Annual technologies included in limit_tech_output_split table. '
            'Use limit_tech_output_split_annual table instead or these constraints will '
            'be ignored: {}'
        )
        logger.warning(msg.format(ann_indices))

    return indices


def limit_tech_output_split_annual_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Technology, Vintage, Commodity, str]]:
    return {
        (r, p, t, v, o, op)
        for r, p, t, o, op in model.output_split_annual_vintages
        if t in model.tech_annual
        for v in model.output_split_annual_vintages[r, p, t, o, op]
    }


def limit_tech_output_split_average_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Technology, Vintage, Commodity, str]]:
    return {
        (r, p, t, v, o, op)
        for r, p, t, o, op in model.output_split_annual_vintages
        if t not in model.tech_annual
        for v in model.output_split_annual_vintages[r, p, t, o, op]
    }


def limit_seasonal_capacity_factor_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, Technology, str]]:
    """Expand the period-free param set to include all time_optimize periods."""
    return {
        (r, p, s, t, op)
        for r, s, t, op in model.limit_seasonal_capacity_factor_constraint_rst
        for p in model.time_optimize
    }


def limit_annual_capacity_factor_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Technology, Vintage, Commodity, str]]:
    return {
        (r, p, t, v, o, op)
        for r, t, v, o, op in model.limit_annual_capacity_factor_constraint_rtvo
        for _r in geography.gather_group_regions(model, r)
        for _t in technology.gather_group_techs(model, t)
        for p in model.time_optimize
        if o in model.process_outputs.get((_r, p, _t, v), [])
    }


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


# @deprecated('Deprecated. Use limit_activityGroupShare instead') # doesn't play well with pyomo
def renewable_portfolio_standard_constraint(
    model: TemoaModel, r: Region, p: Period, g: str
) -> ExprLike:
    r"""
    Allows users to specify the share of electricity generation in a region
    coming from RPS-eligible technologies.
    """
    # devnote: this formulation leans on the reserve set, which is not necessarily
    # the super set we want. We can also generalise this to all groups and so
    # it has been deprecated in favour of the limit_activityGroupShare constraint.

    inp = quicksum(
        model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
        for t in model.tech_group_members[g]
        for (_t, v) in model.process_reserve_periods.get((r, p), [])
        if _t == t
        for s in model.time_season
        for d in model.time_of_day
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    total_inp = quicksum(
        model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
        for (t, v) in model.process_reserve_periods[r, p]
        for s in model.time_season
        for d in model.time_of_day
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    expr = inp >= (value(model.renewable_portfolio_standard[r, p, g]) * total_inp)
    return expr


def limit_resource_constraint(model: TemoaModel, r: Region, t: Technology, op: str) -> ExprLike:
    r"""

    The limit_resource constraint sets a limit on the available resource of a
    given technology across all model time periods. Note that the indices for these
    constraints are region and tech.

    .. math::
       :label: limit_resource

       \sum_{P,S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t \notin T^a, v, o}

       +\sum_{P,I,V,O} \textbf{FOA}_{r, p, i, t \in T^a, v, o}

       \quad \le, \ge, \text{or} = \quad LS_{r, t}

       \forall \{r, t\} \in \Theta_{\text{limit\_resource}}"""
    # dev note:  this constraint is a misnomer.  It is actually a "global activity constraint on a
    #            tech" regardless of whatever "resources" are consumed.
    # dev note:  this would generally be applied to a "dummy import" technology to restrict
    #            something like oil/mineral extraction across all model periods. Looks fine to me.

    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)

    activity = quicksum(
        model.v_flow_out_annual[_r, p, S_i, _t, S_v, S_o]
        for _t in techs
        if _t in model.tech_annual
        for p in model.time_optimize
        for _r in regions
        if (_r, p, _t) in model.process_vintages
        for S_v in model.process_vintages[_r, p, _t]
        for S_i in model.process_inputs[_r, p, _t, S_v]
        for S_o in model.process_outputs_by_input[_r, p, _t, S_v, S_i]
    )
    activity += quicksum(
        model.v_flow_out[_r, p, s, d, S_i, _t, S_v, S_o]
        for _t in techs
        if _t not in model.tech_annual
        for p in model.time_optimize
        for _r in regions
        if (_r, p, _t) in model.process_vintages
        for S_v in model.process_vintages[_r, p, _t]
        for S_i in model.process_inputs[_r, p, _t, S_v]
        for S_o in model.process_outputs_by_input[_r, p, _t, S_v, S_i]
        for s in model.time_season
        for d in model.time_of_day
    )

    resource_lim = value(model.limit_resource[r, t, op])
    expr = operator_expression(activity, Operator(op), resource_lim)
    return expr


def limit_activity_share_constraint(
    model: TemoaModel, r: Region, p: Period, g1: Technology, g2: Technology, op: str
) -> ExprLike:
    r"""
    Limits the activity of a given technology or group as a fraction of another
    technology or group, summed over a period. This can be used to set, for example,
    a renewable portfolio scheme constraint.

    .. math::
        :label: Limit Activity Share

        \sum_{R_g \subseteq R,\ S,\ D,\ I,\ (T^{g_1} \setminus T^a) \subseteq T,\ V,\ O}
        \mathbf{FO}_{r,p,s,d,i,t,v,o}
        + \sum_{R_g \subseteq R,\ I,\ (T^{g_1} \cap T^a) \subseteq T,\ V,\ O}
        \mathbf{FOA}_{r,p,i,t,v,o}
        \\
        \quad \le, \ge, \text{or} = \quad
        \\
        LAS_{r,p,g_1,g_2} \cdot
        \sum_{R_g \subseteq R,\ S,\ D,\ I,\ (T^{g_2} \setminus T^a) \subseteq T,\ V,\ O}
        \mathbf{FO}_{r,p,s,d,i,t,v,o}
        + \sum_{R_g \subseteq R,\ I,\ (T^{g_2} \cap T^a) \subseteq T,\ V,\ O}
        \mathbf{FOA}_{r,p,i,t,v,o}

        \qquad \forall \{r, p, g_1, g_2\} \in \Theta_{\text{limit\_activity\_share}}
    """

    regions = geography.gather_group_regions(model, r)

    sub_group = technology.gather_group_techs(model, g1)
    sub_activity = quicksum(
        model.v_flow_out[_r, p, s, d, S_i, S_t, S_v, S_o]
        for S_t in sub_group
        if S_t not in model.tech_annual
        for _r in regions
        for S_v in model.process_vintages.get((_r, p, S_t), [])
        for S_i in model.process_inputs[_r, p, S_t, S_v]
        for S_o in model.process_outputs_by_input[_r, p, S_t, S_v, S_i]
        for s in model.time_season
        for d in model.time_of_day
    )
    sub_activity += quicksum(
        model.v_flow_out_annual[_r, p, S_i, S_t, S_v, S_o]
        for S_t in sub_group
        if S_t in model.tech_annual
        for _r in regions
        for S_v in model.process_vintages.get((_r, p, S_t), [])
        for S_i in model.process_inputs[_r, p, S_t, S_v]
        for S_o in model.process_outputs_by_input[_r, p, S_t, S_v, S_i]
    )

    super_group = technology.gather_group_techs(model, g2)
    super_activity = quicksum(
        model.v_flow_out[_r, p, s, d, S_i, S_t, S_v, S_o]
        for S_t in super_group
        if S_t not in model.tech_annual
        for _r in regions
        for S_v in model.process_vintages.get((_r, p, S_t), [])
        for S_i in model.process_inputs[_r, p, S_t, S_v]
        for S_o in model.process_outputs_by_input[_r, p, S_t, S_v, S_i]
        for s in model.time_season
        for d in model.time_of_day
    )
    super_activity += quicksum(
        model.v_flow_out_annual[_r, p, S_i, S_t, S_v, S_o]
        for S_t in super_group
        if S_t in model.tech_annual
        for _r in regions
        for S_v in model.process_vintages.get((_r, p, S_t), [])
        for S_i in model.process_inputs[_r, p, S_t, S_v]
        for S_o in model.process_outputs_by_input[_r, p, S_t, S_v, S_i]
    )

    share_lim = value(model.limit_activity_share[r, p, g1, g2, op])
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


def limit_capacity_share_constraint(
    model: TemoaModel, r: Region, p: Period, g1: Technology, g2: Technology, op: str
) -> ExprLike:
    r"""
    The limit_capacity_share constraint limits the available capacity of a given
    technology or technology group as a fraction of another technology or group.
    """

    regions = geography.gather_group_regions(model, r)

    sub_group = technology.gather_group_techs(model, g1)
    sub_capacity = quicksum(
        model.v_capacity_available_by_period_and_tech[_r, p, _t]
        for _t in sub_group
        for _r in regions
        if (_r, p, _t) in model.process_vintages
    )

    super_group = technology.gather_group_techs(model, g2)
    super_capacity = quicksum(
        model.v_capacity_available_by_period_and_tech[_r, p, _t]
        for _t in super_group
        for _r in regions
        if (_r, p, _t) in model.process_vintages
    )
    share_lim = value(model.limit_capacity_share[r, p, g1, g2, op])

    expr = operator_expression(sub_capacity, Operator(op), share_lim * super_capacity)
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def limit_new_capacity_share_constraint(
    model: TemoaModel, r: Region, g1: Technology, g2: Technology, v: Vintage, op: str
) -> ExprLike:
    r"""
    The limit_new_capacity_share constraint limits the share of new capacity
    of a given technology or group as a fraction of another technology or
    group."""

    regions = geography.gather_group_regions(model, r)

    sub_group = technology.gather_group_techs(model, g1)
    sub_new_cap = quicksum(
        model.v_new_capacity[_r, _t, v]
        for _t in sub_group
        for _r in regions
        if (_r, _t, v) in model.process_periods
    )

    super_group = technology.gather_group_techs(model, g2)
    super_new_cap = quicksum(
        model.v_new_capacity[_r, _t, v]
        for _t in super_group
        for _r in regions
        if (_r, _t, v) in model.process_periods
    )

    share_lim = value(model.limit_new_capacity_share[r, g1, g2, v, op])
    expr = operator_expression(sub_new_cap, Operator(op), share_lim * super_new_cap)
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def limit_annual_capacity_factor_constraint(
    model: TemoaModel, r: Region, p: Period, t: Technology, v: Vintage, o: Commodity, op: str
) -> ExprLike:
    r"""
    The limit_annual_capacity_factor sets an upper bound on the annual capacity factor
    from a specific process. The first portion of the constraint pertains to
    technologies with variable output at the time slice level, and the second portion
    pertains to technologies with constant annual output belonging to the
    :code:`tech_annual` set.

    .. math::
        :label: limit_annual_capacity_factor

            \sum_{S,D,I} \textbf{FO}_{r, p, s, d, i, t, v, o}
            \quad \le, \ge, \text{or} = \quad
            LIMACF_{r, t, v, o} \cdot
            \textbf{CAP}_{r, p, t, v} \cdot \text{C2A}_{r, t}

            \forall \{r, p, t \notin T^{a}, v, o\}
            \in \Theta_{\text{limit\_annual\_capacity\_factor}}

            \\\sum_{I} \textbf{FOA}_{r, p, i, t, v, o}
            \quad \le, \ge, \text{or} = \quad
            LIMACF_{r, t, v, o} \cdot
            \textbf{CAP}_{r, p, t, v} \cdot \text{C2A}_{r, t}

            \forall \{r, p, t \in T^{a}, v, o\} \in \Theta_{\text{limit\_annual\_capacity\_factor}}

    """
    # r can be an individual region (r='US'), or a combination of regions separated by plus
    # (r='Mexico+US+Canada'), or 'global'.
    # if r == 'global', the constraint is system-wide
    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)

    activity_rptvo = 0

    for _t in techs:
        if _t not in model.tech_annual:
            activity_rptvo += quicksum(
                model.v_flow_out[_r, p, s, d, S_i, _t, v, o]
                for _r in regions
                for S_i in model.process_inputs_by_output.get((_r, p, _t, v, o), [])
                for s in model.time_season
                for d in model.time_of_day
            )
        else:
            activity_rptvo += quicksum(
                model.v_flow_out_annual[_r, p, S_i, _t, v, o]
                for _r in regions
                for S_i in model.process_inputs_by_output.get((_r, p, _t, v, o), [])
            )

    possible_activity_rptvo = quicksum(
        model.v_capacity[_r, p, _t, v] * value(model.capacity_to_activity[_r, _t])
        for _r in regions
        for _t in techs
        if v in model.process_vintages.get((_r, p, _t), [])
    )
    annual_cf = value(model.limit_annual_capacity_factor[r, t, v, o, op])
    expr = operator_expression(activity_rptvo, Operator(op), annual_cf * possible_activity_rptvo)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


def limit_seasonal_capacity_factor_constraint(
    model: TemoaModel, r: Region, p: Period, s: Season, t: Technology, op: str
) -> ExprLike:
    r"""
    The limit_seasonal_capacity_factor sets an upper bound on the seasonal capacity factor
    from a specific technology. The first portion of the constraint pertains to
    technologies with variable output at the time slice level, and the second portion
    pertains to technologies with constant annual output belonging to the
    :code:`tech_annual` set.

    .. math::
        :label: Limit Seasonal Capacity Factor

        \sum_{D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o}
        \quad \le, \ge, \text{or} = \quad
        LIMSCF_{r, s, t} \cdot
        \textbf{CAPAVL}_{r, p, t} \cdot \text{C2A}_{r, t} \cdot SFS_s

        \forall \{r, p, s, t \notin T^{a}\} \in \Theta_{\text{limit\_seasonal\_capacity\_factor}}

        \\\sum_{I,V,O} \textbf{FOA}_{r, p, i, t, v, o} \cdot SFS_s
        \quad \le, \ge, \text{or} = \quad
        LIMSCF_{r, s, t} \cdot
        \textbf{CAPAVL}_{r, p, t} \cdot \text{C2A}_{r, t} \cdot SFS_s

        \forall \{r, p, s, t \in T^{a}\} \in \Theta_{\text{limit\_seasonal\_capacity\_factor}}
    """
    # r can be an individual region (r='US'), or a combination of regions separated by plus
    # (r='Mexico+US+Canada'), or 'global'.
    # if r == 'global', the constraint is system-wide
    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)

    # we need to screen here because it is possible that the restriction extends beyond the
    # lifetime of any vintage of the tech...
    if all(
        (_r, p, _t) not in model.v_capacity_available_by_period_and_tech
        for _r in regions
        for _t in techs
    ):
        return Constraint.Skip

    if TYPE_CHECKING:
        activity_rpst = cast('Expression', 0)
    else:
        activity_rpst = 0
    for _t in techs:
        if _t not in model.tech_annual:
            activity_rpst += quicksum(
                model.v_flow_out[_r, p, s, d, S_i, _t, S_v, S_o]
                for _r in regions
                for S_v in model.process_vintages.get((_r, p, _t), [])
                for S_i in model.process_inputs.get((_r, p, _t, S_v), [])
                for S_o in model.process_outputs_by_input.get((_r, p, _t, S_v, S_i), [])
                for d in model.time_of_day
            )
        else:
            activity_rpst += quicksum(
                model.v_flow_out_annual[_r, p, S_i, _t, S_v, S_o]
                * model.segment_fraction_per_season[s]
                for _r in regions
                for S_v in model.process_vintages.get((_r, p, _t), [])
                for S_i in model.process_inputs.get((_r, p, _t, S_v), [])
                for S_o in model.process_outputs_by_input.get((_r, p, _t, S_v, S_i), [])
            )

    possible_activity_rpst = quicksum(
        model.v_capacity_available_by_period_and_tech[_r, p, _t]
        * value(model.capacity_to_activity[_r, _t])
        * value(model.segment_fraction_per_season[s])
        for _r in regions
        for _t in techs
        if (_r, p, _t) in model.v_capacity_available_by_period_and_tech
    )
    seasonal_cf = value(model.limit_seasonal_capacity_factor[r, s, t, op])
    expr = operator_expression(activity_rpst, Operator(op), seasonal_cf * possible_activity_rpst)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


def limit_tech_input_split_constraint(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    i: Commodity,
    t: Technology,
    v: Vintage,
    op: str,
) -> ExprLike:
    r"""
    Allows users to limit shares of commodity inputs to a process
    producing a single output. These shares can vary by model time period. See
    limit_tech_output_split_constraint for an analogous explanation. Under this constraint,
    only the technologies with variable output at the timeslice level (i.e.,
    NOT in the :code:`tech_annual` set) are considered."""
    inp = quicksum(
        model.v_flow_out[r, p, s, d, i, t, v, S_o]
        / get_variable_efficiency(model, r, p, s, d, i, t, v, S_o)
        for S_o in model.process_outputs_by_input[r, p, t, v, i]
    )

    total_inp = quicksum(
        model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
        / get_variable_efficiency(model, r, p, s, d, S_i, t, v, S_o)
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    expr = operator_expression(
        inp, Operator(op), value(model.limit_tech_input_split[r, p, i, t, op]) * total_inp
    )
    return expr


def limit_tech_input_split_annual_constraint(
    model: TemoaModel, r: Region, p: Period, i: Commodity, t: Technology, v: Vintage, op: str
) -> ExprLike:
    r"""
    Allows users to limit shares of commodity inputs to a process
    producing a single output. These shares can vary by model time period. See
    limit_tech_output_split_annual_constraint for an analogous explanation. Under this
    function, only the technologies with constant annual output (i.e., members
    of the :code:`tech_annual` set) are considered."""
    inp = quicksum(
        model.v_flow_out_annual[r, p, i, t, v, S_o] / value(model.efficiency[r, i, t, v, S_o])
        for S_o in model.process_outputs_by_input[r, p, t, v, i]
    )

    total_inp = quicksum(
        model.v_flow_out_annual[r, p, S_i, t, v, S_o] / value(model.efficiency[r, S_i, t, v, S_o])
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    expr = operator_expression(
        inp, Operator(op), value(model.limit_tech_input_split_annual[r, p, i, t, op]) * total_inp
    )
    return expr


def limit_tech_input_split_average_constraint(
    model: TemoaModel, r: Region, p: Period, i: Commodity, t: Technology, v: Vintage, op: str
) -> ExprLike:
    r"""
    Allows users to limit shares of commodity inputs to a process
    producing a single output. Under this constraint, only the technologies with variable
    output at the timeslice level (i.e., NOT in the :code:`tech_annual` set) are considered.
    This constraint differs from limit_tech_input_split as it specifies shares on an annual basis,
    so even though it applies to technologies with variable output at the timeslice level,
    the constraint only fixes the input shares over the course of a year."""

    inp = quicksum(
        model.v_flow_out[r, p, S_s, S_d, i, t, v, S_o]
        / get_variable_efficiency(model, r, p, S_s, S_d, i, t, v, S_o)
        for S_s in model.time_season
        for S_d in model.time_of_day
        for S_o in model.process_outputs_by_input[r, p, t, v, i]
    )
    total_inp = quicksum(
        model.v_flow_out[r, p, S_s, S_d, S_i, t, v, S_o]
        / get_variable_efficiency(model, r, p, S_s, S_d, S_i, t, v, S_o)
        for S_s in model.time_season
        for S_d in model.time_of_day
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    expr = operator_expression(
        inp, Operator(op), value(model.limit_tech_input_split_annual[r, p, i, t, op]) * total_inp
    )
    return expr


def limit_tech_output_split_constraint(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
    o: Commodity,
    op: str,
) -> ExprLike:
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
       :label: limit_tech_output_split

         \sum_{I, t \not \in T^{a}} \textbf{FO}_{r, p, s, d, i, t, v, o}
       \quad \le, \ge, \text{or} = \quad
         TOS_{r, p, t, o} \cdot \sum_{I, O, t \not \in T^{a}} \textbf{FO}_{r, p, s, d, i, t, v, o}

       \forall \{r, p, s, d, t, v, o\} \in \Theta_{\text{limit\_tech\_output\_split}}"""
    out = quicksum(
        model.v_flow_out[r, p, s, d, S_i, t, v, o]
        for S_i in model.process_inputs_by_output[r, p, t, v, o]
    )

    total_out = quicksum(
        model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    expr = operator_expression(
        out, Operator(op), value(model.limit_tech_output_split[r, p, t, o, op]) * total_out
    )
    return expr


def limit_tech_output_split_annual_constraint(
    model: TemoaModel, r: Region, p: Period, t: Technology, v: Vintage, o: Commodity, op: str
) -> ExprLike:
    r"""
    This constraint operates similarly to limit_tech_output_split_constraint.
    However, under this function, only the technologies with constant annual
    output (i.e., members of the :code:`tech_annual` set) are considered.

    .. math::
       :label: limit_tech_output_split_annual

            \sum_{I, T^{a}} \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}
            \quad \le, \ge, \text{or} = \quad
            TOSA_{r, p, t, o} \cdot
            \sum_{I, O, T^{a}} \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}

            \forall \{r, p, t \in T^{a}, v, o\} \in
            \Theta_{\text{limit\_tech\_output\_split\_annual}}"""
    out = quicksum(
        model.v_flow_out_annual[r, p, S_i, t, v, o]
        for S_i in model.process_inputs_by_output[r, p, t, v, o]
    )

    total_out = quicksum(
        model.v_flow_out_annual[r, p, S_i, t, v, S_o]
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    expr = operator_expression(
        out, Operator(op), value(model.limit_tech_output_split_annual[r, p, t, o, op]) * total_out
    )
    return expr


def limit_tech_output_split_average_constraint(
    model: TemoaModel, r: Region, p: Period, t: Technology, v: Vintage, o: Commodity, op: str
) -> ExprLike:
    r"""
    Allows users to limit shares of commodity outputs from a process.
    Under this constraint, only the technologies with variable
    output at the timeslice level (i.e., NOT in the :code:`tech_annual` set) are considered.
    This constraint differs from limit_tech_output_split as it specifies shares on an annual basis,
    so even though it applies to technologies with variable output at the timeslice level,
    the constraint only fixes the output shares over the course of a year."""

    out = quicksum(
        model.v_flow_out[r, p, S_s, S_d, S_i, t, v, o]
        for S_i in model.process_inputs_by_output[r, p, t, v, o]
        for S_s in model.time_season
        for S_d in model.time_of_day
    )

    total_out = quicksum(
        model.v_flow_out[r, p, S_s, S_d, S_i, t, v, S_o]
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        for S_s in model.time_season
        for S_d in model.time_of_day
    )

    expr = operator_expression(
        out, Operator(op), value(model.limit_tech_output_split_annual[r, p, t, o, op]) * total_out
    )
    return expr


def limit_emission_constraint(
    model: TemoaModel, r: Region, p: Period, e: Commodity, op: str
) -> ExprLike:
    r"""

    A modeler can track emissions through use of the :code:`commodity_emissions`
    set and :code:`emission_activity` parameter.  The :math:`EAC` parameter is
    analogous to the efficiency table, tying emissions to a unit of activity.  The
    limit_emission constraint allows the modeler to assign an upper bound per period
    to each emission commodity. Note that this constraint sums emissions from
    technologies with output varying at the time slice and those with constant annual
    output in separate terms. It also includes embodied emissions from new capacity
    and end-of-life emissions from retiring capacity.

    .. math::
       :label: limit_emission

           \sum_{S,D,I,T,V,O|{r,e,i,t,v,o} \in EAC} \left (
           EAC_{r, e, i, t, v, o} \cdot \textbf{FO}_{r, p, s, d, i, t, v, o}
           \right ) & \\
           +
           \sum_{I,T,V,O|{r,e,i,t \in T^{a},v,o} \in EAC} (
           EAC_{r, e, i, t, v, o} \cdot & \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}
            ) \\
           +
           \sum_{T} \frac{EE_{r, e, t, v=p} \cdot \textbf{NCAP}_{r, t, v=p}}{LEN_p} & \\
           +
           \sum_{T,V} EEOL_{r, e, t, v} \cdot \textbf{ART}_{r, p, t, v} &
           \\
           \quad \le, \ge, \text{or} = \quad
           LE_{r, p, e}

           \\
           & \forall \{r, p, e\} \in \Theta_{\text{limit\_emission}}

    """
    emission_limit = value(model.limit_emission[r, p, e, op])

    # r can be an individual region (r='US'), or a combination of regions separated by a +
    # (r='Mexico+US+Canada'), or 'global'.  Note that regions!=M.regions. We iterate over regions
    # to find actual_emissions and actual_emissions_annual.

    # if r == 'global', the constraint is system-wide

    regions = geography.gather_group_regions(model, r)

    # ================= Emissions and Flex and Curtailment =================
    # Flex flows are deducted from v_flow_out, so it is NOT NEEDED to tax them again.
    # (See commodity balance constr)
    # Curtailment does not draw any inputs, so it seems logical that curtailed flows not be taxed
    # either

    process_emissions = quicksum(
        model.v_flow_out[reg, p, S_s, S_d, S_i, S_t, S_v, S_o]
        * value(model.emission_activity[reg, e, S_i, S_t, S_v, S_o])
        for reg in regions
        for tmp_r, tmp_e, S_i, S_t, S_v, S_o in model.emission_activity.sparse_keys()
        if tmp_e == e and tmp_r == reg and S_t not in model.tech_annual
        # EmissionsActivity not indexed by p, so make sure (r,p,t,v) combos valid
        if (reg, p, S_t, S_v) in model.process_inputs
        for S_s in model.time_season
        for S_d in model.time_of_day
    )

    process_emissions_annual = quicksum(
        model.v_flow_out_annual[reg, p, S_i, S_t, S_v, S_o]
        * value(model.emission_activity[reg, e, S_i, S_t, S_v, S_o])
        for reg in regions
        for tmp_r, tmp_e, S_i, S_t, S_v, S_o in model.emission_activity.sparse_keys()
        if tmp_e == e and tmp_r == reg and S_t in model.tech_annual
        # EmissionsActivity not indexed by p, so make sure (r,p,t,v) combos valid
        if (reg, p, S_t, S_v) in model.process_inputs
    )

    embodied_emissions = quicksum(
        model.v_new_capacity[reg, t, v]
        * value(model.emission_embodied[reg, e, t, v])
        / value(model.period_length[v])
        for reg in regions
        for (S_r, S_e, t, v) in model.emission_embodied.sparse_keys()
        if v == p and S_r == reg and S_e == e
    )

    retirement_emissions = quicksum(
        model.v_annual_retirement[reg, p, t, v] * value(model.emission_end_of_life[reg, e, t, v])
        for reg in regions
        for (S_r, S_e, t, v) in model.emission_end_of_life.sparse_keys()
        if (reg, t, v) in model.retirement_periods and p in model.retirement_periods[reg, t, v]
        if S_r == reg and S_e == e
    )

    lhs = (
        process_emissions + process_emissions_annual + embodied_emissions + retirement_emissions
        # + emissions_flex # NO! flex is subtracted from flowout, already accounted by flowout
        # + emissions_curtail # NO! curtailed flows are not actual flows, just an accounting tool
        # + emissions_flex_annual # NO! flexannual is subtracted from flowoutannual, already
        # accounted
    )
    expr = operator_expression(lhs, Operator(op), emission_limit)

    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        msg = "Warning: No technology produces emission '%s', though limit was specified as %s.\n"
        logger.warning(msg, (e, emission_limit))
        sys.stderr.write(msg % (e, emission_limit))
        return Constraint.Skip

    return expr


def limit_activity_constraint(
    model: TemoaModel, r: Region, p: Period, t: Technology, op: str
) -> ExprLike:
    r"""

    Sets a limit on the activity from a specific technology.
    Note that the indices for these constraints are region, period and tech, not tech
    and vintage. The first version of the constraint pertains to technologies with
    variable output at the time slice level, and the second version pertains to
    technologies with constant annual output belonging to the :code:`tech_annual`
    set.

    .. math::
       :label: limit_activity

       \sum_{S,D,I,V,O} \textbf{FO}_{r, p, s, d, i, t, v, o}

       \forall \{r, p, t \notin T^{a}\} \in \Theta_{\text{limit\_activity}}

       +\sum_{I,V,O} \textbf{FOA}_{r, p, i, t \in T^{a}, v, o}

       \forall \{r, p, t \in T^{a}\} \in \Theta_{\text{limit\_activity}}

       \quad \le, \ge, \text{or} = \quad LA_{r, p, t}
    """
    # r can be an individual region (r='US'), or a combination of regions separated by
    # a + (r='Mexico+US+Canada'), or 'global'.
    # if r == 'global', the constraint is system-wide
    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)

    activity = quicksum(
        model.v_flow_out[_r, p, s, d, S_i, _t, S_v, S_o]
        for _t in techs
        if _t not in model.tech_annual
        for _r in regions
        for S_v in model.process_vintages.get((_r, p, _t), [])
        for S_i in model.process_inputs[_r, p, _t, S_v]
        for S_o in model.process_outputs_by_input[_r, p, _t, S_v, S_i]
        for s in model.time_season
        for d in model.time_of_day
    )
    activity += quicksum(
        model.v_flow_out_annual[_r, p, S_i, _t, S_v, S_o]
        for _t in techs
        if _t in model.tech_annual
        for _r in regions
        for S_v in model.process_vintages.get((_r, p, _t), [])
        for S_i in model.process_inputs[_r, p, _t, S_v]
        for S_o in model.process_outputs_by_input[_r, p, _t, S_v, S_i]
    )

    act_lim = value(model.limit_activity[r, p, t, op])
    expr = operator_expression(activity, Operator(op), act_lim)
    # in the case that there is nothing to sum, skip
    if isinstance(expr, bool):  # an empty list was generated
        return Constraint.Skip
    return expr


def limit_new_capacity_constraint(
    model: TemoaModel, r: Region, t: Technology, v: Vintage, op: str
) -> ExprLike:
    r"""
    The limit_new_capacity constraint sets a limit on the newly installed capacity of a
    given technology or group in a given vintage year.

    .. math::
        :label: limit_new_capacity

        \textbf{NCAP}_{r, t, v} \quad \le, \ge, \text{or} = \quad LNC_{r, t, v}
    """
    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)
    cap_lim = value(model.limit_new_capacity[r, t, v, op])
    new_cap = quicksum(
        model.v_new_capacity[_r, _t, v]
        for _t in techs
        for _r in regions
        if (_r, _t, v) in model.process_periods
    )
    expr = operator_expression(new_cap, Operator(op), cap_lim)
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def limit_capacity_constraint(
    model: TemoaModel, r: Region, p: Period, t: Technology, op: str
) -> ExprLike:
    r"""

    The limit_capacity constraint sets a limit on the available capacity of a
    given technology. Note that the indices for these constraints are region, period and
    tech, not tech and vintage.

    .. math::
       :label: limit_capacity

       \textbf{CAPAVL}_{r, p, t} \quad \le, \ge, \text{or} = \quad LC_{r, p, t}

       \forall \{r, p, t\} \in \Theta_{\text{limit\_capacity}}"""
    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)
    cap_lim = value(model.limit_capacity[r, p, t, op])
    capacity = quicksum(
        model.v_capacity_available_by_period_and_tech[_r, p, _t]
        for _t in techs
        for _r in regions
        if (_r, p, _t) in model.v_capacity_available_by_period_and_tech
    )
    expr = operator_expression(capacity, Operator(op), cap_lim)
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


# ============================================================================
# PRE-COMPUTATION FUNCTION
# ============================================================================


def create_limit_vintage_sets(model: TemoaModel) -> None:
    """
    Populates vintage-specific dictionaries for input/output split limit constraints.

    This function iterates through active processes and identifies which vintages are
    subject to split constraints, populating dictionaries that are then used by
    the index set functions below.

    Populates:
        - M.input_split_vintages: dict mapping (r, p, i, t, op) to a set of vintages `v`.
        - M.input_split_annual_vintages: dict for annual-specific input splits.
        - M.output_split_vintages: dict mapping (r, p, t, o, op) to a set of vintages `v`.
        - M.output_split_annual_vintages: dict for annual-specific output splits.
    """
    logger.debug('Creating vintage sets for split limits.')
    # Assuming M.process_vintages is already populated
    for r, p, t in model.process_vintages:
        for v in model.process_vintages[r, p, t]:
            for i in model.process_inputs.get((r, p, t, v), []):
                for op in model.operator:
                    if (r, p, i, t, op) in model.limit_tech_input_split:
                        model.input_split_vintages.setdefault((r, p, i, t, op), set()).add(v)
                    if (r, p, i, t, op) in model.limit_tech_input_split_annual:
                        model.input_split_annual_vintages.setdefault((r, p, i, t, op), set()).add(v)

            for o in model.process_outputs.get((r, p, t, v), []):
                for op in model.operator:
                    if (r, p, t, o, op) in model.limit_tech_output_split:
                        model.output_split_vintages.setdefault((r, p, t, o, op), set()).add(v)
                    if (r, p, t, o, op) in model.limit_tech_output_split_annual:
                        model.output_split_annual_vintages.setdefault((r, p, t, o, op), set()).add(
                            v
                        )
