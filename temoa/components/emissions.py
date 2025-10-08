from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


def EmissionActivityIndices(M: 'TemoaModel'):
    indices = set(
        (r, e, i, t, v, o)
        for r, i, t, v, o in M.Efficiency.sparse_iterkeys()
        for e in M.commodity_emissions
        if r in M.regions  # omit any exchange/groups
    )

    return indices


def LinkedTechConstraintIndices(M: 'TemoaModel'):
    linkedtech_indices = set(
        (r, p, s, d, t, v, e)
        for r, t, e in M.LinkedTechs.sparse_iterkeys()
        for p in M.time_optimize
        if (r, p, t) in M.processVintages
        for v in M.processVintages[r, p, t]
        if (r, p, t, v) in M.activeActivity_rptv
        for s in M.TimeSeason[p]
        for d in M.time_of_day
    )

    return linkedtech_indices
