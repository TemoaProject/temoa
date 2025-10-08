from logging import getLogger
from typing import TYPE_CHECKING, Iterable

from deprecated import deprecated

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

logger = getLogger(name=__name__)


def CreateRegionalIndices(M: 'TemoaModel'):
    """Create the set of all regions and all region-region pairs"""
    regional_indices = set()
    for r_i in M.regions:
        if '-' in r_i:
            logger.error("Individual region names can not have '-' in their names: %s", str(r_i))
            raise ValueError("Individual region names can not have '-' in their names: " + str(r_i))
        for r_j in M.regions:
            if r_i == r_j:
                regional_indices.add(r_i)
            else:
                regional_indices.add(r_i + '-' + r_j)
    # dev note:  Sorting these passed them to pyomo in an ordered container and prevents warnings
    return sorted(regional_indices)


@deprecated('No longer used.  See the region_group_check in validators.py')
def RegionalGlobalInitializedIndices(M: 'TemoaModel'):
    from itertools import permutations

    indices = set()
    for n in range(1, len(M.regions) + 1):
        regional_perms = permutations(M.regions, n)
        for i in regional_perms:
            indices.add('+'.join(i))
    indices.add('global')
    indices = indices.union(M.regionalIndices)

    return indices


def gather_group_regions(M: 'TemoaModel', region: str) -> Iterable[str]:
    if region == 'global':
        regions = M.regions
    elif '+' in region:
        regions = region.split('+')
    else:
        regions = (region,)
    return regions
