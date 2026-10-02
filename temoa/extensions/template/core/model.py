"""Type-checking model subtype and component registration for the template extension.

TEMPLATE: This file plays the same role as ``temoa/core/model.py`` does for the
core model: it declares the extension-owned model components (so the type
checker knows about them) and attaches them to a live ``TemoaModel`` instance.

Two things live here:
    1. ``ExampleModel`` - a ``TYPE_CHECKING``-only subtype of ``TemoaModel`` that
       declares every Param/Set/Constraint this extension adds. It exists purely
       for static typing; nothing instantiates it.
    2. ``register_model_components`` - the runtime hook that attaches those
       components to the core model.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pyomo.environ import Any, Constraint, Param, Set

from temoa.extensions.template.components import example_limit

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

    class ExampleModel(TemoaModel):
        """TemoaModel extended with template-extension components.

        TEMPLATE: Declare one annotation per component you create in
        ``register_model_components`` below. Inheriting from ``TemoaModel`` means
        all core sets/params/vars (e.g. ``time_optimize``, ``v_new_capacity``)
        are already visible to the type checker here and in your component
        modules.
        """

        # Params (loaded from the database via data_manifest.py)
        example_new_capacity_limit: Param

        # Constraint index sets
        example_new_capacity_limit_constraint_rpt: Set

        # Constraints
        example_new_capacity_limit_constraint: Constraint


def register_model_components(model: TemoaModel) -> None:
    """Attach template-extension components to the core Temoa model.

    TEMPLATE: Keep the public signature as ``model: TemoaModel`` so this stays
    assignable to ``ExtensionSpec.register_model_components`` (a
    ``Callable[[TemoaModel], None]``). Narrowing the parameter to ``ExampleModel``
    would be a contravariance error in mypy. Instead, ``cast`` once and operate on
    the typed alias ``m`` below.
    """
    m = cast('ExampleModel', model)

    # Param: a per-(region, tech-or-group) cap on cumulative new capacity.
    m.example_new_capacity_limit = Param(m.regional_global_indices, m.tech_or_group, within=Any)

    # Sparse index set for the constraint, built from the param's populated keys.
    m.example_new_capacity_limit_constraint_rpt = Set(
        dimen=3, initialize=example_limit.example_new_capacity_limit_indices
    )

    # The constraint itself.
    m.example_new_capacity_limit_constraint = Constraint(
        m.example_new_capacity_limit_constraint_rpt,
        rule=example_limit.example_new_capacity_limit_constraint_rule,
    )
