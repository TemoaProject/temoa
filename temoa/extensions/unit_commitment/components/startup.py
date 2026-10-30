"""Startup cost and emissions wiring for the unit_commitment extension.

Responsibilities:
  - uc_startup_rte_indices: sparse (r, t, e) set for startup emissions/cost data.
  - uc_startup_emission_expr_rule: per-(r, p, e) Expression of startup emissions
    (used in limit_emission_constraint).
  - append_startup_cost_to_total_cost: BuildAction that appends discounted startup
    cost to the objective.
  - append_startup_emission_cost_to_total_cost: BuildAction that appends discounted
    startup emission cost (started_units * days_in_season * unit_cap * emissions *
    cost_emission) to the objective.

v_uc_started counts starts on one day of a season. Every startup total multiplies it by
days_in_season, the number of days that season stands for.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from pyomo.environ import Expression, quicksum, value

from temoa.components.costs import add_period_cost, fixed_or_variable_cost

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.extensions.unit_commitment.core.model import UnitCommitmentModel
    from temoa.types.core_types import (
        Commodity,
        Period,
        Region,
        Season,
        Technology,
        TimeOfDay,
        Vintage,
    )

logger = logging.getLogger(__name__)


def days_in_season(model: TemoaModel, s: Season) -> float:
    """Number of days season s stands for in each period-year."""
    return value(model.segment_fraction_per_season[s]) * value(model.days_per_period)


def uc_startup_emissions_rpe(model: TemoaModel, r: Region, p: Period, e: Commodity) -> Expression:
    """
    Startup emissions to add to limit_emission_constraint.
    """
    model = cast('UnitCommitmentModel', model)
    return quicksum(
        value(model.uc_startup_emissions[_r, _e, t])
        * value(model.uc_unit_capacity[_r, t])
        * days_in_season(model, s)
        * model.v_uc_started[_r, p, s, d, t, v]
        for _r, _e, t in model.uc_startup_emissions.sparse_keys()
        if _r == r and _e == e
        for v in model.process_vintages.get((_r, p, t), [])
        for s in model.time_season
        for d in model.time_of_day
    )


def uc_startup_input_rpc(
    model: TemoaModel,
    r: Region,
    p: Period,
    c: Commodity,
) -> Expression:
    """
    Startup inputs to add to annual_commodity_balance_constraint.
    """
    model = cast('UnitCommitmentModel', model)
    return quicksum(
        uc_startup_input_rpsdc(model, r, p, s, d, c)
        for s in model.time_season
        for d in model.time_of_day
    )


def uc_startup_input_rpsdc(
    model: TemoaModel,
    r: Region,
    p: Period,
    s: Season,
    d: TimeOfDay,
    c: Commodity,
) -> Expression:
    """
    Startup inputs to add to commodity_balance_constraint.
    """
    model = cast('UnitCommitmentModel', model)
    days = days_in_season(model, s)
    return quicksum(
        value(model.uc_startup_input[r, i, t])
        * value(model.uc_unit_capacity[r, t])
        * days
        * model.v_uc_started[r, p, s, d, t, v]
        for _r, i, t in model.uc_startup_input.sparse_keys()
        if _r == r and i == c
        for v in model.process_vintages.get((_r, p, t), [])
    )


def uc_startup_cost_rptv(
    model: TemoaModel,
    r: Region,
    p: Period,
    t: Technology,
    v: Vintage,
) -> Expression:
    model = cast('UnitCommitmentModel', model)
    unit_cap = value(model.uc_unit_capacity[r, t])
    startup_cost_per_cap = value(model.uc_startup_cost[r, t])
    return quicksum(
        unit_cap
        * days_in_season(model, s)
        * model.v_uc_started[r, p, s, d, t, v]
        * startup_cost_per_cap
        for s in model.time_season
        for d in model.time_of_day
    )


def append_startup_costs(model: UnitCommitmentModel) -> None:
    r"""
    Append discounted startup costs and startup emission costs to the total-cost objective.

    Two cost terms are added:

    1. **Direct startup cost**: for each :math:`(r, t)` in :code:`uc_startup_cost`,
       the cost per timeslice is
       :math:`started\_units \cdot SFS_s \cdot DPP \cdot UC_{r,t}
       \cdot startup\_cost\_per\_capacity`, discounted and summed over all periods and
       vintages.  :math:`started\_units` counts starts on one day of season :math:`s`
       and :math:`SFS_s \cdot DPP` is the number of days that season stands for.

    2. **Startup emission cost**: for each :math:`(r, p, e)` in :code:`cost_emission`,
       the startup emissions (from :code:`uc_startup_emissions`, weighted by the same
       days per season) are multiplied by the emission cost rate, then discounted and
       added to the objective.
    """

    p_0 = min(model.time_optimize)
    gdr = value(model.global_discount_rate)

    for p in model.time_optimize:
        startup_costs = quicksum(
            fixed_or_variable_cost(
                cap_or_flow=1.0,
                cost_factor=uc_startup_cost_rptv(model, r, p, t, v),
                cost_years=value(model.period_length[p]),
                global_discount_rate=gdr,
                p_0=p_0,
                p=p,
            )
            for (r, t) in model.uc_startup_cost.sparse_keys()
            for v in model.process_vintages.get((r, p, t), [])
        )
        startup_costs += quicksum(
            fixed_or_variable_cost(
                cap_or_flow=1.0,
                cost_factor=(
                    model.cost_emission[r, p, e] * uc_startup_emissions_rpe(model, r, p, e)
                ),
                cost_years=value(model.period_length[p]),
                global_discount_rate=gdr,
                p_0=p_0,
                p=p,
            )
            for (r, period, e) in model.cost_emission
            if period == p
        )

        add_period_cost(model, p, startup_costs)
