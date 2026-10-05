"""
Operating reserve margins for the unit commitment extension.

Each operating reserve product (``reserve_name``) applies to one region-group and
tech-group and requires that credited reserve in every time slice exceeds the
group's proxy demand (see :func:`temoa.components.reserves.reserve_margin_proxy_demand`)
by a margin. Reserve is credited from three sources, each weighted by a per-product,
per-technology credit:

  - current generation (``activity_credit``)
  - headroom on online units (``online_credit``)
  - offline unit commitment units that could start (``offline_credit``)

Storage contributions must also be sustainable from the current state of charge
for the product's ``sustain_hours``.

These products are registered by the unit_commitment extension, but technologies
need not themselves be subject to unit commitment: a non-UC technology is simply
treated as always fully online, so its online headroom is just unused installed
capacity. Exchange technologies' ``online_credit`` is constrained equal and opposite
across the pair's two directional entries (outgoing = -incoming; see
:func:`operating_reserve_online_exchange_symmetry_constraint`), so
:func:`operating_reserve_margin_constraint` only ever sums the incoming entry, which
is already correctly signed for either direction of reserve flow.
A process may contribute to several products at once; products are assumed not to
be called on simultaneously.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from pyomo.environ import quicksum, value

from temoa.components import geography
from temoa.components.reserves import initialize_reserve_groups, reserve_margin_proxy_demand
from temoa.components.utils import get_available_output, get_variable_efficiency
from temoa.extensions.unit_commitment.components.commitment import _total_units

if TYPE_CHECKING:
    from pyomo.environ import Expression, NumericValue

    from temoa.extensions.unit_commitment.core.model import UnitCommitmentModel
    from temoa.types import ExprLike
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
# INITIALIZATION
# ============================================================================


def initialize_operating_reserve_margins(model: UnitCommitmentModel) -> None:
    initialize_reserve_groups(
        model,
        model.operating_reserve_margin,
        model.operating_reserve_processes,
    )
    for (orm, r_g, t_g, p), processes in model.operating_reserve_processes.items():
        if not any(
            (orm, r, t) in model.operating_reserve_activity_credit
            or (orm, r, t) in model.operating_reserve_online_credit
            or (orm, r, t) in model.operating_reserve_offline_credit
            for r, t, _v in processes
        ):
            logger.warning('No credits defined for reserve %s', (orm, r_g, t_g, p))


def has_activity_credit(
    model: UnitCommitmentModel, orm: ReserveName, r: Region, t: Technology
) -> bool:
    return (orm, r, t) in model.operating_reserve_activity_credit


def has_online_credit(
    model: UnitCommitmentModel, orm: ReserveName, r: Region, t: Technology
) -> bool:
    return (orm, r, t) in model.operating_reserve_online_credit


def has_offline_credit(
    model: UnitCommitmentModel, orm: ReserveName, r: Region, t: Technology
) -> bool:
    # Only unit commitment techs have offline units
    uc_tech = (r, t) in model.uc_unit_capacity
    has_credit = (orm, r, t) in model.operating_reserve_offline_credit
    return uc_tech and has_credit


def _sustain_hours(
    model: UnitCommitmentModel, orm: ReserveName, r_g: Region, t_g: Technology
) -> float | NumericValue:
    if (orm, r_g, t_g) not in model.operating_reserve_sustain_hours:
        return 0.0
    return value(model.operating_reserve_sustain_hours[orm, r_g, t_g])


# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def operating_reserve_indices(
    model: UnitCommitmentModel,
) -> set[tuple[ReserveName, Region, Technology, Period, Season, TimeOfDay]]:
    return {
        (orm, r_g, t_g, p, s, d)
        for orm, r_g, t_g, p in model.operating_reserve_processes
        for s in model.time_season
        for d in model.time_of_day
    }


def operating_reserve_online_indices(
    model: UnitCommitmentModel,
) -> set[tuple[ReserveName, Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    return {
        (orm, r, p, s, d, t, v)
        for (orm, _r_g, _t_g, p), processes in model.operating_reserve_processes.items()
        for r, t, v in processes
        if has_online_credit(model, orm, r, t)
        for s in model.time_season
        for d in model.time_of_day
    }


def operating_reserve_storage_indices(
    model: UnitCommitmentModel,
) -> set[
    tuple[ReserveName, Region, Technology, Region, Period, Season, TimeOfDay, Technology, Vintage]
]:
    return {
        (orm, r_g, t_g, r, p, s, d, t, v)
        for (orm, r_g, t_g, p), processes in model.operating_reserve_processes.items()
        if _sustain_hours(model, orm, r_g, t_g) > 0
        for r, t, v in processes
        if t in model.tech_storage
        if (
            has_activity_credit(model, orm, r, t)
            or has_online_credit(model, orm, r, t)
            or has_offline_credit(model, orm, r, t)
        )
        for s in model.time_season
        for d in model.time_of_day
    }


def operating_reserve_online_exchange_indices(
    model: UnitCommitmentModel,
) -> set[tuple[ReserveName, Region, Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    """One entry per credited exchange link (r_e < r_i), not per direction."""
    return {
        (orm, r_e, r_i, p, s, d, t, v)
        for orm, r, p, s, d, t, v in model.operating_reserve_online_nrpsdtv
        if t in model.tech_exchange
        for r_e, r_i in (r.split('-'),)
        if (orm, r_i + '-' + r_e, p, s, d, t, v) in model.operating_reserve_online_nrpsdtv
        if r_e < r_i
    }


# ============================================================================
# HELPER EXPRESSIONS
# ============================================================================


def _process_activity(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    """Output of a process in a time slice, including net of storage charging."""
    if t in model.tech_annual:
        return quicksum(
            (
                value(model.demand_specific_distribution[r, p, s, d, o])
                if o in model.commodity_demand
                else value(model.segment_fraction[s, d])
            )
            * model.v_flow_out_annual[r, p, i, t, v, o]
            for i in model.process_inputs[r, p, t, v]
            for o in model.process_outputs_by_input[r, p, t, v, i]
        )

    activity = quicksum(
        model.v_flow_out[r, p, s, d, i, t, v, o]
        for i in model.process_inputs[r, p, t, v]
        for o in model.process_outputs_by_input[r, p, t, v, i]
    )
    if t in model.tech_storage:
        activity -= quicksum(
            model.v_flow_in[r, p, s, d, i, t, v, o]
            for i in model.process_inputs[r, p, t, v]
            for o in model.process_outputs_by_input[r, p, t, v, i]
        )
    return activity


def offline_credit(
    model: UnitCommitmentModel,
    orm: ReserveName,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> Expression:
    """Credited output available from offline unit commitment units.

    The credit is a fraction of installed capacity, so it should already account for
    ``max_output_fraction``.
    """
    capacity_factor = (
        value(model.capacity_factor_process[r, s, d, t, v])
        if model.is_capacity_factor_process[r, t, v]
        else value(model.capacity_factor_tech[r, s, d, t])
    )
    offline_units = _total_units(model, r, p, t, v) - model.v_uc_online[r, p, s, d, t, v]
    return (
        value(model.operating_reserve_offline_credit[orm, r, t])
        * value(model.capacity_to_activity[r, t])
        * value(model.segment_fraction[s, d])
        * value(model.uc_unit_capacity[r, t])
        * capacity_factor
        * offline_units
    )


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


def operating_reserve_online_headroom_constraint(
    model: UnitCommitmentModel,
    orm: ReserveName,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Online headroom credit cannot exceed the unused available output of the process.

    .. math::
        :label: operating_reserve_online_headroom

        \mathbf{ORH}_{n,r,p,s,d,t,v} \le \mathbf{AVL}_{r,p,s,d,t,v} - \mathbf{ACT}_{r,p,s,d,t,v}

    where :math:`\mathbf{AVL}` is the available output (online units for unit commitment
    technologies, installed capacity otherwise, with capacity factors applied) and
    :math:`\mathbf{ACT}` is the process's output net of storage charging.
    """
    activity = _process_activity(model, r, p, s, d, t, v)
    return model.v_orm_online_credit[orm, r, p, s, d, t, v] + activity <= get_available_output(
        model, r, p, s, d, t, v
    )


def operating_reserve_online_headroom_credit_constraint(
    model: UnitCommitmentModel,
    orm: ReserveName,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Online headroom credit cannot exceed the creditable fraction of online capacity.

    .. math::
        :label: operating_reserve_online_headroom_credit

        \mathbf{ORH}_{n,r,p,s,d,t,v} \le ONC_{n,t} \cdot C2A_{r,t} \cdot SEG_{s,d} \cdot
        \begin{cases}
            UC_{r,t} \cdot \mathbf{UCN}_{r,p,s,d,t,v} & (r,t) \in UC \\
            \mathbf{CAP}_{r,p,t,v} & \text{otherwise}
        \end{cases}
    """
    online_capacity = (
        value(model.uc_unit_capacity[r, t]) * model.v_uc_online[r, p, s, d, t, v]
        if (r, t) in model.uc_unit_capacity
        else model.v_capacity[r, p, t, v]
    )
    max_credit = (
        value(model.operating_reserve_online_credit[orm, r, t])
        * value(model.capacity_to_activity[r, t])
        * value(model.segment_fraction[s, d])
        * online_capacity
    )
    return model.v_orm_online_credit[orm, r, p, s, d, t, v] <= max_credit


def operating_reserve_online_exchange_symmetry_constraint(
    model: UnitCommitmentModel,
    orm: ReserveName,
    r_e: Region,
    r_i: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    An exchange link's online headroom is physically the same capacity regardless of
    direction, so crediting it as incoming headroom on one side must be equivalent to
    debiting it as outgoing headroom on the other: the two directional entries are
    constrained to be exact negatives of one another.

    This lets :func:`operating_reserve_margin_constraint` add only the *incoming*
    entry. Two things follow:

    - The sum is always the side bounded above by
      :func:`operating_reserve_online_headroom_constraint` and
      :func:`operating_reserve_online_headroom_credit_constraint`, rather than an
      unconstrained negative, so there's no risk of the credit running away to
      :math:`-\infty`.
    - There's no double counting: if the model instead wants to export reserve out of
      the group, the incoming entry simply goes negative (its magnitude still capped
      by the outgoing side's own headroom constraints via this equality), correctly
      reducing the group's credited reserve instead of being added a second time.

    .. math::
        :label: operating_reserve_online_exchange_symmetry

        \mathbf{ORH}_{n,r_e-r_i,p,s,d,t,v} = -\mathbf{ORH}_{n,r_i-r_e,p,s,d,t,v}
    """
    return (
        model.v_orm_online_credit[orm, r_e + '-' + r_i, p, s, d, t, v]
        == -model.v_orm_online_credit[orm, r_i + '-' + r_e, p, s, d, t, v]
    )


def operating_reserve_storage_energy_constraint(
    model: UnitCommitmentModel,
    orm: ReserveName,
    r_g: Region,
    t_g: Technology,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    The reserve credited to a storage process, sustained for the product's
    :code:`sustain_hours`, plus its net discharge in the time slice must be covered by
    its state of charge at the start of the time slice.

    The same formulation works for seasonal storage because the non-sequential
    :code:`v_storage_level` is the floor state of charge for all sequential seasons
    built on the same non-sequential season.

    .. math::
        :label: operating_reserve_storage_energy

        \left( AC_{n,t} \cdot \mathbf{ACT}_{r,p,s,d,t,v} + \mathbf{ORH}_{n,r,p,s,d,t,v}
        + \mathbf{OFF}_{n,r,p,s,d,t,v} \right) \cdot \frac{SH_{n,r_g,t_g}}{HRS_d}
        + \sum_{I,O} \left( \mathbf{FO}_{r,p,s,d,i,t,v,o} - EFF \cdot \mathbf{FI}_{r,p,s,d,i,t,v,o}
        \right) \le \mathbf{SL}_{r,p,s,d,t,v}

    where :math:`\mathbf{OFF}_{n,r,p,s,d,t,v}` is the offline unit credit term of
    :eq:`operating_reserve_margin`.
    """
    charge = quicksum(
        model.v_flow_in[r, p, s, d, i, t, v, o]
        * get_variable_efficiency(model, r, p, s, d, i, t, v, o)
        for i in model.process_inputs[r, p, t, v]
        for o in model.process_outputs_by_input[r, p, t, v, i]
    )
    discharge = quicksum(
        model.v_flow_out[r, p, s, d, i, t, v, o]
        for i in model.process_inputs[r, p, t, v]
        for o in model.process_outputs_by_input[r, p, t, v, i]
    )

    credit = 0.0
    if has_activity_credit(model, orm, r, t):
        credit += value(model.operating_reserve_activity_credit[orm, r, t]) * _process_activity(
            model, r, p, s, d, t, v
        )
    if has_online_credit(model, orm, r, t):
        credit += model.v_orm_online_credit[orm, r, p, s, d, t, v]
    if has_offline_credit(model, orm, r, t):
        credit += offline_credit(model, orm, r, p, s, d, t, v)

    sustained = credit * (_sustain_hours(model, orm, r_g, t_g) / value(model.time_of_day_hours[d]))

    return sustained + discharge - charge <= model.v_storage_level[r, p, s, d, t, v]


def operating_reserve_margin_constraint(
    model: UnitCommitmentModel,
    orm: ReserveName,
    r_g: Region,
    t_g: Technology,
    p: Period,
    s: Season,
    d: TimeOfDay,
) -> ExprLike:
    r"""
    Credited reserve from processes in the product's region-group and tech-group must
    exceed the group's proxy demand by the product's margin in every time slice.

    Reserve is credited from current generation, headroom on online units, and offline
    unit commitment units that could start, each weighted by a per-product, per-technology
    credit. **All credits default to 0**, so technologies in the tech group contribute to
    the proxy demand but nothing to the reserve unless a credit is set. The tech group must
    include all technologies feeding the demand, even those with zero credit.

    Technologies need not be subject to unit commitment: a non-UC technology is treated as
    always fully online, so its online headroom is simply unused installed capacity, and it
    is never eligible for offline credit.

    Exchange technologies' online headroom credit is constrained equal and opposite across the
    link's two directional entries (outgoing = -incoming; see
    :func:`operating_reserve_online_exchange_symmetry_constraint`), so only the entry incoming
    to the group is summed below -- it is already correctly signed whether the link is
    importing (positive) or exporting (negative) reserve. Offline credit has no such symmetry
    constraint, so it's still credited for imports and debited for exports with an explicit
    sign, as in :func:`~temoa.components.reserves._planning_reserve_margin_static`.

    .. note::
        Unlike the planning reserve margin, :math:`ORM` is the required reserve as a
        fraction of proxy demand, not an excess above it (e.g. 0.1 requires reserve equal
        to 10% of demand).

    .. math::
        :label: operating_reserve_margin

        \begin{aligned}
            &\sum_{(r,t,v) \in \Theta^{res}}
                AC_{n,t} \cdot \mathbf{ACT}_{r,p,s,d,t,v}
                && \text{(current generation)} \\
            &+ \sum_{(r,t,v) \in \Theta^{res} \setminus T^x}
                \mathbf{ORH}_{n,r,p,s,d,t,v}
                && \text{(online headroom)} \\
            &+ \sum_{(r,t,v) \in \Theta^{res} \cap UC \setminus T^x}
                \mathbf{OFF}_{n,r,p,s,d,t,v}
                && \text{(offline units)} \\
            &+ \sum_{\substack{(r_1-r_2,t,v) \in \Theta^{res} \cap T^x \\
                r_2 \in r_g,\ r_1 \notin r_g}}
                \mathbf{ORH}_{n,r_1-r_2,p,s,d,t,v}
                && \text{(incoming exchange online headroom)} \\
            &+ \sum_{(r,t,v) \in \Theta^{res} \cap T^x}
                \sigma_{r,r_g} \cdot \mathbf{OFF}_{n,r,p,s,d,t,v}
                && \text{(net exchange offline)} \\
            &\geq D^{proxy}_{r_g,p,s,d} \cdot ORM_{n,r_g,t_g} \\
            &\forall \{n, r_g, t_g, p, s, d\} \in \Theta_{\text{OperatingReserveMargin}}
        \end{aligned}

    where :math:`\sigma_{r,r_g} = +1` for an exchange process delivering into region-group
    :math:`r_g` and :math:`-1` for one delivering out of it, the incoming-only online headroom
    term already carries the correct sign for either direction by construction of
    :eq:`operating_reserve_online_exchange_symmetry` (no separate :math:`\sigma` needed),
    :math:`\Theta^{res} =
    \Theta^{res}_{n,r_g,t_g,p}` is the set of processes
    contributing to product :math:`{n,r_g,t_g}` in period :math:`p`,
    :math:`D^{proxy}_{r_g,p,s,d}` is the product's proxy demand defined in
    :eq:`reserve_margin_proxy_demand`, and

    .. math::

        \mathbf{OFF}_{n,r,p,s,d,t,v} = OFC_{n,t} \cdot C2A_{r,t} \cdot SEG_{s,d} \cdot UC_{r,t}
        \cdot CFP_{r,s,d,t,v} \cdot \left( \frac{\mathbf{CAP}_{r,p,t,v}}{UC_{r,t}}
        - \mathbf{UCN}_{r,p,s,d,t,v} \right)
    """
    processes = model.operating_reserve_processes[orm, r_g, t_g, p]
    demand, activity_rtv = reserve_margin_proxy_demand(model, processes, r_g, p, s, d)

    # Activity credit reuses activity_rtv, which reserve_margin_proxy_demand already signs for
    # exchange imports/exports; online and offline credit are not similarly signed, so they're
    # computed separately for exchange processes below.
    activity_credits = quicksum(
        activity_rtv[r, t, v] * value(model.operating_reserve_activity_credit[orm, r, t])
        for r, t, v in processes
        if has_activity_credit(model, orm, r, t)
    )
    online_credits = quicksum(
        model.v_orm_online_credit[orm, r, p, s, d, t, v]
        for r, t, v in processes
        if t not in model.tech_exchange
        if has_online_credit(model, orm, r, t)
    )
    offline_credits = quicksum(
        offline_credit(model, orm, r, p, s, d, t, v)
        for r, t, v in processes
        if t not in model.tech_exchange
        if has_offline_credit(model, orm, r, t)
    )

    # Credit exchange online/offline reserve for imports into the group, debit it for exports
    regions = geography.gather_group_regions(model, r_g)
    for r1r2, t, v in processes:
        if t not in model.tech_exchange:
            continue

        r1, r2 = r1r2.split('-')
        if r2 in regions and r1 not in regions:
            if has_online_credit(model, orm, r1r2, t):
                # Online credits are signed-symmetric for imports/exports. We only want the
                # incoming part because the outgoing part is just the same but sign-flipped
                # (would just cancel out).
                online_credits += model.v_orm_online_credit[orm, r1r2, p, s, d, t, v]
            sign = 1
        elif r1 in regions and r2 not in regions:
            sign = -1
        else:
            continue

        if has_offline_credit(model, orm, r1r2, t):
            offline_credits += sign * offline_credit(model, orm, r1r2, p, s, d, t, v)

    reserve = activity_credits + online_credits + offline_credits

    margin = value(model.operating_reserve_margin[orm, r_g, t_g])
    return reserve >= demand * margin
