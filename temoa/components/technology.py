# temoa/components/technology.py
"""
Defines the core technology-related components of the Temoa model.

This module is the foundation of the model, responsible for:
-  Pre-computing the core data structures that link technologies to commodities,
    time periods, and vintages based on the `efficiency` parameter.
-  Handling technology lifetimes, including survival curve validation and interpolation.
-  Defining Pyomo index sets for core technology parameters.
-  Validating model inputs related to technologies, efficiencies, and commodities.
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, cast

from pyomo.environ import value

if TYPE_CHECKING:
    from collections.abc import Iterable

    from temoa.core.model import TemoaModel
    from temoa.types import Period, Region, Technology, Vintage

logger = getLogger(__name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def gather_group_techs(model: TemoaModel, t_or_g: Technology) -> Iterable[Technology]:
    if t_or_g in model.tech_group_names:
        return model.tech_group_members[t_or_g]
    elif '+' in t_or_g:
        return [cast('Technology', tech) for tech in t_or_g.split('+')]
    else:
        return (t_or_g,)


# ============================================================================
# PYOMO INDEX SETS AND PARAMETER RULES
# ============================================================================


def model_process_life_indices(
    model: TemoaModel,
) -> set[tuple[Region, Period, Technology, Vintage]] | None:
    """
    Returns the set of sensical (region, period, tech, vintage) tuples.  The tuple indicates
    the periods in which a process is active, distinct from TechLifeFracIndices that
    returns indices only for processes that EOL mid-period.
    """
    return model.active_activity_rptv


def lifetime_process_indices(model: TemoaModel) -> set[tuple[Region, Technology, Vintage]]:
    """
    Based on the efficiency parameter's indices, this function returns the set of
    process indices that may be specified in the lifetime_process parameter.
    """
    indices = {(r, t, v) for r, i, t, v, o in model.efficiency.sparse_iterkeys()}

    return indices


def get_default_survival(
    model: TemoaModel, r: Region, p: Period, t: Technology, v: Vintage
) -> float:
    """
    Getting lifetime_survival_curve where it is not defined
    If this is a survival curve process, return 0 (likely beyond EOL)
    Otherwise return 1 (no survival curve based EOL)
    """
    return 0.0 if model.is_survival_curve_process[r, t, v] else 1.0


def get_default_process_lifetime(model: TemoaModel, r: Region, t: Technology, v: Vintage) -> int:
    """
    This initializer used to initialize the lifetime_process parameter from lifetime_tech where
    needed

    Priority:
        1.  Specified in lifetime_process data (provided as a fill and would not call this function)
        2.  Specified in lifetime_tech data
        3.  The default value from the lifetime_tech param (automatic)
    :param M: generic model reference (not used)
    :param r: region
    :param t: tech
    :param v: vintage
    :return: the final lifetime value
    """
    return value(model.lifetime_tech[r, t])


def param_process_life_fraction_rule(
    model: TemoaModel, r: Region, p: Period, t: Technology, v: Vintage
) -> float:
    r"""
    Get the effective capacity of a process :math:`<r, t, v>` in a period :math:`p`.

    Accounts for mid-period end of life or average survival over the period
    for processes using survival curves.
    """

    period_length = value(model.period_length[p])

    if model.is_survival_curve_process[r, t, v]:
        # Sum survival fraction over the period
        years_remaining = sum(
            value(model.lifetime_survival_curve[r, _p, t, v])
            for _p in range(p, p + period_length, 1)
        )
    else:
        # Remaining life years within the EOL period
        years_remaining = v + value(model.lifetime_process[r, t, v]) - p

    if years_remaining >= period_length:
        # try to avoid floating point round-off errors for the common case.
        return 1

    frac = years_remaining / float(period_length)
    return frac


# ============================================================================
# PRE-COMPUTATION AND VALIDATION FUNCTIONS
# ============================================================================


def populate_core_dictionaries(model: TemoaModel) -> None:
    """
    Populates the core sparse dictionaries from the `efficiency` parameter.

    This function is foundational for creating the sparse indices used throughout
    the model, defining process relationships, inputs, outputs, and active periods.

    Populates:
        - M.process_inputs, M.process_outputs
        - M.commodity_down_stream_process, M.commodity_up_stream_process
        - M.process_outputs_by_input, M.process_inputs_by_output
        - M.process_vintages, M.process_periods
        - M.used_techs
    """
    logger.debug('Populating core sparse dictionaries from efficiency parameter.')
    first_period = min(model.time_future)
    exist_indices = model.existing_capacity.sparse_keys()

    for r, i, t, v, o in model.efficiency.sparse_iterkeys():
        # A. Basic data validation and warnings
        process = (r, t, v)
        lifetime = value(model.lifetime_process[process])
        if v in model.vintage_exist:
            if process not in exist_indices and t not in model.tech_uncap:
                logger.warning(
                    'Warning: %s has a specified efficiency, but does not '
                    'have any existing install base (existing_capacity).',
                    process,
                )
                continue
            if t not in model.tech_uncap and model.existing_capacity[process] == 0:
                logger.warning(
                    'Notice: Unnecessary specification of existing_capacity for %s. '
                    'Declaring a capacity of zero may be omitted.',
                    process,
                )
                continue
            if v + lifetime <= first_period:
                logger.info(
                    '%s specified as existing_capacity, but its '
                    'lifetime (%s years) does not extend past the '
                    'beginning of time_future (%s).',
                    process,
                    lifetime,
                    first_period,
                )

        if model.efficiency[r, i, t, v, o] == 0:
            logger.info(
                'Notice: Unnecessary specification of efficiency for %s. '
                'Specifying an efficiency of zero may be omitted.',
                (r, i, t, v, o),
            )
            continue

        model.used_techs.add(t)

        # B. Loop through time periods to build time-dependent relationships
        for p in model.time_optimize:
            # Skip if tech is not invented or is already retired
            if p < v or v + lifetime <= p:
                continue

            pindex = (r, p, t, v)

            # C. Initialize dictionary keys if not present
            if pindex not in model.process_inputs:
                model.process_inputs[pindex] = set()
                model.process_outputs[pindex] = set()
            if (r, p, i) not in model.commodity_down_stream_process:
                model.commodity_down_stream_process[r, p, i] = set()
            if (r, p, o) not in model.commodity_up_stream_process:
                model.commodity_up_stream_process[r, p, o] = set()
            if (r, p, t, v, i) not in model.process_outputs_by_input:
                model.process_outputs_by_input[r, p, t, v, i] = set()
            if (r, p, t, v, o) not in model.process_inputs_by_output:
                model.process_inputs_by_output[r, p, t, v, o] = set()
            if (r, p, t) not in model.process_vintages:
                model.process_vintages[r, p, t] = set()
            if (r, t, v) not in model.process_periods:
                model.process_periods[r, t, v] = set()

            # D. Populate the dictionaries
            model.process_inputs[pindex].add(i)
            model.process_outputs[pindex].add(o)
            model.commodity_down_stream_process[r, p, i].add((t, v))
            model.commodity_up_stream_process[r, p, o].add((t, v))
            model.process_outputs_by_input[r, p, t, v, i].add(o)
            model.process_inputs_by_output[r, p, t, v, o].add(i)
            model.process_vintages[r, p, t].add(v)
            model.process_periods[r, t, v].add(p)


def create_survival_curve(model: TemoaModel) -> None:
    rtv_interpolated = set()  # so we only need one warning

    for r, _, t, v, _ in model.efficiency.sparse_iterkeys():
        model.is_survival_curve_process[r, t, v] = False  # by default

    # Collect rptv indices into (r, t, v): p dictionary
    for r, p, t, v in model.lifetime_survival_curve.sparse_iterkeys():
        if (r, t, v) not in model.survival_curve_periods:
            model.survival_curve_periods[r, t, v] = set()
        model.survival_curve_periods[r, t, v].add(p)
        model.is_survival_curve_process[r, t, v] = True

    # Go through all the periods for each (r, t, v) in order
    for r, t, v in model.survival_curve_periods:
        periods_rtv: list[int] = sorted(model.survival_curve_periods[r, t, v])

        p_first = periods_rtv[0]
        p_last = periods_rtv[-1]

        if p_first != v:
            msg = (
                'lifetime_survival_curve must be defined starting in the vintage period. Must '
                f'define ({r}, >{v}<, {t}, {v})'
            )
            logger.error(msg)
            raise ValueError(msg)

        if value(model.lifetime_survival_curve[r, v, t, v]) != 1:
            msg_str = (
                'lifetime_survival_curve must begin at 1 for calculating annual retirements. '
                f'Got {value(model.lifetime_survival_curve[r, v, t, v])} for ({r}, {v}, {t}, {v})'
            )
            logger.error(msg_str)
            raise ValueError(msg_str)

        # Collect a list of processes that needed to be interpolated, for warning
        if periods_rtv != list(range(p_first, p_last + 1, 1)):
            rtv_interpolated.add((r, t, v))

        between_periods: list[Period] = []
        for i, p in enumerate(periods_rtv):
            if i == 0:
                continue  # Cant look back from first period. Could be zero but hey why not

            # Check that the survival curve monotonically decreases
            p_prev = periods_rtv[i - 1]
            lsc = value(model.lifetime_survival_curve[r, p, t, v])
            lsc_prev = value(model.lifetime_survival_curve[r, p_prev, t, v])
            if lsc - lsc_prev > 0.0001:
                msg = (
                    f'lifetime_survival_curve fraction increases going forward in time from '
                    f'{(r, p_prev, t, v)} to {(r, p, t, v)}. '
                    'This is not allowed.'
                )
                logger.error(msg)
                raise ValueError(msg)

            if p - p_prev > 1:
                _between_periods = [cast('Period', _p) for _p in range(p_prev + 1, p, 1)]
                for _p in _between_periods:
                    x = (_p - p_prev) / (p - p_prev)
                    lsc_x = lsc_prev + x * (lsc - lsc_prev)
                    model.lifetime_survival_curve[r, _p, t, v] = lsc_x
                between_periods.extend(_between_periods)

            if lsc < 0.0001:
                if p != p_last:
                    msg = (
                        'There is no need to continue a survival curve beyond fraction ~= 0. '
                        f'ignoring periods beyond {p} for ({r, t, v})'
                    )
                    logger.info(msg)

                # Make sure the lifetime for this process aligns with survival curve end
                if value(model.lifetime_process[r, t, v]) < p - v:
                    msg = (
                        f'The lifetime_process parameter for process ({r, t, v}) with survival '
                        f'curve does not extend beyond the end of that survival curve in {p}. To '
                        'agree with '
                        f'the survival curve, set lifetime_process[{r, t, v}] >= {p - v}'
                    )
                    logger.error(msg)
                    raise ValueError(msg)
                elif value(model.lifetime_process[r, t, v]) != p - v:
                    msg = (
                        f'The lifetime_process parameter for process ({r, t, v}) with survival '
                        'curve '
                        f'does match the end of that survival curve in {p}. This will waste '
                        'compute. To agree with the survival curve and suppress this warning, set '
                        f'lifetime_process[{r, t, v}] = {p - v}'
                    )
                    logger.warning(msg)

                continue

            # Flag if the last period is not fraction = 0. This is important for investment costs
            if p == p_last and lsc > 0.0001:
                msg = (
                    'Any defined survival curve must continue to zero for the purposes of '
                    'investment cost accounting, even if this period would extend beyond '
                    f'defined future periods. Continue ({r, t, v}) to fraction == 0.'
                )
                logger.error(msg)
                raise ValueError(msg)

        model.survival_curve_periods[r, t, v].update(between_periods)

    if rtv_interpolated:
        logger.info(
            'For the purposes of investment cost accounting, lifetime_survival_curve must be '
            'defined for each individual year. Gaps between defined years will be filled by '
            'linear interpolation. Otherwise, these individual years can be defined manually. '
            'Interpolated processes: %s',
            list(rtv_interpolated),
        )


def check_efficiency_indices(model: TemoaModel) -> None:
    """
    Ensure that there are no unused items in any of the efficiency index sets.
    """
    # TODO:  This could be upgraded to scan for finer resolution
    #        by checking by REGION and PERIOD...  Each region/period is unique.
    c_physical = {i for r, i, t, v, o in model.efficiency.sparse_iterkeys()}
    c_physical = c_physical | {i for r, i, t, v in model.construction_input.sparse_iterkeys()}
    techs = {t for r, i, t, v, o in model.efficiency.sparse_iterkeys()}
    c_outputs = {o for r, i, t, v, o in model.efficiency.sparse_iterkeys()}
    c_outputs = c_outputs | {o for r, t, v, o in model.end_of_life_output.sparse_iterkeys()}

    symdiff = c_physical.symmetric_difference(model.commodity_physical)
    if symdiff:
        msg = (
            'Unused or unspecified physical carriers.  Either add or remove '
            'the following elements to the Set commodity_physical.'
            '\n\n    Element(s): {}'
        )
        symdiff_str: set[str] = {str(i) for i in symdiff}
        f_msg = msg.format(', '.join(symdiff_str))
        logger.error(f_msg)
        raise ValueError(f_msg)

    symdiff = techs.symmetric_difference(model.tech_all)
    if symdiff:
        msg = (
            'Unused or unspecified technologies.  Either add or remove '
            'the following technology(ies) to the tech_resource or '
            'tech_production Sets.\n\n    Technology(ies): {}'
        )
        symdiff_str2: set[str] = {str(i) for i in symdiff}
        f_msg = msg.format(', '.join(symdiff_str2))
        logger.error(f_msg)
        raise ValueError(f_msg)

    diff = model.commodity_demand - c_outputs
    if diff:
        msg = (
            'Unused or unspecified outputs.  Either add or remove the '
            'following elements to the commodity_demand Set.'
            '\n\n    Element(s): {}'
        )
        diff_str = (str(i) for i in diff)
        f_msg = msg.format(', '.join(diff_str))
        logger.error(f_msg)
        raise ValueError(f_msg)


def check_efficiency_variable(model: TemoaModel) -> None:
    count_rpitvo = {}
    # Pull non-variable efficiency by default
    for r, i, t, v, o in model.efficiency.sparse_iterkeys():
        if (r, t, v) not in model.process_periods:
            # Probably an existing vintage that retires in p0
            # Still want it for end of life flows
            continue
        for p in model.process_periods[r, t, v]:
            model.is_efficiency_variable[r, p, i, t, v, o] = False
            count_rpitvo[r, p, i, t, v, o] = 0

    annual = set()
    # Check for bad values and count up the good ones
    for r, p, _s, _d, i, t, v, o in model.efficiency_variable.sparse_iterkeys():
        if p not in model.process_periods[r, t, v]:
            msg = f'Invalid period {p} for process {r, t, v} in efficiency_variable table'
            logger.error(msg)
            raise ValueError(msg)

        if t in model.tech_annual:
            annual.add(t)

        # Good value, pull from efficiency_variable table
        count_rpitvo[r, p, i, t, v, o] += 1

    for t in annual:
        msg = (
            f'Variable efficiencies were provided for the annual technology {t}, which has '
            'no variable output. This will only be applied to flows on non-annual commodities. '
            'This is ambiguous behaviour and not recommended.'
        )
        logger.warning(msg)

    # Check if all possible values have been set as variable
    # log a warning if some are missing (allowed but maybe accidental)
    num_seg = len(model.time_season[p]) * len(model.time_of_day)
    for (r, p, i, t, v, o), count in count_rpitvo.items():
        if count > 0:
            model.is_efficiency_variable[r, p, i, t, v, o] = True
            if count < num_seg:
                logger.info(
                    'Some but not all efficiency_variable values were set (%i out of a possible '
                    '%i) for: %s Missing values will default to value set in efficiency table.',
                    count,
                    num_seg,
                    (r, p, i, t, v, o),
                )
