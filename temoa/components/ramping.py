from typing import TYPE_CHECKING

from logging import getLogger
from pyomo.environ import Constraint, value
from pyomo.core import Set

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

logger = getLogger(__name__)


def RampUpDayConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v)
        for r, p, t in M.rampUpVintages
        for v in M.rampUpVintages[r, p, t]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    return indices


def RampDownDayConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v)
        for r, p, t in M.rampDownVintages
        for v in M.rampDownVintages[r, p, t]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    return indices


def RampUpSeasonConstraintIndices(M: 'TemoaModel'):
    if M.TimeSequencing.first() == 'consecutive_days':
        return Set.Skip  # dont need this constraint

    # s, s_next indexing ensures we dont build redundant constraints
    indices = set(
        (r, p, s, s_next, t, v)
        for r, p, t in M.rampUpVintages
        for v in M.rampUpVintages[r, p, t]
        for _p, s_seq, s in M.ordered_season_sequential
        if _p == p
        for s_seq_next in (M.time_next_sequential[p, s_seq],)  # next sequential season
        for s_next in (
            M.sequential_to_season[p, s_seq_next],
        )  # next sequential season's matching season
        if s_next
        != M.time_next[p, s, M.time_of_day.last()][0]  # to avoid redundancy on RampDay constraint
    )

    return indices


def RampDownSeasonConstraintIndices(M: 'TemoaModel'):
    if M.TimeSequencing.first() == 'consecutive_days':
        return Set.Skip  # dont need this constraint

    # s, s_next indexing ensures we dont build redundant constraints
    indices = set(
        (r, p, s, s_next, t, v)
        for r, p, t in M.rampDownVintages
        for v in M.rampDownVintages[r, p, t]
        for _p, s_seq, s in M.ordered_season_sequential
        for s_seq_next in (M.time_next_sequential[p, s_seq],)  # next sequential season
        for s_next in (
            M.sequential_to_season[p, s_seq_next],
        )  # next sequential season's matching season
        if s_next
        != M.time_next[p, s, M.time_of_day.last()][0]  # to avoid redundancy on RampDay constraint
    )

    return indices


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
