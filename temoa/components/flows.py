# temoa/components/flows.py
"""
Defines the flow-related components of the Temoa model.

This module is responsible for:
-  Pre-computing the sparse index sets for all types of commodity flows
    (standard, annual, flexible, storage, curtailment).
-  Defining the Pyomo index set functions used to construct the flow-related
    decision variables (V_FlowOut, V_FlowIn, V_Flex, etc.).
"""

from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

from temoa.types import (
    ActiveFlexAnnualSet,
    ActiveFlowAnnualSet,
    RegionPeriodSeasonTimeInputTechVintageOutput,
)

logger = getLogger(__name__)


# ============================================================================
# PYOMO INDEX SET FUNCTIONS
# ============================================================================


def FlowVariableIndices(
    M: 'TemoaModel',
) -> set[RegionPeriodSeasonTimeInputTechVintageOutput] | None:
    return M.activeFlow_rpsditvo


def FlowVariableAnnualIndices(
    M: 'TemoaModel',
) -> ActiveFlowAnnualSet:
    return M.activeFlow_rpitvo


def FlexVariablelIndices(
    M: 'TemoaModel',
) -> set[RegionPeriodSeasonTimeInputTechVintageOutput] | None:
    return M.activeFlex_rpsditvo


def FlexVariableAnnualIndices(
    M: 'TemoaModel',
) -> ActiveFlexAnnualSet:
    return M.activeFlex_rpitvo


def FlowInStorageVariableIndices(
    M: 'TemoaModel',
) -> set[RegionPeriodSeasonTimeInputTechVintageOutput] | None:
    return M.activeFlowInStorage_rpsditvo


def CurtailmentVariableIndices(
    M: 'TemoaModel',
) -> set[RegionPeriodSeasonTimeInputTechVintageOutput] | None:
    return M.activeCurtailment_rpsditvo


# ============================================================================
# PRE-COMPUTATION FUNCTION
# ============================================================================


def create_commodity_balance_and_flow_sets(M: 'TemoaModel') -> None:
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
        M.commodityUStreamProcess | M.retirementProductionProcesses | M.importRegions
    )
    commodity_downstream = set(
        M.commodityDStreamProcess | M.capacityConsumptionTechs | M.exportRegions
    )
    M.commodityBalance_rpc = commodity_upstream.intersection(commodity_downstream)

    # 2. Active Flow Indices (Time-Sliced)
    M.activeFlow_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.processVintages
        if t not in M.tech_annual
        for v in M.processVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
        for s in M.TimeSeason[p]  # REVERTED THIS LINE
        for d in M.time_of_day
    }

    # 3. Active Flow Indices (Annual)
    M.activeFlow_rpitvo = {
        (r, p, i, t, v, o)
        for r, p, t in M.processVintages
        for v in M.processVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
        if t in M.tech_annual or (t in M.tech_demand and o in M.commodity_demand)
    }

    # 4. Active Flexible Technology Flow Indices
    M.activeFlex_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.processVintages
        if (t not in M.tech_annual) and (t in M.tech_flex)
        for v in M.processVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
        for s in M.TimeSeason[p]  # REVERTED THIS LINE
        for d in M.time_of_day
    }

    M.activeFlex_rpitvo = {
        (r, p, i, t, v, o)
        for r, p, t in M.processVintages
        if (t in M.tech_annual) and (t in M.tech_flex)
        for v in M.processVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
    }

    # 5. Active Storage and Curtailment Indices
    M.activeFlowInStorage_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.storageVintages
        for v in M.storageVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
        for s in M.TimeSeason[p]  # REVERTED THIS LINE
        for d in M.time_of_day
    }

    M.activeCurtailment_rpsditvo = {
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.curtailmentVintages
        for v in M.curtailmentVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
        for s in M.TimeSeason[p]  # REVERTED THIS LINE
        for d in M.time_of_day
    }

    # 6. Active Technology and Capacity Indices
    M.activeActivity_rptv = {
        (r, p, t, v) for r, p, t in M.processVintages for v in M.processVintages[r, p, t]
    }

    # 7. Storage Level Indices
    M.storageLevelIndices_rpsdtv = {
        (r, p, s, d, t, v)
        for r, p, t in M.storageVintages
        for v in M.storageVintages[r, p, t]
        for s in M.TimeSeason[p]  # REVERTED THIS LINE
        for d in M.time_of_day
    }

    M.seasonalStorageLevelIndices_rpstv = {
        (r, p, s_stor, t, v)
        for r, p, t in M.storageVintages
        if t in M.tech_seasonal_storage
        for v in M.storageVintages[r, p, t]
        for _p, s_stor in M.sequential_to_season
        if _p == p
    }
