from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


def BaseloadDiurnalConstraintIndices(M: 'TemoaModel'):
    indices = set(
        (r, p, s, d, t, v)
        for r, p, t in M.baseloadVintages
        for v in M.baseloadVintages[r, p, t]
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    return indices
