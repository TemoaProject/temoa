# temoa/components/flows.py
"""
Defines the flow-related components of the Temoa model.

This module is responsible for:
-  Pre-computing the sparse index sets for all types of commodity flows
    (standard, annual, flexible, storage, curtailment).
-  Defining the Pyomo index set functions used to construct the flow-related
    decision variables (V_FlowOut, V_FlowIn, V_Flex, etc.).
"""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from temoa.types.core_types import (
    Commodity,
    Period,
    Region,
    Season,
    Technology,
    TimeOfDay,
    Vintage,
)

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

from temoa.types import (
    ActiveFlexAnnualSet,
    ActiveFlowAnnualSet,
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
    return model.activeFlow_rpsditvo


def flow_variable_annual_indices(
    model: TemoaModel,
) -> ActiveFlowAnnualSet:
    return model.activeFlow_rpitvo


def flex_variable_indices(
    model: TemoaModel,
) -> (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
):
    return model.activeFlex_rpsditvo


def flex_variable_annual_indices(
    model: TemoaModel,
) -> ActiveFlexAnnualSet:
    return model.activeFlex_rpitvo


def flow_in_storage_variable_indices(
    model: TemoaModel,
) -> (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
):
    return model.activeFlowInStorage_rpsditvo


def curtailment_variable_indices(
    model: TemoaModel,
) -> (
    set[tuple[Region, Period, Season, TimeOfDay, Commodity, Technology, Vintage, Commodity]] | None
):
    return model.activeCurtailment_rpsditvo


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
        - M.commodityBalance_rpc: The master set of (r, p, c) for balance constraints.
        - M.activeFlow_rpsditvo: Indices for time-sliced flows (V_FlowOut).
        - M.activeFlow_rpitvo: Indices for annual flows (V_FlowOutAnnual).
        - M.activeFlex_rpsditvo: Indices for flexible time-sliced flows (V_Flex).
        - M.activeFlex_rpitvo: Indices for flexible annual flows (V_FlexAnnual).
        - M.activeFlowInStorage_rpsditvo: Indices for flows into storage (V_FlowIn).
        - M.activeCurtailment_rpsditvo: Indices for curtailed generation (V_Curtailment).
        - M.activeActivity_rptv: Master set of active (r, p, t, v) processes.
        - M.storageLevelIndices_rpsdtv: Indices for storage state variables (V_StorageLevel).
        - M.seasonalStorageLevelIndices_rpstv: Indices for seasonal storage levels.
    """
    logger.debug('Creating commodity balance and active flow index sets.')
    # 1. Commodity Balance
    commodity_upstream = set(
        model.commodityUStreamProcess | model.retirementProductionProcesses | model.importRegions
    )
    commodity_downstream = set(
        model.commodityDStreamProcess | model.capacityConsumptionTechs | model.exportRegions
    )
    model.commodityBalance_rpc = commodity_upstream.intersection(commodity_downstream)

    # 2. Active Flow Indices (Time-Sliced)
    model.activeFlow_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in model.processVintages
        if t not in model.tech_annual
        for v in model.processVintages[r, p, t]
        for i in model.processInputs.get((r, p, t, v), set())
        for o in model.processOutputsByInput.get((r, p, t, v, i), set())
        for s in model.TimeSeason[p]  # REVERTED THIS LINE
        for d in model.time_of_day
    }

    # 3. Active Flow Indices (Annual)
    model.activeFlow_rpitvo = {
        (r, p, i, t, v, o)
        for r, p, t in model.processVintages
        for v in model.processVintages[r, p, t]
        for i in model.processInputs.get((r, p, t, v), set())
        for o in model.processOutputsByInput.get((r, p, t, v, i), set())
        if t in model.tech_annual or (t in model.tech_demand and o in model.commodity_demand)
    }

    # 4. Active Flexible Technology Flow Indices
    model.activeFlex_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in model.processVintages
        if (t not in model.tech_annual) and (t in model.tech_flex)
        for v in model.processVintages[r, p, t]
        for i in model.processInputs.get((r, p, t, v), set())
        for o in model.processOutputsByInput.get((r, p, t, v, i), set())
        for s in model.TimeSeason[p]  # REVERTED THIS LINE
        for d in model.time_of_day
    }

    model.activeFlex_rpitvo = {
        (r, p, i, t, v, o)
        for r, p, t in model.processVintages
        if (t in model.tech_annual) and (t in model.tech_flex)
        for v in model.processVintages[r, p, t]
        for i in model.processInputs.get((r, p, t, v), set())
        for o in model.processOutputsByInput.get((r, p, t, v, i), set())
    }

    # 5. Active Storage and Curtailment Indices
    model.activeFlowInStorage_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in model.storageVintages
        for v in model.storageVintages[r, p, t]
        for i in model.processInputs.get((r, p, t, v), set())
        for o in model.processOutputsByInput.get((r, p, t, v, i), set())
        for s in model.TimeSeason[p]  # REVERTED THIS LINE
        for d in model.time_of_day
    }

    model.activeCurtailment_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in model.curtailmentVintages
        for v in model.curtailmentVintages[r, p, t]
        for i in model.processInputs.get((r, p, t, v), set())
        for o in model.processOutputsByInput.get((r, p, t, v, i), set())
        for s in model.TimeSeason[p]  # REVERTED THIS LINE
        for d in model.time_of_day
    }

    # 6. Active Technology and Capacity Indices
    model.activeActivity_rptv = {
        (r, p, t, v) for r, p, t in model.processVintages for v in model.processVintages[r, p, t]
    }

    # 7. Storage Level Indices
    model.storageLevelIndices_rpsdtv = {
        (r, p, s, d, t, v)
        for r, p, t in model.storageVintages
        for v in model.storageVintages[r, p, t]
        for s in model.TimeSeason[p]  # REVERTED THIS LINE
        for d in model.time_of_day
    }

    model.seasonalStorageLevelIndices_rpstv = {
        (r, p, s_stor, t, v)
        for r, p, t in model.storageVintages
        if t in model.tech_seasonal_storage
        for v in model.storageVintages[r, p, t]
        for _p, s_stor in model.sequential_to_season
        if _p == p
    }
