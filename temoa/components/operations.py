# temoa/components/operations.py
"""
Defines operational constraints for technologies in the Temoa model.

This module is responsible for constraints that govern the dispatch behavior
of technologies across time slices, including:
-  Pre-computing sets for technologies with special operational characteristics.
-  Baseload constraints, which force constant output within a season.
-  Ramping constraints, which limit the rate of change in output between
    adjacent time slices.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from pyomo.environ import Constraint, value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types import ExprLike
    from temoa.types.core_types import Period, Region, Season, Technology, TimeOfDay, Vintage

logger = getLogger(__name__)

# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def baseload_diurnal_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    indices = {
        (r, p, s, d, t, v)
        for r, p, t in model.baseload_vintages
        for v in model.baseload_vintages[r, p, t]
        for s in model.time_season[p]
        for d in model.time_of_day
    }

    return indices


def ramp_up_day_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    indices = {
        (r, p, s, d, t, v)
        for r, p, t in model.ramp_up_vintages
        for v in model.ramp_up_vintages[r, p, t]
        for s in model.time_season[p]
        for d in model.time_of_day
    }

    return indices


def ramp_down_day_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, TimeOfDay, Technology, Vintage]]:
    indices = {
        (r, p, s, d, t, v)
        for r, p, t in model.ramp_down_vintages
        for v in model.ramp_down_vintages[r, p, t]
        for s in model.time_season[p]
        for d in model.time_of_day
    }

    return indices


def ramp_up_season_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, Season, Technology, Vintage]]:
    if model.time_sequencing.first() == 'consecutive_days':
        return set()

    # s, s_next indexing ensures we dont build redundant constraints
    indices = {
        (r, p, s, s_next, t, v)
        for r, p, t in model.ramp_up_vintages
        for v in model.ramp_up_vintages[r, p, t]
        for _p, s_seq, s in model.ordered_season_sequential
        if _p == p
        for s_next in (model.sequential_to_season[p, model.time_next_sequential[p, s_seq]],)
        if s_next != model.time_next[p, s, model.time_of_day.last()][0]
    }

    return indices


def ramp_down_season_constraint_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Season, Season, Technology, Vintage]]:
    if model.time_sequencing.first() == 'consecutive_days':
        return set()

    # s, s_next indexing ensures we dont build redundant constraints
    indices = {
        (r, p, s, s_next, t, v)
        for r, p, t in model.ramp_down_vintages
        for v in model.ramp_down_vintages[r, p, t]
        for _p, s_seq, s in model.ordered_season_sequential
        if _p == p
        for s_next in (model.sequential_to_season[p, model.time_next_sequential[p, s_seq]],)
        if s_next != model.time_next[p, s, model.time_of_day.last()][0]
    }

    return indices


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


def baseload_diurnal_constraint(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
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
    l_times = sorted(model.time_of_day)  # i.e. a sorted Python list.
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
        model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    activity_sd_0 = sum(
        model.v_flow_out[r, p, s, d_0, S_i, t, v, S_o]
        for S_i in model.process_inputs[r, p, t, v]
        for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
    )

    expr = activity_sd * value(model.segment_fraction[p, s, d_0]) == activity_sd_0 * value(
        model.segment_fraction[p, s, d]
    )

    return expr


# ============================================================================
# PRE-COMPUTATION FUNCTION
# ============================================================================


def create_operational_vintage_sets(model: TemoaModel) -> None:
    """
    Populates vintage-based dictionaries for technologies with special
    operational characteristics like curtailment, baseload, storage, ramping, and reserves.

    Populates:
        - M.curtailment_vintages, M.baseload_vintages, M.storage_vintages,
          M.ramp_up_vintages, M.ramp_down_vintages: Dictionaries mapping (r, p, t)
          to a set of vintages `v`.
        - M.process_reserve_periods: Dictionary mapping (r, p) to a set of (t, v) tuples.
        - M.is_seasonal_storage: A boolean lookup for seasonal storage technologies.
    """
    logger.debug('Creating vintage sets for operational constraints.')

    for r, p, t in model.process_vintages:
        for v in model.process_vintages[r, p, t]:
            key_rpt = (r, p, t)
            key_rp = (r, p)
            if t in model.tech_curtailment:
                model.curtailment_vintages.setdefault(key_rpt, set()).add(v)
            if t in model.tech_baseload:
                model.baseload_vintages.setdefault(key_rpt, set()).add(v)
            if t in model.tech_storage:
                model.storage_vintages.setdefault(key_rpt, set()).add(v)
            if t in model.tech_upramping:
                model.ramp_up_vintages.setdefault(key_rpt, set()).add(v)
            if t in model.tech_downramping:
                model.ramp_down_vintages.setdefault(key_rpt, set()).add(v)
            if t in model.tech_reserve:
                model.process_reserve_periods.setdefault(key_rp, set()).add((t, v))

    # A dictionary of whether a storage tech is seasonal, just to speed things up
    for t in model.tech_storage:
        model.is_seasonal_storage[t] = t in model.tech_seasonal_storage


def ramp_up_day_constraint(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    One of two constraints built from the ramp_up_hourly table, along with the
    ramp_up_season_constraint. ramp_up_day constrains ramp rates between time slices
    within each season and ramp_up_season constrains ramp rates between sequential
    seasons. If the :code:`time_sequencing` parameter is set to :code:`consecutive_days`
    then the ramp_up_season constraint is skipped as seasons already connect together.

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
       :label: ramp_up_day

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
            \forall \{r, p, s, d, t, v\} \in \Theta_{\text{ramp\_up\_day}}
            \\
            \text{where: } \Delta H_{r,p,s,d,s_{next},d_{next}} = \frac{24}{2}
            \left ( \frac{SEG_{r,p,s,d}}{\sum_{D} SEG_{r,p,s,d'}} +
            \frac{SEG_{r,p,s_{next},d_{next}}}{\sum_{D} SEG_{r,p,s_{next},d'}} \right )

    where:

    - :math:`SEG_{r,p,s,d}` is the fraction of the period in time slice :math:`(s,d)`
    - :math:`DPP` is the number of days in each period
    - :math:`R_{r,t}` is the ramp rate per hour
    - :math:`\Delta H_{r,p,s,d,s_{next},d_{next}}` is the number of elapsed hours between midpoints
      of time slices
    - :math:`CAP \cdot C2A` gives the maximum hourly change in activity
    """

    s_next, d_next = model.time_next[p, s, d]

    # How many hours does this time slice represent
    hours_adjust = value(model.segment_fraction[p, s, d]) * value(model.days_per_period) * 24
    hours_adjust_next = (
        value(model.segment_fraction[p, s_next, d_next]) * value(model.days_per_period) * 24
    )

    hourly_activity_sd = (
        sum(
            model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    hourly_activity_sd_next = (
        sum(
            model.v_flow_out[r, p, s_next, d_next, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
        / hours_adjust_next
    )

    # elapsed hours from middle of this time slice to middle of next time slice
    hours_elapsed = (
        24
        / 2
        * (
            value(model.segment_fraction[p, s, d]) / value(model.segment_fraction_per_season[p, s])
            + value(model.segment_fraction[p, s_next, d_next])
            / value(model.segment_fraction_per_season[p, s_next])
        )
    )
    ramp_fraction = hours_elapsed * value(model.ramp_up_hourly[r, t])

    if ramp_fraction >= 1:
        msg = (
            'Warning: Hourly ramp up rate ({}, {}) is too large to be constraining from '
            '({}, {}, {}) to ({}, {}, {}). '
            f'Should be less than {1 / hours_elapsed:.4f}. Constraint skipped.'
        )
        logger.warning(msg.format(r, t, p, s, d, p, s_next, d_next))
        return Constraint.Skip

    activity_increase = hourly_activity_sd_next - hourly_activity_sd  # opposite sign from rampdown
    rampable_activity = (
        ramp_fraction * model.v_capacity[r, p, t, v] * value(model.capacity_to_activity[r, t])
    )
    expr = activity_increase <= rampable_activity

    return expr


def ramp_down_day_constraint(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""

    Similar to the :code`ramp_up_day` constraint, we use the :code:`ramp_down_day`
    constraint to limit ramp down rates between any two adjacent time slices.

    .. math::
       :label: ramp_down_day

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
            \forall \{r, p, s, d, t, v\} \in \Theta_{\text{ramp\_down\_day}}
    """

    s_next, d_next = model.time_next[p, s, d]

    # How many hours does this time slice represent
    hours_adjust = value(model.segment_fraction[p, s, d]) * value(model.days_per_period) * 24
    hours_adjust_next = (
        value(model.segment_fraction[p, s_next, d_next]) * value(model.days_per_period) * 24
    )

    hourly_activity_sd = (
        sum(
            model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    hourly_activity_sd_next = (
        sum(
            model.v_flow_out[r, p, s_next, d_next, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
        / hours_adjust_next
    )

    # elapsed hours from middle of this time slice to middle of next time slice
    hours_elapsed = (
        24
        / 2
        * (
            value(model.segment_fraction[p, s, d]) / value(model.segment_fraction_per_season[p, s])
            + value(model.segment_fraction[p, s_next, d_next])
            / value(model.segment_fraction_per_season[p, s_next])
        )
    )
    ramp_fraction = hours_elapsed * value(model.ramp_down_hourly[r, t])

    if ramp_fraction >= 1:
        msg = (
            'Warning: Hourly ramp down rate  ({}, {}) is too large to be constraining from '
            '({}, {}, {}) to ({}, {}, {}). '
            f'Should be less than {1 / hours_elapsed:.4f}. Constraint skipped.'
        )
        logger.warning(msg.format(r, t, p, s, d, p, s_next, d_next))
        return Constraint.Skip

    activity_decrease = hourly_activity_sd - hourly_activity_sd_next  # opposite sign from rampup
    rampable_activity = (
        ramp_fraction * model.v_capacity[r, p, t, v] * value(model.capacity_to_activity[r, t])
    )
    expr = activity_decrease <= rampable_activity

    return expr


def ramp_up_season_constraint(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    s_next: Season,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Constrains the ramp up rate of activity between time slices at the boundary
    of sequential seasons. Same as ramp_up_day but only applies to the boundary
    between sequential seasons, i.e., :math:`(s^{seq},d_{last})` to
    :math:`(s^{seq}_{next},d_{first})`
    and :math:`s^{seq}_{next}` is based on the TimeSequential table rather than the
    time_season table.
    """

    d = model.time_of_day.last()
    d_next = model.time_of_day.first()

    # How many hours does this time slice represent
    hours_adjust = value(model.segment_fraction[p, s, d]) * value(model.days_per_period) * 24
    hours_adjust_next = (
        value(model.segment_fraction[p, s_next, d_next]) * value(model.days_per_period) * 24
    )

    hourly_activity_sd = (
        sum(
            model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    hourly_activity_sd_next = (
        sum(
            model.v_flow_out[r, p, s_next, d_next, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
        / hours_adjust_next
    )

    # elapsed hours from middle of this time slice to middle of next time slice
    hours_elapsed = (
        24
        / 2
        * (
            value(model.segment_fraction[p, s, d]) / value(model.segment_fraction_per_season[p, s])
            + value(model.segment_fraction[p, s_next, d_next])
            / value(model.segment_fraction_per_season[p, s_next])
        )
    )
    ramp_fraction = hours_elapsed * value(model.ramp_up_hourly[r, t])

    if ramp_fraction >= 1:
        msg = (
            'Warning: Hourly ramp up rate ({}, {}) is too large to be constraining from '
            '({}, {}, {}) to ({}, {}, {}). '
            f'Should be less than {1 / hours_elapsed:.4f}. Constraint skipped.'
        )
        logger.warning(msg.format(r, t, p, s, d, p, s_next, d_next))
        return Constraint.Skip

    activity_increase = hourly_activity_sd_next - hourly_activity_sd  # opposite sign from rampdown
    rampable_activity = (
        ramp_fraction * model.v_capacity[r, p, t, v] * value(model.capacity_to_activity[r, t])
    )
    expr = activity_increase <= rampable_activity

    return expr


def ramp_down_season_constraint(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    s_next: Season,
    t: Technology,
    v: Vintage,
) -> ExprLike:
    r"""
    Constrains the ramp down rate of activity between time slices at the boundary
    of sequential seasons. Same as ramp_down_day but only applies to the boundary
    between sequential seasons, i.e., :math:`(s^{seq},d_{last})` to
    :math:`(s^{seq}_{next},d_{first})`
    and :math:`s^{seq}_{next}` is based on the TimeSequential table rather than the
    time_season table.
    """

    d = model.time_of_day.last()
    d_next = model.time_of_day.first()

    # How many hours does this time slice represent
    hours_adjust = value(model.segment_fraction[p, s, d]) * value(model.days_per_period) * 24
    hours_adjust_next = (
        value(model.segment_fraction[p, s_next, d_next]) * value(model.days_per_period) * 24
    )

    hourly_activity_sd = (
        sum(
            model.v_flow_out[r, p, s, d, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
        / hours_adjust
    )

    hourly_activity_sd_next = (
        sum(
            model.v_flow_out[r, p, s_next, d_next, S_i, t, v, S_o]
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
        / hours_adjust_next
    )

    # elapsed hours from middle of this time slice to middle of next time slice
    hours_elapsed = (
        24
        / 2
        * (
            value(model.segment_fraction[p, s, d]) / value(model.segment_fraction_per_season[p, s])
            + value(model.segment_fraction[p, s_next, d_next])
            / value(model.segment_fraction_per_season[p, s_next])
        )
    )
    ramp_fraction = hours_elapsed * value(model.ramp_down_hourly[r, t])

    if ramp_fraction >= 1:
        msg = (
            'Warning: Hourly ramp down rate ({}, {}) is too large to be constraining from '
            '({}, {}, {}) to ({}, {}, {}). '
            f'Should be less than {1 / hours_elapsed:.4f}. Constraint skipped.'
        )
        logger.warning(msg.format(r, t, p, s, d, p, s_next, d_next))
        return Constraint.Skip

    activity_decrease = hourly_activity_sd - hourly_activity_sd_next  # opposite sign from rampup
    rampable_activity = (
        ramp_fraction * model.v_capacity[r, p, t, v] * value(model.capacity_to_activity[r, t])
    )
    expr = activity_decrease <= rampable_activity

    return expr
