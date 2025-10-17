# temoa/components/time.py
"""
This module contains components related to time indexing in the Temoa model.

It is responsible for:
-  Validating the core time sets (`time_exist`, `time_future`).
-  Validating the user-defined time-slice fractions (`TimeSegmentFraction`).
-  Creating the sequence of time slices (`time_next`) based on the chosen
    sequencing method (e.g., `seasonal_timeslices`, `consecutive_days`).
-  Creating and validating the superimposed sequential seasons used for
    seasonal storage and inter-season ramping constraints.
"""

from logging import getLogger
from typing import TYPE_CHECKING, Any

from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types import Period, Season, TimeOfDay


logger = getLogger(__name__)


# ============================================================================
# INITIAL VALIDATION FUNCTIONS
# These are called early in the model build to ensure time data is coherent.
# ============================================================================


def validate_time(M: 'TemoaModel') -> None:
    """
    We check for integer status here, rather than asking Pyomo to do this via
    a 'within=Integers' clause in the definition so that we can have a very
    specific error message.  If we instead use Pyomo's mechanism, the
    python invocation of Temoa throws an error (including a traceback)
    that has proven to be scary and/or impenetrable for the typical modeler.
    """
    logger.debug('Started validating time index')
    for year in M.time_exist:
        if isinstance(year, int):
            continue

        msg = f'Set "time_exist" requires integer-only elements.\n\n  Invalid element: "{year}"'
        logger.error(msg)
        raise Exception(msg)

    for year in M.time_future:
        if isinstance(year, int):
            continue

        msg = f'Set "time_future" requires integer-only elements.\n\n invalid element: "{year}"'
        logger.error(msg)
        raise Exception(msg)

    if len(M.time_future) < 2:
        msg = (
            'Set "time_future" needs at least 2 specified years.  \nTemoa '
            'treats the integer numbers specified in this set as boundary years \n'
            'between periods, and uses them to automatically ascertain the length \n'
            '(in years) of each period.  Note that this means that there will be \n'
            'one less optimization period than the number of elements in this set.'
        )

        logger.error(msg)
        raise RuntimeError(msg)

    # Ensure that the time_exist < time_future
    if len(M.time_exist) > 0:
        max_exist = max(M.time_exist)
        min_horizon = min(M.time_future)

        if not (max_exist < min_horizon):
            msg = (
                'All items in time_future must be larger than in time_exist.'
                '\ntime_exist max:   {}'
                '\ntime_future min: {}'
            )
            logger.error(msg.format(max_exist, min_horizon))
            raise Exception(msg.format(max_exist, min_horizon))
        logger.debug('Finished validating time')


def validate_SegFrac(M: 'TemoaModel') -> None:
    """Ensure that the segment fractions adds up to 1"""

    for p in M.time_optimize:
        expected_keys = {(p, s, d) for s in M.TimeSeason[p] for d in M.time_of_day}
        keys = {(_p, s, d) for _p, s, d in M.SegFrac.sparse_iterkeys() if _p == p}

        if expected_keys != keys:
            extra = keys.difference(expected_keys)
            missing = expected_keys.difference(keys)
            msg = (
                'TimeSegmentFraction elements for period {} do not match TimeSeason and TimeOfDay.'
                '\n\nIndices missing from TimeSegmentFraction:\n{}'
                '\n\nIndices in TimeSegmentFraction missing from TimeSeason/TimeOfDay:\n{}'
            ).format(p, missing, extra)
            logger.error(msg)
            raise ValueError(msg)

        total = sum(M.SegFrac[k] for k in keys)

        if abs(float(total) - 1.0) > 0.001:
            # We can't explicitly test for "!= 1.0" because of incremental rounding
            # errors associated with the specification of SegFrac by time slice,
            # but we check to make sure it is within the specified tolerance.

            def get_str_padding(obj: Any) -> int:
                return len(str(obj))

            key_padding = max(map(get_str_padding, keys))

            fmt = '%%-%ds = %%s' % key_padding
            # Works out to something like "%-25s = %s"

            items_list: list[tuple[tuple[Any, Any, Any], Any]] = sorted(
                [(k, M.SegFrac[k]) for k in keys]
            )
            items = '\n   '.join(fmt % (str(k), v) for k, v in items_list)

            msg = (
                'The values of TimeSegmentFraction do not sum to 1 for period {}. '
                'Each item in SegFrac represents a fraction of a year, so they must '
                'total to 1.  Current values:\n   {}\n\tsum = {}'
            ).format(p, items, total)
            logger.error(msg)
            raise Exception(msg)


def validate_TimeNext(M: 'TemoaModel') -> None:
    """
    If using this table, check that defined states are actually valid.
    TimeSegmentFraction is already compared to other tables so just compare to SegFrac.
    """
    # Only check TimeNext if it is actually being used
    if M.TimeSequencing.first() != 'manual':
        return

    segfrac_psd = set(M.SegFrac.sparse_iterkeys())
    time_next_psd = {(p, s, d) for p, s, d, s_next, d_next in M.TimeNext}
    time_next_psd_next = {(p, s_next, d_next) for p, s, d, s_next, d_next in M.TimeNext}

    missing_psd = segfrac_psd.difference(time_next_psd)
    missing_psd_next = segfrac_psd.difference(time_next_psd_next)
    if missing_psd or missing_psd_next:
        msg = (
            'Failed to build state sequence. '
            '\nThese states from TimeSegmentFraction were not given a next state:\n{}\n'
            '\nThese states from TimeSegmentFraction do not follow any state:\n{}'
        ).format(missing_psd, missing_psd_next)
        logger.error(msg)
        raise ValueError(msg)


# ============================================================================
# PYOMO SET INITIALIZERS AND PARAMETER RULES
# ============================================================================


def init_set_time_optimize(M: 'TemoaModel') -> list[int]:
    """Initializes the `time_optimize` set (all future years except the last)."""
    return sorted(M.time_future)[:-1]


def init_set_vintage_exist(M: 'TemoaModel') -> list[int]:
    """Initializes the `vintage_exist` set."""
    return sorted(M.time_exist)


def init_set_vintage_optimize(M: 'TemoaModel') -> list[int]:
    """Initializes the `vintage_optimize` set."""
    return sorted(M.time_optimize)


def SegFracPerSeason_rule(M: 'TemoaModel', p: 'Period', s: 'Season') -> float:
    """Rule to calculate the total fraction of a period represented by a season."""
    return sum(value(M.SegFrac[p, s, d]) for d in M.time_of_day if (p, s, d) in M.SegFrac)


def ParamPeriodLength(M: 'TemoaModel', p: 'Period') -> int:
    """Rule to calculate the length of each optimization period in years."""
    periods = sorted(M.time_future)
    i = periods.index(p)
    return periods[i + 1] - periods[i]


# ============================================================================
# HELPER FUNCTIONS FOR TIME SEQUENCING
# ============================================================================


def loop_period_next_timeslice(
    M: 'TemoaModel', p: 'Period', s: 'Season', d: 'TimeOfDay'
) -> tuple[str, str]:
    # Final time slice of final season (end of period)
    # Loop state back to initial state of first season
    # Loop the period
    if s == M.TimeSeason[p].last() and d == M.time_of_day.last():
        s_next = M.TimeSeason[p].first()
        d_next = M.time_of_day.first()

    # Last time slice of any season that is NOT the last season
    # Carry state to initial state of next season
    # Carry state between seasons
    elif d == M.time_of_day.last():
        s_next = M.TimeSeason[p].next(s)
        d_next = M.time_of_day.first()

    # Any other time slice
    # Carry state to next time slice in the same season
    # Continuing through this season
    else:
        s_next = s
        d_next = M.time_of_day.next(d)

    return s_next, d_next


def loop_season_next_timeslice(
    M: 'TemoaModel', p: 'Period', s: 'Season', d: 'TimeOfDay'
) -> tuple[str, str]:
    # We loop each season so never carrying state between seasons
    s_next = s

    # Final time slice of any season
    # Loop state back to initial state of same season
    # Loop each season
    if d == M.time_of_day.last():
        d_next = M.time_of_day.first()

    # Any other time slice
    # Carry state to next time slice in the same season
    # Continuing through this season
    else:
        d_next = M.time_of_day.next(d)

    return s_next, d_next


# ============================================================================
# PRE-COMPUTATION & SEQUENCE CREATION
# ============================================================================


def CreateTimeSequence(M: 'TemoaModel') -> None:
    logger.debug('Creating sequence of time slices.')

    # Establishing sequence of states
    match M.TimeSequencing.first():
        case 'consecutive_days':
            msg = 'Running a consecutive days database.'
            for p in M.time_optimize:
                for s, d in M.TimeSeason[p] * M.time_of_day:
                    M.time_next[p, s, d] = loop_period_next_timeslice(M, p, s, d)
        case 'seasonal_timeslices':
            msg = 'Running a seasonal time slice database.'
            for p in M.time_optimize:
                for s, d in M.TimeSeason[p] * M.time_of_day:
                    M.time_next[p, s, d] = loop_season_next_timeslice(M, p, s, d)
        case 'representative_periods':
            msg = 'Running a representative periods database.'
            for p in M.time_optimize:
                for s, d in M.TimeSeason[p] * M.time_of_day:
                    M.time_next[p, s, d] = loop_season_next_timeslice(M, p, s, d)
        case 'manual':
            # Hidden feature. Define the sequence directly in the TimeNext table
            msg = 'Pulling time sequence from TimeNext table.'
            for p, s, d, s_next, d_next in M.TimeNext:
                M.time_next[p, s, d] = s_next, d_next
        case _:
            # This should have been caught in hybrid_loader
            msg = f"Invalid time sequencing parameter loaded '{M.TimeSequencing.first()}'. Likely code error."
            logger.error(msg)
            raise ValueError(msg)

    msg += ' This behaviour can be changed using the time_sequencing parameter in the config file. '
    logger.info(msg)

    logger.debug('Creating superimposed sequential seasons.')

    # Superimposed sequential seasons
    for p in M.time_optimize:
        seasons = [(s_seq, s) for _p, s_seq, s in M.ordered_season_sequential if _p == p]
        for i, (s_seq, s) in enumerate(seasons):
            M.sequential_to_season[p, s_seq] = s
            if (s_seq, s) == seasons[-1]:
                M.time_next_sequential[p, s_seq] = seasons[0][0]
            else:
                M.time_next_sequential[p, s_seq] = seasons[i + 1][0]

    logger.debug('Created time sequence.')


def CreateTimeSeasonSequential(M: 'TemoaModel') -> None:
    if all(
        (
            not M.tech_seasonal_storage,
            not M.RampUpHourly,
            not M.RampDownHourly,
        )
    ):
        # Don't need it anyway
        return

    if not M.TimeSeasonSequential:
        if M.TimeSequencing.first() in ('consecutive_days', 'seasonal_timeslices'):
            logger.info(
                'No data in TimeSeasonSequential. By default, assuming sequential seasons '
                'match TimeSeason and TimeSegmentFraction.'
            )
            for s in M.time_season:
                M.time_season_sequential.add(s)
            for p in M.TimeSeason:
                for s in M.TimeSeason[p]:
                    M.ordered_season_sequential.add((p, s, s))
                    M.TimeSeasonSequential[p, s, s] = value(M.SegFracPerSeason[p, s]) * value(
                        M.DaysPerPeriod
                    )

        else:
            msg = (
                f'No data in TimeSeasonSequential but time_sequencing parameter set to {M.TimeSequencing.first()} '
                'and inter-season features used. TimeSeasonSequential must be filled for this type of time '
                'sequencing if seasonal storage or inter-season constraints like RampUp/RampDown are used. Check '
                'the config file.'
            )
            logger.error(msg)
            raise ValueError(msg)

    sequential = {}
    prev_n = 0
    for p, s_seq, s in M.TimeSeasonSequential.sparse_iterkeys():
        num_days = value(M.TimeSeasonSequential[p, s_seq, s])
        if (
            M.TimeSequencing.first() == 'consecutive_days'
            and prev_n
            and abs(num_days - prev_n) >= 0.001
        ):
            msg = (
                'TimeSequencing set to consecutive_days but two consecutive seasons do not represent the same '
                f'number of days. This discontinuity will lead to bad model behaviour: {p, s}, days: {num_days}. '
                f'Previous number of days: {prev_n}. Check the config file for more information.'
            )
            logger.error(msg)
            raise ValueError(msg)
        prev_n = num_days  # for validating next in sequence

        # Regardless of their order, make sure the total number of days adds up
        if (p, s) not in sequential:
            sequential[p, s] = 0
        sequential[p, s] += num_days

    # Check that TimeSeasonSequential num_days total to number of days in each period
    count_total = {}  # {p: n} total days per period according to TimeSeasonSequential
    for p in M.time_optimize:
        count_total[p] = sum(sequential[p, s] for _p, s in sequential if _p == p)
        if abs(count_total[p] - value(M.DaysPerPeriod)) >= 0.001:
            logger.warning(
                f'Sum of num_days in TimeSeasonSequential ({count_total[p]}) '
                f'for period {p} does not sum to days_per_period ({value(M.DaysPerPeriod)}) '
                'from the MetaData table.'
            )

    # Check that seasons using in storage seasons are actual seasons
    for p, s in sequential:
        if (p, s) not in M.SegFracPerSeason:
            msg = (
                f'Period-season index {(p, s)} that does not exist in '
                'TimeSegmentFraction referenced in TimeSeasonSequential .'
            )
            logger.error(msg)
            raise ValueError(msg)

    for p, s in M.SegFracPerSeason.sparse_iterkeys():
        if s not in M.TimeSeason[p]:
            continue

        # Check that all seasons are used in sequential seasons
        if (p, s) not in sequential:
            msg = f'Period-season index {(p, s)} absent from TimeSeasonSequential'
            logger.warning(msg)

        # Check that the two tables agree on the total seasonal composition of each period
        segfrac = value(M.SegFracPerSeason[p, s])
        segfracseq = sequential[p, s] / count_total[p]
        if abs(segfrac - segfracseq) >= 0.001:
            msg = (
                'Discrepancy of total period-season composition between '
                'TimeSegmentFraction and TimeSeasonSequential. Total fraction of each '
                'period assigned to each season should match: '
                f'TimeSegmentFraction: {(p, s, value(M.SegFracPerSeason[p, s]))}'
                f', TimeSeasonSequential: {(p, s, segfracseq)}'
            )
            logger.warning(msg)
