from unittest.mock import MagicMock

import pytest

from temoa.model_checking import network_model_data
from temoa.model_checking.commodity_network import CommodityNetwork

# ==============================================================================
# Test Scenarios
# ==============================================================================
# Each scenario defines the mock database data and the expected outcomes.
# The `db_data` dictionary keys are specific, unique fragments of SQL queries.
# This makes the mock robust against changes in the order of execution,
# ensuring backwards compatibility with older versions of the code.
# ==============================================================================
test_scenarios = [
    # Scenario 1: A basic network with several orphan technologies.
    {
        'name': 'basic',
        'db_data': {
            'Technology WHERE retire==1': [],
            'FROM SurvivalCurve': [],
            'FROM TimePeriod': [(2020,), (2025,)],
            # Unique keys for each Commodity query
            "Commodity WHERE flag LIKE '%p%'": [
                ('s1',),
                ('p1',),
                ('p2',),
                ('p3',),
                ('d1',),
                ('d2',),
            ],
            "Commodity WHERE flag LIKE '%w%'": [],
            "Commodity WHERE flag = 's'": [('s1',)],
            'FROM main.Demand': [('R1', 2020, 'd1'), ('R1', 2020, 'd2')],
            # Unique keys for Efficiency and optional tables
            'FROM main.Efficiency': [
                ('R1', 's1', 't4', 2000, 'p3', 100),
                ('R1', 's1', 't4', 1990, 'p3', 100),
                ('R1', 's1', 't1', 2000, 'p1', 100),
                ('R1', 'p1', 't2', 2000, 'd1', 100),
                ('R1', 'p2', 't3', 2000, 'd1', 100),
                ('R1', 'p2', 't5', 2000, 'd2', 100),
            ],
            'FROM EndOfLifeOutput': [],
            'FROM ConstructionInput': [],
            'FROM main.LinkedTech': [],
            'FROM CostVariable': [],
        },
        'expected': {
            'demands_count': 2,
            'techs_count': 6,
            'valid_techs': 2,
            'demand_orphans': 2,
            'other_orphans': 2,
            'unsupported_demands': {'d2'},
        },
    },
    # Scenario 2: A network with a misconfigured linked technology.
    {
        'name': 'bad linked tech',
        'db_data': {
            'Technology WHERE retire==1': [],
            'FROM SurvivalCurve': [],
            'FROM TimePeriod': [(2020,), (2025,)],
            "Commodity WHERE flag LIKE '%p%'": [('s1',), ('p3',), ('d1',), ('d2',)],
            "Commodity WHERE flag LIKE '%w%'": [],
            "Commodity WHERE flag = 's'": [('s1',)],
            'FROM main.Demand': [('R1', 2020, 'd1'), ('R1', 2020, 'd2')],
            'FROM main.Efficiency': [
                ('R1', 's1', 't4', 2000, 'p3', 100),
                ('R1', 'p1', 'driven', 1990, 'd2', 100),
                ('R1', 's1', 't1', 2000, 'd1', 100),
            ],
            'FROM EndOfLifeOutput': [],
            'FROM ConstructionInput': [],
            'FROM main.LinkedTech': [('R1', 't4', 'nox', 'driven')],
            'FROM CostVariable': [],
        },
        'expected': {
            'demands_count': 2,
            'techs_count': 3,
            'valid_techs': 1,
            'demand_orphans': 0,
            'other_orphans': 2,
            'unsupported_demands': {'d2'},
        },
    },
    # Scenario 3: A network with a correctly configured linked technology.
    {
        'name': 'good linked tech',
        'db_data': {
            'Technology WHERE retire==1': [],
            'FROM SurvivalCurve': [],
            'FROM TimePeriod': [(2020,), (2025,)],
            "Commodity WHERE flag LIKE '%p%'": [('s1',), ('d1',), ('d2',), ('s2',)],
            "Commodity WHERE flag LIKE '%w%'": [],
            "Commodity WHERE flag = 's'": [('s1',), ('s2',)],
            'FROM main.Demand': [('R1', 2020, 'd1'), ('R1', 2020, 'd2')],
            'FROM main.Efficiency': [
                ('R1', 's1', 't4', 2000, 'd2', 100),
                ('R1', 's2', 'driven', 1990, 'd2', 100),
                ('R1', 's1', 't1', 2000, 'd1', 100),
            ],
            'FROM EndOfLifeOutput': [],
            'FROM ConstructionInput': [],
            'FROM main.LinkedTech': [('R1', 't4', 'nox', 'driven')],
            'FROM CostVariable': [],
        },
        'expected': {
            'demands_count': 2,
            'techs_count': 3,
            'valid_techs': 3,
            'demand_orphans': 0,
            'other_orphans': 0,
            'unsupported_demands': set(),
        },
    },
]


# ==============================================================================
# Fixtures
# ==============================================================================
@pytest.fixture
def mock_db_connection(request):
    """
    A robust mock of a database connection.

    This fixture uses a "dispatcher" function as a side_effect. The dispatcher
    inspects the SQL query and returns the corresponding data from the
    test scenario's `db_data` dictionary. This makes the test independent
    of the order of SQL calls in the code being tested.
    """
    db_data = request.param['db_data']
    mock_con = MagicMock(name='mock_connection')
    mock_cursor = MagicMock(name='mock_cursor')
    mock_con.cursor.return_value = mock_cursor

    def dispatcher(query: str, *_: object) -> MagicMock:
        for key, data in db_data.items():
            if key in query:
                execute_mock = MagicMock(name=f'execute_mock_for_{key}')
                execute_mock.fetchall.return_value = data
                execute_mock.fetchone.return_value = data[0] if data else None
                return execute_mock
        raise ValueError(f'Mock database received unexpected query: {query}')

    mock_cursor.execute.side_effect = dispatcher
    return mock_con, request.param['expected']


# ==============================================================================
# Tests
# ==============================================================================
@pytest.mark.parametrize(
    'mock_db_connection', test_scenarios, indirect=True, ids=[d['name'] for d in test_scenarios]
)
def test_network_build_and_analysis(mock_db_connection) -> None:
    """Tests both data model construction and network analysis in one go."""
    conn, expected = mock_db_connection

    # --- 1. Build the data object ---
    network_data = network_model_data._build_from_db(conn)

    # --- 2. Test initial data loading ---
    assert (
        sum(len(s) for s in network_data.demand_commodities.values()) == expected['demands_count']
    )
    assert len(network_data.available_techs[('R1', 2020)]) == expected['techs_count']

    # --- 3. Perform network analysis ---
    cn = CommodityNetwork(region='R1', period=2020, model_data=network_data)
    cn.analyze_network()

    # --- 4. Test analysis results ---
    assert len(cn.get_valid_tech()) == expected['valid_techs'], 'Incorrect number of valid techs'
    assert len(cn.get_demand_side_orphans()) == expected['demand_orphans'], (
        'Incorrect number of demand orphans'
    )
    assert len(cn.get_other_orphans()) == expected['other_orphans'], (
        'Incorrect number of other orphans'
    )
    assert cn.unsupported_demands() == expected['unsupported_demands'], (
        'Incorrect set of unsupported demands'
    )


@pytest.mark.parametrize('mock_db_connection', [test_scenarios[0]], indirect=True)
def test_clone(mock_db_connection):
    """Verifies that the clone() method creates a deep enough copy."""
    conn, _ = mock_db_connection
    network_data = network_model_data._build_from_db(conn)

    clone = network_data.clone()

    assert clone is not network_data, 'Clone should be a new object'
    assert network_data.available_techs == clone.available_techs, (
        'Data should be identical after cloning'
    )

    clone.available_techs.pop(('R1', 2020))
    assert network_data.available_techs != clone.available_techs, (
        'Modifying clone should not affect original'
    )
