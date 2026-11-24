"""
Expressions for the objective functions that can be explored in a MOO run
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, cast

from pyomo.environ import quicksum, value

from temoa.components.costs import total_cost_rule
from temoa.extensions.multi_objective_optimization.moo_constants import MooObjective

if TYPE_CHECKING:
    from collections.abc import Iterable

    from temoa.core.model import TemoaModel
    from temoa.types import Commodity

logger = getLogger(__name__)


def _select_commodities(
    requested: Iterable[str] | None, available: set[str], description: str
) -> set[str]:
    """Return the requested commodities, or all the available ones if none is requested"""
    if not requested:
        return set(available)
    selected = set(requested)
    unknown = selected - available
    if unknown:
        msg = (
            f'MOO {description} not found in the model: {sorted(unknown)}.  '
            f'Available: {sorted(available)}'
        )
        logger.error(msg)
        raise ValueError(msg)
    return selected


def emission_commodities_in_model(model: TemoaModel) -> set[str]:
    commodities = {e for _r, e, *_ in model.emission_activity.sparse_keys()}
    commodities |= {e for _r, e, *_ in model.emission_embodied.sparse_keys()}
    commodities |= {e for _r, e, *_ in model.emission_end_of_life.sparse_keys()}
    if 'unit_commitment' in model.enabled_extensions:
        uc_model = cast('Any', model)
        commodities |= {e for _r, e, _t in uc_model.uc_startup_emissions.sparse_keys()}
    return commodities


def construction_input_commodities_in_model(model: TemoaModel) -> set[str]:
    return {i for _r, i, _t, _v in model.construction_input.sparse_keys()}


def total_emission_expression(model: TemoaModel, emission_commodities: Iterable[str] | None) -> Any:
    """
    Total emissions over the whole time horizon, summed over the selected emission commodities
    (all of them if none is selected).  Activity, embodied and end of life emissions are included.
    """
    selected = _select_commodities(
        emission_commodities, emission_commodities_in_model(model), 'emission commodities'
    )

    base = [
        (r, p, e, i, t, v, o)
        for (r, e, i, t, v, o) in model.emission_activity.sparse_keys()
        if e in selected
        for p in model.time_optimize
        if (r, p, t, v) in model.process_inputs
    ]

    process_emissions = quicksum(
        model.v_flow_out[r, p, s, d, i, t, v, o]
        * value(model.emission_activity[r, e, i, t, v, o])
        * value(model.period_length[p])
        for (r, p, e, i, t, v, o) in base
        if t not in model.tech_annual
        for s in model.time_season
        for d in model.time_of_day
    )

    process_emissions_annual = quicksum(
        model.v_flow_out_annual[r, p, i, t, v, o]
        * value(model.emission_activity[r, e, i, t, v, o])
        * value(model.period_length[p])
        for (r, p, e, i, t, v, o) in base
        if t in model.tech_annual
    )

    startup_emissions: Any = 0
    if 'unit_commitment' in model.enabled_extensions:
        from temoa.extensions.unit_commitment.components import startup

        startup_emissions = quicksum(
            startup.uc_startup_emissions_rpe(model, r, p, cast('Commodity', e))
            * value(model.period_length[p])
            for r in model.regions
            for p in model.time_optimize
            for e in selected
        )

    embodied_emissions = quicksum(
        model.v_new_capacity[r, t, v] * value(model.emission_embodied[r, e, t, v])
        for (r, e, t, v) in model.emission_embodied.sparse_keys()
        if e in selected and (r, t, v) in model.v_new_capacity
    )

    retirement_emissions = quicksum(
        model.v_annual_retirement[r, p, t, v]
        * value(model.emission_end_of_life[r, e, t, v])
        * value(model.period_length[p])
        for (r, e, t, v) in model.emission_end_of_life.sparse_keys()
        if e in selected and (r, t, v) in model.retirement_periods
        for p in model.retirement_periods[r, t, v]
    )

    return (
        process_emissions
        + process_emissions_annual
        + startup_emissions
        + embodied_emissions
        + retirement_emissions
    )


def total_construction_input_expression(
    model: TemoaModel, construction_input_commodities: Iterable[str] | None
) -> Any:
    """
    Total commodity consumption due to construction inputs over the whole time horizon, summed
    over the selected commodities (all of them if none is selected).
    """
    selected = _select_commodities(
        construction_input_commodities,
        construction_input_commodities_in_model(model),
        'construction input commodities',
    )

    return quicksum(
        model.v_new_capacity[r, t, v] * value(model.construction_input[r, i, t, v])
        for (r, i, t, v) in model.construction_input.sparse_keys()
        if i in selected and (r, t, v) in model.v_new_capacity
    )


def objective_expression(
    model: TemoaModel,
    objective: MooObjective,
    emission_commodities: Iterable[str] | None = None,
    construction_input_commodities: Iterable[str] | None = None,
) -> Any:
    match objective:
        case MooObjective.COST:
            return total_cost_rule(model)
        case MooObjective.EMISSION:
            return total_emission_expression(model, emission_commodities)
        case MooObjective.CONSTRUCTION_INPUT:
            return total_construction_input_expression(model, construction_input_commodities)
