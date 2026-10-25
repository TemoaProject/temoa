"""
Tests for the CommodityNetwork analysis class.

This test suite verifies the core logic of the network analysis, ensuring that
it correctly identifies valid ("good") connections, demand-side orphans, and
other orphans under various network topologies.
"""

from collections import defaultdict
from typing import TypedDict, cast
from unittest.mock import MagicMock

import pytest

# Assuming the refactored code is in this location
from temoa.model_checking.commodity_network import CommodityNetwork
from temoa.model_checking.network_model_data import EdgeTuple
from temoa.types.core_types import Commodity, Period, Region, Technology, Vintage


class CaseType(TypedDict):
    test_id: str  # Descriptive name for the test case
    start_nodes: set[str]  # Demand commodities to start the backward trace from
    end_nodes: set[str]  # Source commodities that validate a path
    connections: dict[str, set[tuple[str, str]]]  # The network structure {output: {(input, tech)}}.
    expected_good: set[tuple[str, str, str]]  # The connections that should be fully valid
    expected_demand_orphans: set[
        tuple[str, str, str]
    ]  # Connections reachable from demand but not a source
    expected_other_orphans: set[
        tuple[str, str, str]
    ]  # Connections not reachable from demand at all


TEST_CASES: list[CaseType] = [
    # s = source commodity, p = physical commodity, d = demand, t = tech
    # Test 1: A simple, valid, linear chain from source to demand.
    # s1 -> t1 -> p1 -> t2 -> d1
    {
        'test_id': 'simple_linear_chain',
        'start_nodes': {'d1'},
        'end_nodes': {'s1'},
        'connections': {'d1': {('p1', 't2')}, 'p1': {('s1', 't1')}},
        'expected_good': {('s1', 't1', 'p1'), ('p1', 't2', 'd1')},
        'expected_demand_orphans': set(),
        'expected_other_orphans': set(),
    },
    # Test 2: One valid chain and one orphaned branch feeding into the same demand.
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    {
        'test_id': 'one_good_one_orphan_branch',
        'start_nodes': {'d1'},
        'end_nodes': {'s1'},
        'connections': {'d1': {('p1', 't2'), ('p2', 't3')}, 'p1': {('s1', 't1')}},
        'expected_good': {('s1', 't1', 'p1'), ('p1', 't2', 'd1')},
        'expected_demand_orphans': {('p2', 't3', 'd1')},
        'expected_other_orphans': set(),
    },
    # Test 3: Multiple valid paths from one intermediate commodity, plus an orphan branch.
    #                 - t4  -
    #               /        \
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    {
        'test_id': 'multiple_paths_from_one_source',
        'start_nodes': {'d1'},
        'end_nodes': {'s1'},
        'connections': {'d1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')}, 'p1': {('s1', 't1')}},
        'expected_good': {('s1', 't1', 'p1'), ('p1', 't2', 'd1'), ('p1', 't4', 'd1')},
        'expected_demand_orphans': {('p2', 't3', 'd1')},
        'expected_other_orphans': set(),
    },
    # Test 4: Two independent, valid supply chains for two different demands.
    #                 - t4  -
    #               /        \
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    #
    #             s2 -> t5 -> d2
    {
        'test_id': 'multiple_demands_and_sources',
        'start_nodes': {'d1', 'd2'},
        'end_nodes': {'s1', 's2'},
        'connections': {
            'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
            'p1': {('s1', 't1')},
            'd2': {('s2', 't5')},
        },
        'expected_good': {
            ('s1', 't1', 'p1'),
            ('p1', 't2', 'd1'),
            ('p1', 't4', 'd1'),
            ('s2', 't5', 'd2'),
        },
        'expected_demand_orphans': {('p2', 't3', 'd1')},
        'expected_other_orphans': set(),
    },
    # Test 5: One demand is valid, the other is completely orphaned (no path to any source).
    #                 - t4  -
    #               /        \
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    #
    #             p3 -> t5 -> d2
    {
        'test_id': 'one_demand_is_fully_orphaned',
        'start_nodes': {'d1', 'd2'},
        'end_nodes': {'s1'},
        'connections': {
            'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
            'p1': {('s1', 't1')},
            'd2': {('p3', 't5')},
        },
        'expected_good': {('s1', 't1', 'p1'), ('p1', 't2', 'd1'), ('p1', 't4', 'd1')},
        'expected_demand_orphans': {('p2', 't3', 'd1'), ('p3', 't5', 'd2')},
        'expected_other_orphans': set(),
    },
    # Test 6: A valid network that includes a loop (e.g., storage technology).
    #           - t4 -
    #            \  /
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    {
        'test_id': 'network_with_a_loop',
        'start_nodes': {'d1'},
        'end_nodes': {'s1', 's2'},
        'connections': {
            'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
            'p1': {('s1', 't1'), ('p1', 't4')},  # t4 loops on p1
        },
        'expected_good': {
            ('s1', 't1', 'p1'),
            ('p1', 't2', 'd1'),
            ('p1', 't4', 'd1'),
            ('p1', 't4', 'p1'),
        },
        'expected_demand_orphans': {('p2', 't3', 'd1')},
        'expected_other_orphans': set(),
    },
    # Test 7: No source nodes are defined, so no connections can be "good".
    # s1 -> t1 -> p1 -> t2 -> d1
    # s2 -> t5 -> d2
    {
        'test_id': 'no_source_nodes_defined',
        'start_nodes': {'d1', 'd2'},
        'end_nodes': set(),  # No sources
        'connections': {
            'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
            'p1': {('s1', 't1')},
            'd2': {('s2', 't5')},
        },
        'expected_good': set(),  # No good connections are possible
        'expected_demand_orphans': {
            ('p1', 't2', 'd1'),
            ('p2', 't3', 'd1'),
            ('p1', 't4', 'd1'),
            ('s1', 't1', 'p1'),
            ('s2', 't5', 'd2'),
        },
        'expected_other_orphans': set(),
    },
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
    [
        (
            case['test_id'],
            case['start_nodes'],
            case['end_nodes'],
            case['connections'],
            case['expected_good'],
            case['expected_demand_orphans'],
            case['expected_other_orphans'],
        )
        for case in TEST_CASES
    ],
    ids=[case['test_id'] for case in TEST_CASES],
)
def test_network_analysis(
    test_id: str,
    start_nodes: set[str],
    end_nodes: set[str],
    connections: dict[Commodity, set[tuple[Commodity, Technology]]],
    expected_good: set[tuple[str, str, str]],
    expected_demand_orphans: set[tuple[str, str, str]],
    expected_other_orphans: set[tuple[str, str, str]],
) -> None:
    """
    Tests the CommodityNetwork analysis logic against various topologies.
    """
    # 1. Setup mock model data for the test case
    mock_model_data = MagicMock()
    region = cast('Region', 'test_region')
    period = cast('Period', 2025)

    # The mock needs to return the correct data for the (region, period) key
    mock_model_data.demand_commodities = defaultdict(set, {(region, period): start_nodes})
    mock_model_data.source_commodities = defaultdict(set, {(region, period): end_nodes})
    mock_model_data.waste_commodities = defaultdict(set)  # Assume empty
    mock_model_data.available_linked_techs = set()  # Assume no linked techs

    # Convert the connections dict into a set of Tech namedtuples
    available_techs = {
        EdgeTuple(
            input_comm=ic, output_comm=oc, tech=tech, vintage=cast('Vintage', period), region=region
        )
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
