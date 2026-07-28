"""Example constraint family for the template extension.

TEMPLATE: A component module holds the index-set function(s) and constraint
rule(s) for a single family of constraints, mirroring the modules under
``temoa/components``. Group related constraints together; create one module per
family.

This example caps the new capacity built in each period for a technology (or
technology group) in a region. Replace it with your own logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyomo.environ import Constraint, quicksum, value

import temoa.components.geography as geography
import temoa.components.technology as technology

if TYPE_CHECKING:
    from temoa.extensions.template.core.model import ExampleModel
    from temoa.types import ExprLike, Period, Region, Technology


def example_new_capacity_limit_indices(
    model: ExampleModel,
) -> set[tuple[Region, Period, Technology]]:
    """Build the sparse (region, period, tech-or-group) index for the constraint.

    TEMPLATE: Annotate ``model`` with the extension subtype (``ExampleModel``) so
    the extension-owned param ``example_new_capacity_limit`` and its
    ``sparse_keys()`` method are visible to the type checker.
    """
    return {
        (r, p, t)
        for r, t in model.example_new_capacity_limit.sparse_keys()
        for p in model.time_optimize
    }


def example_new_capacity_limit_constraint_rule(
    model: ExampleModel, r: Region, p: Period, t: Technology
) -> ExprLike:
    """Cap total new capacity built in period ``p`` for region/group ``r``/``t``."""
    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)

    limit = value(model.example_new_capacity_limit[r, t])

    new_cap_rtv = model.v_new_capacity
    new_cap = quicksum(
        new_cap_rtv[_r, _t, _v]
        for _r, _t, _v in new_cap_rtv.keys()
        if _r in regions and _t in techs and _v == p
    )

    if isinstance(new_cap, (int, float)):
        # No decision variables in this period/region/group: nothing to constrain.
        return Constraint.Skip

    return new_cap <= limit
