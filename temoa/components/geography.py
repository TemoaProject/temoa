# temoa/components/geography.py
"""
Defines the geography-related components of the Temoa model.

This module is responsible for handling all logic related to multi-region models,
including:
-  Pre-computing the data structures for inter-regional commodity transfers
    (imports and exports).
-  Defining the sets of valid regions and regional groupings.
-  Defining constraints that govern inter-regional capacity and flows.
"""

from logging import getLogger
from typing import TYPE_CHECKING, Any, Iterable

from deprecated import deprecated
from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

logger = getLogger(name=__name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def gather_group_regions(M: 'TemoaModel', region: str) -> Iterable[str]:
    if region == 'global':
        regions = M.regions
    elif '+' in region:
        regions = region.split('+')
    else:
        regions = (region,)
    return regions


# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def CreateRegionalIndices(M: 'TemoaModel') -> list[str]:
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
def RegionalGlobalInitializedIndices(M: 'TemoaModel') -> set[str]:
    from itertools import permutations

    indices = set()
    for n in range(1, len(M.regions) + 1):
        regional_perms = permutations(M.regions, n)
        for i in regional_perms:
            indices.add('+'.join(i))
    indices.add('global')
    indices = indices.union(M.regionalIndices)

    return indices


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


def RegionalExchangeCapacity_Constraint(
    M: 'TemoaModel', r_e: str, r_i: str, p: int, t: str, v: int
) -> Any:
    r"""

    This constraint ensures that the process (t,v) connecting regions
    r_e and r_i is handled by one capacity variables.

    .. math::
       :label: RegionalExchangeCapacity

          \textbf{CAP}_{r_e,t,v}
          =
          \textbf{CAP}_{r_i,t,v}

          \\
          \forall \{r_e, r_i, t, v\} \in \Theta_{\text{RegionalExchangeCapacity}}
    """

    expr = M.V_Capacity[r_e + '-' + r_i, p, t, v] == M.V_Capacity[r_i + '-' + r_e, p, t, v]

    return expr


# ============================================================================
# PRE-COMPUTATION FUNCTION
# ============================================================================


def create_geography_sets(M: 'TemoaModel') -> None:
    """
    Populates dictionaries related to inter-regional commodity exchange.

    This function iterates through exchange technologies (identified by a '-' in
    their region name) and populates the `M.exportRegions` and `M.importRegions`
    dictionaries. These are used later in the commodity balance constraints.

    Populates:
        - M.exportRegions: dict mapping (region_from, p, commodity) to a set
          of (region_to, t, v, o) tuples.
        - M.importRegions: dict mapping (region_to, p, commodity) to a set
          of (region_from, t, v, i) tuples.
    """
    logger.debug('Creating geography-related sets for exchange technologies.')
    for r, i, t, v, o in M.Efficiency.sparse_iterkeys():
        if t not in M.tech_exchange:
            continue

        if '-' not in r:
            msg = f"Exchange technology {t} has an invalid region '{r}'. Must be 'region_from-region_to'."
            logger.error(msg)
            raise ValueError(msg)

        region_from, region_to = r.split('-', 1)

        lifetime = value(M.LifetimeProcess[r, t, v])
        for p in M.time_optimize:
            if p >= v and v + lifetime > p:
                M.exportRegions.setdefault((region_from, p, i), set()).add((region_to, t, v, o))
                M.importRegions.setdefault((region_to, p, o), set()).add((region_from, t, v, i))
