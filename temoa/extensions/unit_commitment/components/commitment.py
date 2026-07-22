"""Unit-commitment constraints for the unit_commitment extension.

Implements:
  - cyclic previous-time map (uc_time_prev) built from model.time_next
  - integer-domain promotion for UC variables
  - online/started/stopped upper bounds + tightening constraints
  - commitment transition
  - min/max output from online units
  - min up-time and min down-time via cyclic windows
  - ramp-up and ramp-down constraints that account for online units and started/stopped units
  - dynamic reserve margin constraint that accounts for online units and started/stopped units
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pyomo.environ import Constraint, NonNegativeIntegers, quicksum, value

import temoa.components.utils as utils
from temoa.components.operations import _ramp_activity_increase
from temoa.components.time import tod_elapsed_hours
from temoa.components.utils import available_output_base

if TYPE_CHECKING:
    from pyomo.environ import Expression

    from temoa.extensions.unit_commitment.core.model import UnitCommitmentModel
    from temoa.types import ExprLike
    from temoa.types.core_types import Period, Region, Season, Technology, TimeOfDay, Vintage

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------


def apply_integer_domains(model: UnitCommitmentModel) -> None:
    """Set integer domain on UC variable indices where integer_flag == 1."""
    for r, p, s, d, t, v in model.uc_indices_rpsdtv:
        if not value(model.uc_linearized[r, t]):
            model.v_uc_online[r, p, s, d, t, v].domain = NonNegativeIntegers
            model.v_uc_started[r, p, s, d, t, v].domain = NonNegativeIntegers
            model.v_uc_stopped[r, p, s, d, t, v].domain = NonNegativeIntegers


# ---------------------------------------------------------------------------
# Index set
# ---------------------------------------------------------------------------


def initialize_unit_commitment(model: UnitCommitmentModel) -> None:
    """Initialize the unit commitment index set."""

    # Override get_available_output with the UC-aware version for this run.
    utils.available_output_function = uc_available_output

    # Annual techs cant use unit commitment as their flows are not flexible
    bad_techs = {t for _, t in model.uc_unit_capacity.sparse_keys() if t in model.tech_annual}
    if bad_techs:
        msg = (
            'Unit commitment constraints cannot be applied to annual technologies as they '
            'have no flexibility in operations: {}'
        ).format(', '.join(sorted(bad_techs)))
        logger.error(msg)
        raise ValueError(msg)

    # Make sure any startup parameters have a valid unit commitment process
    startup_rt = (
        set(model.uc_startup_cost.sparse_keys())
        | {(r, t) for r, e, t in model.uc_startup_emissions.sparse_keys()}
        | {(r, t) for r, i, t in model.uc_startup_input.sparse_keys()}
    )
    bad_rt = set(startup_rt) - set(model.uc_unit_capacity.sparse_keys())
    if bad_rt:
        msg = (
            'Startup parameters provided for (region, tech) pairs not in unit_commitment: {}'
        ).format(', '.join(f'({r}, {t})' for r, t in sorted(bad_rt)))
        logger.error(msg)
        raise ValueError(msg)

    # Initialise the time slice back-check lists for min up/down time constraints
    # Tells us which previous time slices' startups/shutdowns are relevant
    epsilon = 1e-6  # To buffer float/integer interactions

    # We only care about how many hours back we're looking, so why redo work?
    hours_back = {
        int(value(model.uc_min_down_time_hours[r, t]))
        for (r, t) in model.uc_min_down_time_hours.sparse_keys()
    }
    hours_back |= {
        int(value(model.uc_min_up_time_hours[r, t]))
        for (r, t) in model.uc_min_up_time_hours.sparse_keys()
    }

    # Invert the time next sequence to start...
    time_prev = {model.time_next[s, d]: (s, d) for s, d in model.time_next}
    # Then back down the chain until the next timeslice back is irrelevant
    for hb in hours_back:
        for s, d in time_prev:
            model.uc_backslices[s, d, hb] = set()
            _s, _d = s, d
            _hours = float(hb)
            i = 0  # Some loop safety
            while i + 1 < len(model.time_next):
                s_prev, d_prev = time_prev[_s, _d]
                if s_prev == _s and d_prev == _d:
                    msg = (
                        'When finding relevant past time slices for min up/downtime '
                        'constraints, looped back to the same time slice. This would '
                        'likely cause infeasibility and is not supported.  If the '
                        'min up/downtime is longer than a season, try instead '
                        'flagging the technology as production baseload "pb" and '
                        'setting min up/down times to zero to skip the constraints. '
                    )
                    logger.error(msg)
                    raise ValueError(msg)
                elapsed = tod_elapsed_hours(model, d_prev, _d)
                _hours -= elapsed
                if _hours < -epsilon:
                    break  # too far back (with some rounding buffer) so ignore
                i += 1
                model.uc_backslices[s, d, hb].add((s_prev, d_prev))
                _s, _d = s_prev, d_prev


def uc_constraint_indices(
    model: UnitCommitmentModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    """All (r, p, s, d, t, v) indices for unit commitment constraints."""
    return {
        (r, p, s, d, t, v)
        for r, t in model.uc_unit_capacity.sparse_keys()
        for p in model.time_optimize
        for v in model.process_vintages.get((r, p, t), [])
        for s in model.time_season
        for d in model.time_of_day
    }


def capacity_constraint_indices(
    model: UnitCommitmentModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    # Non uc processes back to default capacity constraint
    return set(model.capacity_constraint_rpsdtv - model.uc_indices_rpsdtv)


def ramp_up_constraint_indices(
    model: UnitCommitmentModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    # Non uc processes back to default ramp up constraint
    return set(model.ramp_up_constraint_rpsdtv - model.uc_indices_rpsdtv)


def ramp_down_constraint_indices(
    model: UnitCommitmentModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    # Non uc processes back to default ramp down constraint
    return set(model.ramp_down_constraint_rpsdtv - model.uc_indices_rpsdtv)


def uc_ramp_up_constraint_indices(
    model: UnitCommitmentModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    # UC processes ramp up constraint
    return set(model.ramp_up_constraint_rpsdtv & model.uc_indices_rpsdtv)


def uc_ramp_down_constraint_indices(
    model: UnitCommitmentModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    # UC processes ramp down constraint
    return set(model.ramp_down_constraint_rpsdtv & model.uc_indices_rpsdtv)


# ---------------------------------------------------------------------------
# Helper expressions
# ---------------------------------------------------------------------------


def _total_units(
    model: UnitCommitmentModel, r: Region, p: Period, t: Technology, v: Vintage
) -> ExprLike:
    return model.v_capacity[r, p, t, v] / value(model.uc_unit_capacity[r, t])


def _flow_out_sum(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> Expression:
    """Total output energy for process (r,p,s,d,t,v): sum over inputs/outputs of v_flow_out."""
    return quicksum(
        model.v_flow_out[r, p, s, d, _i, t, v, _o]
        for _i in model.process_inputs[r, p, t, v]
        for _o in model.process_outputs_by_input[r, p, t, v, _i]
    )


def uc_available_output(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Commitment-aware maximum available output for a process in a specific time slice.

    For non-UC technologies, delegates to
    :func:`~temoa.components.utils.available_output_base`.  For UC technologies,
    online units replace installed capacity:

    .. math::

        \textit{available} =
        \mathbf{UCN}_{r,p,s,d,t,v}
        \cdot UC_{r,t}
        \cdot \overline{f}_{r,t}
        \cdot CF_{r,s,d,t,v}
        \cdot C2A_{r,t}
        \cdot SEG_{s,d}

    where :math:`\overline{f}_{r,t}` is ``max_output_fraction`` and
    :math:`CF_{r,s,d,t,v}` is taken from ``capacity_factor_process`` or
    ``capacity_factor_tech`` as appropriate.  Offline units contribute zero.

    This function is registered as :data:`~temoa.components.utils.available_output_function`
    during model initialization when the ``unit_commitment`` extension is active,
    so it is called transparently by :func:`~temoa.components.utils.get_available_output`
    throughout the core model.
    """
    if (r, t) not in model.uc_unit_capacity:
        return available_output_base(model, r, p, s, d, t, v)
    base = (
        model.capacity_to_activity[r, t]
        * model.segment_fraction[s, d]
        * value(model.uc_max_output_fraction[r, t])
        * value(model.uc_unit_capacity[r, t])
        * model.v_uc_online[r, p, s, d, t, v]
    )
    if model.is_capacity_factor_process[r, t, v]:
        return base * value(model.capacity_factor_process[r, s, d, t, v])
    else:
        return base * value(model.capacity_factor_tech[r, s, d, t])


# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------


def uc_online_upper_constraint(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Online units cannot exceed the number of available (physical) units:

    .. math::

        \textbf{UCN}_{r,p,s,d,t,v} \le \frac{\textbf{CAP}_{r,p,t,v}}{UC_{r,t}}
    """
    return model.v_uc_online[r, p, s, d, t, v] <= _total_units(model, r, p, t, v)


def uc_started_upper_tightening_constraint(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Tightening: cannot start more units than are currently offline.
    Redundant but makes the integer formulation a bit more efficient.

    .. math::

        \textbf{UCST}_{r,p,s,d,t,v}
        \le \frac{\textbf{CAP}_{r,p,t,v}}{UC_{r,t}}
          - \textbf{UCN}_{r,p,s,d,t,v}
    """
    offline = _total_units(model, r, p, t, v) - model.v_uc_online[r, p, s, d, t, v]
    return model.v_uc_started[r, p, s, d, t, v] <= offline


def uc_stopped_upper_tightening_constraint(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Tightening: cannot shutdown more units than are currently online.
    Redundant but makes the integer formulation a bit more efficient.

    .. math::

        \textbf{UCSP}_{r,p,s,d,t,v}
        \le \textbf{UCN}_{r,p,s,d,t,v}
    """
    return model.v_uc_stopped[r, p, s, d, t, v] <= model.v_uc_online[r, p, s, d, t, v]


def uc_transition_constraint(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Commitment transition: change in online units equals started minus stopped.
    The constraint is indexed by the current slice :math:`(s,d)` and links to its
    successor :math:`(s_{next}, d_{next})` via :code:`model.time_next`.

    .. math::

        \textbf{UCN}_{r,p,s_{next},d_{next},t,v} - \textbf{UCN}_{r,p,s,d,t,v}
        = \textbf{UCST}_{r,p,s,d,t,v} - \textbf{UCSP}_{r,p,s,d,t,v}
    """
    s_next, d_next = model.time_next[s, d]
    return (
        model.v_uc_online[r, p, s_next, d_next, t, v] - model.v_uc_online[r, p, s, d, t, v]
        == model.v_uc_started[r, p, s, d, t, v] - model.v_uc_stopped[r, p, s, d, t, v]
    )


def uc_min_output_constraint(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Output must be at least min_output_fraction * unit_capacity per online unit,
    converted to energy units via capacity_to_activity and segment_fraction.

    .. math::

        \sum_{i,o} \textbf{FO}_{r,p,s,d,i,t,v,o}
        \ge \text{minFrac} \cdot UC_{r,t} \cdot C2A_{r,t} \cdot SEG_{s,d}
            \cdot \textbf{UCN}_{r,p,s,d,t,v}
    """
    min_frac = value(model.uc_min_output_fraction[r, t])
    if min_frac <= 0.0:
        return Constraint.Skip

    output = _flow_out_sum(model, r, p, s, d, t, v)
    # We can't use the regular available output here because it includes the max_output_fraction
    available = (
        model.capacity_to_activity[r, t]
        * model.segment_fraction[s, d]
        * value(model.uc_unit_capacity[r, t])
        * model.v_uc_online[r, p, s, d, t, v]
    )
    return output >= min_frac * available


def uc_min_up_time_constraint(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Sum of starts over a cyclic window of length min_up_time_steps ending at (s,d)
    must not exceed online units at (s,d).

    .. math::

        \sum_{\tau \in W^{\text{up}}_{s,d}} \textbf{UCST}_{r,p,\tau,t,v}
        \le \textbf{UCN}_{r,p,s,d,t,v}
    """
    hours_back = int(value(model.uc_min_up_time_hours[r, t]))
    started_sum = quicksum(
        model.v_uc_started[r, p, _s, _d, t, v] for _s, _d in model.uc_backslices[s, d, hours_back]
    )
    return model.v_uc_online[r, p, s, d, t, v] >= started_sum


def uc_min_down_time_constraint(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Sum of stops over a cyclic window of length min_down_time_steps ending at (s,d)
    must not exceed offline units at (s,d).

    .. math::

        \sum_{\tau \in W^{\text{dn}}_{s,d}} \textbf{UCSP}_{r,p,\tau,t,v}
        \le \frac{\textbf{CAP}_{r,p,t,v}}{UC_{r,t}} - \textbf{UCN}_{r,p,s,d,t,v}

    .. warning::

        **Floating-point precision of time-slice hours.**  The
        :code:`min_x_time_hours` values are integers, but the hour length of
        each time-of-day segment is stored as a float.  When walking
        backwards through the time-slice sequence to build the look-back window
        :math:`W^{\text{dn}}_{s,d}`, the cumulative elapsed hours are compared
        against the integer target with a tolerance of :math:`10^{-6}` hours.
        This buffer is intentionally tiny
        and will not mask genuine misalignment, and means that the look-back cyclic
        window is only correct when the segment hours are near-exact fractions
        of the day.  If your :code:`time_of_day`: :code:`hours` or :code:`time_season`:
        :code:`segment_fraction` data are rounded imprecisely, the window boundary may be
        mis-classified by one time slice.
    """
    hours_back = int(value(model.uc_min_down_time_hours[r, t]))
    stopped_sum = quicksum(
        model.v_uc_stopped[r, p, _s, _d, t, v] for _s, _d in model.uc_backslices[s, d, hours_back]
    )
    offline = _total_units(model, r, p, t, v) - model.v_uc_online[r, p, s, d, t, v]
    return offline >= stopped_sum


def _rampable_activity(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
    ramp_up: bool,
    ramp_fraction: float,
) -> ExprLike:

    unit_cap = value(model.uc_unit_capacity[r, t])
    online = ramp_fraction * model.v_uc_online[r, p, s, d, t, v] * unit_cap

    min_fraction = max(value(model.uc_min_output_fraction[r, t]), ramp_fraction)
    startup = min_fraction * model.v_uc_started[r, p, s, d, t, v] * unit_cap
    shutdown = min_fraction * model.v_uc_stopped[r, p, s, d, t, v] * unit_cap

    capacity_ramp = (online + startup - shutdown) if ramp_up else (online + shutdown - startup)
    return (
        capacity_ramp
        * value(model.capacity_to_activity[r, t])
        / (24 * value(model.days_per_period))
    )


def _ramp_constraint(
    model: UnitCommitmentModel,
    ramp_up: bool,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    s_next, d_next = model.time_next[s, d]
    result = _ramp_activity_increase(model, ramp_up, r, p, s, d, s_next, d_next, t, v)
    if result is None:
        return Constraint.Skip
    activity_increase, ramp_fraction = result
    rampable = _rampable_activity(model, r, p, s, d, t, v, ramp_up, ramp_fraction)
    if ramp_up:
        return activity_increase <= rampable
    else:
        return -activity_increase <= rampable


def uc_ramp_up_constraint(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    UC-aware ramp-up constraint.  Replaces the core
    :code:`ramp_up_constraint` for technologies that appear in both the
    :code:`unit_commitment` and :code:`ramp_up_hourly` tables.

    The ramp envelope is driven by *online units* rather than total installed
    capacity.  Units that start during slice :math:`(s,d)` arrive part-way to
    their maximum output, providing additional headroom; units that stop reduce
    it:

    .. math::
       :label: uc_ramp_up

        \frac{\sum_{I,O}\textbf{FO}_{r,p,s_{next},d_{next},i,t,v,o}}{H_{s_{next},d_{next}}}
        -
        \frac{\sum_{I,O}\textbf{FO}_{r,p,s,d,i,t,v,o}}{H_{s,d}}
        \;\le\;
        \left[
            RH_{r,t} \cdot \Delta H \cdot \textbf{UCN}_{r,p,s,d,t,v}
            + f^{\min}_{\text{eff}} \cdot \textbf{UCST}_{r,p,s,d,t,v}
            - f^{\min}_{\text{eff}} \cdot \textbf{UCSP}_{r,p,s,d,t,v}
        \right]
        \cdot \frac{UC_{r,t} \cdot C2A_{r,t}}{24 \cdot DPP}

    where :math:`f^{\min}_{\text{eff}} = \max(\underline{f}_{r,t},\, RH_{r,t} \cdot \Delta H)`
    is the effective minimum output fraction for started/stopped units, and
    :math:`\Delta H = (H_{s,d} + H_{s_{next},d_{next}}) / 2`.
    """
    return _ramp_constraint(
        model=model,
        ramp_up=True,
        r=r,
        p=p,
        s=s,
        d=d,
        t=t,
        v=v,
    )


def uc_ramp_down_constraint(
    model: UnitCommitmentModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    UC-aware ramp-down constraint.  Replaces the core
    :code:`ramp_down_constraint` for technologies that appear in both the
    :code:`unit_commitment` and :code:`ramp_down_hourly` tables.

    Symmetric to :func:`uc_ramp_up_constraint` with signs on
    :math:`\textbf{UCST}` and :math:`\textbf{UCSP}` reversed: a unit that stops
    during :math:`(s,d)` adds headroom (output falls), while a starting unit
    reduces it:

    .. math::
       :label: uc_ramp_down

        \frac{\sum_{I,O}\textbf{FO}_{r,p,s,d,i,t,v,o}}{H_{s,d}}
        -
        \frac{\sum_{I,O}\textbf{FO}_{r,p,s_{next},d_{next},i,t,v,o}}{H_{s_{next},d_{next}}}
        \;\le\;
        \left[
            RD_{r,t} \cdot \Delta H \cdot \textbf{UCN}_{r,p,s,d,t,v}
            + f^{\min}_{\text{eff}} \cdot \textbf{UCSP}_{r,p,s,d,t,v}
            - f^{\min}_{\text{eff}} \cdot \textbf{UCST}_{r,p,s,d,t,v}
        \right]
        \cdot \frac{UC_{r,t} \cdot C2A_{r,t}}{24 \cdot DPP}

    where :math:`f^{\min}_{\text{eff}} = \max(\underline{f}_{r,t},\, RD_{r,t} \cdot \Delta H)`.
    """
    return _ramp_constraint(
        model=model,
        ramp_up=False,
        r=r,
        p=p,
        s=s,
        d=d,
        t=t,
        v=v,
    )
