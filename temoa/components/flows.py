from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

logger = getLogger(__name__)


def FlowVariableIndices(M: 'TemoaModel'):
    return M.activeFlow_rpsditvo


def FlowVariableAnnualIndices(M: 'TemoaModel'):
    return M.activeFlow_rpitvo


def FlexVariablelIndices(M: 'TemoaModel'):
    return M.activeFlex_rpsditvo


def FlexVariableAnnualIndices(M: 'TemoaModel'):
    return M.activeFlex_rpitvo


def FlowInStorageVariableIndices(M: 'TemoaModel'):
    return M.activeFlowInStorage_rpsditvo


def CurtailmentVariableIndices(M: 'TemoaModel'):
    return M.activeCurtailment_rpsditvo


def create_commodity_balance_and_flow_sets(M: 'TemoaModel'):
    """
    Creates the aggregated sets required for commodity balance constraints
    and the indexed sets for active technology flows, capacities, and storage levels.
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
    M.activeFlow_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.processVintages
        if t not in M.tech_annual
        for v in M.processVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
        for s in M.TimeSeason[p]  # REVERTED THIS LINE
        for d in M.time_of_day
    )

    # 3. Active Flow Indices (Annual)
    M.activeFlow_rpitvo = set(
        (r, p, i, t, v, o)
        for r, p, t in M.processVintages
        for v in M.processVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
        if t in M.tech_annual or (t in M.tech_demand and o in M.commodity_demand)
    )

    # 4. Active Flexible Technology Flow Indices
    M.activeFlex_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.processVintages
        if (t not in M.tech_annual) and (t in M.tech_flex)
        for v in M.processVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
        for s in M.TimeSeason[p]  # REVERTED THIS LINE
        for d in M.time_of_day
    )

    M.activeFlex_rpitvo = set(
        (r, p, i, t, v, o)
        for r, p, t in M.processVintages
        if (t in M.tech_annual) and (t in M.tech_flex)
        for v in M.processVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
    )

    # 5. Active Storage and Curtailment Indices
    M.activeFlowInStorage_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.storageVintages
        for v in M.storageVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
        for s in M.TimeSeason[p]  # REVERTED THIS LINE
        for d in M.time_of_day
    )

    M.activeCurtailment_rpsditvo = set(
        (r, p, s, d, i, t, v, o)
        for r, p, t in M.curtailmentVintages
        for v in M.curtailmentVintages[r, p, t]
        for i in M.processInputs.get((r, p, t, v), set())
        for o in M.processOutputsByInput.get((r, p, t, v, i), set())
        for s in M.TimeSeason[p]  # REVERTED THIS LINE
        for d in M.time_of_day
    )

    # 6. Active Technology and Capacity Indices
    M.activeActivity_rptv = set(
        (r, p, t, v) for r, p, t in M.processVintages for v in M.processVintages[r, p, t]
    )

    # 7. Storage Level Indices
    M.storageLevelIndices_rpsdtv = set(
        (r, p, s, d, t, v)
        for r, p, t in M.storageVintages
        for v in M.storageVintages[r, p, t]
        for s in M.TimeSeason[p]  # REVERTED THIS LINE
        for d in M.time_of_day
    )

    M.seasonalStorageLevelIndices_rpstv = set(
        (r, p, s_stor, t, v)
        for r, p, t in M.storageVintages
        if t in M.tech_seasonal_storage
        for v in M.storageVintages[r, p, t]
        for _p, s_stor in M.sequential_to_season
        if _p == p
    )
