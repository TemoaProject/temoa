#!/usr/bin/env python

"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging

from pyomo.core import BuildCheck
from pyomo.environ import (
    Any,
    NonNegativeReals,
    AbstractModel,
    BuildAction,
    Param,
    Objective,
    minimize,
)

from temoa.temoa_model.model_checking.validators import (
    validate_linked_tech,
    region_check,
    validate_CapacityFactorProcess,
    region_group_check,
    validate_Efficiency,
    check_flex_curtail,
    no_slash_or_pipe,
)
from temoa.temoa_model.temoa_initialize import *
from temoa.temoa_model.temoa_initialize import get_loan_life
from temoa.temoa_model.temoa_rules import *

logger = logging.getLogger(__name__)

# disable linter rule that complains about star imports for this file
# ruff: noqa: F405


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
        """currently available (within lifespan) (r, p, t, v) tuples (from M.processVintages)"""

        M.activeRegionsForTech = None
        """currently available regions by period and tech {(p, t) : r}"""

        M.activeCapacity_rtv = None
        M.activeCapacityAvailable_rpt = None
        M.activeCapacityAvailable_rptv = None
        M.commodityDStreamProcess = dict()  # The downstream process of a commodity during a period
        M.commodityUStreamProcess = dict()  # The upstream process of a commodity during a period
        M.ProcessInputsByOutput = dict()
        M.ProcessOutputsByInput = dict()
        M.processTechs = dict()
        M.processReservePeriods = dict()
        M.processVintages = dict()
        """current available (within lifespan) vintages {(r, p, t) : set(v)}"""

        M.baseloadVintages = dict()
        M.curtailmentVintages = dict()
        M.storageVintages = dict()
        M.rampVintages = dict()
        M.inputsplitVintages = dict()
        M.inputsplitannualVintages = dict()
        M.outputsplitVintages = dict()
        M.outputsplitannualVintages = dict()
        M.ProcessByPeriodAndOutput = dict()
        M.exportRegions = dict()
        M.importRegions = dict()
        M.flex_commodities = set()

        ################################################
        #                 Model Sets                   #
        #    (used for indexing model elements)        #
        ################################################

        M.progress_marker_1 = BuildAction(['Starting to build Sets'], rule=progress_check)

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
        M.time_of_day = Set(ordered=True, validate=no_slash_or_pipe)

        # Define regions
        M.regions = Set(validate=region_check)
        # RegionalIndices is the set of all the possible combinations of interregional exchanges
        # plus original region indices. If tech_exchange is empty, RegionalIndices =regions.
        M.RegionalIndices = Set(initialize=CreateRegionalIndices)
        M.RegionalGlobalIndices = Set(validate=region_group_check)

        # Define technology-related sets
        M.tech_resource = Set()
        M.tech_production = Set()
        M.tech_all = Set(initialize=M.tech_resource | M.tech_production, validate=no_slash_or_pipe)
        M.tech_baseload = Set(within=M.tech_all)
        M.tech_annual = Set(within=M.tech_all)
        # annual storage not supported in Storage constraint or TableWriter, so exclude from domain
        M.tech_storage = Set(within=M.tech_all - M.tech_annual)
        M.tech_reserve = Set(within=M.tech_all)
        M.tech_ramping = Set(within=M.tech_all)
        M.tech_curtailment = Set(within=M.tech_all)
        M.tech_flex = Set(within=M.tech_all)
        # ensure there is no overlap flex <=> curtailable technologies
        M.check_flex_and_curtailment = BuildAction(rule=check_flex_curtail)
        M.tech_exchange = Set(within=M.tech_all)

        # Define groups for technologies
        M.tech_group_names = Set()
        M.tech_group_members = Set(M.tech_group_names, within=M.tech_all)

        M.tech_uncap = Set(within=M.tech_all - M.tech_reserve)
        """techs with unlimited capacity, ALWAYS available within lifespan"""

        # the below is a convenience for domain checking in params below that should not accept uncap techs...
        M.tech_with_capacity = Set(initialize=M.tech_all - M.tech_uncap)
        """techs eligible for capacitization"""
        # Define techs for which economic retirement is an option
        # Note:  Storage techs cannot (currently) be retired due to linkage to initialization
        #        process, which is currently incapable of reducing initializations on retirements.
        M.tech_retirement = Set(within=M.tech_all - M.tech_storage)

        # Define commodity-related sets
        M.commodity_demand = Set()
        M.commodity_emissions = Set()
        M.commodity_physical = Set()
        M.commodity_source = Set(within=M.commodity_physical)
        M.commodity_annual = Set(within=M.commodity_physical)
        M.commodity_carrier = Set(initialize=M.commodity_physical | M.commodity_demand)
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

        M.GlobalDiscountRate = Param()

        # Define time-related parameters
        M.PeriodLength = Param(M.time_optimize, initialize=ParamPeriodLength)
        M.SegFrac = Param(M.time_season, M.time_of_day)
        M.validate_SegFrac = BuildAction(rule=validate_SegFrac)

        # Define demand- and resource-related parameters
        # Dev Note:  There does not appear to be a DB table supporting DemandDefaultDistro.  This does not
        #            cause any problems, so let it be for now.
        M.DemandDefaultDistribution = Param(M.time_season, M.time_of_day, mutable=True)
        M.DemandSpecificDistribution = Param(
            M.regions, M.time_season, M.time_of_day, M.commodity_demand, mutable=True, default=0
        )

        M.Demand = Param(M.regions, M.time_optimize, M.commodity_demand)
        M.initialize_Demands = BuildAction(rule=CreateDemands)

        M.ResourceConstraint_rpr = Set(within=M.regions * M.time_optimize * M.commodity_physical)

        # Dev Note:  This parameter is currently NOT implemented.  Preserved for later refactoring
        M.ResourceBound = Param(M.ResourceConstraint_rpr)

        # Define technology performance parameters
        M.CapacityToActivity = Param(M.RegionalIndices, M.tech_all, default=1)

        M.ExistingCapacity = Param(M.RegionalIndices, M.tech_with_capacity, M.vintage_exist)

        # Dev Note:  The below is temporarily useful for passing down to validator to find set violations
        #            Uncomment this assignment, and comment out the orig below it...
        # M.Efficiency = Param(
        #     Any, Any, Any, Any, Any,
        #     within=NonNegativeReals, validate=validate_Efficiency
        # )
        M.Efficiency = Param(
            M.RegionalIndices,
            M.commodity_physical,
            M.tech_all,
            M.vintage_all,
            M.commodity_carrier,
            within=NonNegativeReals,
            validate=validate_Efficiency,
        )

        M.validate_UsedEfficiencyIndices = BuildAction(rule=CheckEfficiencyIndices)

        M.CapacityFactor_rsdt = Set(dimen=4, initialize=CapacityFactorTechIndices)
        M.CapacityFactorTech = Param(M.CapacityFactor_rsdt, default=1)

        # Dev note:  using a default function below alleviates need to make this set.
        # M.CapacityFactor_rsdtv = Set(dimen=5, initialize=CapacityFactorProcessIndices)
        M.CapacityFactorProcess = Param(
            M.regions,
            M.time_season,
            M.time_of_day,
            M.tech_with_capacity,
            M.vintage_all,
            validate=validate_CapacityFactorProcess,
            default=get_default_capacity_factor,
        )

        # M.initialize_CapacityFactors = BuildAction(rule=CreateCapacityFactors)

        M.LifetimeTech = Param(
            M.RegionalIndices, M.tech_all, default=TemoaModel.default_lifetime_tech
        )

        M.LifetimeProcess_rtv = Set(dimen=3, initialize=LifetimeProcessIndices)
        M.LifetimeProcess = Param(M.LifetimeProcess_rtv, default=get_default_process_lifetime)

        M.LoanLifetimeTech = Param(M.RegionalIndices, M.tech_all, default=10)
        M.LoanLifetimeProcess_rtv = Set(dimen=3, initialize=LifetimeLoanProcessIndices)

        # Dev Note:  The LoanLifetimeProcess table *could* be removed.  There is no longer a supporting
        #            table in the database.  It is just a "passthrough" now to the default LoanLifetimeTech.
        #            It is already stitched in to the model, so will leave it for now.  Table may be revived.

        M.LoanLifetimeProcess = Param(M.LoanLifetimeProcess_rtv, default=get_loan_life)

        M.TechInputSplit = Param(M.regions, M.time_optimize, M.commodity_physical, M.tech_all)
        M.TechInputSplitAnnual = Param(M.regions, M.time_optimize, M.commodity_physical, M.tech_all)
        M.TechOutputSplit = Param(M.regions, M.time_optimize, M.tech_all, M.commodity_carrier)
        M.TechOutputSplitAnnual = Param(M.regions, M.time_optimize, M.tech_all, M.commodity_carrier)

        M.RenewablePortfolioStandardConstraint_rpg = Set(
            within=M.regions * M.time_optimize * M.tech_group_names
        )
        M.RenewablePortfolioStandard = Param(M.RenewablePortfolioStandardConstraint_rpg)

        # The method below creates a series of helper functions that are used to
        # perform the sparse matrix of indexing for the parameters, variables, and
        # equations below.
        M.Create_SparseDicts = BuildAction(rule=CreateSparseDicts)

        # Define technology cost parameters
        # dev note:  the CostFixed_rptv isn't truly needed, but it is included in a constraint, so
        #            let it go for now
        M.CostFixed_rptv = Set(dimen=4, initialize=CostFixedIndices)
        M.CostFixed = Param(M.CostFixed_rptv)

        M.CostInvest_rtv = Set(within=M.RegionalIndices * M.tech_all * M.time_optimize)
        M.CostInvest = Param(M.CostInvest_rtv)

        M.DefaultLoanRate = Param(domain=NonNegativeReals)
        M.LoanRate = Param(M.CostInvest_rtv, domain=NonNegativeReals, default=get_default_loan_rate)
        M.LoanAnnualize = Param(M.CostInvest_rtv, initialize=ParamLoanAnnualize_rule)

        M.CostVariable_rptv = Set(dimen=4, initialize=CostVariableIndices)
        M.CostVariable = Param(M.CostVariable_rptv)

        M.CostEmission_rpe = Set(
            dimen=3, domain=M.regions * M.time_optimize * M.commodity_emissions
        )  # read from data
        M.CostEmission = Param(M.CostEmission_rpe, domain=NonNegativeReals)

        M.ModelProcessLife_rptv = Set(dimen=4, initialize=ModelProcessLifeIndices)
        M.ModelProcessLife = Param(M.ModelProcessLife_rptv, initialize=ParamModelProcessLife_rule)

        M.ProcessLifeFrac_rptv = Set(dimen=4, initialize=ModelProcessLifeIndices)
        M.ProcessLifeFrac = Param(M.ProcessLifeFrac_rptv, initialize=ParamProcessLifeFraction_rule)

        M.MinCapacityConstraint_rpt = Set(
            within=M.RegionalIndices * M.time_optimize * M.tech_with_capacity
        )

        M.MinCapacity = Param(M.MinCapacityConstraint_rpt)

        M.MaxCapacityConstraint_rpt = Set(
            within=M.RegionalIndices * M.time_optimize * M.tech_with_capacity
        )
        M.MaxCapacity = Param(M.MaxCapacityConstraint_rpt)

        M.MinNewCapacityConstraint_rpt = Set(
            within=M.RegionalIndices * M.time_optimize * M.tech_with_capacity
        )
        M.MinNewCapacity = Param(M.MinNewCapacityConstraint_rpt)

        M.MaxNewCapacityConstraint_rpt = Set(
            within=M.RegionalIndices * M.time_optimize * M.tech_with_capacity
        )
        M.MaxNewCapacity = Param(M.MaxNewCapacityConstraint_rpt)

        M.MaxResourceConstraint_rt = Set(within=M.RegionalIndices * M.tech_all)
        M.MaxResource = Param(M.MaxResourceConstraint_rt)

        M.MaxActivityConstraint_rpt = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.tech_all
        )
        M.MaxActivity = Param(M.MaxActivityConstraint_rpt)

        M.MinActivityConstraint_rpt = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.tech_all
        )
        M.MinActivity = Param(M.MinActivityConstraint_rpt)

        M.MaxSeasonalActivityConstraint_rpst = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.time_season * M.tech_all
        )
        M.MaxSeasonalActivity = Param(M.MaxSeasonalActivityConstraint_rpst)

        M.MinSeasonalActivityConstraint_rpst = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.time_season * M.tech_all
        )
        M.MinSeasonalActivity = Param(M.MinSeasonalActivityConstraint_rpst)

        M.MinAnnualCapacityFactorConstraint_rpto = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.tech_all * M.commodity_carrier
        )
        M.MinAnnualCapacityFactor = Param(M.MinAnnualCapacityFactorConstraint_rpto)

        M.MaxAnnualCapacityFactorConstraint_rpto = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.tech_all * M.commodity_carrier
        )
        M.MaxAnnualCapacityFactor = Param(M.MaxAnnualCapacityFactorConstraint_rpto)
        M.GrowthRateMax = Param(M.RegionalIndices, M.tech_all)
        M.GrowthRateSeed = Param(M.RegionalIndices, M.tech_all)

        M.EmissionLimitConstraint_rpe = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.commodity_emissions
        )
        M.EmissionLimit = Param(M.EmissionLimitConstraint_rpe)
        M.EmissionActivity_reitvo = Set(dimen=6, initialize=EmissionActivityIndices)
        M.EmissionActivity = Param(M.EmissionActivity_reitvo)

        M.MinActivityGroup_rpg = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.tech_group_names
        )
        M.MinActivityGroup = Param(M.MinActivityGroup_rpg)

        M.MaxActivityGroup_rpg = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.tech_group_names
        )

        M.MaxActivityGroup = Param(M.MaxActivityGroup_rpg)

        M.MinCapacityGroupConstraint_rpg = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.tech_group_names
        )
        M.MinCapacityGroup = Param(M.MinCapacityGroupConstraint_rpg)

        M.MaxCapacityGroupConstraint_rpg = Set(
            within=M.RegionalGlobalIndices * M.time_optimize * M.tech_group_names
        )
        M.MaxCapacityGroup = Param(M.MaxCapacityGroupConstraint_rpg)

        M.MinNewCapacityGroupConstraint_rpg = Set(
            within=M.RegionalIndices * M.time_optimize * M.tech_group_names
        )
        M.MinNewCapacityGroup = Param(M.MinNewCapacityGroupConstraint_rpg)

        M.MaxNewCapacityGroupConstraint_rpg = Set(
            within=M.RegionalIndices * M.time_optimize * M.tech_group_names
        )
        M.MaxNewCapacityGroup = Param(M.MaxNewCapacityGroupConstraint_rpg)
        M.GroupShareIndices = Set(dimen=4, initialize=GroupShareIndices)

        M.MinCapacityShareConstraint_rptg = Set(within=M.GroupShareIndices)
        M.MinCapacityShare = Param(M.GroupShareIndices)

        M.MaxCapacityShareConstraint_rptg = Set(within=M.GroupShareIndices)
        M.MaxCapacityShare = Param(M.GroupShareIndices)

        M.MinActivityShareConstraint_rptg = Set(within=M.GroupShareIndices)
        M.MinActivityShare = Param(M.GroupShareIndices)

        M.MaxActivityShareConstraint_rptg = Set(within=M.GroupShareIndices)
        M.MaxActivityShare = Param(M.GroupShareIndices)

        M.MinNewCapacityShareConstraint_rptg = Set(within=M.GroupShareIndices)
        M.MinNewCapacityShare = Param(M.GroupShareIndices)

        M.MaxNewCapacityShareConstraint_rptg = Set(within=M.GroupShareIndices)
        M.MaxNewCapacityShare = Param(M.GroupShareIndices)
        M.LinkedTechs = Param(M.RegionalIndices, M.tech_all, M.commodity_emissions, within=Any)

        # Define parameters associated with electric sector operation
        M.RampUp = Param(M.regions, M.tech_ramping)
        M.RampDown = Param(M.regions, M.tech_ramping)
        M.CapacityCredit = Param(
            M.RegionalIndices, M.time_optimize, M.tech_all, M.vintage_all, default=0
        )
        M.PlanningReserveMargin = Param(M.regions, default=0.2)
        # Storage duration is expressed in hours
        M.StorageDuration = Param(M.regions, M.tech_storage, default=4)
        # Initial storage charge level, expressed as fraction of full energy capacity.
        # If the parameter is not defined, the model optimizes the initial storage charge level.
        # Dev note: needs overhaul
        M.StorageInitFrac = Param(M.regions, M.time_optimize, M.time_season, M.tech_storage, M.vintage_all)

        M.MyopicBaseyear = Param(default=0)
        M.link_seasons = Param(default=0) # do states carry from one season to the next? otherwise loop each season

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

        M.StorageInit_rpstv = Set(dimen=5, initialize=StorageInitIndices)
        M.V_StorageInit = Var(M.StorageInit_rpstv, domain=NonNegativeReals)
        M.StorageLevel_rpsdtv = Set(dimen=6, initialize=StorageStateIndices)
        M.V_StorageLevel = Var(M.StorageLevel_rpsdtv, domain=NonNegativeReals)

        # Derived decision variables

        M.CapacityVar_rptv = Set(dimen=4, initialize=CostFixedIndices)
        M.V_Capacity = Var(M.CapacityVar_rptv, domain=NonNegativeReals)

        M.NewCapacityVar_rtv = Set(dimen=3, initialize=CapacityVariableIndices)
        M.V_NewCapacity = Var(M.NewCapacityVar_rtv, domain=NonNegativeReals, initialize=0)

        M.RetiredCapacityVar_rptv = Set(dimen=4, initialize=RetiredCapacityVariableIndices)
        M.V_RetiredCapacity = Var(M.RetiredCapacityVar_rptv, domain=NonNegativeReals, initialize=0)

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
        M.CapacityConstraint_rpsdtv = Set(dimen=6, initialize=CapacityConstraintIndices)
        M.CapacityConstraint = Constraint(M.CapacityConstraint_rpsdtv, rule=Capacity_Constraint)

        M.CapacityAnnualConstraint_rptv = Set(dimen=4, initialize=CapacityAnnualConstraintIndices)
        M.CapacityAnnualConstraint = Constraint(
            M.CapacityAnnualConstraint_rptv, rule=CapacityAnnual_Constraint
        )

        M.CapacityAvailableByPeriodAndTechConstraint = Constraint(
            M.CapacityAvailableVar_rpt, rule=CapacityAvailableByPeriodAndTech_Constraint
        )

        M.RetiredCapacityConstraint = Constraint(
            M.RetiredCapacityVar_rptv, rule=RetiredCapacity_Constraint
        )
        M.AdjustedCapacityConstraint = Constraint(
            M.CostFixed_rptv, rule=AdjustedCapacity_Constraint
        )
        M.progress_marker_5 = BuildAction(['Finished Capacity Constraints'], rule=progress_check)

        # Declare core model constraints that ensure proper system functioning
        # In driving order, starting with the need to meet end-use demands

        M.DemandConstraint_rpsdc = Set(dimen=5, initialize=DemandConstraintIndices)
        M.DemandConstraint = Constraint(M.DemandConstraint_rpsdc, rule=Demand_Constraint)

        M.DemandActivityConstraint_rpsdtv_dem_s0d0 = Set(
            dimen=9, initialize=DemandActivityConstraintIndices
        )
        M.DemandActivityConstraint = Constraint(
            M.DemandActivityConstraint_rpsdtv_dem_s0d0, rule=DemandActivity_Constraint
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

        M.ResourceExtractionConstraint = Constraint(
            M.ResourceConstraint_rpr, rule=ResourceExtraction_Constraint
        )

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
        # This set works for all the storage-related constraints
        M.StorageConstraints_rpsdtv = Set(dimen=6, initialize=StorageConstraintIndices)

        M.StorageEnergyConstraint = Constraint(
            M.StorageConstraints_rpsdtv, rule=StorageEnergy_Constraint
        )

        # We make use of this following set in some of the storage constraints.
        # Pre-computing it is considerably faster.
        M.SegFracPerSeason = Param(M.time_season, initialize=SegFracPerSeason_rule)

        M.StorageEnergyUpperBoundConstraint = Constraint(
            M.StorageConstraints_rpsdtv, rule=StorageEnergyUpperBound_Constraint
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

        M.StorageInitFracConstraint_rpstv = Set(dimen=5, initialize=StorageInitFracIndices)
        M.StorageInitFracConstraint = Constraint(
            M.StorageInitFracConstraint_rpstv, rule=StorageInitFrac_Constraint
        )

        M.RampConstraint_rpsdtv = Set(dimen=6, initialize=RampConstraintIndices)
        M.RampUpConstraint = Constraint(M.RampConstraint_rpsdtv, rule=RampUpDay_Constraint)
        M.RampDownConstraint = Constraint(M.RampConstraint_rpsdtv, rule=RampDownDay_Constraint)

        M.ReserveMargin_rpsd = Set(dimen=4, initialize=ReserveMarginIndices)
        M.ReserveMarginConstraint = Constraint(M.ReserveMargin_rpsd, rule=ReserveMargin_Constraint)

        M.EmissionLimitConstraint = Constraint(
            M.EmissionLimitConstraint_rpe, rule=EmissionLimit_Constraint
        )
        M.progress_marker_7 = BuildAction(
            ['Starting Growth and Activity Constraints'], rule=progress_check
        )

        M.GrowthRateMaxConstraint_rtv = Set(dimen=3, initialize=GrowthRateMaxIndices)
        M.GrowthRateMaxConstraint = Constraint(
            M.GrowthRateMaxConstraint_rtv, rule=GrowthRateMaxConstraint_rule
        )

        M.MaxActivityConstraint = Constraint(
            M.MaxActivityConstraint_rpt, rule=MaxActivity_Constraint
        )

        M.MinActivityConstraint = Constraint(
            M.MinActivityConstraint_rpt, rule=MinActivity_Constraint
        )

        M.MaxSeasonalActivityConstraint = Constraint(
            M.MaxSeasonalActivityConstraint_rpst, rule=MaxSeasonalActivity_Constraint
        )

        M.MinSeasonalActivityConstraint = Constraint(
            M.MinSeasonalActivityConstraint_rpst, rule=MinSeasonalActivity_Constraint
        )

        M.MinActivityGroupConstraint = Constraint(
            M.MinActivityGroup_rpg, rule=MinActivityGroup_Constraint
        )

        M.MaxActivityGroupConstraint = Constraint(
            M.MaxActivityGroup_rpg, rule=MaxActivityGroup_Constraint
        )

        M.MaxCapacityConstraint = Constraint(
            M.MaxCapacityConstraint_rpt, rule=MaxCapacity_Constraint
        )

        M.MaxNewCapacityConstraint = Constraint(
            M.MaxNewCapacityConstraint_rpt, rule=MaxNewCapacity_Constraint
        )

        M.MaxCapacityGroupConstraint = Constraint(
            M.MaxCapacityGroupConstraint_rpg, rule=MaxCapacityGroup_Constraint
        )

        M.MinCapacityGroupConstraint = Constraint(
            M.MinCapacityGroupConstraint_rpg, rule=MinCapacityGroup_Constraint
        )

        M.MinNewCapacityGroupConstraint = Constraint(
            M.MinNewCapacityGroupConstraint_rpg, rule=MinNewCapacityGroup_Constraint
        )

        M.MaxNewCapacityGroupConstraint = Constraint(
            M.MinNewCapacityGroupConstraint_rpg, rule=MaxNewCapacityGroup_Constraint
        )

        M.MinCapacityShareConstraint = Constraint(
            M.MinCapacityShareConstraint_rptg, rule=MinCapacityShare_Constraint
        )

        M.MaxCapacityShareConstraint = Constraint(
            M.MaxCapacityShareConstraint_rptg, rule=MaxCapacityShare_Constraint
        )

        M.MinActivityShareConstraint = Constraint(
            M.MinActivityShareConstraint_rptg, rule=MinActivityShare_Constraint
        )

        M.MaxActivityShareConstraint = Constraint(
            M.MaxActivityShareConstraint_rptg, rule=MaxActivityShare_Constraint
        )

        M.MinNewCapacityShareConstraint = Constraint(
            M.MinNewCapacityShareConstraint_rptg, rule=MinNewCapacityShare_Constraint
        )

        M.MaxNewCapacityShareConstraint = Constraint(
            M.MaxNewCapacityShareConstraint_rptg, rule=MaxNewCapacityShare_Constraint
        )

        M.progress_marker_8 = BuildAction(
            ['Starting Max/Min Capacity and Tech Split ' 'Constraints'], rule=progress_check
        )

        M.MaxResourceConstraint = Constraint(
            M.MaxResourceConstraint_rt, rule=MaxResource_Constraint
        )

        M.MinCapacityConstraint = Constraint(
            M.MinCapacityConstraint_rpt, rule=MinCapacity_Constraint
        )

        M.MinNewCapacityConstraint = Constraint(
            M.MinNewCapacityConstraint_rpt, rule=MinNewCapacity_Constraint
        )

        M.MinAnnualCapacityFactorConstraint = Constraint(
            M.MinAnnualCapacityFactorConstraint_rpto, rule=MinAnnualCapacityFactor_Constraint
        )

        M.MaxAnnualCapacityFactorConstraint = Constraint(
            M.MaxAnnualCapacityFactorConstraint_rpto, rule=MaxAnnualCapacityFactor_Constraint
        )

        M.TechInputSplitConstraint_rpsditv = Set(
            dimen=7, initialize=TechInputSplitConstraintIndices
        )
        M.TechInputSplitConstraint = Constraint(
            M.TechInputSplitConstraint_rpsditv, rule=TechInputSplit_Constraint
        )

        M.TechInputSplitAnnualConstraint_rpitv = Set(
            dimen=5, initialize=TechInputSplitAnnualConstraintIndices
        )
        M.TechInputSplitAnnualConstraint = Constraint(
            M.TechInputSplitAnnualConstraint_rpitv, rule=TechInputSplitAnnual_Constraint
        )

        M.TechInputSplitAverageConstraint_rpitv = Set(
            dimen=5, initialize=TechInputSplitAverageConstraintIndices
        )
        M.TechInputSplitAverageConstraint = Constraint(
            M.TechInputSplitAverageConstraint_rpitv, rule=TechInputSplitAverage_Constraint
        )

        M.TechOutputSplitConstraint_rpsdtvo = Set(
            dimen=7, initialize=TechOutputSplitConstraintIndices
        )
        M.TechOutputSplitConstraint = Constraint(
            M.TechOutputSplitConstraint_rpsdtvo, rule=TechOutputSplit_Constraint
        )

        M.TechOutputSplitAnnualConstraint_rptvo = Set(
            dimen=5, initialize=TechOutputSplitAnnualConstraintIndices
        )
        M.TechOutputSplitAnnualConstraint = Constraint(
            M.TechOutputSplitAnnualConstraint_rptvo, rule=TechOutputSplitAnnual_Constraint
        )

        M.TechOutputSplitAverageConstraint_rptvo = Set(
            dimen=5, initialize=TechOutputSplitAverageConstraintIndices
        )
        M.TechOutputSplitAverageConstraint = Constraint(
            M.TechOutputSplitAverageConstraint_rptvo, rule=TechOutputSplitAverage_Constraint
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
