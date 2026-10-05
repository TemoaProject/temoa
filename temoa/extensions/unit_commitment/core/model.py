from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pyomo.environ import (
    Binary,
    BuildAction,
    Constraint,
    Integers,
    NonNegativeReals,
    Param,
    PositiveReals,
    Reals,
    Set,
    Var,
)

from temoa.components import operations
from temoa.extensions.unit_commitment.components import commitment, operating_reserves, startup

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types import ReserveProcessesDict
    from temoa.types.core_types import Season, TimeOfDay

    class UnitCommitmentModel(TemoaModel):
        """TemoaModel extended with unit-commitment components for type hinting/checking."""

        # --- Instantiation helpers ---
        uc_backslices: dict[tuple[Season, TimeOfDay, int], set[tuple[Season, TimeOfDay]]]
        operating_reserve_processes: ReserveProcessesDict

        # --- UC process parameters (indexed by region, tech) ---
        uc_unit_capacity: Param
        uc_min_output_fraction: Param
        uc_max_output_fraction: Param
        uc_min_up_time_hours: Param
        uc_min_down_time_hours: Param
        uc_linearized: Param

        # --- Startup parameters (indexed by region, tech, emission_commodity) ---
        uc_startup_cost: Param
        uc_startup_emissions: Param
        uc_startup_input: Param

        # --- Operating reserve sets and parameters ---
        operating_reserves: Set
        operating_reserve_margin: Param
        operating_reserve_sustain_hours: Param
        operating_reserve_activity_credit: Param
        operating_reserve_online_credit: Param
        operating_reserve_offline_credit: Param

        # --- Index sets ---
        uc_indices_rpsdtv: Set  # all (r,p,s,d,t,v) subject to UC
        default_ramp_up_constraint_rpsdtv: Set
        default_ramp_down_constraint_rpsdtv: Set
        uc_ramp_up_constraint_rpsdtv: Set
        uc_ramp_down_constraint_rpsdtv: Set
        operating_reserve_nrtpsd: Set
        operating_reserve_online_nrpsdtv: Set
        operating_reserve_storage_nrtrpsdtv: Set
        operating_reserve_online_exchange_nrrpsdtv: Set

        # --- Build actions ---
        uc_initialise: BuildAction
        uc_apply_integer_domains: BuildAction
        uc_append_startup_costs: BuildAction
        initialize_operating_reserves: BuildAction

        # --- Decision variables ---
        v_uc_online: Var
        v_uc_started: Var
        v_uc_stopped: Var
        v_orm_online_credit: Var

        # --- Constraints ---
        uc_online_upper_constraint: Constraint
        uc_min_output_constraint: Constraint
        uc_started_upper_tightening_constraint: Constraint
        uc_stopped_upper_tightening_constraint: Constraint
        uc_transition_constraint: Constraint
        uc_min_up_time_constraint: Constraint
        uc_min_down_time_constraint: Constraint
        uc_ramp_up_constraint: Constraint
        uc_ramp_down_constraint: Constraint
        operating_reserve_margin_constraint: Constraint
        operating_reserve_online_headroom_constraint: Constraint
        operating_reserve_online_headroom_credit_constraint: Constraint
        operating_reserve_storage_energy_constraint: Constraint
        operating_reserve_online_exchange_symmetry_constraint: Constraint


def register_early_components(model: TemoaModel) -> None:
    """Attach unit-commitment components to the core Temoa model."""
    m = cast('UnitCommitmentModel', model)

    # Instantiation helpers
    m.uc_backslices = {}

    # Params
    m.uc_unit_capacity = Param(m.regional_indices, m.tech_with_capacity, domain=PositiveReals)
    m.uc_min_output_fraction = Param(
        m.regional_indices, m.tech_with_capacity, domain=NonNegativeReals, default=0.0
    )
    m.uc_max_output_fraction = Param(
        m.regional_indices, m.tech_with_capacity, domain=NonNegativeReals, default=1.0
    )
    m.uc_min_up_time_hours = Param(
        m.regional_indices, m.tech_with_capacity, domain=Integers, default=0
    )
    m.uc_min_down_time_hours = Param(
        m.regional_indices, m.tech_with_capacity, domain=Integers, default=0
    )
    m.uc_linearized = Param(m.regional_indices, m.tech_with_capacity, domain=Binary, default=0)

    # Startup params
    m.uc_startup_cost = Param(m.regional_indices, m.tech_with_capacity, domain=PositiveReals)
    m.uc_startup_emissions = Param(
        m.regional_indices, m.commodity_emissions, m.tech_with_capacity, domain=PositiveReals
    )
    m.uc_startup_input = Param(
        m.regional_indices, m.commodity_physical, m.tech_with_capacity, domain=PositiveReals
    )

    # Index sets
    m.uc_indices_rpsdtv = Set(dimen=6, initialize=commitment.uc_constraint_indices)

    # BuildAction to initialise
    m.uc_initialise = BuildAction(rule=commitment.initialize_unit_commitment)

    # Decision variables
    m.v_uc_online = Var(m.uc_indices_rpsdtv, domain=NonNegativeReals, initialize=0)
    m.v_uc_started = Var(m.uc_indices_rpsdtv, domain=NonNegativeReals, initialize=0)
    m.v_uc_stopped = Var(m.uc_indices_rpsdtv, domain=NonNegativeReals, initialize=0)

    # BuildAction to upgrade domains to integers where flag is set
    m.uc_apply_integer_domains = BuildAction(rule=commitment.apply_integer_domains)


def register_model_components(model: TemoaModel) -> None:
    """Attach unit-commitment components to the core Temoa model."""
    m = cast('UnitCommitmentModel', model)

    # We intercepted these earlier. Split them by unit commitment vs default
    m.default_ramp_up_constraint_rpsdtv = Set(
        dimen=6, initialize=commitment.ramp_up_constraint_indices
    )
    m.default_ramp_down_constraint_rpsdtv = Set(
        dimen=6, initialize=commitment.ramp_down_constraint_indices
    )
    m.uc_ramp_up_constraint_rpsdtv = Set(
        dimen=6, initialize=commitment.uc_ramp_up_constraint_indices
    )
    m.uc_ramp_down_constraint_rpsdtv = Set(
        dimen=6, initialize=commitment.uc_ramp_down_constraint_indices
    )

    # Rebuild default constraints we intercepted
    m.ramp_up_constraint = Constraint(
        m.default_ramp_up_constraint_rpsdtv, rule=operations.ramp_up_constraint
    )
    m.ramp_down_constraint = Constraint(
        m.default_ramp_down_constraint_rpsdtv, rule=operations.ramp_down_constraint
    )

    # Constraints
    m.uc_online_upper_constraint = Constraint(
        m.uc_indices_rpsdtv, rule=commitment.uc_online_upper_constraint
    )
    m.uc_started_upper_tightening_constraint = Constraint(
        m.uc_indices_rpsdtv, rule=commitment.uc_started_upper_tightening_constraint
    )
    m.uc_stopped_upper_tightening_constraint = Constraint(
        m.uc_indices_rpsdtv, rule=commitment.uc_stopped_upper_tightening_constraint
    )
    m.uc_transition_constraint = Constraint(
        m.uc_indices_rpsdtv, rule=commitment.uc_transition_constraint
    )
    m.uc_min_output_constraint = Constraint(
        m.uc_indices_rpsdtv, rule=commitment.uc_min_output_constraint
    )
    m.uc_min_up_time_constraint = Constraint(
        m.uc_indices_rpsdtv, rule=commitment.uc_min_up_time_constraint
    )
    m.uc_min_down_time_constraint = Constraint(
        m.uc_indices_rpsdtv, rule=commitment.uc_min_down_time_constraint
    )
    m.uc_ramp_up_constraint = Constraint(
        m.uc_ramp_up_constraint_rpsdtv, rule=commitment.uc_ramp_up_constraint
    )
    m.uc_ramp_down_constraint = Constraint(
        m.uc_ramp_down_constraint_rpsdtv, rule=commitment.uc_ramp_down_constraint
    )

    # Startup costs to objective function
    m.uc_append_startup_costs = BuildAction(rule=startup.append_startup_costs)

    _register_operating_reserves(m)


def _register_operating_reserves(m: UnitCommitmentModel) -> None:
    """Attach operating reserve margin components."""
    m.operating_reserve_processes = {}

    m.operating_reserves = Set()
    m.operating_reserve_margin = Param(
        m.operating_reserves,
        m.regional_global_indices,
        m.tech_or_group,
        domain=PositiveReals,
    )
    m.operating_reserve_sustain_hours = Param(
        m.operating_reserves,
        m.regional_global_indices,
        m.tech_or_group,
        domain=NonNegativeReals,
    )
    m.operating_reserve_activity_credit = Param(
        m.operating_reserves, m.regional_indices, m.tech_all, domain=Reals
    )
    m.operating_reserve_online_credit = Param(
        m.operating_reserves, m.regional_indices, m.tech_with_capacity, domain=Reals
    )
    m.operating_reserve_offline_credit = Param(
        m.operating_reserves, m.regional_indices, m.tech_with_capacity, domain=Reals
    )

    m.initialize_operating_reserves = BuildAction(
        rule=operating_reserves.initialize_operating_reserve_margins
    )

    m.operating_reserve_nrtpsd = Set(
        dimen=6, initialize=operating_reserves.operating_reserve_indices
    )
    m.operating_reserve_online_nrpsdtv = Set(
        dimen=7, initialize=operating_reserves.operating_reserve_online_indices
    )
    m.operating_reserve_storage_nrtrpsdtv = Set(
        dimen=9, initialize=operating_reserves.operating_reserve_storage_indices
    )
    m.operating_reserve_online_exchange_nrrpsdtv = Set(
        dimen=8, initialize=operating_reserves.operating_reserve_online_exchange_indices
    )

    m.v_orm_online_credit = Var(m.operating_reserve_online_nrpsdtv, domain=Reals)

    m.operating_reserve_online_headroom_constraint = Constraint(
        m.operating_reserve_online_nrpsdtv,
        rule=operating_reserves.operating_reserve_online_headroom_constraint,
    )
    m.operating_reserve_online_headroom_credit_constraint = Constraint(
        m.operating_reserve_online_nrpsdtv,
        rule=operating_reserves.operating_reserve_online_headroom_credit_constraint,
    )
    m.operating_reserve_storage_energy_constraint = Constraint(
        m.operating_reserve_storage_nrtrpsdtv,
        rule=operating_reserves.operating_reserve_storage_energy_constraint,
    )
    m.operating_reserve_online_exchange_symmetry_constraint = Constraint(
        m.operating_reserve_online_exchange_nrrpsdtv,
        rule=operating_reserves.operating_reserve_online_exchange_symmetry_constraint,
    )
    m.operating_reserve_margin_constraint = Constraint(
        m.operating_reserve_nrtpsd, rule=operating_reserves.operating_reserve_margin_constraint
    )
