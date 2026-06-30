from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pyomo.environ import Any, Integers, Binary, Constraint, Param, Set, Var

from temoa.extensions.integer_capacity.components import integer_capacity

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

    class IntegerCapacityModel(TemoaModel):

        limit_integer_new_capacity: Param
        limit_integer_new_capacity_constraint_rtv: Set
        limit_integer_new_capacity_constraint: Constraint
        v_integer_new_capacity: Var

        limit_integer_net_capacity: Param
        limit_integer_net_capacity_constraint_rpt: Set
        limit_integer_net_capacity_constraint: Constraint
        v_integer_net_capacity: Var


def register_model_components(model: TemoaModel) -> None:
    m = cast('IntegerCapacityModel', model)

    m.limit_integer_new_capacity = Param(
        m.regional_global_indices, m.tech_or_group, within=Any
    )
    m.limit_integer_new_capacity_constraint_rtv = Set(
        dimen=3, initialize=integer_capacity.limit_integer_new_capacity_indices
    )
    m.v_integer_new_capacity = Var(
        m.limit_integer_new_capacity_constraint_rtv, within=Integers, bounds=(0, None)
    )
    m.limit_integer_new_capacity_constraint = Constraint(
        m.limit_integer_new_capacity_constraint_rtv,
        rule=integer_capacity.limit_integer_new_capacity_constraint_rule,
    )


    m.limit_integer_net_capacity = Param(
        m.regional_global_indices, m.tech_or_group, within=Any
    )
    m.limit_integer_net_capacity_constraint_rpt = Set(
        dimen=3, initialize=integer_capacity.limit_integer_net_capacity_indices
    )
    m.v_integer_net_capacity = Var(
        m.limit_integer_net_capacity_constraint_rpt, within=Integers, bounds=(0, None)
    )
    m.limit_integer_net_capacity_constraint = Constraint(
        m.limit_integer_net_capacity_constraint_rpt,
        rule=integer_capacity.limit_integer_net_capacity_constraint_rule,
    )
