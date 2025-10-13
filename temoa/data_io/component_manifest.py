# temoa/data_io/component_manifest.py

from temoa.core.model import TemoaModel
from temoa.data_io.loader_manifest import LoadItem


def build_manifest(M: TemoaModel) -> list[LoadItem]:
    """
    Builds the manifest of all data components to be loaded into the Pyomo model.

    This declarative approach separates the configuration of what to load from the
    procedural logic of how to load it.

    Args:
        M: An instance of TemoaModel to link components.

    Returns:
        A list of LoadItem objects describing the data to be loaded.
    """
    manifest = [
        # === REGION SETS ===
        LoadItem(
            component=M.regions,
            table='Region',
            columns=['region'],
            is_period_filtered=False,
        ),
        # === TECH SETS ===
        LoadItem(
            component=M.tech_production,
            table='Technology',
            columns=['tech'],
            where_clause="flag LIKE 'p%'",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.tech_uncap,
            table='Technology',
            columns=['tech'],
            where_clause='unlim_cap > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
            is_table_required=False,  # unlim_cap is a newer column
        ),
        LoadItem(
            component=M.tech_baseload,
            table='Technology',
            columns=['tech'],
            where_clause="flag = 'pb'",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.tech_storage,
            table='Technology',
            columns=['tech'],
            where_clause="flag = 'ps'",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.tech_seasonal_storage,
            table='Technology',
            columns=['tech'],
            where_clause="flag = 'ps' AND seas_stor > 0",
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.tech_reserve,
            table='Technology',
            columns=['tech'],
            where_clause='reserve > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.tech_curtailment,
            table='Technology',
            columns=['tech'],
            where_clause='curtail > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.tech_flex,
            table='Technology',
            columns=['tech'],
            where_clause='flex > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.tech_exchange,
            table='Technology',
            columns=['tech'],
            where_clause='exchange > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.tech_annual,
            table='Technology',
            columns=['tech'],
            where_clause='annual > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.tech_retirement,
            table='Technology',
            columns=['tech'],
            where_clause='retire > 0',
            validator_name='viable_techs',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        # Tech Groups
        LoadItem(
            component=M.tech_group_names,
            table='TechGroup',
            columns=['group_name'],
            is_period_filtered=False,
            is_table_required=False,
        ),
        # === COMMODITIES ===
        LoadItem(
            component=M.commodity_demand,
            table='Commodity',
            columns=['name'],
            where_clause="flag = 'd'",
            validator_name='viable_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.commodity_emissions,
            table='Commodity',
            columns=['name'],
            where_clause="flag = 'e'",
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.commodity_physical,
            table='Commodity',
            columns=['name'],
            where_clause="flag LIKE '%p%' OR flag = 's' OR flag LIKE '%a%'",
            validator_name='viable_input_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.commodity_source,
            table='Commodity',
            columns=['name'],
            where_clause="flag = 's'",
            validator_name='viable_input_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.commodity_annual,
            table='Commodity',
            columns=['name'],
            where_clause="flag LIKE '%a%'",
            validator_name='viable_input_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        LoadItem(
            component=M.commodity_waste,
            table='Commodity',
            columns=['name'],
            where_clause="flag LIKE '%w%'",
            validator_name='viable_output_comms',
            validation_map=(0,),
            is_period_filtered=False,
        ),
        # === OPERATORS ===
        LoadItem(
            component=M.operator,
            table='Operator',
            columns=['operator'],
            is_period_filtered=False,
            is_table_required=False,
        ),
        # === PARAMS ===
        LoadItem(
            component=M.Demand, table='Demand', columns=['region', 'period', 'commodity', 'demand']
        ),
        LoadItem(
            component=M.CapacityToActivity,
            table='CapacityToActivity',
            columns=['region', 'tech', 'c2a'],
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=M.CapacityFactorTech,
            table='CapacityFactorTech',
            columns=['region', 'period', 'season', 'tod', 'tech', 'factor'],
            validator_name='viable_rt',
            validation_map=(0, 4),
            is_table_required=False,
        ),
        LoadItem(
            component=M.CapacityFactorProcess,
            table='CapacityFactorProcess',
            columns=['region', 'period', 'season', 'tod', 'tech', 'vintage', 'factor'],
            validator_name='viable_rtv',
            validation_map=(0, 4, 5),
            is_table_required=False,
        ),
        LoadItem(
            component=M.LifetimeTech,
            table='LifetimeTech',
            columns=['region', 'tech', 'lifetime'],
            validator_name='viable_rt',
            validation_map=(0, 1),
            is_period_filtered=False,
            is_table_required=False,
        ),
        LoadItem(
            component=M.LifetimeProcess,
            table='LifetimeProcess',
            columns=['region', 'tech', 'vintage', 'lifetime'],
            validator_name='viable_rtv',
            validation_map=(0, 1, 2),
            is_period_filtered=False,
            is_table_required=False,
        ),
    ]
    return manifest
