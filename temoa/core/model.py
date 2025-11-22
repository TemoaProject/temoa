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

if TYPE_CHECKING:
    from temoa import types as t
    from temoa.types.core_types import Technology

logger = logging.getLogger(__name__)


def create_sparse_dicts(model: 'TemoaModel') -> None:
    """
    Creates and populates all sparse dictionaries and sets required for the model
    by calling component-specific precomputation functions.
    """

    # Call the decomposed functions in logical order
    # 1. Populate core relationships from efficiency table
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
                "Notice: '%s' is specified as a technology but is not "
                'utilized in the efficiency parameter.',
                tech,
            )

    logger.debug('Completed creation of SparseDicts')


class TemoaModel(AbstractModel):
    """
    An instance of the abstract Temoa model
    """

    # this is used in several places outside this class, and this provides no-build access to it
    default_lifetime_tech = 40

    def __init__(self, *args: object, **kwargs: object) -> None:
        AbstractModel.__init__(self, *args, **kwargs)

        ################################################
        #       Internally used Data Containers        #
        #       (not formal model elements)            #
        ################################################

        self.process_inputs: t.ProcessInputsDict = {}
        self.process_outputs: t.ProcessOutputsDict = {}
        self.process_loans: t.ProcessLoansDict = {}
        self.active_flow_rpsditvo: t.ActiveFlowSet = set()
        """a flow index for techs NOT in tech_annual"""

        self.active_flow_rpitvo: t.ActiveFlowAnnualSet = set()
        """a flow index for techs in tech_annual only"""

        self.active_flex_rpsditvo: t.ActiveFlexSet = set()
        self.active_flex_rpitvo: t.ActiveFlexAnnualSet = set()
        self.active_flow_in_storage_rpsditvo: t.ActiveFlowInStorageSet = set()
        self.active_curtailment_rpsditvo: t.ActiveCurtailmentSet = set()
        self.active_activity_rptv: t.ActiveActivitySet = set()
        self.storage_level_indices_rpsdtv: t.StorageLevelIndicesSet = set()
        self.seasonal_storage_level_indices_rpstv: t.SeasonalStorageLevelIndicesSet = set()
        """
        currently available (within lifespan) (r, p, t, v) tuples (from model.process_vintages)
        """

        self.active_regions_for_tech: t.ActiveRegionsForTechDict = {}
        """currently available regions by period and tech {(p, t) : r}"""

        self.new_capacity_rtv: t.NewCapacitySet = set()
        self.active_capacity_available_rpt: t.ActiveCapacityAvailableSet = set()
        self.active_capacity_available_rptv: t.ActiveCapacityAvailableVintageSet = set()
        self.group_region_active_flow_rpt: t.GroupRegionActiveFlowSet = (
            set()  # Set of valid group-region, period, tech indices
        )
        self.commodity_balance_rpc: t.CommodityBalancedSet = (
            set()
        )  # Set of valid region-period-commodity indices to balance
        # The downstream process of a commodity during a period
        self.commodity_down_stream_process: t.CommodityStreamProcessDict = {}
        # The upstream process of a commodity during a period
        self.commodity_up_stream_process: t.CommodityStreamProcessDict = {}
        # New capacity consuming a commodity during a period [r,p,c] -> t
        self.capacity_consumption_techs: t.CapacityConsumptionTechsDict = {}
        # Retired capacity producing a commodity during a period [r,p,c] -> t,v
        self.retirement_production_processes: t.RetirementProductionProcessesDict = {}
        self.process_inputs_by_output: t.ProcessInputsByOutputDict = {}
        self.process_outputs_by_input: t.ProcessOutputsByInputDict = {}
        self.process_techs: t.ProcessTechsDict = {}
        self.process_reserve_periods: t.ProcessReservePeriodsDict = {}
        self.process_periods: t.ProcessPeriodsDict = {}  # {(r, t, v): set(p)}
        # {(r, t, v): set(p)} periods in which a process can economically or naturally retire
        self.retirement_periods: t.RetirementPeriodsDict = {}
        self.process_vintages: t.ProcessVintagesDict = {}
        # {(r, t, v): set(p)} periods for which the process has a defined survival fraction
        self.survival_curve_periods: t.SurvivalCurvePeriodsDict = {}
        """current available (within lifespan) vintages {(r, p, t) : set(v)}"""

        self.baseload_vintages: t.BaseloadVintagesDict = {}
        self.curtailment_vintages: t.CurtailmentVintagesDict = {}
        self.storage_vintages: t.StorageVintagesDict = {}
        self.ramp_up_vintages: t.RampUpVintagesDict = {}
        self.ramp_down_vintages: t.RampDownVintagesDict = {}
        self.input_split_vintages: t.InputSplitVintagesDict = {}
        self.input_split_annual_vintages: t.InputSplitAnnualVintagesDict = {}
        self.output_split_vintages: t.OutputSplitVintagesDict = {}
        self.output_split_annual_vintages: t.OutputSplitAnnualVintagesDict = {}
        # M.processByPeriodAndOutput = {} # not currently used
        self.export_regions: t.ExportRegionsDict = {}
        self.import_regions: t.ImportRegionsDict = {}

        # These establish time sequencing
        # {(p, s, d): (s_next, d_next)} sequence of following time slices
        self.time_next: t.TimeNextDict = {}
        # {(p, s_seq): (s_seq_next)} next virtual storage season
        self.time_next_sequential: t.TimeNextSequentialDict = {}
        # {(p, s_seq): (s)} season matching this virtual storage season
        self.sequential_to_season: t.SequentialToSeasonDict = {}

        ################################################
        #             Switching Sets                   #
        #  (to avoid slow searches in initialisation)  #
        ################################################

        # {(r, p, i, t, v, o): bool} which efficiencies have variable indexing
        self.is_efficiency_variable: t.EfficiencyVariableDict = {}
        # {(r, p, t, v): bool} which capacity factors have have period-vintage indexing
        self.is_capacity_factor_process: t.CapacityFactorProcessDict = {}
        # {t: bool} whether a storage tech is seasonal storage
        self.is_seasonal_storage: t.SeasonalStorageDict = {}
        # {(r, t, v): bool} whether a process uses survival curves.
        self.is_survival_curve_process: t.SurvivalCurveProcessDict = {}

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
        self.time_season_all = Set(ordered=True, validate=no_slash_or_pipe)
        self.time_season_to_sequential = Set(ordered=True, validate=no_slash_or_pipe)
        self.time_season = Set(self.time_optimize, within=self.time_season_all, ordered=True)
        self.time_of_day = Set(ordered=True, validate=no_slash_or_pipe)

        # This is just to get the TimeStorageSeason table sequentially.
        # There must be a better way but this works for now
        self.ordered_season_sequential = Set(
            dimen=3,
            within=self.time_optimize * self.time_season_to_sequential * self.time_season_all,
            ordered=True,
        )

        # Define regions
        self.regions = Set(validate=region_check)
        # regional_indices is the set of all the possible combinations of interregional exchanges
        # plus original region indices. If tech_exchange is empty, RegionalIndices =regions.
        self.regional_indices = Set(initialize=geography.create_regional_indices)
        self.regional_global_indices = Set(validate=region_group_check)

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
        """ track techs used in efficiency table used in create_sparse_dicts """

        # the below is a convenience for domain checking in params below that should not accept
        # uncap techs...
        self.tech_with_capacity = Set(initialize=self.tech_all - self.tech_uncap)
        """techs eligible for capacitization"""
        # Define techs for which economic retirement is an option
        # Note:  Storage techs cannot (currently) be retired due to linkage to initialization
        #        process, which is currently incapable of reducing initializations on retirements.
        # Note2: I think this has been fixed but I can't tell what the problem was. Suspect
        #        it was the old storage_init constraint
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

        self.global_discount_rate = Param(default=0.05)

        # Define time-related parameters
        self.period_length = Param(self.time_optimize, initialize=time.param_period_length)
        self.segment_fraction = Param(self.time_optimize, self.time_season_all, self.time_of_day)
        self.validate_segment_fraction = BuildAction(rule=time.validate_segment_fraction)
        self.time_sequencing = Set()  # How do states carry between time segments?
        self.time_manual = Set(
            ordered=True
        )  # This is just to get data from the table. Hidden feature and usually not used
        self.validate_time_next = BuildAction(rule=time.validate_time_manual)

        # Define demand- and resource-related parameters
        # Dev Note:  There does not appear to be a DB table supporting DemandDefaultDistro.
        #            This does not cause any problems, so let it be for now.
        #            Doesn't seem to be much point in the table. Just clones segment_fraction
        # M.DemandDefaultDistribution = Param(
        #     M.time_optimize, M.time_season, M.time_of_day, mutable=True
        # )
        self.demand_specific_distribution = Param(
            self.regions,
            self.time_optimize,
            self.time_season_all,
            self.time_of_day,
            self.commodity_demand,
            mutable=True,
            default=0,
        )

        self.demand_constraint_rpc = Set(
            within=self.regions * self.time_optimize * self.commodity_demand
        )
        self.demand = Param(self.demand_constraint_rpc)

        # Dev Note:  This parameter is currently NOT implemented.  Preserved for later refactoring
        # limit_resource IS implemented but sums cumulatively for a technology rather than
        # resource commodity
        # M.ResourceConstraint_rpr = Set(within=M.regions * M.time_optimize * M.commodity_physical)
        # M.resource_bound = Param(M.ResourceConstraint_rpr)

        # Define technology performance parameters
        self.capacity_to_activity = Param(self.regional_indices, self.tech_all, default=1)

        self.existing_capacity = Param(self.regional_indices, self.tech_exist, self.vintage_exist)

        # Dev Note:  The below is temporarily useful for passing down to validator to find
        # set violations
        #            Uncomment this assignment, and comment out the orig below it...
        # M.efficiency = Param(
        #     Any, Any, Any, Any, Any,
        #     within=NonNegativeReals, validate=validate_efficiency
        # )

        # devnote: need these here or CheckefficiencyIndices may flag these commodities as unused
        self.construction_input = Param(
            self.regions,
            self.commodity_physical,
            self.tech_with_capacity,
            self.vintage_optimize,
        )
        self.end_of_life_output = Param(
            self.regions, self.tech_with_capacity, self.vintage_all, self.commodity_carrier
        )

        self.efficiency = Param(
            self.regional_indices,
            self.commodity_physical,
            self.tech_all,
            self.vintage_all,
            self.commodity_carrier,
            within=NonNegativeReals,
            validate=validate_efficiency,
        )
        self.validate_used_efficiency_indices = BuildAction(
            rule=technology.check_efficiency_indices
        )

        self.efficiency_variable = Param(
            self.regional_indices,
            self.time_optimize,
            self.time_season_all,
            self.time_of_day,
            self.commodity_physical,
            self.tech_all,
            self.vintage_all,
            self.commodity_carrier,
            within=NonNegativeReals,
            default=1,
        )

        self.lifetime_tech = Param(
            self.regional_indices, self.tech_all, default=TemoaModel.default_lifetime_tech
        )

        self.lifetime_process_rtv = Set(dimen=3, initialize=technology.lifetime_process_indices)
        self.lifetime_process = Param(
            self.lifetime_process_rtv, default=technology.get_default_process_lifetime
        )

        self.lifetime_survival_curve = Param(
            self.regional_indices,
            Integers,
            self.tech_all,
            self.vintage_all,
            default=technology.get_default_survival,
            validate=validate_0to1,
            mutable=True,
        )
        self.create_survival_curve = BuildAction(rule=technology.create_survival_curve)

        self.loan_lifetime_process_rtv = Set(
            dimen=3, initialize=costs.lifetime_loan_process_indices
        )

        # Dev Note:  The loan_lifetime_process table *could* be removed.  There is no longer a
        #            supporting table in the database.  It is just a "passthrough" now to the
        #            default loan_lifetime_tech. It is already stitched in to the model,
        #            so will leave it for now.  Table may be revived.

        self.loan_lifetime_process = Param(
            self.loan_lifetime_process_rtv, default=costs.get_loan_life
        )

        self.limit_tech_input_split = Param(
            self.regions,
            self.time_optimize,
            self.commodity_physical,
            self.tech_all,
            self.operator,
            validate=validate_0to1,
        )
        self.limit_tech_input_split_annual = Param(
            self.regions,
            self.time_optimize,
            self.commodity_physical,
            self.tech_all,
            self.operator,
            validate=validate_0to1,
        )

        self.limit_tech_output_split = Param(
            self.regions,
            self.time_optimize,
            self.tech_all,
            self.commodity_carrier,
            self.operator,
            validate=validate_0to1,
        )
        self.limit_tech_output_split_annual = Param(
            self.regions,
            self.time_optimize,
            self.tech_all,
            self.commodity_carrier,
            self.operator,
            validate=validate_0to1,
        )

        self.renewable_portfolio_standard_constraint_rpg = Set(
            within=self.regions * self.time_optimize * self.tech_group_names
        )
        self.renewable_portfolio_standard = Param(
            self.renewable_portfolio_standard_constraint_rpg, validate=validate_0to1
        )

        # These need to come before validate_season_sequential
        self.ramp_up_hourly = Param(self.regions, self.tech_upramping, validate=validate_0to1)
        self.ramp_down_hourly = Param(self.regions, self.tech_downramping, validate=validate_0to1)

        # Set up representation of time
        self.days_per_period = Param()
        self.segment_fraction_per_season = Param(
            self.time_optimize,
            self.time_season_all,
            initialize=time.segment_fraction_per_season_rule,
        )
        self.time_season_sequential = Param(
            self.time_optimize, self.time_season_to_sequential, self.time_season_all, mutable=True
        )
        self.validate_season_sequential = BuildAction(rule=time.create_time_season_to_sequential)
        self.create_time_sequence = BuildAction(rule=time.create_time_sequence)

        # The method below creates a series of helper functions that are used to
        # perform the sparse matrix of indexing for the parameters, variables, and
        # equations below.
        self.create_sparse_dicts = BuildAction(rule=create_sparse_dicts)
        self.initialize_demands = BuildAction(rule=commodities.create_demands)

        self.capacity_factor_rpsdt = Set(dimen=5, initialize=capacity.capacity_factor_tech_indices)
        self.capacity_factor_tech = Param(
            self.capacity_factor_rpsdt, default=1, validate=validate_0to1
        )

        # Dev note:  using a default function below alleviates need to make this set.
        # M.CapacityFactor_rsdtv = Set(dimen=5, initialize=capacity_factor_processIndices)
        self.capacity_factor_process = Param(
            self.regional_indices,
            self.time_optimize,
            self.time_season_all,
            self.time_of_day,
            self.tech_with_capacity,
            self.vintage_all,
            # validate=validate_capacity_factor_process,
            # opting for a quicker validation, just 0->1
            validate=validate_0to1,
            # slow but only called if a value is missing
            default=capacity.get_default_capacity_factor,
        )

        self.capacity_constraint_rpsdtv = Set(
            dimen=6, initialize=capacity.capacity_constraint_indices
        )
        self.initialize_CapacityFactors = BuildAction(rule=capacity.check_capacity_factor_process)
        self.initialize_efficiency_variable = BuildAction(rule=technology.check_efficiency_variable)

        # Define technology cost parameters
        # dev note:  the cost_fixed_rptv isn't truly needed, but it is included in a constraint, so
        #            let it go for now
        self.cost_fixed_rptv = Set(dimen=4, initialize=costs.cost_fixed_indices)
        self.cost_fixed = Param(self.cost_fixed_rptv)

        self.cost_invest_rtv = Set(
            within=self.regional_indices * self.tech_all * self.time_optimize
        )
        self.cost_invest = Param(self.cost_invest_rtv)

        self.default_loan_rate = Param(domain=NonNegativeReals)
        self.loan_rate = Param(
            self.cost_invest_rtv, domain=NonNegativeReals, default=costs.get_default_loan_rate
        )
        self.loan_annualize = Param(
            self.cost_invest_rtv, initialize=costs.param_loan_annualize_rule
        )

        self.cost_variable_rptv = Set(dimen=4, initialize=costs.cost_variable_indices)
        self.cost_variable = Param(self.cost_variable_rptv)

        self.cost_emission_rpe = Set(
            within=self.regions * self.time_optimize * self.commodity_emissions
        )
        self.cost_emission = Param(self.cost_emission_rpe)

        self.process_life_frac_rptv = Set(dimen=4, initialize=technology.model_process_life_indices)
        self.process_life_frac = Param(
            self.process_life_frac_rptv, initialize=technology.param_process_life_fraction_rule
        )

        self.limit_capacity_constraint_rpt = Set(
            within=self.regional_global_indices
            * self.time_optimize
            * self.tech_or_group
            * self.operator
        )
        self.limit_capacity = Param(self.limit_capacity_constraint_rpt)

        self.limit_new_capacity_constraint_rpt = Set(
            within=self.regional_global_indices
            * self.time_optimize
            * self.tech_or_group
            * self.operator
        )
        self.limit_new_capacity = Param(self.limit_new_capacity_constraint_rpt)

        self.limit_resource_constraint_rt = Set(
            within=self.regional_global_indices * self.tech_or_group * self.operator
        )
        self.limit_resource = Param(self.limit_resource_constraint_rt)

        self.limit_activity_constraint_rpt = Set(
            within=self.regional_global_indices
            * self.time_optimize
            * self.tech_or_group
            * self.operator
        )
        self.limit_activity = Param(self.limit_activity_constraint_rpt)

        self.limit_seasonal_capacity_factor_constraint_rpst = Set(
            within=self.regional_global_indices
            * self.time_optimize
            * self.time_season_all
            * self.tech_all
            * self.operator
        )
        self.limit_seasonal_capacity_factor = Param(
            self.limit_seasonal_capacity_factor_constraint_rpst, validate=validate_0to1
        )

        self.limit_annual_capacity_factor_constraint_rpto = Set(
            within=self.regional_global_indices
            * self.time_optimize
            * self.tech_all
            * self.commodity_carrier
            * self.operator
        )
        self.limit_annual_capacity_factor = Param(
            self.limit_annual_capacity_factor_constraint_rpto, validate=validate_0to1
        )

        self.limit_growth_capacity = Param(
            self.regional_global_indices, self.tech_or_group, self.operator
        )
        self.limit_degrowth_capacity = Param(
            self.regional_global_indices, self.tech_or_group, self.operator
        )
        self.limit_growth_new_capacity = Param(
            self.regional_global_indices, self.tech_or_group, self.operator
        )
        self.limit_degrowth_new_capacity = Param(
            self.regional_global_indices, self.tech_or_group, self.operator
        )
        self.limit_growth_new_capacity_delta = Param(
            self.regional_global_indices, self.tech_or_group, self.operator
        )
        self.limit_degrowth_new_capacity_delta = Param(
            self.regional_global_indices, self.tech_or_group, self.operator
        )

        self.limit_emission_constraint_rpe = Set(
            within=self.regional_global_indices
            * self.time_optimize
            * self.commodity_emissions
            * self.operator
        )
        self.limit_emission = Param(self.limit_emission_constraint_rpe)
        self.emission_activity_reitvo = Set(dimen=6, initialize=emissions.emission_activity_indices)
        self.emission_activity = Param(self.emission_activity_reitvo)

        self.limit_capacity_share_constraint_rpgg = Set(
            within=self.regional_global_indices
            * self.time_optimize
            * self.tech_or_group
            * self.tech_or_group
            * self.operator
        )
        self.limit_capacity_share = Param(self.limit_capacity_share_constraint_rpgg)

        self.limit_activity_share_constraint_rpgg = Set(
            within=self.regional_global_indices
            * self.time_optimize
            * self.tech_or_group
            * self.tech_or_group
            * self.operator
        )
        self.limit_activity_share = Param(self.limit_activity_share_constraint_rpgg)

        self.limit_new_capacity_share_constraint_rpgg = Set(
            within=self.regional_global_indices
            * self.time_optimize
            * self.tech_or_group
            * self.tech_or_group
            * self.operator
        )
        self.limit_new_capacity_share = Param(self.limit_new_capacity_share_constraint_rpgg)

        # This set works for all storage-related constraints
        self.storage_constraints_rpsdtv = Set(
            dimen=6, initialize=storage.storage_constraint_indices
        )
        self.seasonal_storage_constraints_rpsdtv = Set(
            dimen=6, initialize=storage.seasonal_storage_constraint_indices
        )
        self.limit_storage_fraction_constraint_rpsdtv = Set(
            within=(self.storage_constraints_rpsdtv | self.seasonal_storage_constraints_rpsdtv)
            * self.operator
        )
        self.limit_storage_fraction = Param(
            self.limit_storage_fraction_constraint_rpsdtv, validate=validate_0to1
        )

        # Storage duration is expressed in hours
        self.storage_duration = Param(self.regions, self.tech_storage, default=4)

        self.linked_techs = Param(self.regional_indices, self.tech_all, self.commodity_emissions)

        # Define parameters associated with electric sector operation
        self.reserve_margin_method = Set()  # How contributions to the reserve margin are calculated
        self.capacity_credit = Param(
            self.regional_indices,
            self.time_optimize,
            self.tech_reserve,
            self.vintage_all,
            default=0,
            validate=validate_0to1,
        )
        self.reserve_capacity_derate = Param(
            self.regional_indices,
            self.time_optimize,
            self.time_season_all,
            self.tech_reserve,
            self.vintage_all,
            default=1,
            validate=validate_0to1,
        )
        self.planning_reserve_margin = Param(self.regions)

        self.emission_embodied = Param(
            self.regions,
            self.commodity_emissions,
            self.tech_with_capacity,
            self.vintage_optimize,
        )
        self.emission_end_of_life = Param(
            self.regions, self.commodity_emissions, self.tech_with_capacity, self.vintage_all
        )

        self.myopic_discounting_year = Param(default=0)

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
        self.flow_var_rpsditvo = Set(dimen=8, initialize=flows.flow_variable_indices)
        self.v_flow_out = Var(self.flow_var_rpsditvo, domain=NonNegativeReals)

        self.flow_var_annual_rpitvo = Set(dimen=6, initialize=flows.flow_variable_annual_indices)
        self.v_flow_out_annual = Var(self.flow_var_annual_rpitvo, domain=NonNegativeReals)

        self.flex_var_rpsditvo = Set(dimen=8, initialize=flows.flex_variable_indices)
        self.v_flex = Var(self.flex_var_rpsditvo, domain=NonNegativeReals)

        self.flex_var_annual_rpitvo = Set(dimen=6, initialize=flows.flex_variable_annual_indices)
        self.v_flex_annual = Var(self.flex_var_annual_rpitvo, domain=NonNegativeReals)

        self.curtailment_var_rpsditvo = Set(dimen=8, initialize=flows.curtailment_variable_indices)
        self.v_curtailment = Var(
            self.curtailment_var_rpsditvo, domain=NonNegativeReals, initialize=0
        )

        self.flow_in_storage_rpsditvo = Set(
            dimen=8, initialize=flows.flow_in_storage_variable_indices
        )
        self.v_flow_in = Var(self.flow_in_storage_rpsditvo, domain=NonNegativeReals)

        self.storage_level_rpsdtv = Set(dimen=6, initialize=storage.storage_level_variable_indices)
        self.v_storage_level = Var(self.storage_level_rpsdtv, domain=NonNegativeReals)

        self.seasonal_storage_level_rpstv = Set(
            dimen=5, initialize=storage.seasonal_storage_level_variable_indices
        )
        self.v_seasonal_storage_level = Var(
            self.seasonal_storage_level_rpstv, domain=NonNegativeReals
        )

        # Derived decision variables
        self.capacity_var_rptv = Set(dimen=4, initialize=costs.cost_fixed_indices)
        self.v_capacity = Var(self.capacity_var_rptv, domain=NonNegativeReals)

        self.new_capacity_var_rtv = Set(dimen=3, initialize=capacity.capacity_variable_indices)
        self.v_new_capacity = Var(self.new_capacity_var_rtv, domain=NonNegativeReals, initialize=0)

        self.retired_capacity_var_rptv = Set(
            dimen=4, initialize=capacity.retired_capacity_variable_indices
        )
        self.v_retired_capacity = Var(
            self.retired_capacity_var_rptv, domain=NonNegativeReals, initialize=0
        )

        self.annual_retirement_var_rptv = Set(
            dimen=4, initialize=capacity.annual_retirement_variable_indices
        )
        self.v_annual_retirement = Var(
            self.annual_retirement_var_rptv, domain=NonNegativeReals, initialize=0
        )

        self.capacity_available_var_rpt = Set(
            dimen=3, initialize=capacity.capacity_available_variable_indices
        )
        self.v_capacity_available_by_period_and_tech = Var(
            self.capacity_available_var_rpt, domain=NonNegativeReals, initialize=0
        )

        ################################################
        #              Objective Function              #
        #             (minimize total cost)            #
        ################################################

        self.total_cost = Objective(rule=costs.total_cost_rule, sense=minimize)

        ################################################
        #                   Constraints                #
        #                                              #
        ################################################

        self.progress_marker_4 = BuildAction(['Starting to build Constraints'], rule=progress_check)

        # Declare constraints to calculate derived decision variables
        self.capacity_constraint = Constraint(
            self.capacity_constraint_rpsdtv, rule=capacity.capacity_constraint
        )

        self.capacity_annual_constraint_rptv = Set(
            dimen=4, initialize=capacity.capacity_annual_constraint_indices
        )
        self.capacity_annual_constraint = Constraint(
            self.capacity_annual_constraint_rptv, rule=capacity.capacity_annual_constraint
        )

        self.capacity_available_by_period_and_tech_constraint = Constraint(
            self.capacity_available_var_rpt,
            rule=capacity.capacity_available_by_period_and_tech_constraint,
        )

        # devnote: I think this constraint is redundant
        # M.Retiredcapacity_constraint = Constraint(
        #     M.retired_capacity_var_rptv, rule=RetiredCapacity_constraint
        # )
        self.progress_marker_4a = BuildAction(
            ['Starting annual_retirement_constraint'], rule=progress_check
        )
        self.annual_retirement_constraint = Constraint(
            self.annual_retirement_var_rptv, rule=capacity.annual_retirement_constraint
        )
        self.progress_marker_4b = BuildAction(
            ['Starting adjusted_capacity_constraint'], rule=progress_check
        )
        self.adjusted_capacity_constraint = Constraint(
            self.cost_fixed_rptv, rule=capacity.adjusted_capacity_constraint
        )
        self.progress_marker_5 = BuildAction(['Finished Capacity Constraints'], rule=progress_check)

        # Declare core model constraints that ensure proper system functioning
        # In driving order, starting with the need to meet end-use demands

        self.demand_constraint = Constraint(
            self.demand_constraint_rpc, rule=commodities.demand_constraint
        )

        # devnote: testing a workaround
        self.demand_activity_constraint_rpsdtv_dem = Set(
            dimen=7, initialize=commodities.demand_activity_constraint_indices
        )
        self.demand_activity_constraint = Constraint(
            self.demand_activity_constraint_rpsdtv_dem, rule=commodities.demand_activity_constraint
        )

        self.commodity_balance_constraint_rpsdc = Set(
            dimen=5, initialize=commodities.commodity_balance_constraint_indices
        )
        self.commodity_balance_constraint = Constraint(
            self.commodity_balance_constraint_rpsdc, rule=commodities.commodity_balance_constraint
        )

        self.annual_commodity_balance_constraint_rpc = Set(
            dimen=3, initialize=commodities.annual_commodity_balance_constraint_indices
        )
        self.annual_commodity_balance_constraint = Constraint(
            self.annual_commodity_balance_constraint_rpc,
            rule=commodities.annual_commodity_balance_constraint,
        )

        # M.ResourceExtractionConstraint = Constraint(
        #     M.ResourceConstraint_rpr, rule=ResourceExtraction_constraint
        # )

        self.baseload_diurnal_constraint_rpsdtv = Set(
            dimen=6, initialize=operations.baseload_diurnal_constraint_indices
        )
        self.baseload_diurnal_constraint = Constraint(
            self.baseload_diurnal_constraint_rpsdtv, rule=operations.baseload_diurnal_constraint
        )

        self.regional_exchange_capacity_constraint_rrptv = Set(
            dimen=5, initialize=capacity.regional_exchange_capacity_constraint_indices
        )
        self.regional_exchange_capacity_constraint = Constraint(
            self.regional_exchange_capacity_constraint_rrptv,
            rule=geography.regional_exchange_capacity_constraint,
        )

        self.progress_marker_6 = BuildAction(['Starting Storage Constraints'], rule=progress_check)

        self.storage_energy_constraint = Constraint(
            self.storage_constraints_rpsdtv, rule=storage.storage_energy_constraint
        )

        self.storage_energy_upper_bound_constraint = Constraint(
            self.storage_constraints_rpsdtv, rule=storage.storage_energy_upper_bound_constraint
        )

        self.seasonal_storage_energy_constraint = Constraint(
            self.seasonal_storage_level_rpstv, rule=storage.seasonal_storage_energy_constraint
        )

        self.seasonal_storage_energy_upper_bound_constraint = Constraint(
            self.seasonal_storage_constraints_rpsdtv,
            rule=storage.seasonal_storage_energy_upper_bound_constraint,
        )

        self.storage_charge_rate_constraint = Constraint(
            self.storage_constraints_rpsdtv, rule=storage.storage_charge_rate_constraint
        )

        self.storage_discharge_rate_constraint = Constraint(
            self.storage_constraints_rpsdtv, rule=storage.storage_discharge_rate_constraint
        )

        self.storage_throughput_constraint = Constraint(
            self.storage_constraints_rpsdtv, rule=storage.storage_throughput_constraint
        )

        self.limit_storage_fraction_constraint = Constraint(
            self.limit_storage_fraction_constraint_rpsdtv,
            rule=storage.limit_storage_fraction_constraint,
        )

        self.ramp_up_day_constraint_rpsdtv = Set(
            dimen=6, initialize=operations.ramp_up_day_constraint_indices
        )
        self.ramp_up_day_constraint = Constraint(
            self.ramp_up_day_constraint_rpsdtv, rule=operations.ramp_up_day_constraint
        )
        self.ramp_down_day_constraint_rpsdtv = Set(
            dimen=6, initialize=operations.ramp_down_day_constraint_indices
        )
        self.ramp_down_day_constraint = Constraint(
            self.ramp_down_day_constraint_rpsdtv, rule=operations.ramp_down_day_constraint
        )

        self.ramp_up_season_constraint_rpsstv = Set(
            dimen=6, initialize=operations.ramp_up_season_constraint_indices
        )
        self.ramp_up_season_constraint = Constraint(
            self.ramp_up_season_constraint_rpsstv, rule=operations.ramp_up_season_constraint
        )
        self.ramp_down_season_constraint_rpsstv = Set(
            dimen=6, initialize=operations.ramp_down_season_constraint_indices
        )
        self.ramp_down_season_constraint = Constraint(
            self.ramp_down_season_constraint_rpsstv, rule=operations.ramp_down_season_constraint
        )

        self.reserve_margin_rpsd = Set(dimen=4, initialize=reserves.reserve_margin_indices)
        self.validate_reserve_margin = BuildAction(rule=validate_reserve_margin)
        self.reserve_margin_constraint = Constraint(
            self.reserve_margin_rpsd, rule=reserves.reserve_margin_constraint
        )

        self.limit_emission_constraint = Constraint(
            self.limit_emission_constraint_rpe, rule=limits.limit_emission_constraint
        )
        self.progress_marker_7 = BuildAction(
            ['Starting LimitGrowth and Activity Constraints'], rule=progress_check
        )

        self.limit_growth_capacity_constraint_rpt = Set(
            dimen=4, initialize=limits.limit_growth_capacity_indices
        )
        self.limit_growth_capacity_constraint = Constraint(
            self.limit_growth_capacity_constraint_rpt,
            rule=limits.limit_growth_capacity_constraint_rule,
        )
        self.limit_degrowth_capacity_constraint_rpt = Set(
            dimen=4, initialize=limits.limit_degrowth_capacity_indices
        )
        self.limit_degrowth_capacity_constraint = Constraint(
            self.limit_degrowth_capacity_constraint_rpt,
            rule=limits.limit_degrowth_capacity_constraint_rule,
        )

        self.limit_growth_new_capacity_constraint_rpt = Set(
            dimen=4, initialize=limits.limit_growth_new_capacity_indices
        )
        self.limit_growth_new_capacity_constraint = Constraint(
            self.limit_growth_new_capacity_constraint_rpt,
            rule=limits.limit_growth_new_capacity_constraint_rule,
        )
        self.limit_degrowth_new_capacity_constraint_rpt = Set(
            dimen=4, initialize=limits.limit_degrowth_new_capacity_indices
        )
        self.limit_degrowth_new_capacity_constraint = Constraint(
            self.limit_degrowth_new_capacity_constraint_rpt,
            rule=limits.limit_degrowth_new_capacity_constraint_rule,
        )

        self.limit_growth_new_capacity_delta_constraint_rpt = Set(
            dimen=4, initialize=limits.limit_growth_new_capacity_delta_indices
        )
        self.limit_growth_new_capacity_delta_constraint = Constraint(
            self.limit_growth_new_capacity_delta_constraint_rpt,
            rule=limits.limit_growth_new_capacity_delta_constraint_rule,
        )
        self.limit_degrowth_new_capacity_delta_constraint_rpt = Set(
            dimen=4, initialize=limits.limit_degrowth_new_capacity_delta_indices
        )
        self.limit_degrowth_new_capacity_delta_constraint = Constraint(
            self.limit_degrowth_new_capacity_delta_constraint_rpt,
            rule=limits.limit_degrowth_new_capacity_delta_constraint_rule,
        )

        self.limit_activity_constraint = Constraint(
            self.limit_activity_constraint_rpt, rule=limits.limit_activity_constraint
        )

        self.limit_seasonal_capacity_factor_constraint = Constraint(
            self.limit_seasonal_capacity_factor_constraint_rpst,
            rule=limits.limit_seasonal_capacity_factor_constraint,
        )

        self.limit_capacity_constraint = Constraint(
            self.limit_capacity_constraint_rpt, rule=limits.limit_capacity_constraint
        )

        self.limit_new_capacity_constraint = Constraint(
            self.limit_new_capacity_constraint_rpt, rule=limits.limit_new_capacity_constraint
        )

        self.limit_capacity_share_constraint = Constraint(
            self.limit_capacity_share_constraint_rpgg, rule=limits.limit_capacity_share_constraint
        )

        self.limit_activity_share_constraint = Constraint(
            self.limit_activity_share_constraint_rpgg, rule=limits.limit_activity_share_constraint
        )

        self.limit_new_capacity_share_constraint = Constraint(
            self.limit_new_capacity_share_constraint_rpgg,
            rule=limits.limit_new_capacity_share_constraint,
        )

        self.progress_marker_8 = BuildAction(
            ['Starting Limit Capacity and Tech Split Constraints'], rule=progress_check
        )

        self.limit_resource_constraint = Constraint(
            self.limit_resource_constraint_rt, rule=limits.limit_resource_constraint
        )

        self.limit_annual_capacity_factor_constraint = Constraint(
            self.limit_annual_capacity_factor_constraint_rpto,
            rule=limits.limit_annual_capacity_factor_constraint,
        )

        ## Tech input splits
        self.limit_tech_input_split_constraint_rpsditv = Set(
            dimen=8, initialize=limits.limit_tech_input_split_constraint_indices
        )
        self.limit_tech_input_split_constraint = Constraint(
            self.limit_tech_input_split_constraint_rpsditv,
            rule=limits.limit_tech_input_split_constraint,
        )

        self.limit_tech_input_split_annual_constraint_rpitv = Set(
            dimen=6, initialize=limits.limit_tech_input_split_annual_constraint_indices
        )
        self.limit_tech_input_split_annual_constraint = Constraint(
            self.limit_tech_input_split_annual_constraint_rpitv,
            rule=limits.limit_tech_input_split_annual_constraint,
        )

        self.limit_tech_input_split_average_constraint_rpitv = Set(
            dimen=6, initialize=limits.limit_tech_input_split_average_constraint_indices
        )
        self.limit_tech_input_split_average_constraint = Constraint(
            self.limit_tech_input_split_average_constraint_rpitv,
            rule=limits.limit_tech_input_split_average_constraint,
        )

        ## Tech output splits
        self.limit_tech_output_split_constraint_rpsdtvo = Set(
            dimen=8, initialize=limits.limit_tech_output_split_constraint_indices
        )
        self.limit_tech_output_split_constraint = Constraint(
            self.limit_tech_output_split_constraint_rpsdtvo,
            rule=limits.limit_tech_output_split_constraint,
        )

        self.limit_tech_output_split_annual_constraint_rptvo = Set(
            dimen=6, initialize=limits.limit_tech_output_split_annual_constraint_indices
        )
        self.limit_tech_output_split_annual_constraint = Constraint(
            self.limit_tech_output_split_annual_constraint_rptvo,
            rule=limits.limit_tech_output_split_annual_constraint,
        )

        self.limit_tech_output_split_average_constraint_rptvo = Set(
            dimen=6, initialize=limits.limit_tech_output_split_average_constraint_indices
        )
        self.limit_tech_output_split_average_constraint = Constraint(
            self.limit_tech_output_split_average_constraint_rptvo,
            rule=limits.limit_tech_output_split_average_constraint,
        )

        self.renewable_portfolio_standard_constraint = Constraint(
            self.renewable_portfolio_standard_constraint_rpg,
            rule=limits.renewable_portfolio_standard_constraint,
        )

        self.linked_emissions_tech_constraint_rpsdtve = Set(
            dimen=7, initialize=emissions.linked_tech_constraint_indices
        )
        # the validation requires that the set above be built first:
        self.validate_LinkedTech_lifetimes = BuildCheck(rule=validate_linked_tech)

        self.linked_emissions_tech_constraint = Constraint(
            self.linked_emissions_tech_constraint_rpsdtve,
            rule=emissions.linked_emissions_tech_constraint,
        )

        self.progress_marker_9 = BuildAction(['Finished Constraints'], rule=progress_check)


def progress_check(model: TemoaModel, checkpoint: str) -> None:
    """A quick widget which is called by BuildAction in order to log creation progress"""
    logger.debug('Model build progress: %s', checkpoint)
