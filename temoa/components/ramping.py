from typing import TYPE_CHECKING

from pyomo.core import Set

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


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
