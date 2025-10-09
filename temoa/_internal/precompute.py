# temoa/_internal/precompute.py
from logging import getLogger
from typing import TYPE_CHECKING

from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel

logger = getLogger(__name__)


def _populate_core_dictionaries(M: 'TemoaModel'):
    """
    Loops through the Efficiency parameter to populate the core sparse dictionaries
    that define process relationships, inputs, outputs, and active periods.

    This function is foundational for creating the sparse indices used throughout the model.
    """
    logger.debug('Populating core sparse dictionaries from Efficiency parameter.')
    first_period = min(M.time_future)
    exist_indices = M.ExistingCapacity.sparse_keys()

    for r, i, t, v, o in M.Efficiency.sparse_iterkeys():
        # A. Basic data validation and warnings
        process = (r, t, v)
        lifetime = value(M.LifetimeProcess[process])
        if v in M.vintage_exist:
            if process not in exist_indices and t not in M.tech_uncap:
                logger.warning(
                    f'Warning: {process} has a specified Efficiency, but does not '
                    f'have any existing install base (ExistingCapacity).'
                )
                continue
            if t not in M.tech_uncap and M.ExistingCapacity[process] == 0:
                logger.warning(
                    f'Notice: Unnecessary specification of ExistingCapacity for {process}. '
                    f'Declaring a capacity of zero may be omitted.'
                )
                continue
            if v + lifetime <= first_period:
                logger.info(
                    f'{process} specified as ExistingCapacity, but its '
                    f'lifetime ({lifetime} years) does not extend past the '
                    f'beginning of time_future ({first_period}).'
                )

        if M.Efficiency[r, i, t, v, o] == 0:
            logger.info(
                f'Notice: Unnecessary specification of Efficiency for {(r, i, t, v, o)}. '
                f'Specifying an efficiency of zero may be omitted.'
            )
            continue

        M.used_techs.add(t)

        # B. Loop through time periods to build time-dependent relationships
        for p in M.time_optimize:
            # Skip if tech is not invented or is already retired
            if p < v or v + lifetime <= p:
                continue

            pindex = (r, p, t, v)

            # C. Initialize dictionary keys if not present
            if pindex not in M.processInputs:
                M.processInputs[pindex] = set()
                M.processOutputs[pindex] = set()
            if (r, p, i) not in M.commodityDStreamProcess:
                M.commodityDStreamProcess[r, p, i] = set()
            if (r, p, o) not in M.commodityUStreamProcess:
                M.commodityUStreamProcess[r, p, o] = set()
            if (r, p, t, v, i) not in M.processOutputsByInput:
                M.processOutputsByInput[r, p, t, v, i] = set()
            if (r, p, t, v, o) not in M.processInputsByOutput:
                M.processInputsByOutput[r, p, t, v, o] = set()
            if (r, p, t) not in M.processVintages:
                M.processVintages[r, p, t] = set()
            if (r, t, v) not in M.processPeriods:
                M.processPeriods[r, t, v] = set()

            # D. Populate the dictionaries
            M.processInputs[pindex].add(i)
            M.processOutputs[pindex].add(o)
            M.commodityDStreamProcess[r, p, i].add((t, v))
            M.commodityUStreamProcess[r, p, o].add((t, v))
            M.processOutputsByInput[r, p, t, v, i].add(o)
            M.processInputsByOutput[r, p, t, v, o].add(i)
            M.processVintages[r, p, t].add(v)
            M.processPeriods[r, t, v].add(p)


def _create_technology_and_commodity_sets(M: 'TemoaModel'):
    """
    Populates technology and commodity subset definitions based on their roles
    (e.g., demand, flexible) identified from the Efficiency parameter.
    """
    logger.debug('Creating technology and commodity subsets.')
    for _r, _i, t, _v, o in M.Efficiency.sparse_iterkeys():
        if t in M.tech_flex and o not in M.commodity_flex:
            M.commodity_flex.add(o)

        if o in M.commodity_demand and t not in M.tech_demand:
            M.tech_demand.add(t)


def _create_operational_vintage_sets(M: 'TemoaModel'):
    """
    Populates vintage-based dictionaries for technologies with special
    operational characteristics like curtailment, baseload, storage, ramping, and reserves.
    """
    logger.debug('Creating vintage sets for operational constraints.')

    # Initialize the dictionaries to prevent KeyErrors later
    M.curtailmentVintages = {}
    M.baseloadVintages = {}
    M.storageVintages = {}
    M.rampUpVintages = {}
    M.rampDownVintages = {}
    M.isSeasonalStorage = {}
    M.processReservePeriods = {}  # Initialize the missing dictionary

    # Now populate them
    for r, p, t in M.processVintages:
        for v in M.processVintages[r, p, t]:
            key_rpt = (r, p, t)
            key_rp = (r, p)
            if t in M.tech_curtailment:
                M.curtailmentVintages.setdefault(key_rpt, set()).add(v)
            if t in M.tech_baseload:
                M.baseloadVintages.setdefault(key_rpt, set()).add(v)
            if t in M.tech_storage:
                M.storageVintages.setdefault(key_rpt, set()).add(v)
            if t in M.tech_upramping:
                M.rampUpVintages.setdefault(key_rpt, set()).add(v)
            if t in M.tech_downramping:
                M.rampDownVintages.setdefault(key_rpt, set()).add(v)
            if t in M.tech_reserve:
                M.processReservePeriods.setdefault(key_rp, set()).add((t, v))

    # A dictionary of whether a storage tech is seasonal, just to speed things up
    for t in M.tech_storage:
        M.isSeasonalStorage[t] = t in M.tech_seasonal_storage


def _create_limit_vintage_sets(M: 'TemoaModel'):
    """
    Populates vintage sets for technologies constrained by input/output split limits.
    """
    logger.debug('Creating vintage sets for split limits.')
    # Assuming M.processVintages is already populated
    for r, p, t in M.processVintages:
        for v in M.processVintages[r, p, t]:
            for i in M.processInputs.get((r, p, t, v), []):
                for op in M.operator:
                    if (r, p, i, t, op) in M.LimitTechInputSplit:
                        M.inputSplitVintages.setdefault((r, p, i, t, op), set()).add(v)
                    if (r, p, i, t, op) in M.LimitTechInputSplitAnnual:
                        M.inputSplitAnnualVintages.setdefault((r, p, i, t, op), set()).add(v)

            for o in M.processOutputs.get((r, p, t, v), []):
                for op in M.operator:
                    if (r, p, t, o, op) in M.LimitTechOutputSplit:
                        M.outputSplitVintages.setdefault((r, p, t, o, op), set()).add(v)
                    if (r, p, t, o, op) in M.LimitTechOutputSplitAnnual:
                        M.outputSplitAnnualVintages.setdefault((r, p, t, o, op), set()).add(v)


# In temoa/_internal/precompute.py
def _create_geography_sets(M: 'TemoaModel'):
    """Populates dictionaries related to inter-regional commodity exchange."""
    logger.debug('Creating geography-related sets for exchange technologies.')
    for r, i, t, v, o in M.Efficiency.sparse_iterkeys():
        if t not in M.tech_exchange:
            continue

        if '-' not in r:
            msg = f"Exchange technology {t} has an invalid region '{r}'. Must be 'region_from-region_to'."
            logger.error(msg)
            raise ValueError(msg)

        region_from, region_to = r.split('-', 1)

        lifetime = value(M.LifetimeProcess[r, t, v])
        for p in M.time_optimize:
            if p >= v and v + lifetime > p:
                M.exportRegions.setdefault((region_from, p, i), set()).add((region_to, t, v, o))
                M.importRegions.setdefault((region_to, p, o), set()).add((region_from, t, v, i))


# In temoa/_internal/precompute.py
def _create_capacity_and_retirement_sets(M: 'TemoaModel'):
    """
    Creates sets and dictionaries related to technology capacity, retirement,
    and end-of-life material flows.
    """
    logger.debug('Creating capacity, retirement, and construction/EOL sets.')
    # Retirement periods
    for r, _i, t, v, _o in M.Efficiency.sparse_iterkeys():
        lifetime = value(M.LifetimeProcess[r, t, v])
        for p in M.time_optimize:
            is_natural_eol = p <= v + lifetime < p + value(M.PeriodLength[p])
            is_early_retire = t in M.tech_retirement and v < p <= v + lifetime - value(
                M.PeriodLength[p]
            )
            is_survival_curve = M.isSurvivalCurveProcess[r, t, v] and v <= p <= v + lifetime

            if t not in M.tech_uncap and any((is_natural_eol, is_early_retire, is_survival_curve)):
                M.retirementPeriods.setdefault((r, t, v), set()).add(p)

    # Construction and End-of-life flows
    for r, i, t, v in M.ConstructionInput.sparse_iterkeys():
        M.capacityConsumptionTechs.setdefault((r, v, i), set()).add(t)

    for r, t, v, o in M.EndOfLifeOutput.sparse_iterkeys():
        if (r, t, v) in M.retirementPeriods:
            for p in M.retirementPeriods[r, t, v]:
                M.retirementProductionProcesses.setdefault((r, p, o), set()).add((t, v))

    # Active capacity sets
    M.newCapacity_rtv = set(
        (r, t, v)
        for r, p, t in M.processVintages
        for v in M.processVintages[r, p, t]
        if t not in M.tech_uncap and v in M.time_optimize
    )
    M.activeCapacityAvailable_rpt = set(
        (r, p, t)
        for r, p, t in M.processVintages
        if M.processVintages[r, p, t] and t not in M.tech_uncap
    )
    M.activeCapacityAvailable_rptv = set(
        (r, p, t, v)
        for r, p, t in M.processVintages
        for v in M.processVintages[r, p, t]
        if t not in M.tech_uncap
    )


def _create_commodity_balance_and_flow_sets(M: 'TemoaModel'):
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
