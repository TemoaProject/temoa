from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

logger = getLogger(__name__)


def LimitTechInputSplitConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, i, t, v, op)
        for r, p, i, t, op in M.inputSplitVintages
        if t not in M.tech_annual
        for v in M.inputSplitVintages[r, p, i, t, op]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )
    ann_indices = set(
        (r, p, i, t, op) for r, p, i, t, op in M.inputSplitVintages if t in M.tech_annual
    )
    if len(ann_indices) > 0:
        msg = (
            'Warning: Annual technologies included in LimitTechInputSplit table. '
            'Use LimitTechInputSplitAnnual table instead or these constraints will be ignored: {}'
        )
        logger.warning(msg.format(ann_indices))

    return indices


def LimitTechInputSplitAnnualConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, i, t, v, op)
        for r, p, i, t, op in M.inputSplitAnnualVintages
        if t in M.tech_annual
        for v in M.inputSplitAnnualVintages[r, p, i, t, op]
    )

    return indices


def LimitTechInputSplitAverageConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, i, t, v, op)
        for r, p, i, t, op in M.inputSplitAnnualVintages
        if t not in M.tech_annual
        for v in M.inputSplitAnnualVintages[r, p, i, t, op]
    )
    return indices


def LimitTechOutputSplitConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v, o, op)
        for r, p, t, o, op in M.outputSplitVintages
        if t not in M.tech_annual
        for v in M.outputSplitVintages[r, p, t, o, op]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )
    ann_indices = set(
        (r, p, t, o, op) for r, p, t, o, op in M.outputSplitVintages if t in M.tech_annual
    )
    if len(ann_indices) > 0:
        msg = (
            'Warning: Annual technologies included in LimitTechOutputSplit table. '
            'Use LimitTechOutputSplitAnnual table instead or these constraints will be ignored: {}'
        )
        logger.warning(msg.format(ann_indices))

    return indices


def LimitTechOutputSplitAnnualConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, v, o, op)
        for r, p, t, o, op in M.outputSplitAnnualVintages
        if t in M.tech_annual
        for v in M.outputSplitAnnualVintages[r, p, t, o, op]
    )
    return indices


def LimitTechOutputSplitAverageConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, v, o, op)
        for r, p, t, o, op in M.outputSplitAnnualVintages
        if t not in M.tech_annual
        for v in M.outputSplitAnnualVintages[r, p, t, o, op]
    )
    return indices


def LimitGrowthCapacityIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, op)
        for r, t, op in M.LimitGrowthCapacity.sparse_iterkeys()
        for p in M.time_optimize
    )
    return indices


def LimitDegrowthCapacityIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, op)
        for r, t, op in M.LimitDegrowthCapacity.sparse_iterkeys()
        for p in M.time_optimize
    )
    return indices


def LimitGrowthNewCapacityIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, op)
        for r, t, op in M.LimitGrowthNewCapacity.sparse_iterkeys()
        for p in M.time_optimize
    )
    return indices


def LimitDegrowthNewCapacityIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, op)
        for r, t, op in M.LimitDegrowthNewCapacity.sparse_iterkeys()
        for p in M.time_optimize
    )
    return indices


def LimitGrowthNewCapacityDeltaIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, op)
        for r, t, op in M.LimitGrowthNewCapacityDelta.sparse_iterkeys()
        for p in M.time_optimize
    )
    return indices


def LimitDegrowthNewCapacityDeltaIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, t, op)
        for r, t, op in M.LimitDegrowthNewCapacityDelta.sparse_iterkeys()
        for p in M.time_optimize
    )
    return indices
