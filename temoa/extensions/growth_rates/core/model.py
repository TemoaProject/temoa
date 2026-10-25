from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pyomo.environ import Any, Constraint, Param, Set

from temoa.extensions.growth_rates.components import (
    growth_capacity,
    growth_new_capacity,
    growth_new_capacity_delta,
)

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

    class GrowthRatesModel(TemoaModel):
        """TemoaModel extended with growth-rates components.

        This subtype exists only for static type checking. At runtime the
        growth-rates components are attached to the core ``TemoaModel``
        instance by :func:`register_model_components`.
        """

        # Params
        limit_growth_capacity: Param
        limit_degrowth_capacity: Param
        limit_growth_new_capacity: Param
        limit_degrowth_new_capacity: Param
        limit_growth_new_capacity_delta: Param
        limit_degrowth_new_capacity_delta: Param

        # Constraint index sets
        limit_growth_capacity_constraint_rpt: Set
        limit_degrowth_capacity_constraint_rpt: Set
        limit_growth_new_capacity_constraint_rpt: Set
        limit_degrowth_new_capacity_constraint_rpt: Set
        limit_growth_new_capacity_delta_constraint_rpt: Set
        limit_degrowth_new_capacity_delta_constraint_rpt: Set

        # Constraints
        limit_growth_capacity_constraint: Constraint
        limit_degrowth_capacity_constraint: Constraint
        limit_growth_new_capacity_constraint: Constraint
        limit_degrowth_new_capacity_constraint: Constraint
        limit_growth_new_capacity_delta_constraint: Constraint
        limit_degrowth_new_capacity_delta_constraint: Constraint


def register_model_components(model: TemoaModel) -> None:
    """Register growth rates model components on the core Temoa model."""
    m = cast('GrowthRatesModel', model)

    m.limit_growth_capacity = Param(
        m.regional_global_indices, m.tech_or_group, m.operator, within=Any
    )
    m.limit_degrowth_capacity = Param(
        m.regional_global_indices, m.tech_or_group, m.operator, within=Any
    )
    m.limit_growth_new_capacity = Param(
        m.regional_global_indices, m.tech_or_group, m.operator, within=Any
    )
    m.limit_degrowth_new_capacity = Param(
        m.regional_global_indices, m.tech_or_group, m.operator, within=Any
    )
    m.limit_growth_new_capacity_delta = Param(
        m.regional_global_indices, m.tech_or_group, m.operator, within=Any
    )
    m.limit_degrowth_new_capacity_delta = Param(
        m.regional_global_indices, m.tech_or_group, m.operator, within=Any
    )

    m.limit_growth_capacity_constraint_rpt = Set(
        dimen=4, initialize=growth_capacity.limit_growth_capacity_indices
    )
    m.limit_growth_capacity_constraint = Constraint(
        m.limit_growth_capacity_constraint_rpt,
        rule=growth_capacity.limit_growth_capacity_constraint_rule,
    )
    m.limit_degrowth_capacity_constraint_rpt = Set(
        dimen=4, initialize=growth_capacity.limit_degrowth_capacity_indices
    )
    m.limit_degrowth_capacity_constraint = Constraint(
        m.limit_degrowth_capacity_constraint_rpt,
        rule=growth_capacity.limit_degrowth_capacity_constraint_rule,
    )

    m.limit_growth_new_capacity_constraint_rpt = Set(
        dimen=4, initialize=growth_new_capacity.limit_growth_new_capacity_indices
    )
    m.limit_growth_new_capacity_constraint = Constraint(
        m.limit_growth_new_capacity_constraint_rpt,
        rule=growth_new_capacity.limit_growth_new_capacity_constraint_rule,
    )
    m.limit_degrowth_new_capacity_constraint_rpt = Set(
        dimen=4, initialize=growth_new_capacity.limit_degrowth_new_capacity_indices
    )
    m.limit_degrowth_new_capacity_constraint = Constraint(
        m.limit_degrowth_new_capacity_constraint_rpt,
        rule=growth_new_capacity.limit_degrowth_new_capacity_constraint_rule,
    )

    m.limit_growth_new_capacity_delta_constraint_rpt = Set(
        dimen=4, initialize=growth_new_capacity_delta.limit_growth_new_capacity_delta_indices
    )
    m.limit_growth_new_capacity_delta_constraint = Constraint(
        m.limit_growth_new_capacity_delta_constraint_rpt,
        rule=growth_new_capacity_delta.limit_growth_new_capacity_delta_constraint_rule,
    )
    m.limit_degrowth_new_capacity_delta_constraint_rpt = Set(
        dimen=4, initialize=growth_new_capacity_delta.limit_degrowth_new_capacity_delta_indices
    )
    m.limit_degrowth_new_capacity_delta_constraint = Constraint(
        m.limit_degrowth_new_capacity_delta_constraint_rpt,
        rule=growth_new_capacity_delta.limit_degrowth_new_capacity_delta_constraint_rule,
    )
