from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


from logging import getLogger
from typing import Iterable

from pyomo.environ import value

logger = getLogger(__name__)


def CheckEfficiencyIndices(M: 'TemoaModel'):
    """
    Ensure that there are no unused items in any of the Efficiency index sets.
    """
    # TODO:  This could be upgraded to scan for finer resolution
    #        by checking by REGION and PERIOD...  Each region/period is unique.
    c_physical = set(i for r, i, t, v, o in M.Efficiency.sparse_iterkeys())
    c_physical = c_physical | set(i for r, i, t, v in M.ConstructionInput.sparse_iterkeys())
    techs = set(t for r, i, t, v, o in M.Efficiency.sparse_iterkeys())
    c_outputs = set(o for r, i, t, v, o in M.Efficiency.sparse_iterkeys())
    c_outputs = c_outputs | set(o for r, t, v, o in M.EndOfLifeOutput.sparse_iterkeys())

    symdiff = c_physical.symmetric_difference(M.commodity_physical)
    if symdiff:
        msg = (
            'Unused or unspecified physical carriers.  Either add or remove '
            'the following elements to the Set commodity_physical.'
            '\n\n    Element(s): {}'
        )
        symdiff = (str(i) for i in symdiff)
        f_msg = msg.format(', '.join(symdiff))
        logger.error(f_msg)
        raise ValueError(f_msg)

    symdiff = techs.symmetric_difference(M.tech_all)
    if symdiff:
        msg = (
            'Unused or unspecified technologies.  Either add or remove '
            'the following technology(ies) to the tech_resource or '
            'tech_production Sets.\n\n    Technology(ies): {}'
        )
        symdiff = (str(i) for i in symdiff)
        f_msg = msg.format(', '.join(symdiff))
        logger.error(f_msg)
        raise ValueError(f_msg)

    diff = M.commodity_demand - c_outputs
    if diff:
        msg = (
            'Unused or unspecified outputs.  Either add or remove the '
            'following elements to the commodity_demand Set.'
            '\n\n    Element(s): {}'
        )
        diff = (str(i) for i in diff)
        f_msg = msg.format(', '.join(diff))
        logger.error(f_msg)
        raise ValueError(f_msg)


def CheckEfficiencyVariable(M: 'TemoaModel'):
    count_rpitvo = dict()
    # Pull non-variable efficiency by default
    for r, i, t, v, o in M.Efficiency.sparse_iterkeys():
        if (r, t, v) not in M.processPeriods:
            # Probably an existing vintage that retires in p0
            # Still want it for end of life flows
            continue
        for p in M.processPeriods[r, t, v]:
            M.isEfficiencyVariable[r, p, i, t, v, o] = False
            count_rpitvo[r, p, i, t, v, o] = 0

    annual = set()
    # Check for bad values and count up the good ones
    for r, p, _s, _d, i, t, v, o in M.EfficiencyVariable.sparse_iterkeys():
        if p not in M.processPeriods[r, t, v]:
            msg = f'Invalid period {p} for process {r, t, v} in EfficiencyVariable table'
            logger.error(msg)
            raise ValueError(msg)

        if t in M.tech_annual:
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
    num_seg = len(M.TimeSeason[p]) * len(M.time_of_day)
    for (r, p, i, t, v, o), count in count_rpitvo.items():
        if count > 0:
            M.isEfficiencyVariable[r, p, i, t, v, o] = True
            if count < num_seg:
                logger.info(
                    'Some but not all EfficiencyVariable values were set (%i out of a possible %i) for: %s'
                    ' Missing values will default to value set in Efficiency table.',
                    count,
                    num_seg,
                    (r, p, i, t, v, o),
                )


def ModelProcessLifeIndices(M: 'TemoaModel'):
    """\
Returns the set of sensical (region, period, tech, vintage) tuples.  The tuple indicates
the periods in which a process is active, distinct from TechLifeFracIndices that
returns indices only for processes that EOL mid-period.
"""
    return M.activeActivity_rptv


def LifetimeProcessIndices(M: 'TemoaModel'):
    """\
Based on the Efficiency parameter's indices, this function returns the set of
process indices that may be specified in the LifetimeProcess parameter.
"""
    indices = set((r, t, v) for r, i, t, v, o in M.Efficiency.sparse_iterkeys())

    return indices


def get_default_survival(M: 'TemoaModel', r, p, t, v):
    """
    Getting LifetimeSurvivalCurve where it is not defined
    If this is a survival curve process, return 0 (likely beyond EOL)
    Otherwise return 1 (no survival curve based EOL)
    """
    if M.isSurvivalCurveProcess[r, t, v]:
        return 0
    else:
        return 1


def get_default_process_lifetime(M: 'TemoaModel', r, t, v):
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
    return M.LifetimeTech[r, t]


def gather_group_techs(M: 'TemoaModel', t_or_g: str) -> Iterable[str]:
    if t_or_g in M.tech_group_names:
        techs = M.tech_group_members[t_or_g]
    elif '+' in t_or_g:
        techs = t_or_g.split('+')
    else:
        techs = (t_or_g,)
    return techs


def CreateSurvivalCurve(M: 'TemoaModel'):
    rtv_interpolated = set()  # so we only need one warning

    for r, _, t, v, _ in M.Efficiency.sparse_iterkeys():
        M.isSurvivalCurveProcess[r, t, v] = False  # by default

    # Collect rptv indices into (r, t, v): p dictionary
    for r, p, t, v in M.LifetimeSurvivalCurve.sparse_iterkeys():
        if (r, t, v) not in M.survivalCurvePeriods:
            M.survivalCurvePeriods[r, t, v] = list()
        M.survivalCurvePeriods[r, t, v].append(p)
        M.isSurvivalCurveProcess[r, t, v] = True

    # Go through all the periods for each (r, t, v) in order
    for r, t, v in M.survivalCurvePeriods:
        periods_rtv = sorted(M.survivalCurvePeriods[r, t, v])

        p_first = periods_rtv[0]
        p_last = periods_rtv[-1]

        if p_first != v:
            msg = (
                'LifetimeSurvivalCurve must be defined starting in the vintage period. Must '
                f'define ({r}, >{v}<, {t}, {v})'
            )
            logger.error(msg)
            raise ValueError(msg)

        if value(M.LifetimeSurvivalCurve[r, v, t, v]) != 1:
            msg = (
                'LifetimeSurvivalCurve must begin at 1 for calculating annual retirements. ',
                f'Got {value(M.LifetimeSurvivalCurve[r, v, t, v])} for ({r}, {v}, {t}, {v})',
            )
            logger.error(msg)
            raise ValueError(msg)

        # Collect a list of processes that needed to be interpolated, for warning
        if periods_rtv != list(range(p_first, p_last + 1, 1)):
            rtv_interpolated.add((r, t, v))

        between_periods = []
        for i, p in enumerate(periods_rtv):
            if i == 0:
                continue  # Cant look back from first period. Could be zero but hey why not

            # Check that the survival curve monotonically decreases
            p_prev = periods_rtv[i - 1]
            lsc = value(M.LifetimeSurvivalCurve[r, p, t, v])
            lsc_prev = value(M.LifetimeSurvivalCurve[r, p_prev, t, v])
            if lsc - lsc_prev > 0.0001:
                msg = (
                    'LifetimeSurvivalCurve fraction increases going forward in time from {} to {}. '
                    'This is not allowed.'
                ).format((r, p_prev, t, v), (r, p, t, v))
                logger.error(msg)
                raise ValueError(msg)

            if p - p_prev > 1:
                _between_periods = list(range(p_prev + 1, p, 1))
                for _p in _between_periods:
                    x = (_p - p_prev) / (p - p_prev)
                    lsc_x = lsc_prev + x * (lsc - lsc_prev)
                    M.LifetimeSurvivalCurve[r, _p, t, v] = lsc_x
                between_periods.extend(_between_periods)

            if lsc < 0.0001:
                if p != p_last:
                    msg = (
                        'There is no need to continue a survival curve beyond fraction ~= 0. '
                        f'ignoring periods beyond {p} for ({r, t, v})'
                    )
                    logger.info(msg)

                # Make sure the lifetime for this process aligns with survival curve end
                if value(M.LifetimeProcess[r, t, v]) < p - v:
                    msg = (
                        f'The LifetimeProcess parameter for process ({r, t, v}) with survival curve  '
                        f'does not extend beyond the end of that survival curve in {p}. To agree with '
                        f'the survival curve, set LifetimeProcess[{r, t, v}] >= {p - v}'
                    )
                    logger.error(msg)
                    raise ValueError(msg)
                elif value(M.LifetimeProcess[r, t, v]) != p - v:
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

        M.survivalCurvePeriods[r, t, v].extend(between_periods)
        M.survivalCurvePeriods[r, t, v] = set(M.survivalCurvePeriods[r, t, v])

    if rtv_interpolated:
        msg = (
            'For the purposes of investment cost accounting, LifetimeSurvivalCurve must be defined '
            'for each individual year. Gaps between defined years will be filled by linear interpolation. '
            'Otherwise, these individual years can be defined manually. Interpolated processes: {}'
        ).format([rtv for rtv in rtv_interpolated])
        logger.info(msg)
