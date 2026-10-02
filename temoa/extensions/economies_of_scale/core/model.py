from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pyomo.environ import (
    Any,
    Binary,
    BuildAction,
    Constraint,
    Integers,
    NonNegativeReals,
    Param,
    Set,
    Var,
)

from temoa.extensions.economies_of_scale.components import (
    cost_fixed_eos,
    cost_invest_eos,
    cost_variable_eos,
)

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types.core_types import Period, Region, Technology

    class EOSModel(TemoaModel):
        """Inherits the base TemoaModel class and declares EOS extension
        components for type checking/hinting purposes"""

        # Param (data from database table)
        cost_invest_eos: Param
        cost_fixed_eos: Param
        cost_variable_eos: Param

        # Primitive components (instantiation helpers)
        cost_invest_eos_segments: dict[tuple[Region, Technology], set[int]]
        cost_invest_eos_reference_process: dict[
            tuple[Region, Period, Technology], tuple[Region, Technology]
        ]
        cost_fixed_eos_segments: dict[tuple[Region, Period, Technology], set[int]]
        cost_variable_eos_segments: dict[tuple[Region, Period, Technology], set[int]]

        # Sets (indexing sets for variables and constraints)
        cost_invest_eos_rtn: Set
        cost_invest_eos_segment_rptn: Set
        cost_invest_eos_period_rpt: Set
        cost_fixed_eos_rptn: Set
        cost_variable_eos_rptn: Set
        cost_fixed_eos_period_rpt: Set
        cost_variable_eos_period_rpt: Set

        # Instantiation build actions
        append_cost_invest_eos_to_cost_invest_rtv: BuildAction
        initialize_cost_invest_eos: BuildAction
        append_cost_invest_eos_to_total_cost: BuildAction
        initialize_cost_fixed_eos: BuildAction
        append_cost_fixed_eos_to_total_cost: BuildAction
        initialize_cost_variable_eos: BuildAction
        append_cost_variable_eos_to_total_cost: BuildAction

        # Decision variables
        v_cost_invest_eos_cumulative_capacity: Var
        v_cost_invest_eos_segment_binary: Var
        v_cost_fixed_eos_capacity: Var
        v_cost_fixed_eos_segment_binary: Var
        v_cost_variable_eos_activity: Var
        v_cost_variable_eos_segment_binary: Var

        # Constraints
        cost_invest_eos_segment_binary_constraint: Constraint
        cost_invest_eos_capacity_lower_bound_constraint: Constraint
        cost_invest_eos_capacity_upper_bound_constraint: Constraint
        cost_invest_eos_cumulative_capacity_constraint: Constraint
        cost_fixed_eos_segment_binary_constraint: Constraint
        cost_fixed_eos_capacity_lower_bound_constraint: Constraint
        cost_fixed_eos_capacity_upper_bound_constraint: Constraint
        cost_fixed_eos_capacity_constraint: Constraint
        cost_variable_eos_segment_binary_constraint: Constraint
        cost_variable_eos_activity_lower_bound_constraint: Constraint
        cost_variable_eos_activity_upper_bound_constraint: Constraint
        cost_variable_eos_activity_constraint: Constraint


def register_early_eos_components(model: TemoaModel) -> None:
    """Build cost_invest_eos components that must be instantiated before loan parameters."""
    m = cast('EOSModel', model)

    m.cost_invest_eos_rtn = Set(
        within=model.regional_global_indices * model.tech_or_group * Integers
    )
    m.cost_invest_eos = Param(m.cost_invest_eos_rtn, domain=Any)

    m.cost_invest_eos_segments = {}
    m.cost_invest_eos_reference_process = {}

    m.cost_invest_eos_segment_rptn = Set(
        dimen=4, initialize=cost_invest_eos.cost_invest_eos_cumulative_capacity_indices
    )
    m.cost_invest_eos_period_rpt = Set(
        dimen=3, initialize=cost_invest_eos.cost_invest_eos_period_cost_indices
    )

    m.append_cost_invest_eos_to_cost_invest_rtv = BuildAction(
        rule=cost_invest_eos.append_cost_invest_eos_rtv
    )


def register_model_components(model: TemoaModel) -> None:
    """Build remaining components that can be instantiated at the end of model instantiation"""
    m = cast('EOSModel', model)

    # --- cost_invest_eos ---
    m.initialize_cost_invest_eos = BuildAction(rule=cost_invest_eos.initialize_cost_invest_eos)

    m.v_cost_invest_eos_cumulative_capacity = Var(
        m.cost_invest_eos_segment_rptn, domain=NonNegativeReals, initialize=0
    )
    m.v_cost_invest_eos_segment_binary = Var(
        m.cost_invest_eos_segment_rptn, domain=Binary, initialize=0
    )

    m.cost_invest_eos_segment_binary_constraint = Constraint(
        m.cost_invest_eos_period_rpt,
        rule=cost_invest_eos.cost_invest_eos_segment_binary_constraint,
    )
    m.cost_invest_eos_cumulative_capacity_constraint = Constraint(
        m.cost_invest_eos_period_rpt,
        rule=cost_invest_eos.cost_invest_eos_cumulative_capacity_constraint,
    )
    m.cost_invest_eos_capacity_lower_bound_constraint = Constraint(
        m.cost_invest_eos_segment_rptn,
        rule=cost_invest_eos.cost_invest_eos_capacity_lower_bound_constraint,
    )
    m.cost_invest_eos_capacity_upper_bound_constraint = Constraint(
        m.cost_invest_eos_segment_rptn,
        rule=cost_invest_eos.cost_invest_eos_capacity_upper_bound_constraint,
    )

    m.append_cost_invest_eos_to_total_cost = BuildAction(rule=cost_invest_eos.total_cost)

    # --- cost_fixed_eos ---
    m.cost_fixed_eos_rptn = Set(
        within=model.regional_global_indices * model.time_optimize * model.tech_or_group * Integers
    )
    m.cost_fixed_eos = Param(m.cost_fixed_eos_rptn, domain=Any)

    m.cost_fixed_eos_segments = {}

    m.cost_fixed_eos_period_rpt = Set(dimen=3, initialize=cost_fixed_eos.period_cost_indices)

    m.initialize_cost_fixed_eos = BuildAction(rule=cost_fixed_eos.initialize_components)

    m.v_cost_fixed_eos_capacity = Var(m.cost_fixed_eos_rptn, domain=NonNegativeReals, initialize=0)
    m.v_cost_fixed_eos_segment_binary = Var(m.cost_fixed_eos_rptn, domain=Binary, initialize=0)

    m.cost_fixed_eos_segment_binary_constraint = Constraint(
        m.cost_fixed_eos_period_rpt, rule=cost_fixed_eos.cost_fixed_eos_segment_binary_constraint
    )
    m.cost_fixed_eos_capacity_constraint = Constraint(
        m.cost_fixed_eos_period_rpt, rule=cost_fixed_eos.cost_fixed_eos_capacity_constraint
    )
    m.cost_fixed_eos_capacity_lower_bound_constraint = Constraint(
        m.cost_fixed_eos_rptn,
        rule=cost_fixed_eos.cost_fixed_eos_capacity_lower_bound_constraint,
    )
    m.cost_fixed_eos_capacity_upper_bound_constraint = Constraint(
        m.cost_fixed_eos_rptn,
        rule=cost_fixed_eos.cost_fixed_eos_capacity_upper_bound_constraint,
    )

    m.append_cost_fixed_eos_to_total_cost = BuildAction(rule=cost_fixed_eos.total_cost)

    # -- cost_variable_eos ---
    m.cost_variable_eos_segments = {}

    m.cost_variable_eos_rptn = Set(
        within=model.regional_global_indices * model.time_optimize * model.tech_or_group * Integers
    )
    m.cost_variable_eos = Param(m.cost_variable_eos_rptn, domain=Any)

    m.cost_variable_eos_period_rpt = Set(dimen=3, initialize=cost_variable_eos.period_cost_indices)

    m.initialize_cost_variable_eos = BuildAction(rule=cost_variable_eos.initialize_components)

    m.v_cost_variable_eos_activity = Var(
        m.cost_variable_eos_rptn, domain=NonNegativeReals, initialize=0
    )
    m.v_cost_variable_eos_segment_binary = Var(
        m.cost_variable_eos_rptn, domain=Binary, initialize=0
    )

    m.cost_variable_eos_segment_binary_constraint = Constraint(
        m.cost_variable_eos_period_rpt,
        rule=cost_variable_eos.cost_variable_eos_segment_binary_constraint,
    )
    m.cost_variable_eos_activity_constraint = Constraint(
        m.cost_variable_eos_period_rpt,
        rule=cost_variable_eos.cost_variable_eos_activity_constraint,
    )
    m.cost_variable_eos_activity_lower_bound_constraint = Constraint(
        m.cost_variable_eos_rptn,
        rule=cost_variable_eos.cost_variable_eos_activity_lower_bound_constraint,
    )
    m.cost_variable_eos_activity_upper_bound_constraint = Constraint(
        m.cost_variable_eos_rptn,
        rule=cost_variable_eos.cost_variable_eos_activity_upper_bound_constraint,
    )

    m.append_cost_variable_eos_to_total_cost = BuildAction(rule=cost_variable_eos.total_cost)
