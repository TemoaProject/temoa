"""
Tests for the CommodityNetwork analysis class.

This test suite verifies the core logic of the network analysis, ensuring that
it correctly identifies valid ("good") connections, demand-side orphans, and
other orphans under various network topologies.
"""

from collections import defaultdict
from unittest.mock import MagicMock

import pytest

# Assuming the refactored code is in this location
from temoa.model_checking.commodity_network import CommodityNetwork
from temoa.model_checking.network_model_data import EdgeTuple

# --- Test Case Definitions ---
# Each tuple contains:
# 1. test_id (str): A descriptive name for the test case.
# 2. start_nodes (set): Demand commodities to start the backward trace from.
# 3. end_nodes (set): Source commodities that validate a path.
# 4. connections (dict): The network structure {output: {(input, tech)}}.
# 5. expected_good (set): The connections that should be fully valid.
# 6. expected_demand_orphans (set): Connections reachable from demand but not a source.
# 7. expected_other_orphans (set): Connections not reachable from demand at all.

TEST_CASES = [
    # s = source commodity, p = physical commodity, d = demand, t = tech
    # Test 1: A simple, valid, linear chain from source to demand.
    # s1 -> t1 -> p1 -> t2 -> d1
    (
        'simple_linear_chain',
        {'d1'},
        {'s1'},
        {'d1': {('p1', 't2')}, 'p1': {('s1', 't1')}},
        {('s1', 't1', 'p1'), ('p1', 't2', 'd1')},
        set(),
        set(),
    ),
    # Test 2: One valid chain and one orphaned branch feeding into the same demand.
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    (
        'one_good_one_orphan_branch',
        {'d1'},
        {'s1'},
        {'d1': {('p1', 't2'), ('p2', 't3')}, 'p1': {('s1', 't1')}},
        {('s1', 't1', 'p1'), ('p1', 't2', 'd1')},
        {('p2', 't3', 'd1')},
        set(),
    ),
    # Test 3: Multiple valid paths from one intermediate commodity, plus an orphan branch.
    #                 - t4  -
    #               /        \
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    (
        'multiple_paths_from_one_source',
        {'d1'},
        {'s1'},
        {'d1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')}, 'p1': {('s1', 't1')}},
        {('s1', 't1', 'p1'), ('p1', 't2', 'd1'), ('p1', 't4', 'd1')},
        {('p2', 't3', 'd1')},
        set(),
    ),
    # Test 4: Two independent, valid supply chains for two different demands.
    #                 - t4  -
    #               /        \
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    #
    #             s2 -> t5 -> d2
    (
        'multiple_demands_and_sources',
        {'d1', 'd2'},
        {'s1', 's2'},
        {
            'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
            'p1': {('s1', 't1')},
            'd2': {('s2', 't5')},
        },
        {('s1', 't1', 'p1'), ('p1', 't2', 'd1'), ('p1', 't4', 'd1'), ('s2', 't5', 'd2')},
        {('p2', 't3', 'd1')},
        set(),
    ),
    # Test 5: One demand is valid, the other is completely orphaned (no path to any source).
    #                 - t4  -
    #               /        \
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    #
    #             p3 -> t5 -> d2
    (
        'one_demand_is_fully_orphaned',
        {'d1', 'd2'},
        {'s1'},
        {
            'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
            'p1': {('s1', 't1')},
            'd2': {('p3', 't5')},
        },
        {('s1', 't1', 'p1'), ('p1', 't2', 'd1'), ('p1', 't4', 'd1')},
        {('p2', 't3', 'd1'), ('p3', 't5', 'd2')},
        set(),
    ),
    # Test 6: A valid network that includes a loop (e.g., storage technology).
    #           - t4 -
    #            \  /
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    (
        'network_with_a_loop',
        {'d1'},
        {'s1', 's2'},
        {
            'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
            'p1': {('s1', 't1'), ('p1', 't4')},  # t4 loops on p1
        },
        {('s1', 't1', 'p1'), ('p1', 't2', 'd1'), ('p1', 't4', 'd1'), ('p1', 't4', 'p1')},
        {('p2', 't3', 'd1')},
        set(),
    ),
    # Test 7: No source nodes are defined, so no connections can be "good".
    # s1 -> t1 -> p1 -> t2 -> d1
    # s2 -> t5 -> d2
    (
        'no_source_nodes_defined',
        {'d1', 'd2'},
        set(),  # No sources
        {
            'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
            'p1': {('s1', 't1')},
            'd2': {('s2', 't5')},
        },
        set(),  # No good connections are possible
        {
            ('p1', 't2', 'd1'),
            ('p2', 't3', 'd1'),
            ('p1', 't4', 'd1'),
            ('s1', 't1', 'p1'),
            ('s2', 't5', 'd2'),
        },
        set(),
    ),
]


@pytest.mark.parametrize(
    (
        'test_id',
        'start_nodes',
        'end_nodes',
        'connections',
        'expected_good',
        'expected_demand_orphans',
        'expected_other_orphans',
    ),
    TEST_CASES,
    ids=[case[0] for case in TEST_CASES],
)
def test_network_analysis(
    test_id,
    start_nodes,
    end_nodes,
    connections,
    expected_good,
    expected_demand_orphans,
    expected_other_orphans,
):
    """
    Tests the CommodityNetwork analysis logic against various topologies.
    """
    # 1. Setup mock model data for the test case
    mock_model_data = MagicMock()
    region = 'test_region'
    period = 2025

    # The mock needs to return the correct data for the (region, period) key
    mock_model_data.demand_commodities = defaultdict(set, {(region, period): start_nodes})
    mock_model_data.source_commodities = defaultdict(set, {(region, period): end_nodes})
    mock_model_data.waste_commodities = defaultdict(set)  # Assume empty
    mock_model_data.available_linked_techs = set()  # Assume no linked techs

    # Convert the connections dict into a set of Tech namedtuples
    available_techs = {
        EdgeTuple(input_comm=ic, output_comm=oc, tech=tech, vintage=period, region=region)
        for oc, links in connections.items()
        for ic, tech in links
    }
    mock_model_data.available_techs = defaultdict(set, {(region, period): available_techs})

    # 2. Instantiate the class with the mock data
    network = CommodityNetwork(region=region, period=period, model_data=mock_model_data)

    # 3. Run the analysis
    network.analyze_network()

    # 4. Assert the results
    assert network.good_connections == expected_good, (
        f'[{test_id}] Failed to identify good connections'
    )
    assert network.demand_orphans == expected_demand_orphans, (
        f'[{test_id}] Failed to identify demand-side orphans'
    )
    assert network.other_orphans == expected_other_orphans, (
        f'[{test_id}] Failed to identify other orphans'
    )
