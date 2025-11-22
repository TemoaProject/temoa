# temoa/components/time.py
"""
This module contains components related to time indexing in the Temoa model.

It is responsible for:
-  Validating the core time sets (`time_exist`, `time_future`).
-  Validating the user-defined time-slice fractions (`time_segment_fraction`).
-  Creating the sequence of time slices (`time_next`) based on the chosen
    sequencing method (e.g., `seasonal_timeslices`, `consecutive_days`).
-  Creating and validating the superimposed sequential seasons used for
    seasonal storage and inter-season ramping constraints.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types import Period, Season, TimeOfDay


logger = getLogger(__name__)


# ============================================================================
# INITIAL VALIDATION FUNCTIONS
# These are called early in the model build to ensure time data is coherent.
# ============================================================================


def validate_time(model: TemoaModel) -> None:
    """
    We check for integer status here, rather than asking Pyomo to do this via
    a 'within=Integers' clause in the definition so that we can have a very
    specific error message.  If we instead use Pyomo's mechanism, the
    python invocation of Temoa throws an error (including a traceback)
    that has proven to be scary and/or impenetrable for the typical modeler.
    """
    logger.debug('Started validating time index')
    for year in model.time_exist:
        if isinstance(year, int):
            continue

        msg: str = (
            f'Set "time_exist" requires integer-only elements.\n\n  Invalid element: "{year}"'
        )
        logger.error(msg)
        raise Exception(msg)

    for year in model.time_future:
        if isinstance(year, int):
            continue

        msg = f'Set "time_future" requires integer-only elements.\n\n invalid element: "{year}"'
        logger.error(msg)
        raise Exception(msg)

    if len(model.time_future) < 2:
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
    if len(model.time_exist) > 0:
        max_exist: int = max(model.time_exist)
        min_horizon: int = min(model.time_future)

        if not (max_exist < min_horizon):
            msg = (
                'All items in time_future must be larger than in time_exist.'
                '\ntime_exist max:   {}'
                '\ntime_future min: {}'
            )
            logger.error(msg.format(max_exist, min_horizon))
            raise Exception(msg.format(max_exist, min_horizon))
        logger.debug('Finished validating time')


def validate_segment_fraction(model: TemoaModel) -> None:
    """Ensure that the segment fractions adds up to 1"""

    for p in model.time_optimize:
        expected_keys: set[tuple[int, str, str]] = {
            (p, s, d) for s in model.time_season[p] for d in model.time_of_day
        }
        keys: set[tuple[int, str, str]] = {
            (_p, s, d) for _p, s, d in model.segment_fraction.sparse_iterkeys() if _p == p
        }

        if expected_keys != keys:
            extra: set[tuple[int, str, str]] = keys.difference(expected_keys)
            missing: set[tuple[int, str, str]] = expected_keys.difference(keys)
            msg: str = (
                f'time_segment_fraction elements for period {p} do not match time_season and '
                'time_of_day.'
                f'\n\nIndices missing from time_segment_fraction:\n{missing}'
                f'\n\nIndices in time_segment_fraction missing from time_season/time_of_day:\n'
                f'{extra}'
            )
            logger.error(msg)
            raise ValueError(msg)

        total: float = sum(value(model.segment_fraction[k]) for k in keys)

        if abs(float(total) - 1.0) > 0.001:
            # We can't explicitly test for "!= 1.0" because of incremental rounding
            # errors associated with the specification of segment_fraction by time slice,
            # but we check to make sure it is within the specified tolerance.

            def get_str_padding(obj: object) -> int:
                return len(str(obj))

            key_padding: int = max(map(get_str_padding, keys))

            # Works out to something like "%-25s = %s"

            items_list: list[tuple[tuple[object, object, object], object]] = sorted(
                [(k, model.segment_fraction[k]) for k in keys]
            )
            items: str = '\n   '.join(f'{str(k):<{key_padding}} = {v}' for k, v in items_list)

            msg = (
                f'The values of time_segment_fraction do not sum to 1 for period {p}. '
                'Each item in segment_fraction represents a fraction of a year, so they must '
                f'total to 1.  Current values:\n   {items}\n\tsum = {total}'
            )
            logger.error(msg)
            raise Exception(msg)


def validate_time_manual(model: TemoaModel) -> None:
    """
    If using the manual sequencing table, check that all defined states are valid.
    segment_fraction keys are already validated, so we compare time_manual against those.

    """
    # Only check TimeNext if it is actually being used
    if model.time_sequencing.first() != 'manual':
        return

    segment_fraction_psd: set[tuple[int, str, str]] = set(model.segment_fraction.sparse_iterkeys())
    time_manual_psd: set[tuple[int, str, str]] = {
        (p, s, d) for p, s, d, s_next, d_next in model.time_manual
    }
    time_manual_psd_next: set[tuple[int, str, str]] = {
        (p, s_next, d_next) for p, s, d, s_next, d_next in model.time_manual
    }

    missing_psd: set[tuple[int, str, str]] = segment_fraction_psd.difference(time_manual_psd)
    missing_psd_next: set[tuple[int, str, str]] = segment_fraction_psd.difference(
        time_manual_psd_next
    )
    if missing_psd or missing_psd_next:
        msg: str = (
            'Failed to build state sequence. '
            f'\nThese states from time_segment_fraction were not given a next state:\n'
            f'{missing_psd}\n'
            f'\nThese states from time_segment_fraction do not follow any state:\n'
            f'{missing_psd_next}'
        )
        logger.error(msg)
        raise ValueError(msg)


# ============================================================================
# PYOMO SET INITIALIZERS AND PARAMETER RULES
# ============================================================================


def init_set_time_optimize(model: TemoaModel) -> list[int]:
    """Initializes the `time_optimize` set (all future years except the last)."""
    return sorted(model.time_future)[:-1]


def init_set_vintage_exist(model: TemoaModel) -> list[int]:
    """Initializes the `vintage_exist` set."""
    return sorted(model.time_exist)


def init_set_vintage_optimize(model: TemoaModel) -> list[int]:
    """Initializes the `vintage_optimize` set."""
    return sorted(model.time_optimize)


def segment_fraction_per_season_rule(model: TemoaModel, p: Period, s: Season) -> float:
    """Rule to calculate the total fraction of a period represented by a season."""
    return sum(
        value(model.segment_fraction[p, s, d])
        for d in model.time_of_day
        if (p, s, d) in model.segment_fraction
    )


def param_period_length(model: TemoaModel, p: Period) -> int:
    """Rule to calculate the length of each optimization period in years."""
    periods: list[int] = sorted(model.time_future)
    i: int = periods.index(p)
    return periods[i + 1] - periods[i]


# ============================================================================
# HELPER FUNCTIONS FOR TIME SEQUENCING
# ============================================================================


def loop_period_next_timeslice(
    model: TemoaModel, p: Period, s: Season, d: TimeOfDay
) -> tuple[Season, TimeOfDay]:
    # Final time slice of final season (end of period)
    # Loop state back to initial state of first season
    # Loop the period
    if s == model.time_season[p].last() and d == model.time_of_day.last():
        s_next: Season = model.time_season[p].first()
        d_next: TimeOfDay = model.time_of_day.first()

    # Last time slice of any season that is NOT the last season
    # Carry state to initial state of next season
    # Carry state between seasons
    elif d == model.time_of_day.last():
        s_next = model.time_season[p].next(s)
        d_next = model.time_of_day.first()

    # Any other time slice
    # Carry state to next time slice in the same season
    # Continuing through this season
    else:
        s_next = s
        d_next = model.time_of_day.next(d)

    return s_next, d_next


def loop_season_next_timeslice(
    model: TemoaModel, p: Period, s: Season, d: TimeOfDay
) -> tuple[Season, TimeOfDay]:
    # We loop each season so never carrying state between seasons
    s_next: Season = s

    # Final time slice of any season
    # Loop state back to initial state of same season
    # Loop each season
    if d == model.time_of_day.last():
        d_next = model.time_of_day.first()

    # Any other time slice
    # Carry state to next time slice in the same season
    # Continuing through this season
    else:
        d_next = model.time_of_day.next(d)

    return s_next, d_next


# ============================================================================
# PRE-COMPUTATION & SEQUENCE CREATION
# ============================================================================


def create_time_sequence(model: TemoaModel) -> None:
    logger.debug('Creating sequence of time slices.')

    # Establishing sequence of states
    match model.time_sequencing.first():
        case 'consecutive_days':
            msg: str = 'Running a consecutive days database.'
            for p in model.time_optimize:
                for s, d in model.time_season[p] * model.time_of_day:
                    model.time_next[p, s, d] = loop_period_next_timeslice(model, p, s, d)
        case 'seasonal_timeslices':
            msg = 'Running a seasonal time slice database.'
            for p in model.time_optimize:
                for s, d in model.time_season[p] * model.time_of_day:
                    model.time_next[p, s, d] = loop_season_next_timeslice(model, p, s, d)
        case 'representative_periods':
            msg = 'Running a representative periods database.'
            for p in model.time_optimize:
                for s, d in model.time_season[p] * model.time_of_day:
                    model.time_next[p, s, d] = loop_season_next_timeslice(model, p, s, d)
        case 'manual':
            # Hidden feature. Define the sequence directly in the time_manual table
            msg = 'Pulling time sequence from time_manual table.'
            for p, s, d, s_next, d_next in model.time_manual:
                model.time_next[p, s, d] = s_next, d_next
        case _:
            # This should have been caught in hybrid_loader
            msg = (
                f"Invalid time sequencing parameter loaded '{model.time_sequencing.first()}'. "
                'Likely code error.'
            )
            logger.error(msg)
            raise ValueError(msg)

    msg += ' This behaviour can be changed using the time_sequencing parameter in the config file. '
    logger.info(msg)

    logger.debug('Creating superimposed sequential seasons.')

    # Superimposed sequential seasons
    for p in model.time_optimize:
        seasons: list[tuple[Season, Season]] = [
            (s_seq, s) for _p, s_seq, s in model.ordered_season_sequential if _p == p
        ]
        for i, (s_seq, s) in enumerate(seasons):
            model.sequential_to_season[p, s_seq] = s
            if (s_seq, s) == seasons[-1]:
                model.time_next_sequential[p, s_seq] = seasons[0][0]
            else:
                model.time_next_sequential[p, s_seq] = seasons[i + 1][0]

    logger.debug('Created time sequence.')


def create_time_season_to_sequential(model: TemoaModel) -> None:
    if all(
        (
            not model.tech_seasonal_storage,
            not model.ramp_up_hourly,
            not model.ramp_down_hourly,
        )
    ):
        # Don't need it anyway
        return

    if not model.time_season_sequential:
        if model.time_sequencing.first() in ('consecutive_days', 'seasonal_timeslices'):
            logger.info(
                'No data in time_season_sequential. By default, assuming sequential seasons '
                'match time_season and time_segment_fraction.'
            )
            for s in model.time_season_all:
                model.time_season_to_sequential.add(s)
            for p in model.time_season:
                for s in model.time_season[p]:
                    model.ordered_season_sequential.add((p, s, s))
                    model.time_season_sequential[p, s, s] = value(
                        model.segment_fraction_per_season[p, s]
                    ) * value(model.days_per_period)

        else:
            msg = (
                f'No data in time_season_sequential but time_sequencing parameter set to '
                f'{model.time_sequencing.first()} and inter-season features used. '
                'time_season_sequential must be filled for this type of time sequencing if '
                'seasonal storage or inter-season constraints like ramp_up/ramp_down are used. '
                'Check '
                'the config file.'
            )
            logger.error(msg)
            raise ValueError(msg)

    sequential: dict[tuple[int, str], float] = {}
    prev_n: float = 0
    for p, s_seq, s in model.time_season_sequential.sparse_iterkeys():
        num_days: float = value(model.time_season_sequential[p, s_seq, s])
        if (
            model.time_sequencing.first() == 'consecutive_days'
            and prev_n
            and abs(num_days - prev_n) >= 0.001
        ):
            msg = (
                'time_sequencing set to consecutive_days but two consecutive seasons do not '
                'represent the same number of days. This discontinuity will lead to bad model '
                f'behaviour: {p, s}, days: {num_days}. '
                f'Previous number of days: {prev_n}. Check the config file for more information.'
            )
            logger.error(msg)
            raise ValueError(msg)
        prev_n = num_days  # for validating next in sequence

        # Regardless of their order, make sure the total number of days adds up
        if (p, s) not in sequential:
            sequential[p, s] = 0
        sequential[p, s] += num_days

    # Check that time_season_sequential num_days total to number of days in each period
    count_total: dict[
        int, float
    ] = {}  # {p: n} total days per period according to time_season_sequential
    for p in model.time_optimize:
        count_total[p] = sum(sequential[p, s] for _p, s in sequential if _p == p)
        if abs(count_total[p] - value(model.days_per_period)) >= 0.001:
            logger.warning(
                'Sum of num_days in time_season_sequential (%s) '
                'for period %s does not sum to days_per_period (%s) '
                'from the MetaData table.',
                count_total[p],
                p,
                value(model.days_per_period),
            )

    # Check that seasons using in storage seasons are actual seasons
    for p, s in sequential:
        if (p, s) not in model.segment_fraction_per_season:
            msg = (
                f'Period-season index {(p, s)} that does not exist in '
                'time_segment_fraction referenced in time_season_sequential .'
            )
            logger.error(msg)
            raise ValueError(msg)

    for p, s in model.segment_fraction_per_season.sparse_iterkeys():
        if s not in model.time_season[p]:
            continue

        # Check that all seasons are used in sequential seasons
        if (p, s) not in sequential:
            msg = f'Period-season index {(p, s)} absent from time_season_sequential'
            logger.warning(msg)

        # Check that the two tables agree on the total seasonal composition of each period
        segment_fraction = value(model.segment_fraction_per_season[p, s])
        segment_fraction_seq = sequential[p, s] / count_total[p]
        if abs(segment_fraction - segment_fraction_seq) >= 0.001:
            msg = (
                'Discrepancy of total period-season composition between '
                'time_segment_fraction and time_season_sequential. Total fraction of each '
                'period assigned to each season should match: '
                f'time_segment_fraction: {(p, s, value(model.segment_fraction_per_season[p, s]))}'
                f', time_season_sequential: {(p, s, segment_fraction_seq)}'
            )
            logger.warning(msg)
