#!/usr/bin/env python

"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

SPDX-License-Identifier: MIT

"""

import logging

from pyomo.core import BuildCheck, Set, Var
from pyomo.environ import (
    AbstractModel,
    Any,
    BuildAction,
    Constraint,
    Integers,
    NonNegativeReals,
    Objective,
    Param,
    minimize,
)

from temoa._internal.temoa_initialize import (
    # ============================================================================
    # Index creation functions for constraints and variables
    # ============================================================================
    AnnualCommodityBalanceConstraintIndices,
    AnnualRetirementVariableIndices,
    BaseloadDiurnalConstraintIndices,
    CapacityAnnualConstraintIndices,
    CapacityAvailableVariableIndices,
    CapacityConstraintIndices,
    CapacityFactorTechIndices,
    CapacityVariableIndices,
    CheckCapacityFactorProcess,
    CheckEfficiencyIndices,
    CheckEfficiencyVariable,
    CommodityBalanceConstraintIndices,
    CostFixedIndices,
    CostVariableIndices,
    CreateDemands,
    CreateRegionalIndices,
    CreateSparseDicts,
    CreateSurvivalCurve,
    CreateTimeSeasonSequential,
    CreateTimeSequence,
    CurtailmentVariableIndices,
    DemandActivityConstraintIndices,
    EmissionActivityIndices,
    FlexVariableAnnualIndices,
    FlexVariablelIndices,
    FlowInStorageVariableIndices,
    FlowVariableAnnualIndices,
    FlowVariableIndices,
    LifetimeLoanProcessIndices,
    LifetimeProcessIndices,
    LimitDegrowthCapacityIndices,
    LimitDegrowthNewCapacityDeltaIndices,
    LimitDegrowthNewCapacityIndices,
    LimitGrowthCapacityIndices,
    LimitGrowthNewCapacityDeltaIndices,
    LimitGrowthNewCapacityIndices,
    LimitTechInputSplitAnnualConstraintIndices,
    LimitTechInputSplitAverageConstraintIndices,
    LimitTechInputSplitConstraintIndices,
    LimitTechOutputSplitAnnualConstraintIndices,
    LimitTechOutputSplitAverageConstraintIndices,
    LimitTechOutputSplitConstraintIndices,
    LinkedTechConstraintIndices,
    ModelProcessLifeIndices,
    RampDownDayConstraintIndices,
    RampDownSeasonConstraintIndices,
    RampUpDayConstraintIndices,
    RampUpSeasonConstraintIndices,
    RegionalExchangeCapacityConstraintIndices,
    ReserveMarginIndices,
    RetiredCapacityVariableIndices,
    SeasonalStorageConstraintIndices,
    SeasonalStorageLevelVariableIndices,
    StorageConstraintIndices,
    StorageLevelVariableIndices,
    # Default value functions
    get_default_capacity_factor,
    get_default_loan_rate,
    get_default_process_lifetime,
    get_default_survival,
    get_loan_life,
    # Set initialization functions
    init_set_time_optimize,
    init_set_vintage_exist,
    init_set_vintage_optimize,
    # Validation functions
    validate_SegFrac,
    validate_time,
    validate_TimeNext,
)

# ============================================================================
# Temoa Constraint Functions
# Core model constraints and business logic rules
# ============================================================================
from temoa._internal.temoa_rules import (
    # Core capacity constraints
    AdjustedCapacity_Constraint,
    AnnualCommodityBalance_Constraint,
    # Retirement constraints
    AnnualRetirement_Constraint,
    # Ramping constraints
    BaseloadDiurnal_Constraint,
    Capacity_Constraint,
    CapacityAnnual_Constraint,
    CapacityAvailableByPeriodAndTech_Constraint,
    CommodityBalance_Constraint,
    # Activity and flow constraints
    Demand_Constraint,
    DemandActivity_Constraint,
    # Limit constraints (capacity, activity, emissions, etc.)
    LimitActivity_Constraint,
    LimitActivityShare_Constraint,
    LimitAnnualCapacityFactor_Constraint,
    LimitCapacity_Constraint,
    LimitCapacityShare_Constraint,
    # Growth/degrowth constraints
    LimitDegrowthCapacityConstraint_rule,
    LimitDegrowthNewCapacityConstraint_rule,
    LimitDegrowthNewCapacityDeltaConstraint_rule,
    LimitEmission_Constraint,
    LimitGrowthCapacityConstraint_rule,
    LimitGrowthNewCapacityConstraint_rule,
    LimitGrowthNewCapacityDeltaConstraint_rule,
    LimitNewCapacity_Constraint,
    LimitNewCapacityShare_Constraint,
    LimitResource_Constraint,
    LimitSeasonalCapacityFactor_Constraint,
    LimitStorageFraction_Constraint,
    # Technology split constraints
    LimitTechInputSplit_Constraint,
    LimitTechInputSplitAnnual_Constraint,
    LimitTechInputSplitAverage_Constraint,
    LimitTechOutputSplit_Constraint,
    LimitTechOutputSplitAnnual_Constraint,
    LimitTechOutputSplitAverage_Constraint,
    LinkedEmissionsTech_Constraint,
    # Parameter calculation rules
    ParamLoanAnnualize_rule,
    ParamPeriodLength,
    ParamProcessLifeFraction_rule,
    RampDownDay_Constraint,
    RampDownSeason_Constraint,
    RampUpDay_Constraint,
    RampUpSeason_Constraint,
    # Regional and special constraints
    RegionalExchangeCapacity_Constraint,
    RenewablePortfolioStandard_Constraint,
    ReserveMargin_Constraint,
    SeasonalStorageEnergy_Constraint,
    SeasonalStorageEnergyUpperBound_Constraint,
    SegFracPerSeason_rule,
    StorageChargeRate_Constraint,
    StorageDischargeRate_Constraint,
    # Storage constraints
    StorageEnergy_Constraint,
    StorageEnergyUpperBound_Constraint,
    StorageThroughput_Constraint,
    # Objective function
    TotalCost_rule,
)

# ============================================================================
# Validation Functions
# Input validation and data integrity checks
# ============================================================================
from temoa.model_checking.validators import (
    no_slash_or_pipe,
    region_check,
    region_group_check,
    validate_0to1,
    validate_Efficiency,
    validate_linked_tech,
    validate_ReserveMargin,
    validate_tech_sets,
)

logger = logging.getLogger(__name__)


class TemoaModel(AbstractModel):
    """
    An instance of the abstract Temoa model
    """

    # this is used in several places outside this class, and this provides no-build access to it
    default_lifetime_tech = 40

    def __init__(M, *args, **kwargs):
        AbstractModel.__init__(M, *args, **kwargs)

        ################################################
        #       Internally used Data Containers        #
        #       (not formal model elements)            #
        ################################################

        # Dev Note:  The triple-quotes UNDER the items below pop up as dox in most IDEs
        M.processInputs = dict()
        M.processOutputs = dict()
        M.processLoans = dict()
        M.activeFlow_rpsditvo = None
        """a flow index for techs NOT in tech_annual"""

        M.activeFlow_rpitvo = None
        """a flow index for techs in tech_annual only"""

        M.activeFlex_rpsditvo = None
        M.activeFlex_rpitvo = None
        M.activeFlowInStorage_rpsditvo = None
        M.activeCurtailment_rpsditvo = None
        M.activeActivity_rptv = None
        M.storageLevelIndices_rpsdtv = None
        M.seasonalStorageLevelIndices_rpstv = None
        """currently available (within lifespan) (r, p, t, v) tuples (from M.processVintages)"""

        M.activeRegionsForTech = None
        """currently available regions by period and tech {(p, t) : r}"""

        M.newCapacity_rtv = None
        M.activeCapacityAvailable_rpt = None
        M.activeCapacityAvailable_rptv = None
        M.groupRegionActiveFlow_rpt = None  # Set of valid group-region, period, tech indices
        M.commodityBalance_rpc = None  # Set of valid region-period-commodity indices to balance
        M.commodityDStreamProcess = dict()  # The downstream process of a commodity during a period
        M.commodityUStreamProcess = dict()  # The upstream process of a commodity during a period
        M.capacityConsumptionTechs = (
            dict()
        )  # New capacity consuming a commodity during a period [r,p,c] -> t
        M.retirementProductionProcesses = (
            dict()
        )  # Retired capacity producing a commodity during a period [r,p,c] -> t,v
        M.processInputsByOutput = dict()
        M.processOutputsByInput = dict()
        M.processTechs = dict()
        M.processReservePeriods = dict()
        M.processPeriods = dict()  # {(r, t, v): set(p)}
        M.retirementPeriods = (
            dict()
        )  # {(r, t, v): set(p)} periods in which a process can economically or naturally retire
        M.processVintages = dict()
        M.survivalCurvePeriods: dict[tuple, set] = (
            dict()
        )  # {(r, t, v): set(p)} periods for which the process has a defined survival fraction
        """current available (within lifespan) vintages {(r, p, t) : set(v)}"""

        M.baseloadVintages = dict()
        M.curtailmentVintages = dict()
        M.storageVintages = dict()
        M.rampUpVintages = dict()
        M.rampDownVintages = dict()
        M.inputSplitVintages = dict()
        M.inputSplitAnnualVintages = dict()
        M.outputSplitVintages = dict()
        M.outputSplitAnnualVintages = dict()
        # M.processByPeriodAndOutput = dict() # not currently used
        M.exportRegions = dict()
        M.importRegions = dict()

        # These establish time sequencing
        M.time_next = dict()  # {(p, s, d): (s_next, d_next)} sequence of following time slices
        M.time_next_sequential = dict()  # {(p, s_seq): (s_seq_next)} next virtual storage season
        M.sequential_to_season = (
            dict()
        )  # {(p, s_seq): (s)} season matching this virtual storage season

        ################################################
        #             Switching Sets                   #
        #  (to avoid slow searches in initialisation)  #
        ################################################

        M.isEfficiencyVariable: dict[tuple, bool] = (
            dict()
        )  # {(r, p, i, t, v, o): bool} which efficiencies have variable indexing
        M.isCapacityFactorProcess: dict[tuple, bool] = (
            dict()
        )  # {(r, p, t, v): bool} which capacity factors have have period-vintage indexing
        M.isSeasonalStorage: dict[tuple, bool] = (
            dict()
        )  # {t: bool} whether a storage tech is seasonal storage
        M.isSurvivalCurveProcess: dict[tuple, bool] = (
            dict()
        )  # {(r, t, v): bool} whether a process uses survival curves.

        ################################################
        #                 Model Sets                   #
        #    (used for indexing model elements)        #
        ################################################

        M.progress_marker_1 = BuildAction(['Starting to build Sets'], rule=progress_check)

        M.operator = Set()

        # Define time periods
        M.time_exist = Set(ordered=True)
        M.time_future = Set(ordered=True)
        M.time_optimize = Set(ordered=True, initialize=init_set_time_optimize, within=M.time_future)
        # Define time period vintages to track capacity installation
        M.vintage_exist = Set(ordered=True, initialize=init_set_vintage_exist)
        M.vintage_optimize = Set(ordered=True, initialize=init_set_vintage_optimize)
        M.vintage_all = Set(initialize=M.time_exist | M.time_optimize)
        # Perform some basic validation on the specified time periods.
        M.validate_time = BuildAction(rule=validate_time)

        # Define the model time slices
        M.time_season = Set(ordered=True, validate=no_slash_or_pipe)
        M.time_season_sequential = Set(ordered=True, validate=no_slash_or_pipe)
        M.TimeSeason = Set(M.time_optimize, within=M.time_season, ordered=True)
        M.time_of_day = Set(ordered=True, validate=no_slash_or_pipe)

        # This is just to get the TimeStorageSeason table sequentially.
        # There must be a better way but this works for now
        M.ordered_season_sequential = Set(
            dimen=3, within=M.time_optimize * M.time_season_sequential * M.time_season, ordered=True
        )

        # Define regions
        M.regions = Set(validate=region_check)
        # RegionalIndices is the set of all the possible combinations of interregional exchanges
        # plus original region indices. If tech_exchange is empty, RegionalIndices =regions.
        M.regionalIndices = Set(initialize=CreateRegionalIndices)
        M.regionalGlobalIndices = Set(validate=region_group_check)

        # Define technology-related sets
        # M.tech_resource = Set() # not actually used by anything
        M.tech_production = Set()
        M.tech_all = Set(
            initialize=M.tech_production, validate=no_slash_or_pipe
        )  # was M.tech_resource | M.tech_production
        M.tech_baseload = Set(within=M.tech_all)
        M.tech_annual = Set(within=M.tech_all)
        M.tech_demand = Set(within=M.tech_all)
        # annual storage not supported in Storage constraint or TableWriter, so exclude from domain
        M.tech_storage = Set(within=M.tech_all)
        M.tech_reserve = Set(within=M.tech_all)
        M.tech_upramping = Set(within=M.tech_all)
        M.tech_downramping = Set(within=M.tech_all)
        M.tech_curtailment = Set(within=M.tech_all)
        M.tech_flex = Set(within=M.tech_all)
        # ensure there is no overlap flex <=> curtailable technologies
        M.tech_exchange = Set(within=M.tech_all)

        # Define groups for technologies
        M.tech_group_names = Set()
        M.tech_group_members = Set(M.tech_group_names, within=M.tech_all)
        M.tech_or_group = Set(initialize=M.tech_group_names | M.tech_all)

        M.tech_seasonal_storage = Set(within=M.tech_storage)
        """storage technologies using the interseasonal storage feature"""

        M.tech_uncap = Set(within=M.tech_all - M.tech_reserve)
        """techs with unlimited capacity, ALWAYS available within lifespan"""

        M.tech_exist = Set()
        """techs with existing capacity, want to keep these for accounting reasons"""

        # the below is a convenience for domain checking in params below that should not accept
        # uncap techs...
        M.tech_with_capacity = Set(initialize=M.tech_all - M.tech_uncap)
        """techs eligible for capacitization"""
        # Define techs for which economic retirement is an option
        # Note:  Storage techs cannot (currently) be retired due to linkage to initialization
        #        process, which is currently incapable of reducing initializations on retirements.
        # Note2: I think this has been fixed but I can't tell what the problem was. Suspect
        #        it was the old StorageInit constraint
        M.tech_retirement = Set(within=M.tech_with_capacity)  # - M.tech_storage)

        M.validate_techs = BuildAction(rule=validate_tech_sets)

        # Define commodity-related sets
        M.commodity_demand = Set()
        M.commodity_emissions = Set()
        M.commodity_physical = Set()
        M.commodity_waste = Set()
        M.commodity_flex = Set(within=M.commodity_physical)
        M.commodity_source = Set(within=M.commodity_physical)
        M.commodity_annual = Set(within=M.commodity_physical)
        M.commodity_carrier = Set(
            initialize=M.commodity_physical | M.commodity_demand | M.commodity_waste
        )
        M.commodity_all = Set(
            initialize=M.commodity_carrier | M.commodity_emissions, validate=no_slash_or_pipe
        )

        ################################################
        #              Model Parameters                #
        #    (data gathered/derived from source)       #
        ################################################

        # ---------------------------------------------------------------
        # Dev Note:
        # In order to increase model efficiency, we use sparse
        # indexing of parameters, variables, and equations to prevent the
        # creation of indices for which no data exists. While basic model sets
        # are defined above, sparse index sets are defined below adjacent to the
        # appropriate parameter, variable, or constraint and all are initialized
        # in temoa_initialize.py.
        # Because the function calls that define the sparse index sets obscure the
        # sets utilized, we use a suffix that includes a one character name for each
        # set. Example: "_tv" indicates a set defined over "technology" and "vintage".
        # The complete index set is: psditvo, where p=period, s=season, d=day,
        # i=input commodity, t=technology, v=vintage, o=output commodity.
        # ---------------------------------------------------------------

        # these "progress markers" report build progress in the log, if the level == debug
        M.progress_marker_2 = BuildAction(['Starting to build Params'], rule=progress_check)

        M.GlobalDiscountRate = Param(default=0.05)

        # Define time-related parameters
        M.PeriodLength = Param(M.time_optimize, initialize=ParamPeriodLength)
        M.SegFrac = Param(M.time_optimize, M.time_season, M.time_of_day)
        M.validate_SegFrac = BuildAction(rule=validate_SegFrac)
        M.TimeSequencing = Set()  # How do states carry between time segments?
        M.TimeNext = Set(
            ordered=True
        )  # This is just to get data from the table. Hidden feature and usually not used
        M.validate_TimeNext = BuildAction(rule=validate_TimeNext)

        # Define demand- and resource-related parameters
        # Dev Note:  There does not appear to be a DB table supporting DemandDefaultDistro.
        #            This does not cause any problems, so let it be for now.
        #            Doesn't seem to be much point in the table. Just clones SegFrac
        # M.DemandDefaultDistribution = Param(
        #     M.time_optimize, M.time_season, M.time_of_day, mutable=True
        # )
        M.DemandSpecificDistribution = Param(
            M.regions,
            M.time_optimize,
            M.time_season,
            M.time_of_day,
            M.commodity_demand,
            mutable=True,
            default=0,
        )

        M.DemandConstraint_rpc = Set(within=M.regions * M.time_optimize * M.commodity_demand)
        M.Demand = Param(M.DemandConstraint_rpc)

        # Dev Note:  This parameter is currently NOT implemented.  Preserved for later refactoring
        # LimitResource IS implemented but sums cumulatively for a technology rather than
        # resource commodity
        # M.ResourceConstraint_rpr = Set(within=M.regions * M.time_optimize * M.commodity_physical)
        # M.ResourceBound = Param(M.ResourceConstraint_rpr)

        # Define technology performance parameters
        M.CapacityToActivity = Param(M.regionalIndices, M.tech_all, default=1)

        M.ExistingCapacity = Param(M.regionalIndices, M.tech_exist, M.vintage_exist)

        # Dev Note:  The below is temporarily useful for passing down to validator to find
        # set violations
        #            Uncomment this assignment, and comment out the orig below it...
        # M.Efficiency = Param(
        #     Any, Any, Any, Any, Any,
        #     within=NonNegativeReals, validate=validate_Efficiency
        # )

        # devnote: need these here or CheckEfficiencyIndices may flag these commodities as unused
        M.ConstructionInput = Param(
            M.regions, M.commodity_physical, M.tech_with_capacity, M.vintage_optimize
        )
        M.EndOfLifeOutput = Param(
            M.regions, M.tech_with_capacity, M.vintage_all, M.commodity_carrier
        )

        M.Efficiency = Param(
            M.regionalIndices,
            M.commodity_physical,
            M.tech_all,
            M.vintage_all,
            M.commodity_carrier,
            within=NonNegativeReals,
            validate=validate_Efficiency,
        )
        M.validate_UsedEfficiencyIndices = BuildAction(rule=CheckEfficiencyIndices)

        M.EfficiencyVariable = Param(
            M.regionalIndices,
            M.time_optimize,
            M.time_season,
            M.time_of_day,
            M.commodity_physical,
            M.tech_all,
            M.vintage_all,
            M.commodity_carrier,
            within=NonNegativeReals,
            default=1,
        )

        M.LifetimeTech = Param(
            M.regionalIndices, M.tech_all, default=TemoaModel.default_lifetime_tech
        )

        M.LifetimeProcess_rtv = Set(dimen=3, initialize=LifetimeProcessIndices)
        M.LifetimeProcess = Param(M.LifetimeProcess_rtv, default=get_default_process_lifetime)

        M.LifetimeSurvivalCurve = Param(
            M.regionalIndices,
            Integers,
            M.tech_all,
            M.vintage_all,
            default=get_default_survival,
            validate=validate_0to1,
            mutable=True,
        )
        M.Create_SurvivalCurve = BuildAction(rule=CreateSurvivalCurve)

        M.LoanLifetimeProcess_rtv = Set(dimen=3, initialize=LifetimeLoanProcessIndices)

        # Dev Note:  The LoanLifetimeProcess table *could* be removed.  There is no longer a
        #            supporting table in the database.  It is just a "passthrough" now to the
        #            default LoanLifetimeTech. It is already stitched in to the model,
        #            so will leave it for now.  Table may be revived.

        M.LoanLifetimeProcess = Param(M.LoanLifetimeProcess_rtv, default=get_loan_life)

        M.LimitTechInputSplit = Param(
            M.regions,
            M.time_optimize,
            M.commodity_physical,
            M.tech_all,
            M.operator,
            validate=validate_0to1,
        )
        M.LimitTechInputSplitAnnual = Param(
            M.regions,
            M.time_optimize,
            M.commodity_physical,
            M.tech_all,
            M.operator,
            validate=validate_0to1,
        )

        M.LimitTechOutputSplit = Param(
            M.regions,
            M.time_optimize,
            M.tech_all,
            M.commodity_carrier,
            M.operator,
            validate=validate_0to1,
        )
        M.LimitTechOutputSplitAnnual = Param(
            M.regions,
            M.time_optimize,
            M.tech_all,
            M.commodity_carrier,
            M.operator,
            validate=validate_0to1,
        )

        M.RenewablePortfolioStandardConstraint_rpg = Set(
            within=M.regions * M.time_optimize * M.tech_group_names
        )
        M.RenewablePortfolioStandard = Param(
            M.RenewablePortfolioStandardConstraint_rpg, validate=validate_0to1
        )

        # These need to come before validate_SeasonSequential
        M.RampUpHourly = Param(M.regions, M.tech_upramping, validate=validate_0to1)
        M.RampDownHourly = Param(M.regions, M.tech_downramping, validate=validate_0to1)

        # Set up representation of time
        M.DaysPerPeriod = Param()
        M.SegFracPerSeason = Param(M.time_optimize, M.time_season, initialize=SegFracPerSeason_rule)
        M.TimeSeasonSequential = Param(
            M.time_optimize, M.time_season_sequential, M.time_season, mutable=True
        )
        M.validate_SeasonSequential = BuildAction(rule=CreateTimeSeasonSequential)
        M.Create_TimeSequence = BuildAction(rule=CreateTimeSequence)

        # The method below creates a series of helper functions that are used to
        # perform the sparse matrix of indexing for the parameters, variables, and
        # equations below.
        M.Create_SparseDicts = BuildAction(rule=CreateSparseDicts)
        M.initialize_Demands = BuildAction(rule=CreateDemands)

        M.CapacityFactor_rpsdt = Set(dimen=5, initialize=CapacityFactorTechIndices)
        M.CapacityFactorTech = Param(M.CapacityFactor_rpsdt, default=1, validate=validate_0to1)

        # Dev note:  using a default function below alleviates need to make this set.
        # M.CapacityFactor_rsdtv = Set(dimen=5, initialize=CapacityFactorProcessIndices)
        M.CapacityFactorProcess = Param(
            M.regionalIndices,
            M.time_optimize,
            M.time_season,
            M.time_of_day,
            M.tech_with_capacity,
            M.vintage_all,
            # validate=validate_CapacityFactorProcess, # opting for a quicker validation, just 0->1
            validate=validate_0to1,
            default=get_default_capacity_factor,  # slow but only called if a value is missing
        )

        M.CapacityConstraint_rpsdtv = Set(dimen=6, initialize=CapacityConstraintIndices)
        M.initialize_CapacityFactors = BuildAction(rule=CheckCapacityFactorProcess)
        M.initialize_EfficiencyVariable = BuildAction(rule=CheckEfficiencyVariable)

        # Define technology cost parameters
        # dev note:  the CostFixed_rptv isn't truly needed, but it is included in a constraint, so
        #            let it go for now
        M.CostFixed_rptv = Set(dimen=4, initialize=CostFixedIndices)
        M.CostFixed = Param(M.CostFixed_rptv)

        M.CostInvest_rtv = Set(within=M.regionalIndices * M.tech_all * M.time_optimize)
        M.CostInvest = Param(M.CostInvest_rtv)

        M.DefaultLoanRate = Param(domain=NonNegativeReals)
        M.LoanRate = Param(M.CostInvest_rtv, domain=NonNegativeReals, default=get_default_loan_rate)
        M.LoanAnnualize = Param(M.CostInvest_rtv, initialize=ParamLoanAnnualize_rule)

        M.CostVariable_rptv = Set(dimen=4, initialize=CostVariableIndices)
        M.CostVariable = Param(M.CostVariable_rptv)

        M.CostEmission_rpe = Set(within=M.regions * M.time_optimize * M.commodity_emissions)
        M.CostEmission = Param(M.CostEmission_rpe)

        # devnote: no longer used
        # M.ModelProcessLife_rptv = Set(dimen=4, initialize=ModelProcessLifeIndices)
        # M.ModelProcessLife = Param(M.ModelProcessLife_rptv, initialize=ParamModelProcessLife_rule)

        M.ProcessLifeFrac_rptv = Set(dimen=4, initialize=ModelProcessLifeIndices)
        M.ProcessLifeFrac = Param(M.ProcessLifeFrac_rptv, initialize=ParamProcessLifeFraction_rule)

        M.LimitCapacityConstraint_rpt = Set(
            within=M.regionalGlobalIndices * M.time_optimize * M.tech_or_group * M.operator
        )
        M.LimitCapacity = Param(M.LimitCapacityConstraint_rpt)

        M.LimitNewCapacityConstraint_rpt = Set(
            within=M.regionalGlobalIndices * M.time_optimize * M.tech_or_group * M.operator
        )
        M.LimitNewCapacity = Param(M.LimitNewCapacityConstraint_rpt)

        M.LimitResourceConstraint_rt = Set(
            within=M.regionalGlobalIndices * M.tech_or_group * M.operator
        )
        M.LimitResource = Param(M.LimitResourceConstraint_rt)

        M.LimitActivityConstraint_rpt = Set(
            within=M.regionalGlobalIndices * M.time_optimize * M.tech_or_group * M.operator
        )
        M.LimitActivity = Param(M.LimitActivityConstraint_rpt)

        M.LimitSeasonalCapacityFactorConstraint_rpst = Set(
            within=M.regionalGlobalIndices
            * M.time_optimize
            * M.time_season
            * M.tech_all
            * M.operator
        )
        M.LimitSeasonalCapacityFactor = Param(
            M.LimitSeasonalCapacityFactorConstraint_rpst, validate=validate_0to1
        )

        M.LimitAnnualCapacityFactorConstraint_rpto = Set(
            within=M.regionalGlobalIndices
            * M.time_optimize
            * M.tech_all
            * M.commodity_carrier
            * M.operator
        )
        M.LimitAnnualCapacityFactor = Param(
            M.LimitAnnualCapacityFactorConstraint_rpto, validate=validate_0to1
        )

        M.LimitGrowthCapacity = Param(
            M.regionalGlobalIndices, M.tech_or_group, M.operator, domain=Any
        )
        M.LimitDegrowthCapacity = Param(
            M.regionalGlobalIndices, M.tech_or_group, M.operator, domain=Any
        )
        M.LimitGrowthNewCapacity = Param(
            M.regionalGlobalIndices, M.tech_or_group, M.operator, domain=Any
        )
        M.LimitDegrowthNewCapacity = Param(
            M.regionalGlobalIndices, M.tech_or_group, M.operator, domain=Any
        )
        M.LimitGrowthNewCapacityDelta = Param(
            M.regionalGlobalIndices, M.tech_or_group, M.operator, domain=Any
        )
        M.LimitDegrowthNewCapacityDelta = Param(
            M.regionalGlobalIndices, M.tech_or_group, M.operator, domain=Any
        )

        M.LimitEmissionConstraint_rpe = Set(
            within=M.regionalGlobalIndices * M.time_optimize * M.commodity_emissions * M.operator
        )
        M.LimitEmission = Param(M.LimitEmissionConstraint_rpe)
        M.EmissionActivity_reitvo = Set(dimen=6, initialize=EmissionActivityIndices)
        M.EmissionActivity = Param(M.EmissionActivity_reitvo)

        # devnote: deprecated when generalising tech/group columns in Limit tables
        # M.LimitActivityGroupConstraint_rpg = Set(
        #     within=M.regionalGlobalIndices * M.time_optimize * M.tech_group_names * M.operator
        # )
        # M.LimitActivityGroup = Param(M.LimitActivityGroupConstraint_rpg)

        # M.LimitCapacityGroupConstraint_rpg = Set(
        #     within=M.regionalGlobalIndices * M.time_optimize * M.tech_group_names * M.operator
        # )
        # M.LimitCapacityGroup = Param(M.LimitCapacityGroupConstraint_rpg)

        # M.LimitNewCapacityGroupConstraint_rpg = Set(
        #     within=M.regionalGlobalIndices * M.time_optimize * M.tech_group_names * M.operator
        # )
        # M.LimitNewCapacityGroup = Param(M.LimitNewCapacityGroupConstraint_rpg)
        # M.GroupShareIndices = Set(dimen=5, initialize=GroupShareIndices) # doesn't feel worth it

        M.LimitCapacityShareConstraint_rpgg = Set(
            within=M.regionalGlobalIndices
            * M.time_optimize
            * M.tech_or_group
            * M.tech_or_group
            * M.operator
        )
        M.LimitCapacityShare = Param(M.LimitCapacityShareConstraint_rpgg)

        M.LimitActivityShareConstraint_rpgg = Set(
            within=M.regionalGlobalIndices
            * M.time_optimize
            * M.tech_or_group
            * M.tech_or_group
            * M.operator
        )
        M.LimitActivityShare = Param(M.LimitActivityShareConstraint_rpgg)

        M.LimitNewCapacityShareConstraint_rpgg = Set(
            within=M.regionalGlobalIndices
            * M.time_optimize
            * M.tech_or_group
            * M.tech_or_group
            * M.operator
        )
        M.LimitNewCapacityShare = Param(M.LimitNewCapacityShareConstraint_rpgg)

        # devnote: deprecated when generalising tech/group columns in Limit tables
        # M.TwoGroupShareIndices = Set(dimen=5, initialize=TwoGroupShareIndices)

        # M.LimitNewCapacityGroupShareConstraint_rpgg = Set(within=M.TwoGroupShareIndices)
        # M.LimitNewCapacityGroupShare = Param(M.TwoGroupShareIndices)

        # M.LimitActivityGroupShareConstraint_rpgg = Set(within=M.TwoGroupShareIndices)
        # M.LimitActivityGroupShare = Param(M.TwoGroupShareIndices)

        # This set works for all storage-related constraints
        M.StorageConstraints_rpsdtv = Set(dimen=6, initialize=StorageConstraintIndices)
        M.SeasonalStorageConstraints_rpsdtv = Set(
            dimen=6, initialize=SeasonalStorageConstraintIndices
        )
        M.LimitStorageFractionConstraint_rpsdtv = Set(
            within=(M.StorageConstraints_rpsdtv | M.SeasonalStorageConstraints_rpsdtv) * M.operator
        )
        M.LimitStorageFraction = Param(
            M.LimitStorageFractionConstraint_rpsdtv, validate=validate_0to1
        )

        # Storage duration is expressed in hours
        M.StorageDuration = Param(M.regions, M.tech_storage, default=4)

        M.LinkedTechs = Param(M.regionalIndices, M.tech_all, M.commodity_emissions, within=Any)

        # Define parameters associated with electric sector operation
        M.ReserveMarginMethod = Set()  # How contributions to the reserve margin are calculated
        M.CapacityCredit = Param(
            M.regionalIndices,
            M.time_optimize,
            M.tech_reserve,
            M.vintage_all,
            default=0,
            validate=validate_0to1,
        )
        M.ReserveCapacityDerate = Param(
            M.regionalIndices,
            M.time_optimize,
            M.time_season,
            M.tech_reserve,
            M.vintage_all,
            default=1,
            validate=validate_0to1,
        )
        M.PlanningReserveMargin = Param(M.regions)

        M.EmissionEmbodied = Param(
            M.regions, M.commodity_emissions, M.tech_with_capacity, M.vintage_optimize
        )
        M.EmissionEndOfLife = Param(
            M.regions, M.commodity_emissions, M.tech_with_capacity, M.vintage_all
        )

        M.MyopicDiscountingYear = Param(default=0)

        ################################################
        #                 Model Variables              #
        #               (assigned by solver)           #
        ################################################

        # ---------------------------------------------------------------
        # Dev Note:
        # Decision variables are optimized in order to minimize cost.
        # Base decision variables represent the lowest-level variables
        # in the model. Derived decision variables are calculated for
        # convenience, where 1 or more indices in the base variables are
        # summed over.
        # ---------------------------------------------------------------

        M.progress_marker_3 = BuildAction(['Starting to build Variables'], rule=progress_check)

        # Define base decision variables
        M.FlowVar_rpsditvo = Set(dimen=8, initialize=FlowVariableIndices)
        M.V_FlowOut = Var(M.FlowVar_rpsditvo, domain=NonNegativeReals)

        M.FlowVarAnnual_rpitvo = Set(dimen=6, initialize=FlowVariableAnnualIndices)
        M.V_FlowOutAnnual = Var(M.FlowVarAnnual_rpitvo, domain=NonNegativeReals)

        M.FlexVar_rpsditvo = Set(dimen=8, initialize=FlexVariablelIndices)
        M.V_Flex = Var(M.FlexVar_rpsditvo, domain=NonNegativeReals)

        M.FlexVarAnnual_rpitvo = Set(dimen=6, initialize=FlexVariableAnnualIndices)
        M.V_FlexAnnual = Var(M.FlexVarAnnual_rpitvo, domain=NonNegativeReals)

        M.CurtailmentVar_rpsditvo = Set(dimen=8, initialize=CurtailmentVariableIndices)
        M.V_Curtailment = Var(M.CurtailmentVar_rpsditvo, domain=NonNegativeReals, initialize=0)

        M.FlowInStorage_rpsditvo = Set(dimen=8, initialize=FlowInStorageVariableIndices)
        M.V_FlowIn = Var(M.FlowInStorage_rpsditvo, domain=NonNegativeReals)

        M.StorageLevel_rpsdtv = Set(dimen=6, initialize=StorageLevelVariableIndices)
        M.V_StorageLevel = Var(M.StorageLevel_rpsdtv, domain=NonNegativeReals)

        M.SeasonalStorageLevel_rpstv = Set(dimen=5, initialize=SeasonalStorageLevelVariableIndices)
        M.V_SeasonalStorageLevel = Var(M.SeasonalStorageLevel_rpstv, domain=NonNegativeReals)

        # Derived decision variables
        M.CapacityVar_rptv = Set(dimen=4, initialize=CostFixedIndices)
        M.V_Capacity = Var(M.CapacityVar_rptv, domain=NonNegativeReals)

        M.NewCapacityVar_rtv = Set(dimen=3, initialize=CapacityVariableIndices)
        M.V_NewCapacity = Var(M.NewCapacityVar_rtv, domain=NonNegativeReals, initialize=0)

        M.RetiredCapacityVar_rptv = Set(dimen=4, initialize=RetiredCapacityVariableIndices)
        M.V_RetiredCapacity = Var(M.RetiredCapacityVar_rptv, domain=NonNegativeReals, initialize=0)

        M.AnnualRetirementVar_rptv = Set(dimen=4, initialize=AnnualRetirementVariableIndices)
        M.V_AnnualRetirement = Var(
            M.AnnualRetirementVar_rptv, domain=NonNegativeReals, initialize=0
        )

        M.CapacityAvailableVar_rpt = Set(dimen=3, initialize=CapacityAvailableVariableIndices)
        M.V_CapacityAvailableByPeriodAndTech = Var(
            M.CapacityAvailableVar_rpt, domain=NonNegativeReals, initialize=0
        )

        ################################################
        #              Objective Function              #
        #             (minimize total cost)            #
        ################################################

        M.TotalCost = Objective(rule=TotalCost_rule, sense=minimize)

        ################################################
        #                   Constraints                #
        #                                              #
        ################################################

        # ---------------------------------------------------------------
        # Dev Note:
        # Constraints are specified to ensure proper system behavior,
        # and also to calculate some derived quantities. Note that descriptions
        # of these constraints are provided in the associated comment blocks
        # in temoa_rules.py, where the constraints are defined.
        # ---------------------------------------------------------------
        M.progress_marker_4 = BuildAction(['Starting to build Constraints'], rule=progress_check)

        # Declare constraints to calculate derived decision variables
        M.CapacityConstraint = Constraint(M.CapacityConstraint_rpsdtv, rule=Capacity_Constraint)

        M.CapacityAnnualConstraint_rptv = Set(dimen=4, initialize=CapacityAnnualConstraintIndices)
        M.CapacityAnnualConstraint = Constraint(
            M.CapacityAnnualConstraint_rptv, rule=CapacityAnnual_Constraint
        )

        M.CapacityAvailableByPeriodAndTechConstraint = Constraint(
            M.CapacityAvailableVar_rpt, rule=CapacityAvailableByPeriodAndTech_Constraint
        )

        # devnote: I think this constraint is redundant
        # M.RetiredCapacityConstraint = Constraint(
        #     M.RetiredCapacityVar_rptv, rule=RetiredCapacity_Constraint
        # )
        M.progress_marker_4a = BuildAction(
            ['Starting AnnualRetirementConstraint'], rule=progress_check
        )
        M.AnnualRetirementConstraint = Constraint(
            M.AnnualRetirementVar_rptv, rule=AnnualRetirement_Constraint
        )
        M.progress_marker_4b = BuildAction(
            ['Starting AdjustedCapacityConstraint'], rule=progress_check
        )
        M.AdjustedCapacityConstraint = Constraint(
            M.CostFixed_rptv, rule=AdjustedCapacity_Constraint
        )
        M.progress_marker_5 = BuildAction(['Finished Capacity Constraints'], rule=progress_check)

        # Declare core model constraints that ensure proper system functioning
        # In driving order, starting with the need to meet end-use demands

        M.DemandConstraint = Constraint(M.DemandConstraint_rpc, rule=Demand_Constraint)

        # devnote: testing a workaround
        M.DemandActivityConstraint_rpsdtv_dem = Set(
            dimen=7, initialize=DemandActivityConstraintIndices
        )
        M.DemandActivityConstraint = Constraint(
            M.DemandActivityConstraint_rpsdtv_dem, rule=DemandActivity_Constraint
        )

        M.CommodityBalanceConstraint_rpsdc = Set(
            dimen=5, initialize=CommodityBalanceConstraintIndices
        )
        M.CommodityBalanceConstraint = Constraint(
            M.CommodityBalanceConstraint_rpsdc, rule=CommodityBalance_Constraint
        )

        M.AnnualCommodityBalanceConstraint_rpc = Set(
            dimen=3, initialize=AnnualCommodityBalanceConstraintIndices
        )
        M.AnnualCommodityBalanceConstraint = Constraint(
            M.AnnualCommodityBalanceConstraint_rpc, rule=AnnualCommodityBalance_Constraint
        )

        # M.ResourceExtractionConstraint = Constraint(
        #     M.ResourceConstraint_rpr, rule=ResourceExtraction_Constraint
        # )

        M.BaseloadDiurnalConstraint_rpsdtv = Set(
            dimen=6, initialize=BaseloadDiurnalConstraintIndices
        )
        M.BaseloadDiurnalConstraint = Constraint(
            M.BaseloadDiurnalConstraint_rpsdtv, rule=BaseloadDiurnal_Constraint
        )

        M.RegionalExchangeCapacityConstraint_rrptv = Set(
            dimen=5, initialize=RegionalExchangeCapacityConstraintIndices
        )
        M.RegionalExchangeCapacityConstraint = Constraint(
            M.RegionalExchangeCapacityConstraint_rrptv, rule=RegionalExchangeCapacity_Constraint
        )

        M.progress_marker_6 = BuildAction(['Starting Storage Constraints'], rule=progress_check)

        M.StorageEnergyConstraint = Constraint(
            M.StorageConstraints_rpsdtv, rule=StorageEnergy_Constraint
        )

        M.StorageEnergyUpperBoundConstraint = Constraint(
            M.StorageConstraints_rpsdtv, rule=StorageEnergyUpperBound_Constraint
        )

        M.SeasonalStorageEnergyConstraint = Constraint(
            M.SeasonalStorageLevel_rpstv, rule=SeasonalStorageEnergy_Constraint
        )

        M.SeasonalStorageEnergyUpperBoundConstraint = Constraint(
            M.SeasonalStorageConstraints_rpsdtv, rule=SeasonalStorageEnergyUpperBound_Constraint
        )

        M.StorageChargeRateConstraint = Constraint(
            M.StorageConstraints_rpsdtv, rule=StorageChargeRate_Constraint
        )

        M.StorageDischargeRateConstraint = Constraint(
            M.StorageConstraints_rpsdtv, rule=StorageDischargeRate_Constraint
        )

        M.StorageThroughputConstraint = Constraint(
            M.StorageConstraints_rpsdtv, rule=StorageThroughput_Constraint
        )

        M.LimitStorageFractionConstraint = Constraint(
            M.LimitStorageFractionConstraint_rpsdtv, rule=LimitStorageFraction_Constraint
        )

        M.RampUpDayConstraint_rpsdtv = Set(dimen=6, initialize=RampUpDayConstraintIndices)
        M.RampUpDayConstraint = Constraint(M.RampUpDayConstraint_rpsdtv, rule=RampUpDay_Constraint)
        M.RampDownDayConstraint_rpsdtv = Set(dimen=6, initialize=RampDownDayConstraintIndices)
        M.RampDownDayConstraint = Constraint(
            M.RampDownDayConstraint_rpsdtv, rule=RampDownDay_Constraint
        )

        M.RampUpSeasonConstraint_rpsstv = Set(dimen=6, initialize=RampUpSeasonConstraintIndices)
        M.RampUpSeasonConstraint = Constraint(
            M.RampUpSeasonConstraint_rpsstv, rule=RampUpSeason_Constraint
        )
        M.RampDownSeasonConstraint_rpsstv = Set(dimen=6, initialize=RampDownSeasonConstraintIndices)
        M.RampDownSeasonConstraint = Constraint(
            M.RampDownSeasonConstraint_rpsstv, rule=RampDownSeason_Constraint
        )

        M.ReserveMargin_rpsd = Set(dimen=4, initialize=ReserveMarginIndices)
        M.validate_ReserveMargin = BuildAction(rule=validate_ReserveMargin)
        M.ReserveMarginConstraint = Constraint(M.ReserveMargin_rpsd, rule=ReserveMargin_Constraint)

        M.LimitEmissionConstraint = Constraint(
            M.LimitEmissionConstraint_rpe, rule=LimitEmission_Constraint
        )
        M.progress_marker_7 = BuildAction(
            ['Starting LimitGrowth and Activity Constraints'], rule=progress_check
        )

        M.LimitGrowthCapacityConstraint_rpt = Set(dimen=4, initialize=LimitGrowthCapacityIndices)
        M.LimitGrowthCapacityConstraint = Constraint(
            M.LimitGrowthCapacityConstraint_rpt, rule=LimitGrowthCapacityConstraint_rule
        )
        M.LimitDegrowthCapacityConstraint_rpt = Set(
            dimen=4, initialize=LimitDegrowthCapacityIndices
        )
        M.LimitDegrowthCapacityConstraint = Constraint(
            M.LimitDegrowthCapacityConstraint_rpt, rule=LimitDegrowthCapacityConstraint_rule
        )

        M.LimitGrowthNewCapacityConstraint_rpt = Set(
            dimen=4, initialize=LimitGrowthNewCapacityIndices
        )
        M.LimitGrowthNewCapacityConstraint = Constraint(
            M.LimitGrowthNewCapacityConstraint_rpt, rule=LimitGrowthNewCapacityConstraint_rule
        )
        M.LimitDegrowthNewCapacityConstraint_rpt = Set(
            dimen=4, initialize=LimitDegrowthNewCapacityIndices
        )
        M.LimitDegrowthNewCapacityConstraint = Constraint(
            M.LimitDegrowthNewCapacityConstraint_rpt, rule=LimitDegrowthNewCapacityConstraint_rule
        )

        M.LimitGrowthNewCapacityDeltaConstraint_rpt = Set(
            dimen=4, initialize=LimitGrowthNewCapacityDeltaIndices
        )
        M.LimitGrowthNewCapacityDeltaConstraint = Constraint(
            M.LimitGrowthNewCapacityDeltaConstraint_rpt,
            rule=LimitGrowthNewCapacityDeltaConstraint_rule,
        )
        M.LimitDegrowthNewCapacityDeltaConstraint_rpt = Set(
            dimen=4, initialize=LimitDegrowthNewCapacityDeltaIndices
        )
        M.LimitDegrowthNewCapacityDeltaConstraint = Constraint(
            M.LimitDegrowthNewCapacityDeltaConstraint_rpt,
            rule=LimitDegrowthNewCapacityDeltaConstraint_rule,
        )

        M.LimitActivityConstraint = Constraint(
            M.LimitActivityConstraint_rpt, rule=LimitActivity_Constraint
        )

        M.LimitSeasonalCapacityFactorConstraint = Constraint(
            M.LimitSeasonalCapacityFactorConstraint_rpst,
            rule=LimitSeasonalCapacityFactor_Constraint,
        )

        # devnote: deprecated when generalising tech/group columns in Limit tables
        # M.LimitActivityGroupConstraint = Constraint(
        #     M.LimitActivityGroupConstraint_rpg, rule=LimitActivityGroup_Constraint
        # )

        M.LimitCapacityConstraint = Constraint(
            M.LimitCapacityConstraint_rpt, rule=LimitCapacity_Constraint
        )

        M.LimitNewCapacityConstraint = Constraint(
            M.LimitNewCapacityConstraint_rpt, rule=LimitNewCapacity_Constraint
        )

        # devnote: deprecated when generalising tech/group columns in Limit tables
        # M.LimitCapacityGroupConstraint = Constraint(
        #     M.LimitCapacityGroupConstraint_rpg, rule=LimitCapacityGroup_Constraint
        # )

        # M.LimitNewCapacityGroupConstraint = Constraint(
        #     M.LimitNewCapacityGroupConstraint_rpg, rule=LimitNewCapacityGroup_Constraint
        # )

        M.LimitCapacityShareConstraint = Constraint(
            M.LimitCapacityShareConstraint_rpgg, rule=LimitCapacityShare_Constraint
        )

        M.LimitActivityShareConstraint = Constraint(
            M.LimitActivityShareConstraint_rpgg, rule=LimitActivityShare_Constraint
        )

        M.LimitNewCapacityShareConstraint = Constraint(
            M.LimitNewCapacityShareConstraint_rpgg, rule=LimitNewCapacityShare_Constraint
        )

        # devnote: deprecated when generalising tech/group columns in Limit tables
        # M.LimitNewCapacityGroupShareConstraint = Constraint(
        #     M.LimitNewCapacityGroupShareConstraint_rpgg,
        #     rule=LimitNewCapacityGroupShare_Constraint
        # )

        # M.LimitActivityGroupShareConstraint = Constraint(
        #     M.LimitActivityGroupShareConstraint_rpgg, rule=LimitActivityGroupShare_Constraint
        # )

        M.progress_marker_8 = BuildAction(
            ['Starting Limit Capacity and Tech Split Constraints'], rule=progress_check
        )

        M.LimitResourceConstraint = Constraint(
            M.LimitResourceConstraint_rt, rule=LimitResource_Constraint
        )

        M.LimitAnnualCapacityFactorConstraint = Constraint(
            M.LimitAnnualCapacityFactorConstraint_rpto, rule=LimitAnnualCapacityFactor_Constraint
        )

        ## Tech input splits
        M.LimitTechInputSplitConstraint_rpsditv = Set(
            dimen=8, initialize=LimitTechInputSplitConstraintIndices
        )
        M.LimitTechInputSplitConstraint = Constraint(
            M.LimitTechInputSplitConstraint_rpsditv, rule=LimitTechInputSplit_Constraint
        )

        M.LimitTechInputSplitAnnualConstraint_rpitv = Set(
            dimen=6, initialize=LimitTechInputSplitAnnualConstraintIndices
        )
        M.LimitTechInputSplitAnnualConstraint = Constraint(
            M.LimitTechInputSplitAnnualConstraint_rpitv, rule=LimitTechInputSplitAnnual_Constraint
        )

        M.LimitTechInputSplitAverageConstraint_rpitv = Set(
            dimen=6, initialize=LimitTechInputSplitAverageConstraintIndices
        )
        M.LimitTechInputSplitAverageConstraint = Constraint(
            M.LimitTechInputSplitAverageConstraint_rpitv, rule=LimitTechInputSplitAverage_Constraint
        )

        ## Tech output splits
        M.LimitTechOutputSplitConstraint_rpsdtvo = Set(
            dimen=8, initialize=LimitTechOutputSplitConstraintIndices
        )
        M.LimitTechOutputSplitConstraint = Constraint(
            M.LimitTechOutputSplitConstraint_rpsdtvo, rule=LimitTechOutputSplit_Constraint
        )

        M.LimitTechOutputSplitAnnualConstraint_rptvo = Set(
            dimen=6, initialize=LimitTechOutputSplitAnnualConstraintIndices
        )
        M.LimitTechOutputSplitAnnualConstraint = Constraint(
            M.LimitTechOutputSplitAnnualConstraint_rptvo, rule=LimitTechOutputSplitAnnual_Constraint
        )

        M.LimitTechOutputSplitAverageConstraint_rptvo = Set(
            dimen=6, initialize=LimitTechOutputSplitAverageConstraintIndices
        )
        M.LimitTechOutputSplitAverageConstraint = Constraint(
            M.LimitTechOutputSplitAverageConstraint_rptvo,
            rule=LimitTechOutputSplitAverage_Constraint,
        )

        M.RenewablePortfolioStandardConstraint = Constraint(
            M.RenewablePortfolioStandardConstraint_rpg, rule=RenewablePortfolioStandard_Constraint
        )

        M.LinkedEmissionsTechConstraint_rpsdtve = Set(
            dimen=7, initialize=LinkedTechConstraintIndices
        )
        # the validation requires that the set above be built first:
        M.validate_LinkedTech_lifetimes = BuildCheck(rule=validate_linked_tech)

        M.LinkedEmissionsTechConstraint = Constraint(
            M.LinkedEmissionsTechConstraint_rpsdtve, rule=LinkedEmissionsTech_Constraint
        )

        M.progress_marker_9 = BuildAction(['Finished Constraints'], rule=progress_check)


def progress_check(M, checkpoint: str):
    """A quick widget which is called by BuildAction in order to log creation progress"""
    logger.debug('Model build progress: %s', checkpoint)
