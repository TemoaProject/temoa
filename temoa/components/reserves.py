# temoa/components/reserves.py
"""
Defines the planning reserve margin and shared reserve helpers of the Temoa model.

Each planning reserve product (``reserve_name``, region-group, tech-group) requires
credited capacity or available output to exceed a proxy demand in every time slice,
using either the static or dynamic formulation selected by the ``type`` column.
The same reserve name may be repeated over several region-groups and tech-groups,
in which case they share that name's credits.
Reserve margins are the only constraints in Temoa that, given a region group,
automatically pull in exchange processes connecting a region inside the group
to a region outside it -- see `initialize_reserve_groups`.

The operating reserve margin lives in the unit commitment extension
(`temoa.extensions.unit_commitment.components.operating_reserves`) and reuses the
helpers here.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from pyomo.environ import Constraint, quicksum, value

from temoa.components import geography
from temoa.components.capacity import gather_group_active_processes
from temoa.types.core_types import ReserveMarginType

from .utils import get_available_output, get_variable_efficiency

if TYPE_CHECKING:
    from pyomo.core import Param

    from temoa.core.model import TemoaModel
    from temoa.types import ExprLike, ReserveProcessesDict
    from temoa.types.core_types import (
        Period,
        Region,
        ReserveName,
        Season,
        Technology,
        TimeOfDay,
        Vintage,
    )

logger = getLogger(__name__)

# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def planning_reserve_indices(
    model: TemoaModel,
) -> set[tuple[ReserveName, Region, Technology, Period, Season, TimeOfDay]]:
    return {
        (prm, r_g, t_g, p, s, d)
        for prm, r_g, t_g, p in model.planning_reserve_processes
        for s in model.time_season
        for d in model.time_of_day
    }


# ============================================================================
# INITIALIZATION FUNCTIONS
# ============================================================================


def initialize_reserve_groups(
    model: TemoaModel,
    margin: Param,
    processes: ReserveProcessesDict,
) -> None:
    """Map each reserve product in ``margin`` to its groups and contributing processes.

    A single reserve name may apply to several region-group/tech-group pairs
    (e.g., the same product defined separately in different regions).

    Resolves the group's base regions via `geography.gather_group_regions`, then
    appends any exchange region-pair (`r1-r2`) with exactly one endpoint inside
    the group, so exchange processes crossing the group boundary are counted as
    contributors. This is the only place in Temoa where a group constraint
    auto-includes connected exchange regions; the corresponding import/export
    sign handling is applied in `reserve_margin_proxy_demand`.

    Periods with no contributing processes are omitted.
    """
    for name, r_g, t_g in margin.sparse_keys():
        # Gather boundary-crossing exchange regions and add to the group
        _r_g = r_g
        regions = geography.gather_group_regions(model, r_g)
        for r1r2 in model.regional_indices:
            if r1r2 in regions or '-' not in r1r2:
                continue
            r1, r2 = r1r2.split('-')
            if (r1 in regions) != (r2 in regions):
                _r_g += '+' + r1r2

        # Gather valid processes
        has_contributors = False
        for p in model.time_optimize:
            valid_rtv = {
                (r, t, v)
                for r, t in gather_group_active_processes(model, _r_g, p, t_g)
                for v in model.process_vintages.get((r, p, t), set())
            }
            if valid_rtv:
                processes[name, r_g, t_g, p] = valid_rtv
                has_contributors = True
            else:
                logger.info('Reserve %s has no contributors in period %s', (name, r_g, t_g), p)
        if not has_contributors:
            logger.warning('Reserve has no contributors in any period: %s', (name, r_g, t_g))


def initialize_planning_reserve_margins(model: TemoaModel) -> None:
    initialize_reserve_groups(
        model,
        model.planning_reserve_margin,
        model.planning_reserve_processes,
    )
    for prm, r_g, t_g in model.planning_reserve_margin.sparse_keys():
        for p in model.time_optimize:
            if not any(
                model.planning_reserve_credit[prm, _r, t]
                for _r, t, _v in model.planning_reserve_processes[prm, r_g, t_g, p]
            ):
                logger.warning(
                    'No credits available for reserve %s in region group %s and period %s',
                    prm,
                    r_g,
                    p,
                )


# ============================================================================
# HELPER FUNCTIONS FOR CONSTRAINT LOGIC
# ============================================================================


def _into_region(model: TemoaModel, r: Region, t: Technology, regions: set[Region]) -> int:
    """
    Returns +1 if not an exchange tech or is an exchange tech importing into the region group.
    """
    if t not in model.tech_exchange:
        return 1
    r1, r2 = r.split('-')
    if r2 in regions and r1 not in regions:
        return 1
    return 0


def _out_of_region(model: TemoaModel, r: Region, t: Technology, regions: set[Region]) -> int:
    """
    Returns +1 if and only if is an exchange tech exporting out of the region group.
    """
    if t not in model.tech_exchange:
        return 0
    r1, r2 = r.split('-')
    if r1 in regions and r2 not in regions:
        return 1
    return 0


def reserve_margin_proxy_demand(
    model: TemoaModel,
    processes: set[tuple[Region, Technology, Vintage]],
    r_g: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
) -> tuple[ExprLike, dict[tuple[Region, Technology, Vintage], ExprLike]]:
    r"""In Temoa, demand for a particular commodity (e.g., electricity) may be endogenous to
    decisions in the model. So, we estimate demand as the net production of processes
    in the reserve group, :math:`\Theta^{res}_{n,r_g,t_g,p}`. This provides the RHS demand for
    both reserve constraints. Also returns the net contribution of each process to that
    demand, which the operating reserve margin reuses for activity credits.

    The region group :math:`r_g` indicates the regions in which demand is met, and the
    tech group :math:`t_g` indicates which technologies supply the demanded commodity. The
    technology group should include all technologies that produce, store, or import/export
    the commodity of interest but **not** the technologies that demand it downstream.

    .. note::
        In Temoa, we are not reasonably able to disaggregate the **available** output of a
        process for individual commodities when that process outputs multiple commodities. As a
        result, a reserve margin constraint cannot be applied to a single commodity where supplying
        processes output multiple different commodities (e.g., if a co-generation plant outputs both
        heat and electricity, the heat will be included in the equations). This can be avoided by
        adding an intermediate "dummy" process that throughputs only the output of interest and then
        adding this dummy process to the tech group instead of the original process, but this
        requires careful cloning of other technoeconomic parameters so the reserve contributions
        remain the same.

    .. math::
        :label: reserve_margin_proxy_demand

        \begin{aligned}
            D^{proxy}_{r_g,p,s,d} =&
                \sum_{\substack{(r,t,v) \in \Theta^{res} \setminus T^a \\ \uparrow_{r,r_g},\, I, O}}
                \mathbf{FO}_{r, p, s, d, i, t, v, o}
                && \text{(non-annual production and imports)} \\
            &+ \sum_{\substack{(r,t,v) \in \Theta^{res} \cap T^a \\ \uparrow_{r,r_g},\, I, O}}
                \begin{cases} DSD_{r,s,d,o} & o \in C^d \\ SEG_{s,d} & \text{otherwise}
                \end{cases} \cdot \mathbf{FOA}_{r, p, i, t, v, o}
                && \text{(annual production and imports)} \\
            &- \sum_{(r,t,v) \in \Theta^{res} \cap T^s,\, I, O}
                \mathbf{FI}_{r, p, s, d, i, t, v, o}
                && \text{(storage inputs)} \\
            &- \sum_{\substack{(r,t,v) \in \Theta^{res} \cap T^x \setminus T^a \\
                \downarrow_{r,r_g},\, I, O}}
                \mathbf{FO}_{r, p, s, d, i, t, v, o} / EFF_{r,p,s,d,i,t,v,o}
                && \text{(non-annual exports)} \\
            &- \sum_{\substack{(r,t,v) \in \Theta^{res} \cap T^x \cap T^a \\
                \downarrow_{r,r_g},\, I, O}}
                \begin{cases} DSD_{r,s,d,o} & o \in C^d \\ SEG_{s,d} & \text{otherwise}
                \end{cases} \cdot \mathbf{FOA}_{r, p, i, t, v, o} / EFF_{r,p,i,t,v,o}
                && \text{(annual exports)}
        \end{aligned}

    where :math:`\uparrow_{r,r_g}` selects non-exchange processes and exchange imports
    (:math:`r_2 \in r_g,\ r_1 \notin r_g`), and :math:`\downarrow_{r,r_g}` selects exchange
    exports (:math:`r_1 \in r_g,\ r_2 \notin r_g`).
    :math:`\Theta^{res} = \Theta^{res}_{n,r_g,t_g,p}`
    is the set of all :math:`(r,t,v)` processes contributing to this reserve margin in this period.
    """
    regions = geography.gather_group_regions(model, r_g)

    activity_rtv: dict[tuple[Region, Technology, Vintage], ExprLike] = dict.fromkeys(processes, 0)

    for r, t, v in processes:
        # Non-annual activity
        if t not in model.tech_annual and _into_region(model, r, t, regions):
            activity_rtv[r, t, v] += quicksum(
                model.v_flow_out[r, p, s, d, i, t, v, o]
                for i in model.process_inputs[r, p, t, v]
                for o in model.process_outputs_by_input[r, p, t, v, i]
            )

        # Annual activity (could also just be a demand tech)
        if t in model.tech_annual and _into_region(model, r, t, regions):
            activity_rtv[r, t, v] += quicksum(
                (
                    value(model.demand_specific_distribution[r, p, s, d, o])
                    if o in model.commodity_demand
                    else value(model.segment_fraction[s, d])
                )
                * model.v_flow_out_annual[r, p, i, t, v, o]
                for i in model.process_inputs[r, p, t, v]
                for o in model.process_outputs_by_input[r, p, t, v, i]
            )

        # We must take into account flows into storage technologies.
        # Flows into storage technologies need to be subtracted from the
        # load calculation. Flow_out already summed above.
        if t in model.tech_storage and t not in model.tech_exchange:
            activity_rtv[r, t, v] -= quicksum(
                model.v_flow_in[r, p, s, d, i, t, v, o]
                for i in model.process_inputs[r, p, t, v]
                for o in model.process_outputs_by_input[r, p, t, v, i]
            )

        # Subtract exchange exports
        # Non-annual exports
        if t not in model.tech_annual and _out_of_region(model, r, t, regions):
            activity_rtv[r, t, v] -= quicksum(
                model.v_flow_out[r, p, s, d, i, t, v, o]
                / get_variable_efficiency(model, r, p, s, d, i, t, v, o)
                for i in model.process_inputs[r, p, t, v]
                for o in model.process_outputs_by_input[r, p, t, v, i]
            )
        # Annual exports (could feed a demand)
        if t in model.tech_annual and _out_of_region(model, r, t, regions):
            activity_rtv[r, t, v] -= quicksum(
                (
                    value(model.demand_specific_distribution[r, p, s, d, o])
                    if o in model.commodity_demand
                    else value(model.segment_fraction[s, d])
                )
                * model.v_flow_out_annual[r, p, i, t, v, o]
                / value(model.efficiency[r, i, t, v, o])
                for i in model.process_inputs[r, p, t, v]
                for o in model.process_outputs_by_input[r, p, t, v, i]
            )

    demand = quicksum(activity_rtv.values())
    return demand, activity_rtv


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


def planning_reserve_margin_constraint(
    model: TemoaModel,
    prm: ReserveName,
    r_g: Region,
    t_g: Technology,
    p: Period,
    s: Season,
    d: TimeOfDay,
) -> Constraint:
    r"""
    During each period :math:`p`, the sum of capacity values of all reserve
    technologies, weighted by their planning reserve credit, must exceed the
    proxy demand of reserve product :math:`n` by :math:`PRM_{n,r_g,t_g}` in every
    time slice, where :math:`r_g` and :math:`t_g` are the product's region-group
    and tech-group. Several products may be defined on the same groups.

    The credit formulation is selected per reserve product by the :code:`type` column of
    :code:`planning_reserve_margin` (:code:`planning_reserve_type` in the model), either
    :code:`static` (:func:`~temoa.components.reserves._planning_reserve_margin_static`,
    the default) or :code:`dynamic`
    (:func:`~temoa.components.reserves._planning_reserve_margin_dynamic`).
    Static credits a fraction of installed capacity in every time slice; dynamic credits a
    fraction of the output actually available in each time slice.
    """
    reserve_type = model.planning_reserve_type[prm, r_g, t_g]
    if reserve_type == ReserveMarginType.DYNAMIC:
        return _planning_reserve_margin_dynamic(model, prm, r_g, t_g, p, s, d)
    elif reserve_type == ReserveMarginType.STATIC:
        return _planning_reserve_margin_static(model, prm, r_g, t_g, p, s, d)
    else:
        msg = (
            f"Unknown planning reserve type '{reserve_type}' for reserve product "
            f"'{prm}' in region-group '{r_g}' and tech-group '{t_g}'."
        )
        logger.error(msg)
        raise ValueError(msg)


def _planning_reserve_margin_static(
    model: TemoaModel,
    prm: ReserveName,
    r_g: Region,
    t_g: Technology,
    p: Period,
    s: Season,
    d: TimeOfDay,
) -> Constraint:
    r"""
    In the static formulation, during each period :math:`p`, the sum of capacity
    values of all reserve technologies, weighted by their planning reserve credit,
    must exceed the reserve product's proxy demand by :math:`PRM_{n,r_g,t_g}` in every
    time slice.

    This credit represents the expected availability of nameplate capacity
    during binding demand conditions and is usually determined from stochastic
    modelling of demand/supply scenarios. A credit of 1 indicates the technology is
    expected to be able to output its full nameplate capacity at high demand,
    while 0 indicates it offers no reliable capacity. Technologies in the tech
    group are used to calculate the proxy demand and so must include these zero
    credit processes as well.

    **The default credit is 0** if not set (i.e., we assume technologies offer
    no reserve by default).

    For exchange technologies (e.g., inter-regional transmission), reserve
    contributions are added for import capacity into the region-group but the same
    contribution is *subtracted* for export capacity out of it.

    .. math::
        :label: planning_reserve_margin_static

        \begin{aligned}
            &\sum_{(r,t,v) \in \Theta^{res} \setminus T^x}
                PRC_{n,t} \cdot \mathbf{CAP}_{r,p,t,v} \cdot SEG_{s,d} \cdot C2A_{r,t}
                && \text{(production capacity, includes storage)} \\
            &+ \sum_{(r,t,v) \in \Theta^{res} \cap T^x}
                \sigma_{r,r_g} \cdot PRC_{n,t} \cdot \mathbf{CAP}_{r,p,t,v}
                \cdot SEG_{s,d} \cdot C2A_{r,t}
                && \text{(net import capacity)} \\
            &\geq D^{proxy}_{r_g,p,s,d} \cdot (1 + PRM_{n,r_g,t_g}) \\
            &\forall \{n, r_g, t_g, p, s, d\} \in \Theta_{\text{PlanningReserveMargin}}
        \end{aligned}

    where :math:`\sigma_{r,r_g} = +1` for an exchange process delivering into
    region-group :math:`r_g` and :math:`-1` for one delivering out of it,
    :math:`\Theta^{res} = \Theta^{res}_{n,r_g,t_g,p}` is the set of processes contributing to
    product :math:`{n,r_g,t_g}` in period :math:`p`, and :math:`D^{proxy}_{n,r_g,t_g,p,s,d}` is the
    product's proxy demand defined in :eq:`reserve_margin_proxy_demand`.
    """
    processes = model.planning_reserve_processes[prm, r_g, t_g, p]

    available = quicksum(
        value(model.planning_reserve_credit[prm, r, t])
        * model.v_capacity[r, p, t, v]
        * value(model.capacity_to_activity[r, t])
        * value(model.segment_fraction[s, d])
        for r, t, v in processes
        if t not in model.tech_uncap and t not in model.tech_exchange
    )

    # Add credited imports into the group, subtract credited exports out of it
    regions = geography.gather_group_regions(model, r_g)
    for r1r2, t, v in processes:
        if t not in model.tech_exchange:
            continue

        _available = (
            value(model.planning_reserve_credit[prm, r1r2, t])
            * model.v_capacity[r1r2, p, t, v]
            * value(model.capacity_to_activity[r1r2, t])
            * value(model.segment_fraction[s, d])
        )

        r1, r2 = r1r2.split('-')
        if r2 in regions and r1 not in regions:
            available += _available
        elif r1 in regions and r2 not in regions:
            available -= _available

    demand, _ = reserve_margin_proxy_demand(model, processes, r_g, p, s, d)
    return available >= demand * (1 + value(model.planning_reserve_margin[prm, r_g, t_g]))


def _planning_reserve_margin_dynamic(
    model: TemoaModel,
    prm: ReserveName,
    r_g: Region,
    t_g: Technology,
    p: Period,
    s: Season,
    d: TimeOfDay,
) -> Constraint:
    r"""
    A dynamic alternative to the static planning reserve margin constraint. Capacity values are
    calculated from process output availability in each time slice, accounting for capacity
    factors, unit commitment (if the extension is enabled), and the planning reserve credit
    which may derate contributions for, for example, forced outage rates. A credit of 1
    indicates no derating while a credit of zero indicates zero dependable output.
    The tech group :math:`t_g` should include technologies with no credit as these are still
    used to calculate the proxy demand for the reserve.

    **The default credit is 0** if not set (i.e., we assume technologies offer
    no reserve by default).

    For exchange technologies (e.g., inter-regional transmission), reserve
    contributions are added for available imports into the region-group but *subtracted*
    for available exports out of it.

    The availability of storage technologies is a non-trivial problem as it depends on state
    of charge, which has a temporal dependency (i.e., if we consider a storage technology to
    contribute reserve in time t can it also contribute in time t+1?). In this implementation,
    we let storage contribute only what it actually outputs (net) in each time slice, as a
    conservative but tractable approach (use it or lose it).

    .. math::
        :label: planning_reserve_margin_dynamic

        \begin{aligned}
            &\sum_{(r,t,v) \in \Theta^{res} \setminus T^x \setminus T^s}
                CFP_{r,s,d,t,v} \cdot PRC_{n,t} \cdot \mathbf{CAP}_{r,p,t,v}
                \cdot SEG_{s,d} \cdot C2A_{r,t}
                && \text{(firm production)} \\
            &+ \sum_{(r,t,v) \in \Theta^{res} \cap T^s,\, I, O}
                \left( \mathbf{FO}_{r,p,s,d,i,t,v,o} - \mathbf{FI}_{r,p,s,d,i,t,v,o} \right)
                \cdot PRC_{n,t}
                && \text{(net storage output)} \\
            &+ \sum_{(r,t,v) \in \Theta^{res} \cap T^x}
                \sigma_{r,r_g} \cdot CFP_{r,s,d,t,v} \cdot PRC_{n,t}
                \cdot \mathbf{CAP}_{r,p,t,v} \cdot SEG_{s,d} \cdot C2A_{r,t}
                && \text{(net firm imports)} \\
            &\geq D^{proxy}_{r_g,p,s,d} \cdot (1 + PRM_{n,r_g,t_g}) \\
            &\forall \{n, r_g, t_g, p, s, d\} \in \Theta_{\text{PlanningReserveMargin}}
        \end{aligned}

    where :math:`\sigma_{r,r_g} = +1` for an exchange process delivering into
    region-group :math:`r_g` and :math:`-1` for one delivering out of it,
    :math:`\Theta^{res} = \Theta^{res}_{n,r_g,t_g,p}` is the set of processes contributing to
    product :math:`{n,r_g,t_g}` in period :math:`p`, and :math:`D^{proxy}_{n,r_g,t_g,p,s,d}` is the
    product's proxy demand defined in :eq:`reserve_margin_proxy_demand`.
    """
    processes = model.planning_reserve_processes[prm, r_g, t_g, p]

    # Everything but storage and exchange techs
    # Derated available generation
    available = quicksum(
        get_available_output(model, r, p, s, d, t, v)
        * value(model.planning_reserve_credit[prm, r, t])
        for (r, t, v) in processes
        if not (t in model.tech_uncap or t in model.tech_storage or t in model.tech_exchange)
    )

    # Storage
    # Derated net output flow
    available += quicksum(
        model.v_flow_out[r, p, s, d, i, t, v, o] * value(model.planning_reserve_credit[prm, r, t])
        for (r, t, v) in processes
        if t in model.tech_storage and t not in model.tech_exchange
        for i in model.process_inputs[r, p, t, v]
        for o in model.process_outputs_by_input[r, p, t, v, i]
    )
    available -= quicksum(
        model.v_flow_in[r, p, s, d, i, t, v, o] * value(model.planning_reserve_credit[prm, r, t])
        for (r, t, v) in processes
        if t in model.tech_storage and t not in model.tech_exchange
        for i in model.process_inputs[r, p, t, v]
        for o in model.process_outputs_by_input[r, p, t, v, i]
    )

    # Exchange technologies
    # Add available imports into the group, subtract available exports out of it
    regions = geography.gather_group_regions(model, r_g)
    for r1r2, t, v in processes:
        if t not in model.tech_exchange:
            continue

        _available = get_available_output(model, r1r2, p, s, d, t, v) * value(
            model.planning_reserve_credit[prm, r1r2, t]
        )

        r1, r2 = r1r2.split('-')
        if r2 in regions and r1 not in regions:
            available += _available
        elif r1 in regions and r2 not in regions:
            available -= _available

    demand, _ = reserve_margin_proxy_demand(model, processes, r_g, p, s, d)
    return available >= demand * (1 + value(model.planning_reserve_margin[prm, r_g, t_g]))
