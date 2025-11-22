# temoa/components/flows.py
"""
Defines the flow-related components of the Temoa model.

This module is responsible for:
-  Pre-computing the sparse index sets for all types of commodity flows
    (standard, annual, flexible, storage, curtailment).
-  Defining the Pyomo index set functions used to construct the flow-related
    decision variables (v_flow_out, v_flow_in, v_flex, etc.).
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types import (
        ActiveFlexAnnualSet,
        ActiveFlowAnnualSet,
    )
    from temoa.types.core_types import (
        Commodity,
        Period,
        Region,
        Season,
        Technology,
        TimeOfDay,
        Vintage,
    )


logger = getLogger(__name__)


# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def flow_variable_indices(
    model: TemoaModel,
) -> (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
):
    return model.active_flow_rpsditvo


def flow_variable_annual_indices(
    model: TemoaModel,
) -> ActiveFlowAnnualSet:
    return model.active_flow_rpitvo


def flex_variable_indices(
    model: TemoaModel,
) -> (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
):
    return model.active_flex_rpsditvo


def flex_variable_annual_indices(
    model: TemoaModel,
) -> ActiveFlexAnnualSet:
    return model.active_flex_rpitvo


def flow_in_storage_variable_indices(
    model: TemoaModel,
) -> (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
):
    return model.active_flow_in_storage_rpsditvo


def curtailment_variable_indices(
    model: TemoaModel,
) -> (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
):
    return model.active_curtailment_rpsditvo


# ============================================================================
# PRE-COMPUTATION FUNCTION
# ============================================================================


def create_commodity_balance_and_flow_sets(model: TemoaModel) -> None:
    """
    Creates aggregated sets for commodity balances and detailed index sets for active flows.

    This function is a critical part of the model setup, responsible for
    creating the large, sparse index sets that define where decision variables
    for flows, capacity, and storage levels will be created.

    Populates:
        - model.commodity_balance_rpc: The master set of (r, p, c) for balance constraints.
        - model.active_flow_rpsditvo: Indices for time-sliced flows (v_flow_out).
        - model.active_flow_rpitvo: Indices for annual flows (v_flow_out_annual).
        - model.active_flex_rpsditvo: Indices for flexible time-sliced flows (v_flex).
        - model.active_flex_rpitvo: Indices for flexible annual flows (v_flex_annual).
        - model.active_flow_in_storage_rpsditvo: Indices for flows into storage (v_flow_in).
        - model.active_curtailment_rpsditvo: Indices for curtailed generation (v_curtailment).
        - model.active_activity_rptv: Master set of active (r, p, t, v) processes.
        - model.storage_level_indices_rpsdtv: Indices for storage state variables (v_storage_level).
        - model.seasonal_storage_level_indices_rpstv: Indices for seasonal storage levels.
    """
    logger.debug('Creating commodity balance and active flow index sets.')
    # 1. Commodity Balance
    commodity_upstream = set(
        model.commodity_up_stream_process
        | model.retirement_production_processes
        | model.import_regions
    )
    commodity_downstream = set(
        model.commodity_down_stream_process
        | model.capacity_consumption_techs
        | model.export_regions
    )
    model.commodity_balance_rpc = commodity_upstream.intersection(commodity_downstream)

    # 2. Active Flow Indices (Time-Sliced)
    model.active_flow_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in model.process_vintages
        if t not in model.tech_annual
        for v in model.process_vintages[r, p, t]
        for i in model.process_inputs.get((r, p, t, v), set())
        for o in model.process_outputs_by_input.get((r, p, t, v, i), set())
        for s in model.time_season[p]
        for d in model.time_of_day
    }

    # 3. Active Flow Indices (Annual)
    model.active_flow_rpitvo = {
        (r, p, i, t, v, o)
        for r, p, t in model.process_vintages
        for v in model.process_vintages[r, p, t]
        for i in model.process_inputs.get((r, p, t, v), set())
        for o in model.process_outputs_by_input.get((r, p, t, v, i), set())
        if t in model.tech_annual or (t in model.tech_demand and o in model.commodity_demand)
    }

    # 4. Active Flexible Technology Flow Indices
    model.active_flex_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in model.process_vintages
        if (t not in model.tech_annual) and (t in model.tech_flex)
        for v in model.process_vintages[r, p, t]
        for i in model.process_inputs.get((r, p, t, v), set())
        for o in model.process_outputs_by_input.get((r, p, t, v, i), set())
        for s in model.time_season[p]
        for d in model.time_of_day
    }

    model.active_flex_rpitvo = {
        (r, p, i, t, v, o)
        for r, p, t in model.process_vintages
        if (t in model.tech_annual) and (t in model.tech_flex)
        for v in model.process_vintages[r, p, t]
        for i in model.process_inputs.get((r, p, t, v), set())
        for o in model.process_outputs_by_input.get((r, p, t, v, i), set())
    }

    # 5. Active Storage and Curtailment Indices
    model.active_flow_in_storage_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in model.storage_vintages
        for v in model.storage_vintages[r, p, t]
        for i in model.process_inputs.get((r, p, t, v), set())
        for o in model.process_outputs_by_input.get((r, p, t, v, i), set())
        for s in model.time_season[p]
        for d in model.time_of_day
    }

    model.active_curtailment_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in model.curtailment_vintages
        for v in model.curtailment_vintages[r, p, t]
        for i in model.process_inputs.get((r, p, t, v), set())
        for o in model.process_outputs_by_input.get((r, p, t, v, i), set())
        for s in model.time_season[p]
        for d in model.time_of_day
    }

    # 6. Active Technology and Capacity Indices
    model.active_activity_rptv = {
        (r, p, t, v) for r, p, t in model.process_vintages for v in model.process_vintages[r, p, t]
    }

    # 7. Storage Level Indices
    model.storage_level_indices_rpsdtv = {
        (r, p, s, d, t, v)
        for r, p, t in model.storage_vintages
        for v in model.storage_vintages[r, p, t]
        for s in model.time_season[p]
        for d in model.time_of_day
    }

    model.seasonal_storage_level_indices_rpstv = {
        (r, p, s_stor, t, v)
        for r, p, t in model.storage_vintages
        if t in model.tech_seasonal_storage
        for v in model.storage_vintages[r, p, t]
        for _p, s_stor in model.sequential_to_season
        if _p == p
    }
