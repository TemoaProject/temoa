# temoa/data_io/component_manifest.py
"""
Defines the data loading manifest for the Temoa model.

This module contains a single function, `build_manifest`, which constructs a
list of `LoadItem` objects. This list serves as the declarative configuration
for the `HybridLoader`, specifying every data component to be loaded from the
database into the Pyomo model.

The manifest is organized into logical groups that mirror the structure of the
Temoa model itself (e.g., Time, Regions, Technologies, Costs, Constraints).
This cohesive grouping makes it easier for developers to find and understand
how specific parts of the model are populated with data.

To add a new standard component to the model, a developer typically only needs
to add a new `LoadItem` to this manifest.
"""

from temoa.core.model import TemoaModel
from temoa.data_io.loader_manifest import LoadItem


def build_manifest(model: TemoaModel) -> list[LoadItem]:
    """
    Builds the manifest of all data components to be loaded into the Pyomo model.

    This declarative approach separates the configuration of what to load from the
    procedural logic of how to load it. The manifest is ordered logically to
    enhance readability and maintainability.

    Args:
        M: An instance of TemoaModel to link components.

    Returns:
        A list of LoadItem objects describing all data to be loaded.
    """
    manifest = [
        # =========================================================================
        # Core Model Structure (Regions, Techs, Commodities, Groups)
        # =========================================================================
        LoadItem(
            component=model.regions,
            table='Region',
            columns=['region'],
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.regionalGlobalIndices,
            table='meta_regional_groups',  # Placeholder, custom loader does the work
            columns=['region_or_group'],
            custom_loader_name='_load_regional_global_indices',
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.tech_production,
            table='Technology',
            columns=['tech'],
            where_clause="flag LIKE 'p%'",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_uncap,
            table='Technology',
            columns=['tech'],
            where_clause='unlim_cap > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.tech_baseload,
            table='Technology',
            columns=['tech'],
            where_clause="flag = 'pb'",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_storage,
            table='Technology',
            columns=['tech'],
            where_clause="flag = 'ps'",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_seasonal_storage,
            table='Technology',
            columns=['tech'],
            where_clause="flag = 'ps' AND seas_stor > 0",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_reserve,
            table='Technology',
            columns=['tech'],
            where_clause='reserve > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_curtailment,
            table='Technology',
            columns=['tech'],
            where_clause='curtail > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_flex,
            table='Technology',
            columns=['tech'],
            where_clause='flex > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_exchange,
            table='Technology',
            columns=['tech'],
            where_clause='exchange > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_annual,
            table='Technology',
            columns=['tech'],
            where_clause='annual > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_retirement,
            table='Technology',
            columns=['tech'],
            where_clause='retire > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_group_names,
            table='TechGroup',
            columns=['group_name'],
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.tech_group_members,
            table='TechGroupMember',
            columns=['group_name', 'tech'],
            custom_loader_name='_load_tech_group_members',
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.commodity_demand,
            table='Commodity',
            columns=['name'],
            where_clause="flag = 'd'",
            validator_name='viable_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.commodity_emissions,
            table='Commodity',
            columns=['name'],
            where_clause="flag = 'e'",
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.commodity_physical,
            table='Commodity',
            columns=['name'],
            where_clause="flag LIKE '%p%' OR flag = 's' OR flag LIKE '%a%'",
            validator_name='viable_input_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.commodity_source,
            table='Commodity',
            columns=['name'],
            where_clause="flag = 's'",
            validator_name='viable_input_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.commodity_annual,
            table='Commodity',
            columns=['name'],
            where_clause="flag LIKE '%a%'",
            validator_name='viable_input_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.commodity_waste,
            table='Commodity',
            columns=['name'],
            where_clause="flag LIKE '%w%'",
            validator_name='viable_output_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.operator,
            table='Operator',
            columns=['operator'],
            is_period_filtered=False,
            is_table_required=False,
        ),
        # =========================================================================
        # Time-Related Components
        # =========================================================================
        LoadItem(
            component=model.time_of_day,
            table='TimeOfDay',
            columns=['tod'],
            is_period_filtered=False,
            is_table_required=False,
            fallback_data=[('D',)],
        ),
        LoadItem(
            component=model.TimeSeason,
            table='TimeSeason',
            columns=['period', 'season'],
            custom_loader_name='_load_time_season',
            is_period_filtered=False,  # Custom loader handles myopic filtering
            is_table_required=False,
        ),
        LoadItem(
            component=model.TimeSeasonSequential,
            table='TimeSeasonSequential',
            columns=['period', 'seas_seq', 'season', 'num_days'],
            custom_loader_name='_load_time_season_sequential',
            is_table_required=False,
        ),
        LoadItem(
            component=model.SegFrac,
            table='TimeSegmentFraction',
            columns=['period', 'season', 'tod', 'segfrac'],
            custom_loader_name='_load_seg_frac',
            is_table_required=False,
        ),
        # =========================================================================
        # Capacity and Cost Components
        # =========================================================================
        LoadItem(
            component=model.ExistingCapacity,
            table='ExistingCapacity',
            columns=['region', 'tech', 'vintage', 'capacity'],
            custom_loader_name='_load_existing_capacity',
            is_period_filtered=False,  # Custom loader handles all logic
            is_table_required=False,
        ),
        LoadItem(
            component=model.CostInvest,
            table='CostInvest',
            columns=['region', 'tech', 'vintage', 'cost'],
            validator_name='viable_rtv',
            validation_map=(0, 1, 2),
            custom_loader_name='_load_cost_invest',
            is_period_filtered=False,  # Custom loader handles this
            is_table_required=False,
        ),
        LoadItem(
            component=model.CostFixed,
            table='CostFixed',
            columns=['region', 'period', 'tech', 'vintage', 'cost'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
        ),
        LoadItem(
            component=model.CostVariable,
            table='CostVariable',
            columns=['region', 'period', 'tech', 'vintage', 'cost'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
        ),
        LoadItem(
            component=model.CostEmission,
            table='CostEmission',
            columns=['region', 'period', 'emis_comm', 'cost'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.LoanRate,
            table='LoanRate',
            columns=['region', 'tech', 'vintage', 'rate'],
            validator_name='viable_rtv',
            validation_map=(0, 1, 2),
            custom_loader_name='_load_loan_rate',
            is_period_filtered=False,  # Custom loader handles this
            is_table_required=False,
        ),
        # =========================================================================
        # Singleton and Configuration-based Components
        # =========================================================================
        LoadItem(
            component=model.DaysPerPeriod,
            table='MetaData',
            columns=['value'],
            where_clause="element == 'days_per_period'",
            custom_loader_name='_load_days_per_period',
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.GlobalDiscountRate,
            table='MetaDataReal',
            columns=['value'],
            where_clause="element = 'global_discount_rate'",
            custom_loader_name='_load_global_discount_rate',
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.DefaultLoanRate,
            table='MetaDataReal',
            columns=['value'],
            where_clause="element = 'default_loan_rate'",
            custom_loader_name='_load_default_loan_rate',
            is_period_filtered=False,
            is_table_required=False,
        ),
        # =========================================================================
        # Operational Constraints and Parameters
        # =========================================================================
        LoadItem(
            component=model.Efficiency,
            table='meta_efficiency',  # Placeholder, custom loader does the work
            columns=[],
            custom_loader_name='_load_efficiency',
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.EfficiencyVariable,
            table='EfficiencyVariable',
            columns=[
                'region',
                'period',
                'season',
                'tod',
                'input_comm',
                'tech',
                'vintage',
                'output_comm',
                'efficiency',
            ],
            validator_name='viable_ritvo',
            validation_map=(0, 4, 5, 6, 7),
            is_table_required=False,
        ),
        LoadItem(
            component=model.Demand,
            table='Demand',
            columns=['region', 'period', 'commodity', 'demand'],
        ),
        LoadItem(
            component=model.DemandSpecificDistribution,
            table='DemandSpecificDistribution',
            columns=['region', 'period', 'season', 'tod', 'demand_name', 'dsd'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.CapacityToActivity,
            table='CapacityToActivity',
            columns=['region', 'tech', 'c2a'],
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.CapacityFactorTech,
            table='CapacityFactorTech',
            columns=['region', 'period', 'season', 'tod', 'tech', 'factor'],
            validator_name='viable_rt',
            validation_map=(0, 4),
            is_table_required=False,
        ),
        LoadItem(
            component=model.CapacityFactorProcess,
            table='CapacityFactorProcess',
            columns=['region', 'period', 'season', 'tod', 'tech', 'vintage', 'factor'],
            validator_name='viable_rtv',
            validation_map=(0, 4, 5),
            is_table_required=False,
        ),
        LoadItem(
            component=model.LifetimeTech,
            table='LifetimeTech',
            columns=['region', 'tech', 'lifetime'],
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.LifetimeProcess,
            table='LifetimeProcess',
            columns=['region', 'tech', 'vintage', 'lifetime'],
            validator_name='viable_rtv',
            validation_map=(0, 1, 2),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.LifetimeSurvivalCurve,
            table='LifetimeSurvivalCurve',
            columns=['region', 'period', 'tech', 'vintage', 'fraction'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.LoanLifetimeProcess,
            table='LoanLifetimeProcess',
            columns=['region', 'tech', 'vintage', 'lifetime'],
            validator_name='viable_rtv',
            validation_map=(0, 1, 2),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.RampUpHourly,
            table='RampUpHourly',
            columns=['region', 'tech', 'rate'],
            custom_loader_name='_load_ramping_up',
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.tech_upramping,
            table='RampUpHourly',
            columns=['tech'],
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.RampDownHourly,
            table='RampDownHourly',
            columns=['region', 'tech', 'rate'],
            custom_loader_name='_load_ramping_down',
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.tech_downramping,
            table='RampDownHourly',
            columns=['tech'],
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.RenewablePortfolioStandard,
            table='RPSRequirement',
            columns=['region', 'period', 'tech_group', 'requirement'],
            custom_loader_name='_load_rps_requirement',
            is_table_required=False,
        ),
        LoadItem(
            component=model.CapacityCredit,
            table='CapacityCredit',
            columns=['region', 'period', 'tech', 'vintage', 'credit'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
            is_table_required=False,
        ),
        LoadItem(
            component=model.ReserveCapacityDerate,
            table='ReserveCapacityDerate',
            columns=['region', 'period', 'season', 'tech', 'vintage', 'factor'],
            validator_name='viable_rtv',
            validation_map=(0, 3, 4),
            is_table_required=False,
        ),
        LoadItem(
            component=model.PlanningReserveMargin,
            table='PlanningReserveMargin',
            columns=['region', 'margin'],
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.StorageDuration,
            table='StorageDuration',
            columns=['region', 'tech', 'duration'],
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitStorageFraction,
            table='LimitStorageLevelFraction',
            columns=[
                'region',
                'period',
                'season',
                'tod',
                'tech',
                'vintage',
                'operator',
                'fraction',
            ],
            validator_name='viable_rtv',
            validation_map=(0, 4, 5),
            is_table_required=False,
        ),
        LoadItem(
            component=model.EmissionActivity,
            table='EmissionActivity',
            columns=[
                'region',
                'emis_comm',
                'input_comm',
                'tech',
                'vintage',
                'output_comm',
                'activity',
            ],
            validator_name='viable_ritvo',
            validation_map=(0, 2, 3, 4, 5),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.EmissionEmbodied,
            table='EmissionEmbodied',
            columns=['region', 'emis_comm', 'tech', 'vintage', 'value'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.EmissionEndOfLife,
            table='EmissionEndOfLife',
            columns=['region', 'emis_comm', 'tech', 'vintage', 'value'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.ConstructionInput,
            table='ConstructionInput',
            columns=['region', 'input_comm', 'tech', 'vintage', 'value'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.EndOfLifeOutput,
            table='EndOfLifeOutput',
            columns=['region', 'tech', 'vintage', 'output_comm', 'value'],
            validator_name='viable_rtv',
            validation_map=(0, 1, 2),
            is_period_filtered=False,
            is_table_required=False,
        ),
        # =========================================================================
        # Limit Constraints
        # =========================================================================
        LoadItem(
            component=model.LimitCapacity,
            table='LimitCapacity',
            columns=['region', 'period', 'tech_or_group', 'operator', 'capacity'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitNewCapacity,
            table='LimitNewCapacity',
            columns=['region', 'period', 'tech_or_group', 'operator', 'new_cap'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitCapacityShare,
            table='LimitCapacityShare',
            columns=['region', 'period', 'sub_group', 'super_group', 'operator', 'share'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitNewCapacityShare,
            table='LimitNewCapacityShare',
            columns=['region', 'period', 'sub_group', 'super_group', 'operator', 'share'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitActivity,
            table='LimitActivity',
            columns=['region', 'period', 'tech_or_group', 'operator', 'activity'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitActivityShare,
            table='LimitActivityShare',
            columns=['region', 'period', 'sub_group', 'super_group', 'operator', 'share'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitResource,
            table='LimitResource',
            columns=['region', 'tech_or_group', 'operator', 'cum_act'],
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitSeasonalCapacityFactor,
            table='LimitSeasonalCapacityFactor',
            columns=['region', 'period', 'season', 'tech', 'operator', 'factor'],
            validator_name='viable_rt',
            validation_map=(0, 3),
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitAnnualCapacityFactor,
            table='LimitAnnualCapacityFactor',
            columns=['region', 'period', 'tech', 'output_comm', 'operator', 'factor'],
            validator_name='viable_rpto',
            validation_map=(0, 1, 2, 3),
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitEmission,
            table='LimitEmission',
            columns=['region', 'period', 'emis_comm', 'operator', 'value'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitTechInputSplit,
            table='LimitTechInputSplit',
            columns=['region', 'period', 'input_comm', 'tech', 'operator', 'proportion'],
            validator_name='viable_rpit',
            validation_map=(0, 1, 2, 3),
            custom_loader_name='_load_limit_tech_input_split',
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitTechInputSplitAnnual,
            table='LimitTechInputSplitAnnual',
            columns=['region', 'period', 'input_comm', 'tech', 'operator', 'proportion'],
            validator_name='viable_rpit',
            validation_map=(0, 1, 2, 3),
            custom_loader_name='_load_limit_tech_input_split_annual',
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitTechOutputSplit,
            table='LimitTechOutputSplit',
            columns=['region', 'period', 'tech', 'output_comm', 'operator', 'proportion'],
            validator_name='viable_rpto',
            validation_map=(0, 1, 2, 3),
            custom_loader_name='_load_limit_tech_output_split',
            is_table_required=False,
        ),
        LoadItem(
            component=model.LimitTechOutputSplitAnnual,
            table='LimitTechOutputSplitAnnual',
            columns=['region', 'period', 'tech', 'output_comm', 'operator', 'proportion'],
            validator_name='viable_rpto',
            validation_map=(0, 1, 2, 3),
            custom_loader_name='_load_limit_tech_output_split_annual',
            is_table_required=False,
        ),
        LoadItem(
            component=model.LinkedTechs,
            table='LinkedTech',
            columns=['primary_region', 'primary_tech', 'emis_comm', 'driven_tech'],
            validator_name='viable_rtt',
            validation_map=(0, 1, 3),
            custom_loader_name='_load_linked_techs',
            is_period_filtered=False,
            is_table_required=False,
        ),
    ]
    return manifest
