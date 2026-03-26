"""
Defines the commodity and demand-related components of the Temoa model.

This module is responsible for:
-  Pre-computing technology and commodity subsets (e.g., demand techs, flex techs).
-  Calculating and validating demand distributions across time slices.
-  Defining the core commodity balance and demand satisfaction constraints that
    drive the model's energy system solution.
"""

from __future__ import annotations

import sys
from itertools import product as cross_product
from logging import getLogger
from operator import itemgetter as iget
from typing import TYPE_CHECKING, Any, cast

from pyomo.environ import Constraint, value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types.core_types import Season, Technology, TimeOfDay, Vintage

    from ..types import Commodity, ExprLike, Period, Region

from .utils import get_variable_efficiency

logger = getLogger(name=__name__)

# ============================================================================
# HELPER FUNCTIONS AND VALIDATORS
# ============================================================================


def commodity_balance_constraint_error_check(
    supplied: Any, demanded: Any, r: Region, p: Period, s: Season, d: TimeOfDay, c: Commodity
) -> None:
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem. How this might come up I do not know
    if isinstance(supplied, int) and isinstance(demanded, int):
        expr = str(supplied == demanded)
        msg = (
            'Unable to balance commodity {} in ({}, {}, {}, {}).\n'
            'Nothing produces or consumes it:\n'
            '   {}\n'
            'Possible reasons:\n'
            " - Is there a missing period in set 'time_future'?\n"
            " - Is there a missing tech in set 'tech_resource'?\n"
            " - Is there a missing tech in set 'tech_production'?\n"
            " - Is there a missing commodity in set 'commodity_physical'?\n"
            ' - Are there missing entries in the efficiency table?\n'
            ' - Does a process need a longer Lifetime?'
        )
        logger.error(msg.format(c, r, p, s, d, expr))
        raise Exception(msg.format(c, r, p, s, d, expr))


def annual_commodity_balance_constraint_error_check(
    supplied: Any, demanded: Any, r: Region, p: Period, c: Commodity
) -> None:
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem. How this might come up I do not know
    if isinstance(supplied, int) and isinstance(demanded, int):
        expr = str(supplied == demanded)
        msg = (
            'Unable to balance annual commodity {} in ({}, {}).\n'
            'Nothing produces or consumes it:\n'
            '   {}\n'
            'Possible reasons:\n'
            " - Is there a missing period in set 'time_future'?\n"
            " - Is there a missing tech in set 'tech_resource'?\n"
            " - Is there a missing tech in set 'tech_production'?\n"
            " - Is there a missing commodity in set 'commodity_physical'?\n"
            ' - Are there missing entries in the efficiency table?\n'
            ' - Does a process need a longer Lifetime?'
        )
        logger.error(msg.format(c, r, p, expr))
        raise Exception(msg.format(c, r, p, expr))


def demand_constraint_error_check(supply: Any, r: Region, p: Period, dem: Commodity) -> None:
    # note:  if a pyomo equation simplifies to an int, there are no variables in it, which
    #        is an indicator of a problem
    if isinstance(supply, int):
        msg = (
            "Error: Demand '{}' for ({}, {}) unable to be met by any "
            'technology.\n\tPossible reasons:\n'
            ' - Is the efficiency parameter missing an entry for this demand?\n'
            ' - Does a tech that satisfies this demand need a longer '
            'Lifetime?\n'
        )
        logger.error(msg.format(dem, r, p))
        raise Exception(msg.format(dem, r, p))


def check_singleton_demands(model: TemoaModel) -> None:
    """
    Check for demand commodities that are only produced by a single
    (r, i, t, v, o) sub-process. If such a case is found, the flow variables are
    fixed directly and demand activity and demand constraints are skipped
    as these constraints would otherwise be overdefined and unstable.
    """
    for r, p, dem in model.demand_constraint_rpc:
        upstream_itv = {
            (i, t, v)
            for t, v in model.commodity_up_stream_process.get((r, p, dem), [])
            for i in model.process_inputs_by_output.get((r, p, t, v, dem), [])
        }
        if len(upstream_itv) != 1:
            # not singleton, regular demand constraints
            continue

        # singleton, fix everything and skip demand constraints
        val = value(model.demand[r, p, dem])
        i, t, v = next(iter(upstream_itv))
        model.v_flow_out_annual[r, p, i, t, v, dem].fix(val)
        if t not in model.tech_annual:
            for s, d in cross_product(model.time_season, model.time_of_day):
                dsd = value(model.demand_specific_distribution[r, s, d, dem])
                model.v_flow_out[r, p, s, d, i, t, v, dem].fix(val * dsd)
        model.singleton_demands.add((r, p, dem))


# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def demand_activity_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage, Commodity]]:
    """Index set for DemandActivity. Drops indices for single-tech demands.

    When exactly one non-annual (tech, vintage) pair with a single input serves a
    demand commodity (and no annual techs co-serve it), the flow variables are fixed
    directly and DAC indices are omitted.
    """
    return {
        (r, p, s, d, t, v, dem)
        for r, p, dem in model.demand_constraint_rpc
        if (r, p, dem) not in model.singleton_demands
        for t, v in model.commodity_up_stream_process[r, p, dem]
        if t not in model.tech_annual
        for s in model.time_season
        for d in model.time_of_day
    }


def commodity_balance_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Commodity]]:
    # Generate indices only for those commodities that are produced by
    # technologies with varying output at the time slice level.
    return {
        (r, p, s, d, c)
        for r, p, c in model.commodity_balance_rpc
        # r in this line includes interregional transfer combinations (not needed).
        if r in model.regions  # this line ensures only the regions are included.
        and c not in model.commodity_annual
        for s in model.time_season
        for d in model.time_of_day
    }


def annual_commodity_balance_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Commodity]]:
    # Generate indices only for those commodities that are produced by
    # technologies with constant annual output.
    return {
        (r, p, c)
        for r, p, c in model.commodity_balance_rpc
        # r in this line includes interregional transfer combinations (not needed).
        if r in model.regions  # this line ensures only the regions are included.
        and c in model.commodity_annual
    }


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


def demand_constraint(model: TemoaModel, r: Region, p: Period, dem: Commodity) -> ExprLike:
    r"""

    The Demand constraint drives the model.  This constraint ensures that supply
    meets the demand specified by the Demand parameter in all periods,
    by ensuring that the sum of all the annual demand output commodity (:math:`dem`)
    generated by :math:`\textbf{FOA}` across all technologies and vintages
    equals the modeler-specified demand.

    .. math::
       :label: Demand

           \sum_{I, T, V} \textbf{FOA}_{r, p, i, t, v, dem}
           =
           {DEM}_{r, p, dem}

    The per-timeslice distribution of demand across non-annual technologies
    is enforced by the separate :code:`demand_activity_constraint`. In the case of
    a singleton demand, where only one :code:`(r, i, t, v)` sub-process produces the
    demand commodity, the flow variables are fixed directly and demand constraints
    are skipped.

    Note that the validity of this constraint relies on the fact that the
    :math:`C^d` set is distinct from both :math:`C^e` and :math:`C^p`. In other
    words, an end-use demand must only be an end-use demand.  Note that if an output
    could satisfy both an end-use and internal system demand, then the output from
    :math:`\textbf{FO}` and :math:`\textbf{FOA}` would be double counted."""

    if (r, p, dem) in model.singleton_demands:
        return Constraint.Skip

    supply_annual = sum(
        model.v_flow_out_annual[r, p, s_i, s_t, s_v, dem]
        for s_t, s_v in model.commodity_up_stream_process[r, p, dem]
        for s_i in model.process_inputs_by_output[r, p, s_t, s_v, dem]
    )

    demand_constraint_error_check(supply_annual, r, p, dem)

    expr = supply_annual == value(model.demand[r, p, dem])

    return expr


# devnote: no longer needed
def demand_activity_constraint(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
    dem: Commodity,
) -> ExprLike:
    r"""

    For end-use demands, it is unreasonable to let the model arbitrarily shift the
    use of demand technologies across time slices. For instance, if household A buys
    a natural gas furnace while household B buys an electric furnace, then both units
    should be used throughout the year.  Without this constraint, the model might choose
    to only use the electric furnace during the day, and the natural gas furnace during the
    night.

    This constraint ensures that the ratio of a process activity to demand is
    constant for all time slices. In other words, while the model may choose how
    each technology contributes to a demand at the annual level, the time slice
    level distribution of the technology's contribution to the demand is fixed to
    the demand specific distribution.

    .. math::
       :label: DemandActivity

          \sum_{I}
          \textbf{FOA}_{r, p, i, t, v, dem}
        \cdot \text{DSD}_{r, s, d, dem}
       =
          \sum_{I}
          \textbf{FO}_{r, p, s, d, i, t, v, dem}

       \\
       \forall \{r, p, s, d, t, v, dem\} \in \Theta_{\text{DemandActivity}}

    Note that this constraint is unnecessary and therefore skipped for annual
    technologies or singleton demands.
    """

    activity = sum(
        model.v_flow_out[r, p, s, d, s_i, t, v, dem]
        for s_i in model.process_inputs_by_output[r, p, t, v, dem]
    )

    annual_activity = sum(
        model.v_flow_out_annual[r, p, s_i, t, v, dem]
        for s_i in model.process_inputs_by_output[r, p, t, v, dem]
    )

    expr = annual_activity * value(model.demand_specific_distribution[r, s, d, dem]) == activity
    return expr


def commodity_balance_constraint(
    model: TemoaModel, r: Region, p: Period, s: Season, d: TimeOfDay, c: Commodity
) -> ExprLike:
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
    the excess production in the :code:`CommodityBalanceAnnual_constraint`. Note
    that the :code:`tech_flex` set is different from :code:`tech_curtailment` set;
    the latter is technology- rather than commodity-focused and is used in the
    :code:`Capacity_constraint` to track output that is used to produce useful
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

    *process outputs + imports + end of life outputs = process inputs + construction inputs +
    exports + flex waste*

    .. math::
       :label: CommodityBalance

            \begin{aligned}
            &\sum_{I, t \notin T^a, V} \mathbf{FO}_{r, p, s, d, i, t, v, c}
            && \text{(processes outputting commodity)} \\
            &+ SEG_{s,d} \cdot \sum_{I, t \in T^a, V}
            \mathbf{FOA}_{r, p, i, t, v, c}
            && \text{(annual processes outputting commodity)} \\
            &+ \sum_{\text{reg} \neq r, I, t \in T^x, V}
            \mathbf{FIM}_{r - \text{reg}, p, s, d, i, t, v, c}
            && \text{(inter-regional imports of commodity)} \\
            &+ SEG_{s,d} \sum_{T, V} \left ( EOLO_{r, t, v, c} \cdot \textbf{ART}_{r, p, t, v}
            \right )
            && \text{(end-of-life outputs of commodity)} \\
            &\begin{cases}
            &= \text{if } c \notin C^w \\
            &\geq \text{if } c \in C^w \end{cases} \\
            &\sum_{t \in T^s, V, O} \mathbf{FIS}_{r, p, s, d, c, t, v, o}
            && \text{(commodity stored)} \\
            &+ \sum_{t \notin T^s, V, O}
            \frac{\mathbf{FO}_{r, p, s, d, c, t, v, o}}{EFF_{r, c, t, v, o}}
            && \text{(commodity consumed by processes)} \\
            &+ SEG_{s,d} \cdot \sum_{t \in T^a, V, O}
            \frac{\mathbf{FOA}_{r, p, c, t, v, o}}{EFF_{r, c, t, v, o}}
            && \text{(commodity consumed by annual processes)} \\
            &+ \sum_{\text{reg} \neq r, t \in T^x, V, O}
            \mathbf{FEX}_{r - \text{reg}, p, s, d, c, t, v, o}
            && \text{(inter-regional exports of commodity)} \\
            &+ \sum_{I, t \in T^f, V} \mathbf{FLX}_{r, p, s, d, i, t, v, c}
            && \text{(flex wastes of commodity)} \\
            &+ SEG_{s,d} \cdot \sum_{T, V} \left ( CON_{r, c, t, v} \cdot
            \frac{\textbf{NCAP}_{r, t, v}}{LEN_p} \right )
            && \text{(consumed annually by construction inputs)}
            \end{aligned}

            \qquad \forall \{r, p, s, d, c\} \in \Theta_{\text{CommodityBalance}}

    """

    produced = 0
    consumed = 0

    if (r, p, c) in model.commodity_down_stream_process:
        # Only storage techs have a flow in variable
        # For other techs, it would be redundant as in = out / eff
        consumed += sum(
            model.v_flow_in[r, p, s, d, c, s_t, s_v, s_o]
            for s_t, s_v in model.commodity_down_stream_process[r, p, c]
            if s_t in model.tech_storage
            for s_o in model.process_outputs_by_input[r, p, s_t, s_v, c]
        )

        # Into flows
        consumed += sum(
            model.v_flow_out[r, p, s, d, c, s_t, s_v, s_o]
            / get_variable_efficiency(model, r, p, s, d, c, s_t, s_v, s_o)
            for s_t, s_v in model.commodity_down_stream_process[r, p, c]
            if s_t not in model.tech_storage and s_t not in model.tech_annual
            for s_o in model.process_outputs_by_input[r, p, s_t, s_v, c]
        )

        # Into annual flows
        consumed += sum(
            (
                value(model.demand_specific_distribution[r, s, d, s_o])
                if s_o in model.commodity_demand
                else value(model.segment_fraction[s, d])
            )
            * model.v_flow_out_annual[r, p, c, s_t, s_v, s_o]
            / get_variable_efficiency(model, r, p, s, d, c, s_t, s_v, s_o)
            for s_t, s_v in model.commodity_down_stream_process[r, p, c]
            if s_t in model.tech_annual
            for s_o in model.process_outputs_by_input[r, p, s_t, s_v, c]
        )

    if (r, p, c) in model.capacity_consumption_techs:
        # Consumed by building capacity
        # Assume evenly distributed over a year
        consumed += (
            value(model.segment_fraction[s, d])
            * sum(
                value(model.construction_input[r, c, s_t, p]) * model.v_new_capacity[r, s_t, p]
                for s_t in model.capacity_consumption_techs[r, p, c]
            )
            / model.period_length[p]
        )

    if (r, p, c) in model.commodity_up_stream_process:
        # From flows including output from storage
        produced += sum(
            model.v_flow_out[r, p, s, d, s_i, s_t, s_v, c]
            for s_t, s_v in model.commodity_up_stream_process[r, p, c]
            if s_t not in model.tech_annual
            for s_i in model.process_inputs_by_output[r, p, s_t, s_v, c]
        )

        # From annual flows
        produced += value(model.segment_fraction[s, d]) * sum(
            model.v_flow_out_annual[r, p, s_i, s_t, s_v, c]
            for s_t, s_v in model.commodity_up_stream_process[r, p, c]
            if s_t in model.tech_annual
            for s_i in model.process_inputs_by_output[r, p, s_t, s_v, c]
        )

        if c in model.commodity_flex:
            # Wasted by flex flows
            consumed += sum(
                model.v_flex[r, p, s, d, s_i, s_t, s_v, c]
                for s_t, s_v in model.commodity_up_stream_process[r, p, c]
                if s_t not in model.tech_annual and s_t in model.tech_flex
                for s_i in model.process_inputs_by_output[r, p, s_t, s_v, c]
            )
            # Wasted by annual flex flows
            consumed += value(model.segment_fraction[s, d]) * sum(
                model.v_flex_annual[r, p, s_i, s_t, s_v, c]
                for s_t, s_v in model.commodity_up_stream_process[r, p, c]
                if s_t in model.tech_annual and s_t in model.tech_flex
                for s_i in model.process_inputs_by_output[r, p, s_t, s_v, c]
            )

    if (r, p, c) in model.retirement_production_processes:
        # Produced by retiring capacity
        # Assume evenly distributed over a year
        produced += value(model.segment_fraction[s, d]) * sum(
            value(model.end_of_life_output[r, s_t, s_v, c])
            * model.v_annual_retirement[r, p, s_t, s_v]
            for s_t, s_v in model.retirement_production_processes[r, p, c]
        )

    # export of commodity c from region r to other regions
    if (r, p, c) in model.export_regions:
        consumed += sum(
            model.v_flow_out[r + '-' + reg, p, s, d, c, s_t, s_v, S_o]
            / get_variable_efficiency(
                model, cast('Region', r + '-' + reg), p, s, d, c, s_t, s_v, S_o
            )
            for reg, s_t, s_v, S_o in model.export_regions[r, p, c]
            if s_t not in model.tech_annual
        )
        consumed += sum(
            value(model.segment_fraction[s, d])
            * model.v_flow_out_annual[r + '-' + reg, p, c, s_t, s_v, S_o]
            / get_variable_efficiency(
                model, cast('Region', r + '-' + reg), p, s, d, c, s_t, s_v, S_o
            )
            for reg, s_t, s_v, S_o in model.export_regions[r, p, c]
            if s_t in model.tech_annual
        )

    # import of commodity c from other regions into region r
    if (r, p, c) in model.import_regions:
        produced += sum(
            model.v_flow_out[reg + '-' + r, p, s, d, s_i, s_t, s_v, c]
            for reg, s_t, s_v, s_i in model.import_regions[r, p, c]
            if s_t not in model.tech_annual
        )
        produced += sum(
            value(model.segment_fraction[s, d])
            * model.v_flow_out_annual[reg + '-' + r, p, s_i, s_t, s_v, c]
            for reg, s_t, s_v, s_i in model.import_regions[r, p, c]
            if s_t in model.tech_annual
        )

    commodity_balance_constraint_error_check(
        produced,
        consumed,
        r,
        p,
        s,
        d,
        c,
    )

    if c in model.commodity_waste:
        expr = produced >= consumed
    else:
        expr = produced == consumed

    return expr


def annual_commodity_balance_constraint(
    model: TemoaModel, r: Region, p: Period, c: Commodity
) -> ExprLike:
    r"""
    Similar to CommodityBalance_constraint but only balances the supply and demand of the commodity
    at the period level, summing all flows over the period but allowing imbalances at the time slice
    or seasonal level. Applies only to commodities in the :code:`commodity_annual` set.
    """

    produced = 0
    consumed = 0

    if (r, p, c) in model.commodity_down_stream_process:
        # Only storage techs have a flow in variable
        # For other techs, it would be redundant as in = out / eff
        consumed += sum(
            model.v_flow_in[r, p, s_s, s_d, c, s_t, s_v, s_o]
            for s_s in model.time_season
            for s_d in model.time_of_day
            for s_t, s_v in model.commodity_down_stream_process[r, p, c]
            if s_t in model.tech_storage
            for s_o in model.process_outputs_by_input[r, p, s_t, s_v, c]
        )

        consumed += sum(
            model.v_flow_out[r, p, s_s, s_d, c, s_t, s_v, s_o]
            / get_variable_efficiency(model, r, p, s_s, s_d, c, s_t, s_v, s_o)
            for s_s in model.time_season
            for s_d in model.time_of_day
            for s_t, s_v in model.commodity_down_stream_process[r, p, c]
            if s_t not in model.tech_storage and s_t not in model.tech_annual
            for s_o in model.process_outputs_by_input[r, p, s_t, s_v, c]
        )

        consumed += sum(
            model.v_flow_out_annual[r, p, c, s_t, s_v, s_o]
            / value(model.efficiency[r, c, s_t, s_v, s_o])
            for s_t, s_v in model.commodity_down_stream_process[r, p, c]
            if s_t in model.tech_annual
            for s_o in model.process_outputs_by_input[r, p, s_t, s_v, c]
        )

    if (r, p, c) in model.capacity_consumption_techs:
        # Consumed by building capacity
        # Assume evenly distributed over a year
        consumed += (
            sum(
                value(model.construction_input[r, c, s_t, p]) * model.v_new_capacity[r, s_t, p]
                for s_t in model.capacity_consumption_techs[r, p, c]
            )
            / model.period_length[p]
        )

    if (r, p, c) in model.commodity_up_stream_process:
        # Includes output from storage
        produced += sum(
            model.v_flow_out[r, p, s_s, s_d, s_i, s_t, s_v, c]
            for s_s in model.time_season
            for s_d in model.time_of_day
            for s_t, s_v in model.commodity_up_stream_process[r, p, c]
            if s_t not in model.tech_annual
            for s_i in model.process_inputs_by_output[r, p, s_t, s_v, c]
        )

        produced += sum(
            model.v_flow_out_annual[r, p, s_i, s_t, s_v, c]
            for s_t, s_v in model.commodity_up_stream_process[r, p, c]
            if s_t in model.tech_annual
            for s_i in model.process_inputs_by_output[r, p, s_t, s_v, c]
        )

        if c in model.commodity_flex:
            consumed += sum(
                model.v_flex[r, p, s_s, s_d, s_i, s_t, s_v, c]
                for s_s in model.time_season
                for s_d in model.time_of_day
                for s_t, s_v in model.commodity_up_stream_process[r, p, c]
                if s_t not in model.tech_annual and s_t in model.tech_flex
                for s_i in model.process_inputs_by_output[r, p, s_t, s_v, c]
            )
            consumed += sum(
                model.v_flex_annual[r, p, s_i, s_t, s_v, c]
                for s_t, s_v in model.commodity_up_stream_process[r, p, c]
                if s_t in model.tech_flex and s_t in model.tech_annual
                for s_i in model.process_inputs_by_output[r, p, s_t, s_v, c]
            )

    if (r, p, c) in model.retirement_production_processes:
        # Produced by retiring capacity
        # Assume evenly distributed over a year
        produced += sum(
            value(model.end_of_life_output[r, s_t, s_v, c])
            * model.v_annual_retirement[r, p, s_t, s_v]
            for s_t, s_v in model.retirement_production_processes[r, p, c]
        )

    # export of commodity c from region r to other regions
    if (r, p, c) in model.export_regions:
        consumed += sum(
            model.v_flow_out[cast('Region', r + '-' + s_r), p, s_s, s_d, c, s_t, s_v, s_o]
            / get_variable_efficiency(
                model, cast('Region', r + '-' + s_r), p, s_s, s_d, c, s_t, s_v, s_o
            )
            for s_s in model.time_season
            for s_d in model.time_of_day
            for s_r, s_t, s_v, s_o in model.export_regions[r, p, c]
            if s_t not in model.tech_annual
        )
        consumed += sum(
            model.v_flow_out_annual[cast('Region', r + '-' + s_r), p, c, s_t, s_v, s_o]
            / model.efficiency[cast('Region', r + '-' + s_r), c, s_t, s_v, s_o]
            for s_r, s_t, s_v, s_o in model.export_regions[r, p, c]
            if s_t in model.tech_annual
        )

    # import of commodity c from other regions into region r
    if (r, p, c) in model.import_regions:
        produced += sum(
            model.v_flow_out[cast('Region', s_r + '-' + r), p, s_s, S_d, s_i, s_t, s_v, c]
            for s_s in model.time_season
            for S_d in model.time_of_day
            for s_r, s_t, s_v, s_i in model.import_regions[r, p, c]
            if s_t not in model.tech_annual
        )
        produced += sum(
            model.v_flow_out_annual[cast('Region', s_r + '-' + r), p, s_i, s_t, s_v, c]
            for s_r, s_t, s_v, s_i in model.import_regions[r, p, c]
            if s_t in model.tech_annual
        )

    annual_commodity_balance_constraint_error_check(
        produced,
        consumed,
        r,
        p,
        c,
    )

    if c in model.commodity_waste:
        expr = produced >= consumed
    else:
        expr = produced == consumed

    return expr


# ============================================================================
# PRE-COMPUTATION FUNCTIONS
# ============================================================================


def create_technology_and_commodity_sets(model: TemoaModel) -> None:
    """
    Populates technology and commodity subset definitions based on their roles
    (e.g., demand, flexible) identified from the efficiency parameter.

    This function iterates through the `efficiency` parameter to identify and
    add technologies and commodities to special `Pyomo.Set` objects on the model.

    Populates:
        - M.commodity_flex: Commodities that can be over-produced.
        - M.tech_demand: Technologies that directly satisfy an end-use demand.
    """
    logger.debug('Creating technology and commodity subsets.')
    for _r, _i, t, _v, o in model.efficiency.sparse_keys():
        if t in model.tech_flex and o not in model.commodity_flex:
            model.commodity_flex.add(o)

        if o in model.commodity_demand and t not in model.tech_demand:
            model.tech_demand.add(t)


def create_demands(model: TemoaModel) -> None:
    """
    Steps to create the demand distributions
    1. Use Demand keys to ensure that all demands in commodity_demand are used
    2. Find any slices not set in DemandDefaultDistribution, and set them based
    on the associated segment_fraction slice.
    3. Validate that the DemandDefaultDistribution sums to 1.
    4. Find any per-demand demand_specific_distribution values not set, and set
    them from DemandDefaultDistribution.  Note that this only sets a
    distribution for an end-use demand if the user has *not* specified _any_
    anything for that end-use demand.  Thus, it is up to the user to fully
    specify the distribution, or not.  No in-between.
     5. Validate that the per-demand distributions sum to 1.
    """
    logger.debug('Started creating demand distributions in CreateDemands()')

    # Step 0: some setup for a couple of reusable items
    # Get the nth element from the tuple (r, p, s, d, dem))
    # So we only have to update these indices in one place if they change
    demand_specific_distribution_region = iget(0)
    demand_specific_distributon_period = iget(1)
    demand_specific_distributon_dem = iget(4)

    # Step 1: Check if any demand commodities are going unused
    used_dems = {dem for _r, _p, dem in model.demand.sparse_keys()}
    unused_dems = sorted(model.commodity_demand.difference(used_dems))
    if unused_dems:
        for dem in unused_dems:
            msg = "Warning: Demand '{}' is unused\n"
            logger.warning(msg.format(dem))
            sys.stderr.write(msg.format(dem))

    # devnote: DDD just clones segment_fraction. Unless we want to specify it in the database,
    #          makes sense to just use segment_fraction directly
    # Step 2: Build the demand default distribution (= segment_fraction)
    # DDD = M.DemandDefaultDistribution  # Shorter, for us lazy programmer types
    # unset_defaults = set(M.segment_fraction.sparse_keys())
    # unset_defaults.difference_update(DDD.sparse_keys())
    # if unset_defaults:
    # Some hackery because Pyomo thinks that this Param is constructed.
    # However, in our view, it is not yet, because we're specifically
    # targeting values that have not yet been constructed, that we know are
    # valid, and that we will need.
    # DDD._constructed = False
    # for tslice in unset_defaults:
    #     DDD[tslice] = M.segment_fraction[tslice]  # DDD._constructed = True

    # Step 3: Check that DDD sums to 1
    # devnote: this seems redundant to the segment_fraction sum to 1 check.
    # total = sum(i for i in DDD.values())
    # if abs(value(total) - 1.0) > 0.001:
    #     # We can't explicitly test for "!= 1.0" because of incremental rounding
    #     # errors associated with the specification of demand shares by time slice,
    #     # but we check to make sure it is within the specified tolerance.

    #     key_padding = max(map(get_str_padding, DDD.sparse_keys()))

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
    demand_specific_distribution = model.demand_specific_distribution

    demands_specified = set(
        map(
            demand_specific_distributon_dem,
            (i for i in demand_specific_distribution.sparse_keys()),
        )
    )
    unset_demand_distributions = used_dems.difference(
        demands_specified
    )  # the demands not mentioned in DSD *at all*

    if unset_demand_distributions:
        unset_distributions = set(
            cross_product(
                model.regions,
                model.time_optimize,
                model.time_season,
                model.time_of_day,
                unset_demand_distributions,
            )
        )
        for r, p, s, d, dem in unset_distributions:
            demand_specific_distribution[r, p, s, d, dem] = value(
                model.segment_fraction[s, d]
            )  # DSD._constructed = True

    # Step 5: A final "sum to 1" check for all DSD members (which now should be everything)
    #         Also check that all keys are made...  The demand distro should be supported
    #         by the full set of (r, p, dem) keys because it is an equality constraint
    #         and we need to ensure even the zeros are passed in
    used_rp_dems = {(r, p, dem) for r, p, dem in model.demand.sparse_keys()}
    for r, p, dem in used_rp_dems:
        expected_key_length = len(model.time_season) * len(model.time_of_day)
        keys = [
            k
            for k in demand_specific_distribution.sparse_keys()
            if demand_specific_distribution_region(k) == r
            and demand_specific_distributon_period(k) == p
            and demand_specific_distributon_dem(k) == dem
        ]
        if len(keys) != expected_key_length:
            # this could be very slow but only calls when there's a problem
            missing = {
                (s, d)
                for s in model.time_season
                for d in model.time_of_day
                if (r, p, s, d, dem) not in keys
            }
            logger.info(
                'Missing some time slices for Demand Specific Distribution %s: %s',
                (r, p, dem),
                missing,
            )
        total = sum(value(demand_specific_distribution[i]) for i in keys)
        if abs(value(total) - 1.0) > 0.001:
            # We can't explicitly test for "!= 1.0" because of incremental rounding
            # errors associated with the specification of demand shares by time slice,
            # but we check to make sure it is within the specified tolerance.
            def get_str_padding(obj: Any) -> int:
                return len(str(obj))

            key_padding = max(map(get_str_padding, keys))

            fmt = '%%-%ds = %%s' % key_padding  # noqa: UP031
            # Works out to something like "%-25s = %s"

            items_list: list[tuple[Any, Any]] = sorted(
                [(k, value(demand_specific_distribution[k])) for k in keys]
            )
            items = '\n   '.join(fmt % (str(k), v) for k, v in items_list)
            msg = (
                'The values of the demand_specific_distribution parameter do not '
                'sum to 1 for {}. The demand_specific_distribution specifies how end-use '
                'demands are distributed per time-slice (i.e., time_season, '
                'time_of_day). Within each region, period, end-use demand, then, the distribution '
                'must total to 1.\n\n Demand-specific distribution in error: '
                ' \n   {}\n\tsum = {}'
            )
            logger.error(msg.format((r, p, dem), items, total))
            raise ValueError(msg.format((r, p, dem), items, total))

    logger.debug('Finished creating demand distributions')
