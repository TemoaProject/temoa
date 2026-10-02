from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pyomo.environ import Constraint, Integers, NonNegativeReals, Param, Set, Var

from temoa.extensions.discrete_capacity.components import discrete_capacity

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

    class DiscreteCapacityModel(TemoaModel):
        limit_discrete_new_capacity: Param
        limit_discrete_new_capacity_constraint_rtv: Set
        limit_discrete_new_capacity_constraint: Constraint
        v_discrete_new_capacity: Var

        limit_discrete_capacity: Param
        limit_discrete_capacity_constraint_rpt: Set
        limit_discrete_capacity_constraint: Constraint
        v_discrete_capacity: Var


def register_model_components(model: TemoaModel) -> None:
    m = cast('DiscreteCapacityModel', model)

    m.limit_discrete_new_capacity = Param(
        m.regional_global_indices, m.tech_or_group, within=NonNegativeReals
    )
    m.limit_discrete_new_capacity_constraint_rtv = Set(
        dimen=3, initialize=discrete_capacity.limit_discrete_new_capacity_indices
    )
    m.v_discrete_new_capacity = Var(
        m.limit_discrete_new_capacity_constraint_rtv, within=Integers, bounds=(0, None)
    )
    m.limit_discrete_new_capacity_constraint = Constraint(
        m.limit_discrete_new_capacity_constraint_rtv,
        rule=discrete_capacity.limit_discrete_new_capacity_constraint_rule,
    )

    m.limit_discrete_capacity = Param(
        m.regional_global_indices, m.tech_or_group, within=NonNegativeReals
    )
    m.limit_discrete_capacity_constraint_rpt = Set(
        dimen=3, initialize=discrete_capacity.limit_discrete_capacity_indices
    )
    m.v_discrete_capacity = Var(
        m.limit_discrete_capacity_constraint_rpt, within=Integers, bounds=(0, None)
    )
    m.limit_discrete_capacity_constraint = Constraint(
        m.limit_discrete_capacity_constraint_rpt,
        rule=discrete_capacity.limit_discrete_capacity_constraint_rule,
    )
