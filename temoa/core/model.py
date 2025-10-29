#!/usr/bin/env python

"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

SPDX-License-Identifier: MIT

"""

import logging
from typing import TYPE_CHECKING

from pyomo.core import BuildCheck, Set, Var
from pyomo.environ import (
    AbstractModel,
    BuildAction,
    Constraint,
    Integers,
    NonNegativeReals,
    Objective,
    Param,
    minimize,
)

from temoa.types.core_types import Technology

if TYPE_CHECKING:
    from pyomo.environ import AbstractModel as PyomoAbstractModel

else:
    PyomoAbstractModel = AbstractModel  # type: ignore[misc,assignment]

from temoa import types as t
from temoa.components import (
    capacity,
    commodities,
    costs,
    emissions,
    flows,
    geography,
    limits,
    operations,
    reserves,
    storage,
    technology,
    time,
)
from temoa.model_checking.validators import (
    no_slash_or_pipe,
    region_check,
    region_group_check,
    validate_0to1,
    validate_efficiency,
    validate_linked_tech,
    validate_reserve_margin,
    validate_tech_sets,
)

logger = logging.getLogger(__name__)


def create_sparse_dicts(model: 'TemoaModel') -> None:
    """
    Creates and populates all sparse dictionaries and sets required for the model
    by calling component-specific precomputation functions.
    """

    # Call the decomposed functions in logical order
    # 1. Populate core relationships from Efficiency table
    technology.populate_core_dictionaries(model)

    # 2. Classify technologies and commodities
    commodities.create_technology_and_commodity_sets(model)

    # 3. Create sets for specific components
    operations.create_operational_vintage_sets(model)  # For operations, storage, ramping
    limits.create_limit_vintage_sets(model)  # For limits
    geography.create_geography_sets(model)  # For geography/exchange
    capacity.create_capacity_and_retirement_sets(model)  # For capacity

    # 4. Create final aggregated sets for constraints
    flows.create_commodity_balance_and_flow_sets(model)  # For flows and commodities

    # Final check for unused technologies
    unused_techs = model.tech_all - model.used_techs
    if unused_techs:
        for tech in sorted(unused_techs):
            logger.warning(
                f"Notice: '{tech}' is specified as a technology but is not "
                'utilized in the Efficiency parameter.'
            )

    logger.debug('Completed creation of SparseDicts')


class TemoaModel(PyomoAbstractModel):
    """
    An instance of the abstract Temoa model
    """

    # this is used in several places outside this class, and this provides no-build access to it
    default_lifetime_tech = 40

    def __init__(self, *args: object, **kwargs: object) -> None:
        PyomoAbstractModel.__init__(self, *args, **kwargs)

        ################################################
        #       Internally used Data Containers        #
        #       (not formal model elements)            #
        ################################################

        self.processInputs: t.ProcessInputsDict = {}
        self.processOutputs: t.ProcessOutputsDict = {}
        self.processLoans: t.ProcessLoansDict = {}
        self.activeFlow_rpsditvo: t.ActiveFlowSet = set()
        """a flow index for techs NOT in tech_annual"""

        self.activeFlow_rpitvo: t.ActiveFlowAnnualSet = set()
        """a flow index for techs in tech_annual only"""

        self.activeFlex_rpsditvo: t.ActiveFlexSet = set()
        self.activeFlex_rpitvo: t.ActiveFlexAnnualSet = set()
        self.activeFlowInStorage_rpsditvo: t.ActiveFlowInStorageSet = set()
        self.activeCurtailment_rpsditvo: t.ActiveCurtailmentSet = set()
        self.activeActivity_rptv: t.ActiveActivitySet = set()
        self.storageLevelIndices_rpsdtv: t.StorageLevelIndicesSet = set()
        self.seasonalStorageLevelIndices_rpstv: t.SeasonalStorageLevelIndicesSet = set()
        """currently available (within lifespan) (r, p, t, v) tuples (from M.processVintages)"""

        self.activeRegionsForTech: t.ActiveRegionsForTechDict = {}
        """currently available regions by period and tech {(p, t) : r}"""

        self.newCapacity_rtv: t.NewCapacitySet = set()
        self.activeCapacityAvailable_rpt: t.ActiveCapacityAvailableSet = set()
        self.activeCapacityAvailable_rptv: t.ActiveCapacityAvailableVintageSet = set()
        self.groupRegionActiveFlow_rpt: t.GroupRegionActiveFlowSet = (
            set()  # Set of valid group-region, period, tech indices
        )
        self.commodityBalance_rpc: t.CommodityBalancedSet = (
            set()
        )  # Set of valid region-period-commodity indices to balance
        self.commodityDStreamProcess: t.CommodityStreamProcessDict = {}  # The downstream process of a commodity during a period
        self.commodityUStreamProcess: t.CommodityStreamProcessDict = {}  # The upstream process of a commodity during a period
        self.capacityConsumptionTechs: t.CapacityConsumptionTechsDict = {}  # New capacity consuming a commodity during a period [r,p,c] -> t
        self.retirementProductionProcesses: t.RetirementProductionProcessesDict = {}  # Retired capacity producing a commodity during a period [r,p,c] -> t,v
        self.processInputsByOutput: t.ProcessInputsByOutputDict = {}
        self.processOutputsByInput: t.ProcessOutputsByInputDict = {}
        self.processTechs: t.ProcessTechsDict = {}
        self.processReservePeriods: t.ProcessReservePeriodsDict = {}
        self.processPeriods: t.ProcessPeriodsDict = {}  # {(r, t, v): set(p)}
        self.retirementPeriods: t.RetirementPeriodsDict = {}  # {(r, t, v): set(p)} periods in which a process can economically or naturally retire
        self.processVintages: t.ProcessVintagesDict = {}
        self.survivalCurvePeriods: t.SurvivalCurvePeriodsDict = {}  # {(r, t, v): set(p)} periods for which the process has a defined survival fraction
        """current available (within lifespan) vintages {(r, p, t) : set(v)}"""

        self.baseloadVintages: t.BaseloadVintagesDict = {}
        self.curtailmentVintages: t.CurtailmentVintagesDict = {}
        self.storageVintages: t.StorageVintagesDict = {}
        self.rampUpVintages: t.RampUpVintagesDict = {}
        self.rampDownVintages: t.RampDownVintagesDict = {}
        self.inputSplitVintages: t.InputSplitVintagesDict = {}
        self.inputSplitAnnualVintages: t.InputSplitAnnualVintagesDict = {}
        self.outputSplitVintages: t.OutputSplitVintagesDict = {}
        self.outputSplitAnnualVintages: t.OutputSplitAnnualVintagesDict = {}
        # M.processByPeriodAndOutput = {} # not currently used
        self.exportRegions: t.ExportRegionsDict = {}
        self.importRegions: t.ImportRegionsDict = {}

        # These establish time sequencing
        self.time_next: t.TimeNextDict = {}  # {(p, s, d): (s_next, d_next)} sequence of following time slices
        self.time_next_sequential: t.TimeNextSequentialDict = {}  # {(p, s_seq): (s_seq_next)} next virtual storage season
        self.sequential_to_season: t.SequentialToSeasonDict = {}  # {(p, s_seq): (s)} season matching this virtual storage season

        ################################################
        #             Switching Sets                   #
        #  (to avoid slow searches in initialisation)  #
        ################################################

        self.isEfficiencyVariable: t.EfficiencyVariableDict = {}  # {(r, p, i, t, v, o): bool} which efficiencies have variable indexing
        self.isCapacityFactorProcess: t.CapacityFactorProcessDict = {}  # {(r, p, t, v): bool} which capacity factors have have period-vintage indexing
        self.isSeasonalStorage: t.SeasonalStorageDict = {}  # {t: bool} whether a storage tech is seasonal storage
        self.isSurvivalCurveProcess: t.SurvivalCurveProcessDict = {}  # {(r, t, v): bool} whether a process uses survival curves.

        ################################################
        #                 Model Sets                   #
        #    (used for indexing model elements)        #
        ################################################

        self.progress_marker_1 = BuildAction(['Starting to build Sets'], rule=progress_check)

        self.operator = Set()

        # Define time periods
        self.time_exist = Set(ordered=True)
        self.time_future = Set(ordered=True)
        self.time_optimize = Set(
            ordered=True, initialize=time.init_set_time_optimize, within=self.time_future
        )
        # Define time period vintages to track capacity installation
        self.vintage_exist = Set(ordered=True, initialize=time.init_set_vintage_exist)
        self.vintage_optimize = Set(ordered=True, initialize=time.init_set_vintage_optimize)
        self.vintage_all = Set(initialize=self.time_exist | self.time_optimize)
        # Perform some basic validation on the specified time periods.
        self.validate_time = BuildAction(rule=time.validate_time)

        # Define the model time slices
        self.time_season = Set(ordered=True, validate=no_slash_or_pipe)
        self.time_season_sequential = Set(ordered=True, validate=no_slash_or_pipe)
        self.TimeSeason = Set(self.time_optimize, within=self.time_season, ordered=True)
        self.time_of_day = Set(ordered=True, validate=no_slash_or_pipe)

        # This is just to get the TimeStorageSeason table sequentially.
        # There must be a better way but this works for now
        self.ordered_season_sequential = Set(
            dimen=3,
            within=self.time_optimize * self.time_season_sequential * self.time_season,
            ordered=True,
        )

        # Define regions
        self.regions = Set(validate=region_check)
        # RegionalIndices is the set of all the possible combinations of interregional exchanges
        # plus original region indices. If tech_exchange is empty, RegionalIndices =regions.
        self.regionalIndices = Set(initialize=geography.create_regional_indices)
        self.regionalGlobalIndices = Set(validate=region_group_check)

        # Define technology-related sets
        # M.tech_resource = Set() # not actually used by
        self.tech_production = Set()
        self.tech_all = Set(
            initialize=self.tech_production, validate=no_slash_or_pipe
        )  # was M.tech_resource | M.tech_production
        self.tech_baseload = Set(within=self.tech_all)
        self.tech_annual = Set(within=self.tech_all)
        self.tech_demand = Set(within=self.tech_all)
        # annual storage not supported in Storage constraint or TableWriter, so exclude from domain
        self.tech_storage = Set(within=self.tech_all)
        self.tech_reserve = Set(within=self.tech_all)
        self.tech_upramping = Set(within=self.tech_all)
        self.tech_downramping = Set(within=self.tech_all)
        self.tech_curtailment = Set(within=self.tech_all)
        self.tech_flex = Set(within=self.tech_all)
        # ensure there is no overlap flex <=> curtailable technologies
        self.tech_exchange = Set(within=self.tech_all)

        # Define groups for technologies
        self.tech_group_names = Set()
        self.tech_group_members = Set(self.tech_group_names, within=self.tech_all)
        self.tech_or_group = Set(initialize=self.tech_group_names | self.tech_all)

        self.tech_seasonal_storage = Set(within=self.tech_storage)
        """storage technologies using the interseasonal storage feature"""

        self.tech_uncap = Set(within=self.tech_all - self.tech_reserve)
        """techs with unlimited capacity, ALWAYS available within lifespan"""

        self.tech_exist = Set()
        """techs with existing capacity, want to keep these for accounting reasons"""

        self.used_techs: set[Technology] = set()
        """ track techs used in Efficiency table used in create_sparse_dicts """

        # the below is a convenience for domain checking in params below that should not accept
        # uncap techs...
        self.tech_with_capacity = Set(initialize=self.tech_all - self.tech_uncap)
        """techs eligible for capacitization"""
        # Define techs for which economic retirement is an option
        # Note:  Storage techs cannot (currently) be retired due to linkage to initialization
        #        process, which is currently incapable of reducing initializations on retirements.
        # Note2: I think this has been fixed but I can't tell what the problem was. Suspect
        #        it was the old StorageInit constraint
        self.tech_retirement = Set(within=self.tech_with_capacity)  # - M.tech_storage)

        self.validate_techs = BuildAction(rule=validate_tech_sets)

        # Define commodity-related sets
        self.commodity_demand = Set()
        self.commodity_emissions = Set()
        self.commodity_physical = Set()
        self.commodity_waste = Set()
        self.commodity_flex = Set(within=self.commodity_physical)
        self.commodity_source = Set(within=self.commodity_physical)
        self.commodity_annual = Set(within=self.commodity_physical)
        self.commodity_carrier = Set(
            initialize=self.commodity_physical | self.commodity_demand | self.commodity_waste
        )
        self.commodity_all = Set(
            initialize=self.commodity_carrier | self.commodity_emissions,
            validate=no_slash_or_pipe,
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
        self.progress_marker_2 = BuildAction(['Starting to build Params'], rule=progress_check)

        self.GlobalDiscountRate = Param(default=0.05)

        # Define time-related parameters
        self.PeriodLength = Param(self.time_optimize, initialize=time.param_period_length)
        self.SegFrac = Param(self.time_optimize, self.time_season, self.time_of_day)
        self.validate_SegFrac = BuildAction(rule=time.validate_segment_fraction)
        self.TimeSequencing = Set()  # How do states carry between time segments?
        self.TimeNext = Set(
            ordered=True
        )  # This is just to get data from the table. Hidden feature and usually not used
        self.validate_TimeNext = BuildAction(rule=time.validate_time_next)

        # Define demand- and resource-related parameters
        # Dev Note:  There does not appear to be a DB table supporting DemandDefaultDistro.
        #            This does not cause any problems, so let it be for now.
        #            Doesn't seem to be much point in the table. Just clones SegFrac
        # M.DemandDefaultDistribution = Param(
        #     M.time_optimize, M.time_season, M.time_of_day, mutable=True
        # )
        self.DemandSpecificDistribution = Param(
            self.regions,
            self.time_optimize,
            self.time_season,
            self.time_of_day,
            self.commodity_demand,
            mutable=True,
            default=0,
        )

        self.DemandConstraint_rpc = Set(
            within=self.regions * self.time_optimize * self.commodity_demand
        )
        self.Demand = Param(self.DemandConstraint_rpc)

        # Dev Note:  This parameter is currently NOT implemented.  Preserved for later refactoring
        # LimitResource IS implemented but sums cumulatively for a technology rather than
        # resource commodity
        # M.ResourceConstraint_rpr = Set(within=M.regions * M.time_optimize * M.commodity_physical)
        # M.ResourceBound = Param(M.ResourceConstraint_rpr)

        # Define technology performance parameters
        self.CapacityToActivity = Param(self.regionalIndices, self.tech_all, default=1)

        self.ExistingCapacity = Param(self.regionalIndices, self.tech_exist, self.vintage_exist)

        # Dev Note:  The below is temporarily useful for passing down to validator to find
        # set violations
        #            Uncomment this assignment, and comment out the orig below it...
        # M.Efficiency = Param(
        #     Any, Any, Any, Any, Any,
        #     within=NonNegativeReals, validate=validate_Efficiency
        # )

        # devnote: need these here or CheckEfficiencyIndices may flag these commodities as unused
        self.ConstructionInput = Param(
            self.regions,
            self.commodity_physical,
            self.tech_with_capacity,
            self.vintage_optimize,
        )
        self.EndOfLifeOutput = Param(
            self.regions, self.tech_with_capacity, self.vintage_all, self.commodity_carrier
        )

        self.Efficiency = Param(
            self.regionalIndices,
            self.commodity_physical,
            self.tech_all,
            self.vintage_all,
            self.commodity_carrier,
            within=NonNegativeReals,
            validate=validate_efficiency,
        )
        self.validate_UsedEfficiencyIndices = BuildAction(rule=technology.check_efficiency_indices)

        self.EfficiencyVariable = Param(
            self.regionalIndices,
            self.time_optimize,
            self.time_season,
            self.time_of_day,
            self.commodity_physical,
            self.tech_all,
            self.vintage_all,
            self.commodity_carrier,
            within=NonNegativeReals,
            default=1,
        )

        self.LifetimeTech = Param(
            self.regionalIndices, self.tech_all, default=TemoaModel.default_lifetime_tech
        )

        self.LifetimeProcess_rtv = Set(dimen=3, initialize=technology.lifetime_process_indices)
        self.LifetimeProcess = Param(
            self.LifetimeProcess_rtv, default=technology.get_default_process_lifetime
        )

        self.LifetimeSurvivalCurve = Param(
            self.regionalIndices,
            Integers,
            self.tech_all,
            self.vintage_all,
            default=technology.get_default_survival,
            validate=validate_0to1,
            mutable=True,
        )
        self.Create_SurvivalCurve = BuildAction(rule=technology.create_survival_curve)

        self.LoanLifetimeProcess_rtv = Set(dimen=3, initialize=costs.lifetime_loan_process_indices)

        # Dev Note:  The LoanLifetimeProcess table *could* be removed.  There is no longer a
        #            supporting table in the database.  It is just a "passthrough" now to the
        #            default LoanLifetimeTech. It is already stitched in to the model,
        #            so will leave it for now.  Table may be revived.

        self.LoanLifetimeProcess = Param(self.LoanLifetimeProcess_rtv, default=costs.get_loan_life)

        self.LimitTechInputSplit = Param(
            self.regions,
            self.time_optimize,
            self.commodity_physical,
            self.tech_all,
            self.operator,
            validate=validate_0to1,
        )
        self.LimitTechInputSplitAnnual = Param(
            self.regions,
            self.time_optimize,
            self.commodity_physical,
            self.tech_all,
            self.operator,
            validate=validate_0to1,
        )

        self.LimitTechOutputSplit = Param(
            self.regions,
            self.time_optimize,
            self.tech_all,
            self.commodity_carrier,
            self.operator,
            validate=validate_0to1,
        )
        self.LimitTechOutputSplitAnnual = Param(
            self.regions,
            self.time_optimize,
            self.tech_all,
            self.commodity_carrier,
            self.operator,
            validate=validate_0to1,
        )

        self.RenewablePortfolioStandardConstraint_rpg = Set(
            within=self.regions * self.time_optimize * self.tech_group_names
        )
        self.RenewablePortfolioStandard = Param(
            self.RenewablePortfolioStandardConstraint_rpg, validate=validate_0to1
        )

        # These need to come before validate_SeasonSequential
        self.RampUpHourly = Param(self.regions, self.tech_upramping, validate=validate_0to1)
        self.RampDownHourly = Param(self.regions, self.tech_downramping, validate=validate_0to1)

        # Set up representation of time
        self.DaysPerPeriod = Param()
        self.SegFracPerSeason = Param(
            self.time_optimize, self.time_season, initialize=time.seg_frac_per_season_rule
        )
        self.TimeSeasonSequential = Param(
            self.time_optimize, self.time_season_sequential, self.time_season, mutable=True
        )
        self.validate_SeasonSequential = BuildAction(rule=time.create_time_season_sequential)
        self.Create_TimeSequence = BuildAction(rule=time.create_time_sequence)

        # The method below creates a series of helper functions that are used to
        # perform the sparse matrix of indexing for the parameters, variables, and
        # equations below.
        self.Create_SparseDicts = BuildAction(rule=create_sparse_dicts)
        self.initialize_Demands = BuildAction(rule=commodities.create_demands)

        self.CapacityFactor_rpsdt = Set(dimen=5, initialize=capacity.capacity_factor_tech_indices)
        self.CapacityFactorTech = Param(
            self.CapacityFactor_rpsdt, default=1, validate=validate_0to1
        )

        # Dev note:  using a default function below alleviates need to make this set.
        # M.CapacityFactor_rsdtv = Set(dimen=5, initialize=CapacityFactorProcessIndices)
        self.CapacityFactorProcess = Param(
            self.regionalIndices,
            self.time_optimize,
            self.time_season,
            self.time_of_day,
            self.tech_with_capacity,
            self.vintage_all,
            # validate=validate_CapacityFactorProcess, # opting for a quicker validation, just 0->1
            validate=validate_0to1,
            default=capacity.get_default_capacity_factor,  # slow but only called if a value is missing
        )

        self.CapacityConstraint_rpsdtv = Set(
            dimen=6, initialize=capacity.capacity_constraint_indices
        )
        self.initialize_CapacityFactors = BuildAction(rule=capacity.check_capacity_factor_process)
        self.initialize_EfficiencyVariable = BuildAction(rule=technology.check_efficiency_variable)

        # Define technology cost parameters
        # dev note:  the CostFixed_rptv isn't truly needed, but it is included in a constraint, so
        #            let it go for now
        self.CostFixed_rptv = Set(dimen=4, initialize=costs.cost_fixed_indices)
        self.CostFixed = Param(self.CostFixed_rptv)

        self.CostInvest_rtv = Set(within=self.regionalIndices * self.tech_all * self.time_optimize)
        self.CostInvest = Param(self.CostInvest_rtv)

        self.DefaultLoanRate = Param(domain=NonNegativeReals)
        self.LoanRate = Param(
            self.CostInvest_rtv, domain=NonNegativeReals, default=costs.get_default_loan_rate
        )
        self.LoanAnnualize = Param(self.CostInvest_rtv, initialize=costs.param_loan_annualize_rule)

        self.CostVariable_rptv = Set(dimen=4, initialize=costs.cost_variable_indices)
        self.CostVariable = Param(self.CostVariable_rptv)

        self.CostEmission_rpe = Set(
            within=self.regions * self.time_optimize * self.commodity_emissions
        )
        self.CostEmission = Param(self.CostEmission_rpe)

        # devnote: no longer used
        # M.ModelProcessLife_rptv = Set(dimen=4, initialize=ModelProcessLifeIndices)
        # M.ModelProcessLife = Param(M.ModelProcessLife_rptv, initialize=ParamModelProcessLife_rule)

        self.ProcessLifeFrac_rptv = Set(dimen=4, initialize=technology.model_process_life_indices)
        self.ProcessLifeFrac = Param(
            self.ProcessLifeFrac_rptv, initialize=technology.param_process_life_fraction_rule
        )

        self.LimitCapacityConstraint_rpt = Set(
            within=self.regionalGlobalIndices
            * self.time_optimize
            * self.tech_or_group
            * self.operator
        )
        self.LimitCapacity = Param(self.LimitCapacityConstraint_rpt)

        self.LimitNewCapacityConstraint_rpt = Set(
            within=self.regionalGlobalIndices
            * self.time_optimize
            * self.tech_or_group
            * self.operator
        )
        self.LimitNewCapacity = Param(self.LimitNewCapacityConstraint_rpt)

        self.LimitResourceConstraint_rt = Set(
            within=self.regionalGlobalIndices * self.tech_or_group * self.operator
        )
        self.LimitResource = Param(self.LimitResourceConstraint_rt)

        self.LimitActivityConstraint_rpt = Set(
            within=self.regionalGlobalIndices
            * self.time_optimize
            * self.tech_or_group
            * self.operator
        )
        self.LimitActivity = Param(self.LimitActivityConstraint_rpt)

        self.LimitSeasonalCapacityFactorConstraint_rpst = Set(
            within=self.regionalGlobalIndices
            * self.time_optimize
            * self.time_season
            * self.tech_all
            * self.operator
        )
        self.LimitSeasonalCapacityFactor = Param(
            self.LimitSeasonalCapacityFactorConstraint_rpst, validate=validate_0to1
        )

        self.LimitAnnualCapacityFactorConstraint_rpto = Set(
            within=self.regionalGlobalIndices
            * self.time_optimize
            * self.tech_all
            * self.commodity_carrier
            * self.operator
        )
        self.LimitAnnualCapacityFactor = Param(
            self.LimitAnnualCapacityFactorConstraint_rpto, validate=validate_0to1
        )

        self.LimitGrowthCapacity = Param(
            self.regionalGlobalIndices, self.tech_or_group, self.operator
        )
        self.LimitDegrowthCapacity = Param(
            self.regionalGlobalIndices, self.tech_or_group, self.operator
        )
        self.LimitGrowthNewCapacity = Param(
            self.regionalGlobalIndices, self.tech_or_group, self.operator
        )
        self.LimitDegrowthNewCapacity = Param(
            self.regionalGlobalIndices, self.tech_or_group, self.operator
        )
        self.LimitGrowthNewCapacityDelta = Param(
            self.regionalGlobalIndices, self.tech_or_group, self.operator
        )
        self.LimitDegrowthNewCapacityDelta = Param(
            self.regionalGlobalIndices, self.tech_or_group, self.operator
        )

        self.LimitEmissionConstraint_rpe = Set(
            within=self.regionalGlobalIndices
            * self.time_optimize
            * self.commodity_emissions
            * self.operator
        )
        self.LimitEmission = Param(self.LimitEmissionConstraint_rpe)
        self.EmissionActivity_reitvo = Set(dimen=6, initialize=emissions.emission_activity_indices)
        self.EmissionActivity = Param(self.EmissionActivity_reitvo)

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

        self.LimitCapacityShareConstraint_rpgg = Set(
            within=self.regionalGlobalIndices
            * self.time_optimize
            * self.tech_or_group
            * self.tech_or_group
            * self.operator
        )
        self.LimitCapacityShare = Param(self.LimitCapacityShareConstraint_rpgg)

        self.LimitActivityShareConstraint_rpgg = Set(
            within=self.regionalGlobalIndices
            * self.time_optimize
            * self.tech_or_group
            * self.tech_or_group
            * self.operator
        )
        self.LimitActivityShare = Param(self.LimitActivityShareConstraint_rpgg)

        self.LimitNewCapacityShareConstraint_rpgg = Set(
            within=self.regionalGlobalIndices
            * self.time_optimize
            * self.tech_or_group
            * self.tech_or_group
            * self.operator
        )
        self.LimitNewCapacityShare = Param(self.LimitNewCapacityShareConstraint_rpgg)

        # devnote: deprecated when generalising tech/group columns in Limit tables
        # M.TwoGroupShareIndices = Set(dimen=5, initialize=TwoGroupShareIndices)

        # M.LimitNewCapacityGroupShareConstraint_rpgg = Set(within=M.TwoGroupShareIndices)
        # M.LimitNewCapacityGroupShare = Param(M.TwoGroupShareIndices)

        # M.LimitActivityGroupShareConstraint_rpgg = Set(within=M.TwoGroupShareIndices)
        # M.LimitActivityGroupShare = Param(M.TwoGroupShareIndices)

        # This set works for all storage-related constraints
        self.StorageConstraints_rpsdtv = Set(dimen=6, initialize=storage.storage_constraint_indices)
        self.SeasonalStorageConstraints_rpsdtv = Set(
            dimen=6, initialize=storage.seasonal_storage_constraint_indices
        )
        self.LimitStorageFractionConstraint_rpsdtv = Set(
            within=(self.StorageConstraints_rpsdtv | self.SeasonalStorageConstraints_rpsdtv)
            * self.operator
        )
        self.LimitStorageFraction = Param(
            self.LimitStorageFractionConstraint_rpsdtv, validate=validate_0to1
        )

        # Storage duration is expressed in hours
        self.StorageDuration = Param(self.regions, self.tech_storage, default=4)

        self.LinkedTechs = Param(self.regionalIndices, self.tech_all, self.commodity_emissions)

        # Define parameters associated with electric sector operation
        self.ReserveMarginMethod = Set()  # How contributions to the reserve margin are calculated
        self.CapacityCredit = Param(
            self.regionalIndices,
            self.time_optimize,
            self.tech_reserve,
            self.vintage_all,
            default=0,
            validate=validate_0to1,
        )
        self.ReserveCapacityDerate = Param(
            self.regionalIndices,
            self.time_optimize,
            self.time_season,
            self.tech_reserve,
            self.vintage_all,
            default=1,
            validate=validate_0to1,
        )
        self.PlanningReserveMargin = Param(self.regions)

        self.EmissionEmbodied = Param(
            self.regions,
            self.commodity_emissions,
            self.tech_with_capacity,
            self.vintage_optimize,
        )
        self.EmissionEndOfLife = Param(
            self.regions, self.commodity_emissions, self.tech_with_capacity, self.vintage_all
        )

        self.MyopicDiscountingYear = Param(default=0)

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

        self.progress_marker_3 = BuildAction(['Starting to build Variables'], rule=progress_check)

        # Define base decision variables
        self.FlowVar_rpsditvo = Set(dimen=8, initialize=flows.flow_variable_indices)
        self.V_FlowOut = Var(self.FlowVar_rpsditvo, domain=NonNegativeReals)

        self.FlowVarAnnual_rpitvo = Set(dimen=6, initialize=flows.flow_variable_annual_indices)
        self.V_FlowOutAnnual = Var(self.FlowVarAnnual_rpitvo, domain=NonNegativeReals)

        self.FlexVar_rpsditvo = Set(dimen=8, initialize=flows.flex_variable_indices)
        self.V_Flex = Var(self.FlexVar_rpsditvo, domain=NonNegativeReals)

        self.FlexVarAnnual_rpitvo = Set(dimen=6, initialize=flows.flex_variable_annual_indices)
        self.V_FlexAnnual = Var(self.FlexVarAnnual_rpitvo, domain=NonNegativeReals)

        self.CurtailmentVar_rpsditvo = Set(dimen=8, initialize=flows.curtailment_variable_indices)
        self.V_Curtailment = Var(
            self.CurtailmentVar_rpsditvo, domain=NonNegativeReals, initialize=0
        )

        self.FlowInStorage_rpsditvo = Set(
            dimen=8, initialize=flows.flow_in_storage_variable_indices
        )
        self.V_FlowIn = Var(self.FlowInStorage_rpsditvo, domain=NonNegativeReals)

        self.StorageLevel_rpsdtv = Set(dimen=6, initialize=storage.storage_level_variable_indices)
        self.V_StorageLevel = Var(self.StorageLevel_rpsdtv, domain=NonNegativeReals)

        self.SeasonalStorageLevel_rpstv = Set(
            dimen=5, initialize=storage.seasonal_storage_level_variable_indices
        )
        self.V_SeasonalStorageLevel = Var(self.SeasonalStorageLevel_rpstv, domain=NonNegativeReals)

        # Derived decision variables
        self.CapacityVar_rptv = Set(dimen=4, initialize=costs.cost_fixed_indices)
        self.V_Capacity = Var(self.CapacityVar_rptv, domain=NonNegativeReals)

        self.NewCapacityVar_rtv = Set(dimen=3, initialize=capacity.capacity_variable_indices)
        self.V_NewCapacity = Var(self.NewCapacityVar_rtv, domain=NonNegativeReals, initialize=0)

        self.RetiredCapacityVar_rptv = Set(
            dimen=4, initialize=capacity.retired_capacity_variable_indices
        )
        self.V_RetiredCapacity = Var(
            self.RetiredCapacityVar_rptv, domain=NonNegativeReals, initialize=0
        )

        self.AnnualRetirementVar_rptv = Set(
            dimen=4, initialize=capacity.annual_retirement_variable_indices
        )
        self.V_AnnualRetirement = Var(
            self.AnnualRetirementVar_rptv, domain=NonNegativeReals, initialize=0
        )

        self.CapacityAvailableVar_rpt = Set(
            dimen=3, initialize=capacity.capacity_available_variable_indices
        )
        self.V_CapacityAvailableByPeriodAndTech = Var(
            self.CapacityAvailableVar_rpt, domain=NonNegativeReals, initialize=0
        )

        ################################################
        #              Objective Function              #
        #             (minimize total cost)            #
        ################################################

        self.TotalCost = Objective(rule=costs.total_cost_rule, sense=minimize)

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
        self.progress_marker_4 = BuildAction(['Starting to build Constraints'], rule=progress_check)

        # Declare constraints to calculate derived decision variables
        self.CapacityConstraint = Constraint(
            self.CapacityConstraint_rpsdtv, rule=capacity.capacity_constraint
        )

        self.CapacityAnnualConstraint_rptv = Set(
            dimen=4, initialize=capacity.capacity_annual_constraint_indices
        )
        self.CapacityAnnualConstraint = Constraint(
            self.CapacityAnnualConstraint_rptv, rule=capacity.capacity_annual_constraint
        )

        self.CapacityAvailableByPeriodAndTechConstraint = Constraint(
            self.CapacityAvailableVar_rpt,
            rule=capacity.capacity_available_by_period_and_tech_constraint,
        )

        # devnote: I think this constraint is redundant
        # M.RetiredCapacityConstraint = Constraint(
        #     M.RetiredCapacityVar_rptv, rule=RetiredCapacity_Constraint
        # )
        self.progress_marker_4a = BuildAction(
            ['Starting AnnualRetirementConstraint'], rule=progress_check
        )
        self.AnnualRetirementConstraint = Constraint(
            self.AnnualRetirementVar_rptv, rule=capacity.annual_retirement_constraint
        )
        self.progress_marker_4b = BuildAction(
            ['Starting AdjustedCapacityConstraint'], rule=progress_check
        )
        self.AdjustedCapacityConstraint = Constraint(
            self.CostFixed_rptv, rule=capacity.adjusted_capacity_constraint
        )
        self.progress_marker_5 = BuildAction(['Finished Capacity Constraints'], rule=progress_check)

        # Declare core model constraints that ensure proper system functioning
        # In driving order, starting with the need to meet end-use demands

        self.DemandConstraint = Constraint(
            self.DemandConstraint_rpc, rule=commodities.demand_constraint
        )

        # devnote: testing a workaround
        self.DemandActivityConstraint_rpsdtv_dem = Set(
            dimen=7, initialize=commodities.demand_activity_constraint_indices
        )
        self.DemandActivityConstraint = Constraint(
            self.DemandActivityConstraint_rpsdtv_dem, rule=commodities.demand_activity_constraint
        )

        self.CommodityBalanceConstraint_rpsdc = Set(
            dimen=5, initialize=commodities.commodity_balance_constraint_indices
        )
        self.CommodityBalanceConstraint = Constraint(
            self.CommodityBalanceConstraint_rpsdc, rule=commodities.commodity_balance_constraint
        )

        self.AnnualCommodityBalanceConstraint_rpc = Set(
            dimen=3, initialize=commodities.annual_commodity_balance_constraint_indices
        )
        self.AnnualCommodityBalanceConstraint = Constraint(
            self.AnnualCommodityBalanceConstraint_rpc,
            rule=commodities.annual_commodity_balance_constraint,
        )

        # M.ResourceExtractionConstraint = Constraint(
        #     M.ResourceConstraint_rpr, rule=ResourceExtraction_Constraint
        # )

        self.BaseloadDiurnalConstraint_rpsdtv = Set(
            dimen=6, initialize=operations.baseload_diurnal_constraint_indices
        )
        self.BaseloadDiurnalConstraint = Constraint(
            self.BaseloadDiurnalConstraint_rpsdtv, rule=operations.baseload_diurnal_constraint
        )

        self.RegionalExchangeCapacityConstraint_rrptv = Set(
            dimen=5, initialize=capacity.regional_exchange_capacity_constraint_indices
        )
        self.RegionalExchangeCapacityConstraint = Constraint(
            self.RegionalExchangeCapacityConstraint_rrptv,
            rule=geography.regional_exchange_capacity_constraint,
        )

        self.progress_marker_6 = BuildAction(['Starting Storage Constraints'], rule=progress_check)

        self.StorageEnergyConstraint = Constraint(
            self.StorageConstraints_rpsdtv, rule=storage.storage_energy_constraint
        )

        self.StorageEnergyUpperBoundConstraint = Constraint(
            self.StorageConstraints_rpsdtv, rule=storage.storage_energy_upper_bound_constraint
        )

        self.SeasonalStorageEnergyConstraint = Constraint(
            self.SeasonalStorageLevel_rpstv, rule=storage.seasonal_storage_energy_constraint
        )

        self.SeasonalStorageEnergyUpperBoundConstraint = Constraint(
            self.SeasonalStorageConstraints_rpsdtv,
            rule=storage.seasonal_storage_energy_upper_bound_constraint,
        )

        self.StorageChargeRateConstraint = Constraint(
            self.StorageConstraints_rpsdtv, rule=storage.storage_charge_rate_constraint
        )

        self.StorageDischargeRateConstraint = Constraint(
            self.StorageConstraints_rpsdtv, rule=storage.storage_discharge_rate_constraint
        )

        self.StorageThroughputConstraint = Constraint(
            self.StorageConstraints_rpsdtv, rule=storage.storage_throughput_constraint
        )

        self.LimitStorageFractionConstraint = Constraint(
            self.LimitStorageFractionConstraint_rpsdtv,
            rule=storage.limit_storage_fraction_constraint,
        )

        self.RampUpDayConstraint_rpsdtv = Set(
            dimen=6, initialize=operations.ramp_up_day_constraint_indices
        )
        self.RampUpDayConstraint = Constraint(
            self.RampUpDayConstraint_rpsdtv, rule=operations.ramp_up_day_constraint
        )
        self.RampDownDayConstraint_rpsdtv = Set(
            dimen=6, initialize=operations.ramp_down_day_constraint_indices
        )
        self.RampDownDayConstraint = Constraint(
            self.RampDownDayConstraint_rpsdtv, rule=operations.ramp_down_day_constraint
        )

        self.RampUpSeasonConstraint_rpsstv = Set(
            dimen=6, initialize=operations.ramp_up_season_constraint_indices
        )
        self.RampUpSeasonConstraint = Constraint(
            self.RampUpSeasonConstraint_rpsstv, rule=operations.ramp_up_season_constraint
        )
        self.RampDownSeasonConstraint_rpsstv = Set(
            dimen=6, initialize=operations.ramp_down_season_constraint_indices
        )
        self.RampDownSeasonConstraint = Constraint(
            self.RampDownSeasonConstraint_rpsstv, rule=operations.ramp_down_season_constraint
        )

        self.ReserveMargin_rpsd = Set(dimen=4, initialize=reserves.reserve_margin_indices)
        self.validate_ReserveMargin = BuildAction(rule=validate_reserve_margin)
        self.ReserveMarginConstraint = Constraint(
            self.ReserveMargin_rpsd, rule=reserves.reserve_margin_constraint
        )

        self.LimitEmissionConstraint = Constraint(
            self.LimitEmissionConstraint_rpe, rule=limits.limit_emission_constraint
        )
        self.progress_marker_7 = BuildAction(
            ['Starting LimitGrowth and Activity Constraints'], rule=progress_check
        )

        self.LimitGrowthCapacityConstraint_rpt = Set(
            dimen=4, initialize=limits.limit_growth_capacity_indices
        )
        self.LimitGrowthCapacityConstraint = Constraint(
            self.LimitGrowthCapacityConstraint_rpt,
            rule=limits.limit_growth_capacity_constraint_rule,
        )
        self.LimitDegrowthCapacityConstraint_rpt = Set(
            dimen=4, initialize=limits.limit_degrowth_capacity_indices
        )
        self.LimitDegrowthCapacityConstraint = Constraint(
            self.LimitDegrowthCapacityConstraint_rpt,
            rule=limits.limit_degrowth_capacity_constraint_rule,
        )

        self.LimitGrowthNewCapacityConstraint_rpt = Set(
            dimen=4, initialize=limits.limit_growth_new_capacity_indices
        )
        self.LimitGrowthNewCapacityConstraint = Constraint(
            self.LimitGrowthNewCapacityConstraint_rpt,
            rule=limits.limit_growth_new_capacity_constraint_rule,
        )
        self.LimitDegrowthNewCapacityConstraint_rpt = Set(
            dimen=4, initialize=limits.limit_degrowth_new_capacity_indices
        )
        self.LimitDegrowthNewCapacityConstraint = Constraint(
            self.LimitDegrowthNewCapacityConstraint_rpt,
            rule=limits.limit_degrowth_new_capacity_constraint_rule,
        )

        self.LimitGrowthNewCapacityDeltaConstraint_rpt = Set(
            dimen=4, initialize=limits.limit_growth_new_capacity_delta_indices
        )
        self.LimitGrowthNewCapacityDeltaConstraint = Constraint(
            self.LimitGrowthNewCapacityDeltaConstraint_rpt,
            rule=limits.limit_growth_new_capacity_delta_constraint_rule,
        )
        self.LimitDegrowthNewCapacityDeltaConstraint_rpt = Set(
            dimen=4, initialize=limits.limit_degrowth_new_capacity_delta_indices
        )
        self.LimitDegrowthNewCapacityDeltaConstraint = Constraint(
            self.LimitDegrowthNewCapacityDeltaConstraint_rpt,
            rule=limits.limit_degrowth_new_capacity_delta_constraint_rule,
        )

        self.LimitActivityConstraint = Constraint(
            self.LimitActivityConstraint_rpt, rule=limits.limit_activity_constraint
        )

        self.LimitSeasonalCapacityFactorConstraint = Constraint(
            self.LimitSeasonalCapacityFactorConstraint_rpst,
            rule=limits.limit_seasonal_capacity_factor_constraint,
        )

        # devnote: deprecated when generalising tech/group columns in Limit tables
        # M.LimitActivityGroupConstraint = Constraint(
        #     M.LimitActivityGroupConstraint_rpg, rule=LimitActivityGroup_Constraint
        # )

        self.LimitCapacityConstraint = Constraint(
            self.LimitCapacityConstraint_rpt, rule=limits.limit_capacity_constraint
        )

        self.LimitNewCapacityConstraint = Constraint(
            self.LimitNewCapacityConstraint_rpt, rule=limits.limit_new_capacity_constraint
        )

        # devnote: deprecated when generalising tech/group columns in Limit tables
        # M.LimitCapacityGroupConstraint = Constraint(
        #     M.LimitCapacityGroupConstraint_rpg, rule=LimitCapacityGroup_Constraint
        # )

        # M.LimitNewCapacityGroupConstraint = Constraint(
        #     M.LimitNewCapacityGroupConstraint_rpg, rule=LimitNewCapacityGroup_Constraint
        # )

        self.LimitCapacityShareConstraint = Constraint(
            self.LimitCapacityShareConstraint_rpgg, rule=limits.limit_capacity_share_constraint
        )

        self.LimitActivityShareConstraint = Constraint(
            self.LimitActivityShareConstraint_rpgg, rule=limits.limit_activity_share_constraint
        )

        self.LimitNewCapacityShareConstraint = Constraint(
            self.LimitNewCapacityShareConstraint_rpgg,
            rule=limits.limit_new_capacity_share_constraint,
        )

        # devnote: deprecated when generalising tech/group columns in Limit tables
        # M.LimitNewCapacityGroupShareConstraint = Constraint(
        #     M.LimitNewCapacityGroupShareConstraint_rpgg,
        #     rule=LimitNewCapacityGroupShare_Constraint
        # )

        # M.LimitActivityGroupShareConstraint = Constraint(
        #     M.LimitActivityGroupShareConstraint_rpgg, rule=LimitActivityGroupShare_Constraint
        # )

        self.progress_marker_8 = BuildAction(
            ['Starting Limit Capacity and Tech Split Constraints'], rule=progress_check
        )

        self.LimitResourceConstraint = Constraint(
            self.LimitResourceConstraint_rt, rule=limits.limit_resource_constraint
        )

        self.LimitAnnualCapacityFactorConstraint = Constraint(
            self.LimitAnnualCapacityFactorConstraint_rpto,
            rule=limits.limit_annual_capacity_factor_constraint,
        )

        ## Tech input splits
        self.LimitTechInputSplitConstraint_rpsditv = Set(
            dimen=8, initialize=limits.limit_tech_input_split_constraint_indices
        )
        self.LimitTechInputSplitConstraint = Constraint(
            self.LimitTechInputSplitConstraint_rpsditv,
            rule=limits.limit_tech_input_split_constraint,
        )

        self.LimitTechInputSplitAnnualConstraint_rpitv = Set(
            dimen=6, initialize=limits.limit_tech_input_split_annual_constraint_indices
        )
        self.LimitTechInputSplitAnnualConstraint = Constraint(
            self.LimitTechInputSplitAnnualConstraint_rpitv,
            rule=limits.limit_tech_input_split_annual_constraint,
        )

        self.LimitTechInputSplitAverageConstraint_rpitv = Set(
            dimen=6, initialize=limits.limit_tech_input_split_average_constraint_indices
        )
        self.LimitTechInputSplitAverageConstraint = Constraint(
            self.LimitTechInputSplitAverageConstraint_rpitv,
            rule=limits.limit_tech_input_split_average_constraint,
        )

        ## Tech output splits
        self.LimitTechOutputSplitConstraint_rpsdtvo = Set(
            dimen=8, initialize=limits.limit_tech_output_split_constraint_indices
        )
        self.LimitTechOutputSplitConstraint = Constraint(
            self.LimitTechOutputSplitConstraint_rpsdtvo,
            rule=limits.limit_tech_output_split_constraint,
        )

        self.LimitTechOutputSplitAnnualConstraint_rptvo = Set(
            dimen=6, initialize=limits.limit_tech_output_split_annual_constraint_indices
        )
        self.LimitTechOutputSplitAnnualConstraint = Constraint(
            self.LimitTechOutputSplitAnnualConstraint_rptvo,
            rule=limits.limit_tech_output_split_annual_constraint,
        )

        self.LimitTechOutputSplitAverageConstraint_rptvo = Set(
            dimen=6, initialize=limits.limit_tech_output_split_average_constraint_indices
        )
        self.LimitTechOutputSplitAverageConstraint = Constraint(
            self.LimitTechOutputSplitAverageConstraint_rptvo,
            rule=limits.limit_tech_output_split_average_constraint,
        )

        self.RenewablePortfolioStandardConstraint = Constraint(
            self.RenewablePortfolioStandardConstraint_rpg,
            rule=limits.renewable_portfolio_standard_constraint,
        )

        self.LinkedEmissionsTechConstraint_rpsdtve = Set(
            dimen=7, initialize=emissions.linked_tech_constraint_indices
        )
        # the validation requires that the set above be built first:
        self.validate_LinkedTech_lifetimes = BuildCheck(rule=validate_linked_tech)

        self.LinkedEmissionsTechConstraint = Constraint(
            self.LinkedEmissionsTechConstraint_rpsdtve,
            rule=emissions.linked_emissions_tech_constraint,
        )

        self.progress_marker_9 = BuildAction(['Finished Constraints'], rule=progress_check)


def progress_check(model: TemoaModel, checkpoint: str) -> None:
    """A quick widget which is called by BuildAction in order to log creation progress"""
    logger.debug('Model build progress: %s', checkpoint)
