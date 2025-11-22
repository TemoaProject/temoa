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

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, cast

from deprecated import deprecated
from pyomo.environ import value

if TYPE_CHECKING:
    from collections.abc import Iterable

    from temoa.core.model import TemoaModel
    from temoa.types import ExprLike, Period, Region, Technology, Vintage

# Import type annotations

logger = getLogger(name=__name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def gather_group_regions(model: TemoaModel, region: Region) -> Iterable[Region]:
    regions: list[Region]
    if region == 'global':
        regions = list(model.regions)
    elif '+' in region:
        regions = [cast('Region', r) for r in region.split('+')]
    else:
        regions = [region]
    return regions


# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def create_regional_indices(model: TemoaModel) -> list[Region]:
    """Create the set of all regions and all region-region pairs"""
    regional_indices: set[Region] = set()
    for r_i in model.regions:
        if '-' in r_i:
            logger.error("Individual region names can not have '-' in their names: %s", str(r_i))
            raise ValueError("Individual region names can not have '-' in their names: " + str(r_i))
        for r_j in model.regions:
            if r_i == r_j:
                regional_indices.add(r_i)
            else:
                regional_indices.add(cast('Region', r_i + '-' + r_j))
    # dev note:  Sorting these passed them to pyomo in an ordered container and prevents warnings
    return sorted(regional_indices)


@deprecated('No longer used.  See the region_group_check in validators.py')
def regional_global_initialized_indices(model: TemoaModel) -> set[Region]:
    from itertools import permutations

    indices: set[Region] = set()
    for n in range(1, len(model.regions) + 1):
        regional_perms = permutations(model.regions, n)
        for i in regional_perms:
            indices.add(cast('Region', '+'.join(i)))
    indices.add(cast('Region', 'global'))
    indices = indices.union(model.regional_indices)

    return indices


# ============================================================================
# PYOMO CONSTRAINT RULES
# ============================================================================


def regional_exchange_capacity_constraint(
    model: TemoaModel, r_e: Region, r_i: Region, p: Period, t: Technology, v: Vintage
) -> ExprLike:
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

    expr = model.v_capacity[r_e + '-' + r_i, p, t, v] == model.v_capacity[r_i + '-' + r_e, p, t, v]

    return expr


# ============================================================================
# PRE-COMPUTATION FUNCTION
# ============================================================================


def create_geography_sets(model: TemoaModel) -> None:
    """
    Populates dictionaries related to inter-regional commodity exchange.

    This function iterates through exchange technologies (identified by a '-' in
    their region name) and populates the `M.export_regions` and `M.import_regions`
    dictionaries. These are used later in the commodity balance constraints.

    Populates:
        - M.export_regions: dict mapping (region_from, p, commodity) to a set
          of (region_to, t, v, o) tuples.
        - M.import_regions: dict mapping (region_to, p, commodity) to a set
          of (region_from, t, v, i) tuples.
    """
    logger.debug('Creating geography-related sets for exchange technologies.')
    for r, i, t, v, o in model.efficiency.sparse_iterkeys():
        if t not in model.tech_exchange:
            continue

        if '-' not in r:
            msg = (
                f"Exchange technology {t} has an invalid region '{r}'. Must be "
                "'region_from-region_to'."
            )
            logger.error(msg)
            raise ValueError(msg)

        region_from_str, region_to_str = r.split('-', 1)
        region_from = cast('Region', region_from_str)
        region_to = cast('Region', region_to_str)

        lifetime: float = value(model.lifetime_process[r, t, v])
        for p in model.time_optimize:
            if p >= v and v + lifetime > p:
                model.export_regions.setdefault((region_from, p, i), set()).add(
                    (region_to, t, v, o)
                )
                model.import_regions.setdefault((region_to, p, o), set()).add(
                    (region_from, t, v, i)
                )
