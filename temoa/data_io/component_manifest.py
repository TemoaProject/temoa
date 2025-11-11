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
            table='region',
            columns=['region'],
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.regional_global_indices,
            table='meta_regional_groups',  # Placeholder, custom loader does the work
            columns=['region_or_group'],
            custom_loader_name='_load_regional_global_indices',
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.tech_production,
            table='technology',
            columns=['tech'],
            where_clause="flag LIKE 'p%'",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_uncap,
            table='technology',
            columns=['tech'],
            where_clause='unlim_cap > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.tech_baseload,
            table='technology',
            columns=['tech'],
            where_clause="flag = 'pb'",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_storage,
            table='technology',
            columns=['tech'],
            where_clause="flag = 'ps'",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_seasonal_storage,
            table='technology',
            columns=['tech'],
            where_clause="flag = 'ps' AND seas_stor > 0",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_reserve,
            table='technology',
            columns=['tech'],
            where_clause='reserve > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_curtailment,
            table='technology',
            columns=['tech'],
            where_clause='curtail > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_flex,
            table='technology',
            columns=['tech'],
            where_clause='flex > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_exchange,
            table='technology',
            columns=['tech'],
            where_clause='exchange > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_annual,
            table='technology',
            columns=['tech'],
            where_clause='annual > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_retirement,
            table='technology',
            columns=['tech'],
            where_clause='retire > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.tech_group_names,
            table='tech_group',
            columns=['group_name'],
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.tech_group_members,
            table='tech_group_member',
            columns=['group_name', 'tech'],
            custom_loader_name='_load_tech_group_members',
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.commodity_demand,
            table='commodity',
            columns=['name'],
            where_clause="flag = 'd'",
            validator_name='viable_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.commodity_emissions,
            table='commodity',
            columns=['name'],
            where_clause="flag = 'e'",
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.commodity_physical,
            table='commodity',
            columns=['name'],
            where_clause="flag LIKE '%p%' OR flag = 's' OR flag LIKE '%a%'",
            validator_name='viable_input_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.commodity_source,
            table='commodity',
            columns=['name'],
            where_clause="flag = 's'",
            validator_name='viable_input_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.commodity_annual,
            table='commodity',
            columns=['name'],
            where_clause="flag LIKE '%a%'",
            validator_name='viable_input_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.commodity_waste,
            table='commodity',
            columns=['name'],
            where_clause="flag LIKE '%w%'",
            validator_name='viable_output_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.operator,
            table='operator',
            columns=['operator'],
            is_period_filtered=False,
            is_table_required=False,
        ),
        # =========================================================================
        # Time-Related Components
        # =========================================================================
        LoadItem(
            component=model.time_of_day,
            table='time_of_day',
            columns=['tod'],
            is_period_filtered=False,
            is_table_required=False,
            fallback_data=[('D',)],
        ),
        LoadItem(
            component=model.time_season,
            table='time_season',
            columns=['period', 'season'],
            custom_loader_name='_load_time_season',
            is_period_filtered=False,  # Custom loader handles myopic filtering
            is_table_required=False,
        ),
        LoadItem(
            component=model.time_season_sequential,
            table='time_season_sequential',
            columns=['period', 'seas_seq', 'season', 'num_days'],
            custom_loader_name='_load_time_season_sequential',
            is_table_required=False,
        ),
        LoadItem(
            component=model.segment_fraction,
            table='time_segment_fraction',
            columns=['period', 'season', 'tod', 'segment_fraction'],
            custom_loader_name='_load_segment_fraction',
            is_table_required=False,
        ),
        # =========================================================================
        # Capacity and Cost Components
        # =========================================================================
        LoadItem(
            component=model.existing_capacity,
            table='existing_capacity',
            columns=['region', 'tech', 'vintage', 'capacity'],
            custom_loader_name='_load_existing_capacity',
            is_period_filtered=False,  # Custom loader handles all logic
            is_table_required=False,
        ),
        LoadItem(
            component=model.cost_invest,
            table='cost_invest',
            columns=['region', 'tech', 'vintage', 'cost'],
            validator_name='viable_rtv',
            validation_map=(0, 1, 2),
            custom_loader_name='_load_cost_invest',
            is_period_filtered=False,  # Custom loader handles this
            is_table_required=False,
        ),
        LoadItem(
            component=model.cost_fixed,
            table='cost_fixed',
            columns=['region', 'period', 'tech', 'vintage', 'cost'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
        ),
        LoadItem(
            component=model.cost_variable,
            table='cost_variable',
            columns=['region', 'period', 'tech', 'vintage', 'cost'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
        ),
        LoadItem(
            component=model.cost_emission,
            table='cost_emission',
            columns=['region', 'period', 'emis_comm', 'cost'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.loan_rate,
            table='loan_rate',
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
            component=model.days_per_period,
            table='metadata',
            columns=['value'],
            where_clause="element == 'days_per_period'",
            custom_loader_name='_load_days_per_period',
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.global_discount_rate,
            table='metadata_real',
            columns=['value'],
            where_clause="element = 'global_discount_rate'",
            custom_loader_name='_load_global_discount_rate',
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.default_loan_rate,
            table='metadata_real',
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
            component=model.efficiency,
            table='meta_efficiency',  # Placeholder, custom loader does the work
            columns=[],
            custom_loader_name='_load_efficiency',
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.efficiency_variable,
            table='efficiency_variable',
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
            component=model.demand,
            table='demand',
            columns=['region', 'period', 'commodity', 'demand'],
        ),
        LoadItem(
            component=model.demand_specific_distribution,
            table='demand_specific_distribution',
            columns=['region', 'period', 'season', 'tod', 'demand_name', 'dsd'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.capacity_to_activity,
            table='capacity_to_activity',
            columns=['region', 'tech', 'c2a'],
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.capacity_factor_tech,
            table='capacity_factor_tech',
            columns=['region', 'period', 'season', 'tod', 'tech', 'factor'],
            validator_name='viable_rt',
            validation_map=(0, 4),
            is_table_required=False,
        ),
        LoadItem(
            component=model.capacity_factor_process,
            table='capacity_factor_process',
            columns=['region', 'period', 'season', 'tod', 'tech', 'vintage', 'factor'],
            validator_name='viable_rtv',
            validation_map=(0, 4, 5),
            is_table_required=False,
        ),
        LoadItem(
            component=model.lifetime_tech,
            table='lifetime_tech',
            columns=['region', 'tech', 'lifetime'],
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.lifetime_process,
            table='lifetime_process',
            columns=['region', 'tech', 'vintage', 'lifetime'],
            validator_name='viable_rtv',
            validation_map=(0, 1, 2),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.lifetime_survival_curve,
            table='lifetime_survival_curve',
            columns=['region', 'period', 'tech', 'vintage', 'fraction'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.loan_lifetime_process,
            table='loan_lifetime_process',
            columns=['region', 'tech', 'vintage', 'lifetime'],
            validator_name='viable_rtv',
            validation_map=(0, 1, 2),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.ramp_up_hourly,
            table='ramp_up_hourly',
            columns=['region', 'tech', 'rate'],
            custom_loader_name='_load_ramping_up',
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.tech_upramping,
            table='ramp_up_hourly',
            columns=['tech'],
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.ramp_down_hourly,
            table='ramp_down_hourly',
            columns=['region', 'tech', 'rate'],
            custom_loader_name='_load_ramping_down',
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.tech_downramping,
            table='ramp_down_hourly',
            columns=['tech'],
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=model.renewable_portfolio_standard,
            table='rps_requirement',
            columns=['region', 'period', 'tech_group', 'requirement'],
            custom_loader_name='_load_rps_requirement',
            is_table_required=False,
        ),
        LoadItem(
            component=model.capacity_credit,
            table='capacity_credit',
            columns=['region', 'period', 'tech', 'vintage', 'credit'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
            is_table_required=False,
        ),
        LoadItem(
            component=model.reserve_capacity_derate,
            table='reserve_capacity_derate',
            columns=['region', 'period', 'season', 'tech', 'vintage', 'factor'],
            validator_name='viable_rtv',
            validation_map=(0, 3, 4),
            is_table_required=False,
        ),
        LoadItem(
            component=model.planning_reserve_margin,
            table='planning_reserve_margin',
            columns=['region', 'margin'],
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.storage_duration,
            table='storage_duration',
            columns=['region', 'tech', 'duration'],
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_storage_fraction,
            table='limit_storage_level_fraction',
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
            component=model.emission_activity,
            table='emission_activity',
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
            component=model.emission_embodied,
            table='emission_embodied',
            columns=['region', 'emis_comm', 'tech', 'vintage', 'value'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.emission_end_of_life,
            table='emission_end_of_life',
            columns=['region', 'emis_comm', 'tech', 'vintage', 'value'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.construction_input,
            table='construction_input',
            columns=['region', 'input_comm', 'tech', 'vintage', 'value'],
            validator_name='viable_rtv',
            validation_map=(0, 2, 3),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.end_of_life_output,
            table='end_of_life_output',
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
            component=model.limit_capacity,
            table='limit_capacity',
            columns=['region', 'period', 'tech_or_group', 'operator', 'capacity'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_new_capacity,
            table='limit_new_capacity',
            columns=['region', 'period', 'tech_or_group', 'operator', 'new_cap'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_capacity_share,
            table='limit_capacity_share',
            columns=['region', 'period', 'sub_group', 'super_group', 'operator', 'share'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_new_capacity_share,
            table='limit_new_capacity_share',
            columns=['region', 'period', 'sub_group', 'super_group', 'operator', 'share'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_activity,
            table='limit_activity',
            columns=['region', 'period', 'tech_or_group', 'operator', 'activity'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_activity_share,
            table='limit_activity_share',
            columns=['region', 'period', 'sub_group', 'super_group', 'operator', 'share'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_resource,
            table='limit_resource',
            columns=['region', 'tech_or_group', 'operator', 'cum_act'],
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_seasonal_capacity_factor,
            table='limit_seasonal_capacity_factor',
            columns=['region', 'period', 'season', 'tech', 'operator', 'factor'],
            validator_name='viable_rt',
            validation_map=(0, 3),
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_annual_capacity_factor,
            table='limit_annual_capacity_factor',
            columns=['region', 'period', 'tech', 'output_comm', 'operator', 'factor'],
            validator_name='viable_rpto',
            validation_map=(0, 1, 2, 3),
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_emission,
            table='limit_emission',
            columns=['region', 'period', 'emis_comm', 'operator', 'value'],
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_tech_input_split,
            table='limit_tech_input_split',
            columns=['region', 'period', 'input_comm', 'tech', 'operator', 'proportion'],
            validator_name='viable_rpit',
            validation_map=(0, 1, 2, 3),
            custom_loader_name='_load_limit_tech_input_split',
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_tech_input_split_annual,
            table='limit_tech_input_split_annual',
            columns=['region', 'period', 'input_comm', 'tech', 'operator', 'proportion'],
            validator_name='viable_rpit',
            validation_map=(0, 1, 2, 3),
            custom_loader_name='_load_limit_tech_input_split_annual',
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_tech_output_split,
            table='limit_tech_output_split',
            columns=['region', 'period', 'tech', 'output_comm', 'operator', 'proportion'],
            validator_name='viable_rpto',
            validation_map=(0, 1, 2, 3),
            custom_loader_name='_load_limit_tech_output_split',
            is_table_required=False,
        ),
        LoadItem(
            component=model.limit_tech_output_split_annual,
            table='limit_tech_output_split_annual',
            columns=['region', 'period', 'tech', 'output_comm', 'operator', 'proportion'],
            validator_name='viable_rpto',
            validation_map=(0, 1, 2, 3),
            custom_loader_name='_load_limit_tech_output_split_annual',
            is_table_required=False,
        ),
        LoadItem(
            component=model.linked_techs,
            table='linked_tech',
            columns=['primary_region', 'primary_tech', 'emis_comm', 'driven_tech'],
            validator_name='viable_rtt',
            validation_map=(0, 1, 3),
            custom_loader_name='_load_linked_techs',
            is_period_filtered=False,
            is_table_required=False,
        ),
    ]
    return manifest
