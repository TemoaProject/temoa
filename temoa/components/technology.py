# temoa/components/technology.py
"""
Defines the core technology-related components of the Temoa model.

This module is the foundation of the model, responsible for:
-  Pre-computing the core data structures that link technologies to commodities,
    time periods, and vintages based on the `Efficiency` parameter.
-  Handling technology lifetimes, including survival curve validation and interpolation.
-  Defining Pyomo index sets for core technology parameters.
-  Validating model inputs related to technologies, efficiencies, and commodities.
"""

from __future__ import annotations

from collections.abc import Iterable
from logging import getLogger
from typing import TYPE_CHECKING, cast

from pyomo.environ import value

if TYPE_CHECKING:
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
        return [cast(Technology, tech) for tech in t_or_g.split('+')]
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
    return model.activeActivity_rptv


def lifetime_process_indices(model: TemoaModel) -> set[tuple[Region, Technology, Vintage]]:
    """
    Based on the Efficiency parameter's indices, this function returns the set of
    process indices that may be specified in the LifetimeProcess parameter.
    """
    indices = {(r, t, v) for r, i, t, v, o in model.Efficiency.sparse_iterkeys()}

    return indices


def get_default_survival(
    model: TemoaModel, r: Region, p: Period, t: Technology, v: Vintage
) -> float:
    """
    Getting LifetimeSurvivalCurve where it is not defined
    If this is a survival curve process, return 0 (likely beyond EOL)
    Otherwise return 1 (no survival curve based EOL)
    """
    return 0.0 if model.isSurvivalCurveProcess[r, t, v] else 1.0


def get_default_process_lifetime(model: TemoaModel, r: Region, t: Technology, v: Vintage) -> int:
    """
    This initializer used to initialize the LifetimeProcess parameter from LifetimeTech where needed

    Priority:
        1.  Specified in LifetimeProcess data (provided as a fill and would not call this function)
        2.  Specified in LifetimeTech data
        3.  The default value from the LifetimeTech param (automatic)
    :param M: generic model reference (not used)
    :param r: region
    :param t: tech
    :param v: vintage
    :return: the final lifetime value
    """
    return value(model.LifetimeTech[r, t])


def param_process_life_fraction_rule(
    model: TemoaModel, r: Region, p: Period, t: Technology, v: Vintage
) -> float:
    r"""
    Get the effective capacity of a process :math:`<r, t, v>` in a period :math:`p`.

    Accounts for mid-period end of life or average survival over the period
    for processes using survival curves.
    """

    period_length = value(model.PeriodLength[p])

    if model.isSurvivalCurveProcess[r, t, v]:
        # Sum survival fraction over the period
        years_remaining = sum(
            value(model.LifetimeSurvivalCurve[r, _p, t, v]) for _p in range(p, p + period_length, 1)
        )
    else:
        # Remaining life years within the EOL period
        years_remaining = v + value(model.LifetimeProcess[r, t, v]) - p

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
    Populates the core sparse dictionaries from the `Efficiency` parameter.

    This function is foundational for creating the sparse indices used throughout
    the model, defining process relationships, inputs, outputs, and active periods.

    Populates:
        - M.processInputs, M.processOutputs
        - M.commodityDStreamProcess, M.commodityUStreamProcess
        - M.processOutputsByInput, M.processInputsByOutput
        - M.processVintages, M.processPeriods
        - M.used_techs
    """
    logger.debug('Populating core sparse dictionaries from Efficiency parameter.')
    first_period = min(model.time_future)
    exist_indices = model.ExistingCapacity.sparse_keys()

    for r, i, t, v, o in model.Efficiency.sparse_iterkeys():
        # A. Basic data validation and warnings
        process = (r, t, v)
        lifetime = value(model.LifetimeProcess[process])
        if v in model.vintage_exist:
            if process not in exist_indices and t not in model.tech_uncap:
                logger.warning(
                    f'Warning: {process} has a specified Efficiency, but does not '
                    f'have any existing install base (ExistingCapacity).'
                )
                continue
            if t not in model.tech_uncap and model.ExistingCapacity[process] == 0:
                logger.warning(
                    f'Notice: Unnecessary specification of ExistingCapacity for {process}. '
                    f'Declaring a capacity of zero may be omitted.'
                )
                continue
            if v + lifetime <= first_period:
                logger.info(
                    f'{process} specified as ExistingCapacity, but its '
                    f'lifetime ({lifetime} years) does not extend past the '
                    f'beginning of time_future ({first_period}).'
                )

        if model.Efficiency[r, i, t, v, o] == 0:
            logger.info(
                f'Notice: Unnecessary specification of Efficiency for {(r, i, t, v, o)}. '
                f'Specifying an efficiency of zero may be omitted.'
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
            if pindex not in model.processInputs:
                model.processInputs[pindex] = set()
                model.processOutputs[pindex] = set()
            if (r, p, i) not in model.commodityDStreamProcess:
                model.commodityDStreamProcess[r, p, i] = set()
            if (r, p, o) not in model.commodityUStreamProcess:
                model.commodityUStreamProcess[r, p, o] = set()
            if (r, p, t, v, i) not in model.processOutputsByInput:
                model.processOutputsByInput[r, p, t, v, i] = set()
            if (r, p, t, v, o) not in model.processInputsByOutput:
                model.processInputsByOutput[r, p, t, v, o] = set()
            if (r, p, t) not in model.processVintages:
                model.processVintages[r, p, t] = set()
            if (r, t, v) not in model.processPeriods:
                model.processPeriods[r, t, v] = set()

            # D. Populate the dictionaries
            model.processInputs[pindex].add(i)
            model.processOutputs[pindex].add(o)
            model.commodityDStreamProcess[r, p, i].add((t, v))
            model.commodityUStreamProcess[r, p, o].add((t, v))
            model.processOutputsByInput[r, p, t, v, i].add(o)
            model.processInputsByOutput[r, p, t, v, o].add(i)
            model.processVintages[r, p, t].add(v)
            model.processPeriods[r, t, v].add(p)


def create_survival_curve(model: TemoaModel) -> None:
    rtv_interpolated = set()  # so we only need one warning

    for r, _, t, v, _ in model.Efficiency.sparse_iterkeys():
        model.isSurvivalCurveProcess[r, t, v] = False  # by default

    # Collect rptv indices into (r, t, v): p dictionary
    for r, p, t, v in model.LifetimeSurvivalCurve.sparse_iterkeys():
        if (r, t, v) not in model.survivalCurvePeriods:
            model.survivalCurvePeriods[r, t, v] = set()
        model.survivalCurvePeriods[r, t, v].add(p)
        model.isSurvivalCurveProcess[r, t, v] = True

    # Go through all the periods for each (r, t, v) in order
    for r, t, v in model.survivalCurvePeriods:
        periods_rtv: list[int] = sorted(model.survivalCurvePeriods[r, t, v])

        p_first = periods_rtv[0]
        p_last = periods_rtv[-1]

        if p_first != v:
            msg = (
                'LifetimeSurvivalCurve must be defined starting in the vintage period. Must '
                f'define ({r}, >{v}<, {t}, {v})'
            )
            logger.error(msg)
            raise ValueError(msg)

        if value(model.LifetimeSurvivalCurve[r, v, t, v]) != 1:
            msg_str = (
                'LifetimeSurvivalCurve must begin at 1 for calculating annual retirements. '
                f'Got {value(model.LifetimeSurvivalCurve[r, v, t, v])} for ({r}, {v}, {t}, {v})'
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
            lsc = value(model.LifetimeSurvivalCurve[r, p, t, v])
            lsc_prev = value(model.LifetimeSurvivalCurve[r, p_prev, t, v])
            if lsc - lsc_prev > 0.0001:
                msg = (
                    'LifetimeSurvivalCurve fraction increases going forward in time from {} to {}. '
                    'This is not allowed.'
                ).format((r, p_prev, t, v), (r, p, t, v))
                logger.error(msg)
                raise ValueError(msg)

            if p - p_prev > 1:
                _between_periods = [cast(Period, _p) for _p in range(p_prev + 1, p, 1)]
                for _p in _between_periods:
                    x = (_p - p_prev) / (p - p_prev)
                    lsc_x = lsc_prev + x * (lsc - lsc_prev)
                    model.LifetimeSurvivalCurve[r, _p, t, v] = lsc_x
                between_periods.extend(_between_periods)

            if lsc < 0.0001:
                if p != p_last:
                    msg = (
                        'There is no need to continue a survival curve beyond fraction ~= 0. '
                        f'ignoring periods beyond {p} for ({r, t, v})'
                    )
                    logger.info(msg)

                # Make sure the lifetime for this process aligns with survival curve end
                if value(model.LifetimeProcess[r, t, v]) < p - v:
                    msg = (
                        f'The LifetimeProcess parameter for process ({r, t, v}) with survival curve  '
                        f'does not extend beyond the end of that survival curve in {p}. To agree with '
                        f'the survival curve, set LifetimeProcess[{r, t, v}] >= {p - v}'
                    )
                    logger.error(msg)
                    raise ValueError(msg)
                elif value(model.LifetimeProcess[r, t, v]) != p - v:
                    msg = (
                        f'The LifetimeProcess parameter for process ({r, t, v}) with survival curve  '
                        f'does match the end of that survival curve in {p}. This will waste compute. '
                        'To agree with the survival curve and suppress this warning, set '
                        f'LifetimeProcess[{r, t, v}] = {p - v}'
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

        model.survivalCurvePeriods[r, t, v].update(between_periods)

    if rtv_interpolated:
        msg = (
            'For the purposes of investment cost accounting, LifetimeSurvivalCurve must be defined '
            'for each individual year. Gaps between defined years will be filled by linear interpolation. '
            'Otherwise, these individual years can be defined manually. Interpolated processes: {}'
        ).format([rtv for rtv in rtv_interpolated])
        logger.info(msg)


def check_efficiency_indices(model: TemoaModel) -> None:
    """
    Ensure that there are no unused items in any of the Efficiency index sets.
    """
    # TODO:  This could be upgraded to scan for finer resolution
    #        by checking by REGION and PERIOD...  Each region/period is unique.
    c_physical = {i for r, i, t, v, o in model.Efficiency.sparse_iterkeys()}
    c_physical = c_physical | {i for r, i, t, v in model.ConstructionInput.sparse_iterkeys()}
    techs = {t for r, i, t, v, o in model.Efficiency.sparse_iterkeys()}
    c_outputs = {o for r, i, t, v, o in model.Efficiency.sparse_iterkeys()}
    c_outputs = c_outputs | {o for r, t, v, o in model.EndOfLifeOutput.sparse_iterkeys()}

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
    for r, i, t, v, o in model.Efficiency.sparse_iterkeys():
        if (r, t, v) not in model.processPeriods:
            # Probably an existing vintage that retires in p0
            # Still want it for end of life flows
            continue
        for p in model.processPeriods[r, t, v]:
            model.isEfficiencyVariable[r, p, i, t, v, o] = False
            count_rpitvo[r, p, i, t, v, o] = 0

    annual = set()
    # Check for bad values and count up the good ones
    for r, p, _s, _d, i, t, v, o in model.EfficiencyVariable.sparse_iterkeys():
        if p not in model.processPeriods[r, t, v]:
            msg = f'Invalid period {p} for process {r, t, v} in EfficiencyVariable table'
            logger.error(msg)
            raise ValueError(msg)

        if t in model.tech_annual:
            annual.add(t)

        # Good value, pull from EfficiencyVariable table
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
    num_seg = len(model.TimeSeason[p]) * len(model.time_of_day)
    for (r, p, i, t, v, o), count in count_rpitvo.items():
        if count > 0:
            model.isEfficiencyVariable[r, p, i, t, v, o] = True
            if count < num_seg:
                logger.info(
                    'Some but not all EfficiencyVariable values were set (%i out of a possible %i) for: %s'
                    ' Missing values will default to value set in Efficiency table.',
                    count,
                    num_seg,
                    (r, p, i, t, v, o),
                )
