from unittest.mock import MagicMock

from temoa.model_checking.commodity_graph import generate_commodity_graph
from temoa.model_checking.network_model_data import EdgeTuple, NetworkModelData
from temoa.types.core_types import Period, Region, Sector, Technology, Vintage


def test_special_items_styling():
    """
    Test that demand orphans, other orphans, and driven techs
    are correctly styled in the commodity graph.
    """
    region = Region('test_region')
    period = Period(2025)

    # Mock NetworkModelData
    network_data = MagicMock(spec=NetworkModelData)
    network_data.physical_commodities = {'comm_inter'}
    network_data.source_commodities = {(region, period): {'comm_source'}}
    network_data.demand_commodities = {(region, period): {'comm_demand'}}
    network_data.available_techs = {(region, period): {}}
    network_data.tech_data = {}

    # Define some special items
    demand_orphans = [
        EdgeTuple(
            region,
            'comm_inter',
            Technology('tech_demand_orphan'),
            Vintage(2020),
            'comm_demand',
            sector=Sector('S1'),
        )
    ]
    other_orphans = [
        EdgeTuple(
            region,
            'comm_source',
            Technology('tech_other_orphan'),
            Vintage(2020),
            'comm_inter',
            sector=Sector('S2'),
        )
    ]
    driven_techs = [
        EdgeTuple(
            region,
            'comm_source',
            Technology('tech_driven'),
            Vintage(2020),
            'comm_demand',
            sector=Sector('S3'),
        )
    ]

    # Generate the graph
    dg, _sector_colors = generate_commodity_graph(
        region,
        period,
        network_data,
        demand_orphans=demand_orphans,
        other_orphans=other_orphans,
        driven_techs=driven_techs,
    )

    # 1. Check Node Styling
    assert dg.nodes['comm_demand']['color']['border'] == '#d62728'
    assert dg.nodes['comm_demand']['borderWidth'] == 4
    assert 'Connected to Demand Orphan' in dg.nodes['comm_demand']['title']

    assert dg.nodes['comm_inter']['color']['border'] == '#d62728'
    assert dg.nodes['comm_inter']['borderWidth'] == 4

    assert dg.nodes['comm_source']['color']['border'] == '#ff7f0e'
    assert dg.nodes['comm_source']['borderWidth'] == 4

    # 2. Check Edge Styling
    edges = list(dg.edges(data=True))

    edge_do = next(e for e in edges if (e[0] == 'comm_inter' and e[1] == 'comm_demand'))
    assert edge_do[2]['dashes'] is True
    assert edge_do[2]['color'] == '#d62728'

    edge_oo = next(e for e in edges if (e[0] == 'comm_source' and e[1] == 'comm_inter'))
    assert edge_oo[2]['dashes'] is True
    assert edge_oo[2]['color'] == '#ff7f0e'

    edge_dt = next(e for e in edges if (e[0] == 'comm_source' and e[1] == 'comm_demand'))
    assert edge_dt[2]['dashes'] is True
    assert edge_dt[2]['color'] == '#1f77b4'
