import sqlite3
from typing import TYPE_CHECKING, TypedDict, cast
from unittest.mock import MagicMock

import pytest

from temoa.model_checking import network_model_data
from temoa.model_checking.commodity_network import CommodityNetwork

if TYPE_CHECKING:
    from temoa.types.core_types import Period, Region


class ScenarioType(TypedDict):
    name: str
    db_data: dict[str, object]
    expected: dict[str, object]


# ==============================================================================
# Test Scenarios
# ==============================================================================
# Each scenario defines the mock database data and the expected outcomes.
# The `db_data` dictionary keys are specific, unique fragments of SQL queries.
# This makes the mock robust against changes in the order of execution,
# ensuring backwards compatibility with older versions of the code.
# ==============================================================================
test_scenarios: list[ScenarioType] = [
    # Scenario 1: A basic network with several orphan technologies.
    {
        'name': 'basic',
        'db_data': {
            'technology WHERE retire==1': [],
            'FROM survival_curve': [],
            'FROM time_period': [(2020,), (2025,)],
            # Unique keys for each commodity query
            'FROM main.commodity': [('s1',), ('p1',), ('p2',), ('p3',), ('d1',), ('d2',)],
            "commodity WHERE flag LIKE '%p%'": [
                ('s1',),
                ('p1',),
                ('p2',),
                ('p3',),
                ('d1',),
                ('d2',),
            ],
            "commodity WHERE flag LIKE '%w%'": [],
            "commodity WHERE flag = 's'": [('s1',)],
            "commodity WHERE flag LIKE '%p%' OR flag = 's' OR flag LIKE '%a%'": [
                ('s1',),
                ('p1',),
                ('p2',),
                ('p3',),
                ('d1',),
                ('d2',),
            ],
            'FROM main.demand': [('R1', 2020, 'd1'), ('R1', 2020, 'd2')],
            # Unique keys for efficiency and optional tables
            'FROM main.efficiency': [
                ('R1', 's1', 't4', 2000, 'p3', 100),
                ('R1', 's1', 't4', 1990, 'p3', 100),
                ('R1', 's1', 't1', 2000, 'p1', 100),
                ('R1', 'p1', 't2', 2000, 'd1', 100),
                ('R1', 'p2', 't3', 2000, 'd1', 100),
                ('R1', 'p2', 't5', 2000, 'd2', 100),
            ],
            'FROM end_of_life_output': [],
            'FROM construction_input': [],
            'FROM main.linked_tech': [],
            'FROM cost_variable': [],
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
            'technology WHERE retire==1': [],
            'FROM survival_curve': [],
            'FROM time_period': [(2020,), (2025,)],
            'FROM main.commodity': [('s1',), ('p1',), ('p3',), ('d1',), ('d2',)],
            "commodity WHERE flag LIKE '%p%'": [('s1',), ('p3',), ('d1',), ('d2',)],
            "commodity WHERE flag LIKE '%w%'": [],
            "commodity WHERE flag = 's'": [('s1',)],
            "commodity WHERE flag LIKE '%p%' OR flag = 's' OR flag LIKE '%a%'": [
                ('s1',),
                ('p3',),
                ('d1',),
                ('d2',),
            ],
            'FROM main.demand': [('R1', 2020, 'd1'), ('R1', 2020, 'd2')],
            'FROM main.efficiency': [
                ('R1', 's1', 't4', 2000, 'p3', 100),
                ('R1', 'p1', 'driven', 1990, 'd2', 100),
                ('R1', 's1', 't1', 2000, 'd1', 100),
            ],
            'FROM end_of_life_output': [],
            'FROM construction_input': [],
            'FROM main.linked_tech': [('R1', 't4', 'nox', 'driven')],
            'FROM cost_variable': [],
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
            'technology WHERE retire==1': [],
            'FROM survival_curve': [],
            'FROM time_period': [(2020,), (2025,)],
            'FROM main.commodity': [('s1',), ('p1',), ('d1',), ('d2',), ('s2',)],
            "commodity WHERE flag LIKE '%p%'": [('s1',), ('d1',), ('d2',), ('s2',)],
            "commodity WHERE flag LIKE '%w%'": [],
            "commodity WHERE flag = 's'": [('s1',), ('s2',)],
            "commodity WHERE flag LIKE '%p%' OR flag = 's' OR flag LIKE '%a%'": [
                ('s1',),
                ('d1',),
                ('d2',),
                ('s2',),
            ],
            'FROM main.demand': [('R1', 2020, 'd1'), ('R1', 2020, 'd2')],
            'FROM main.efficiency': [
                ('R1', 's1', 't4', 2000, 'd2', 100),
                ('R1', 's2', 'driven', 1990, 'd2', 100),
                ('R1', 's1', 't1', 2000, 'd1', 100),
            ],
            'FROM end_of_life_output': [],
            'FROM construction_input': [],
            'FROM main.linked_tech': [('R1', 't4', 'nox', 'driven')],
            'FROM cost_variable': [],
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
def mock_db_connection(request: pytest.FixtureRequest) -> tuple[MagicMock, dict[str, object]]:
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
        if 'sector FROM technology' in query:
            raise sqlite3.OperationalError('no such column: sector')
        for key, data in sorted(db_data.items(), key=lambda kv: -len(kv[0])):
            if key in query:
                m = MagicMock(name=f'execute_mock_for_{key}')
                m.fetchall.return_value = data
                m.fetchone.return_value = data[0] if data else None
                return m
        raise AssertionError('Unexpected SQL: ' + query)

    mock_cursor.execute.side_effect = dispatcher
    return mock_con, request.param['expected']


# ==============================================================================
# Tests
# ==============================================================================
@pytest.mark.parametrize(
    'mock_db_connection', test_scenarios, indirect=True, ids=[d['name'] for d in test_scenarios]
)
def test_network_build_and_analysis(
    mock_db_connection: tuple[MagicMock, dict[str, object]],
) -> None:
    """Tests both data model construction and network analysis in one go."""
    conn, expected = mock_db_connection

    # --- 1. Build the data object ---
    network_data = network_model_data._build_from_db(conn)

    # --- 2. Test initial data loading ---
    assert (
        sum(len(s) for s in network_data.demand_commodities.values()) == expected['demands_count']
    )
    assert (
        len(network_data.available_techs[(cast('Region', 'R1'), cast('Period', 2020))])
        == expected['techs_count']
    )

    # --- 3. Perform network analysis ---
    cn = CommodityNetwork(
        region=cast('Region', 'R1'), period=cast('Period', 2020), model_data=network_data
    )
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
def test_clone(mock_db_connection: tuple[MagicMock, dict[str, object]]) -> None:
    """Verifies that the clone() method creates a deep enough copy."""
    conn, _ = mock_db_connection
    network_data = network_model_data._build_from_db(conn)

    clone = network_data.clone()

    assert clone is not network_data, 'Clone should be a new object'
    assert network_data.available_techs == clone.available_techs, (
        'Data should be identical after cloning'
    )

    clone.available_techs.pop((cast('Region', 'R1'), cast('Period', 2020)))
    assert network_data.available_techs != clone.available_techs, (
        'Modifying clone should not affect original'
    )


def test_sector_handling_with_sectors() -> None:
    """Test that sectors are properly handled when they exist in the database."""
    # Mock database with sector column
    mock_con = MagicMock(name='mock_connection')
    mock_cursor = MagicMock(name='mock_cursor')
    mock_con.cursor.return_value = mock_cursor

    # Mock the sector column check to return True
    sector_check_mock = MagicMock()
    sector_check_mock.fetchall.return_value = [('Other',)]
    sector_check_mock.fetchone.return_value = ('Other',)

    # Mock efficiency data with sectors
    efficiency_mock = MagicMock()
    efficiency_mock.fetchall.return_value = [
        ('R1', 's1', 't1', 2000, 'p1', 100, 'supply'),
        ('R1', 'p1', 't2', 2000, 'd1', 100, 'demand'),
    ]

    def dispatcher(query: str, *_: object) -> MagicMock:
        if 'sector FROM technology' in query:
            return sector_check_mock
        elif 'FROM main.efficiency' in query:
            return efficiency_mock
        elif 'technology WHERE retire==1' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif 'FROM survival_curve' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif 'FROM time_period' in query:
            m = MagicMock()
            m.fetchall.return_value = [(2020,), (2025,)]
            return m
        elif "commodity WHERE flag LIKE '%p%'" in query:
            m = MagicMock()
            m.fetchall.return_value = [('s1',), ('p1',), ('d1',)]
            return m
        elif "commodity WHERE flag LIKE '%w%'" in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif "commodity WHERE flag = 's'" in query:
            m = MagicMock()
            m.fetchall.return_value = [('s1',)]
            return m
        elif 'FROM main.demand' in query:
            m = MagicMock()
            m.fetchall.return_value = [('R1', 2020, 'd1')]
            return m
        elif 'FROM end_of_life_output' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif 'FROM construction_input' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif 'FROM main.linked_tech' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif 'FROM cost_variable' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        raise AssertionError('Mock database received unexpected query: ' + query)

    mock_cursor.execute.side_effect = dispatcher

    # Build network data
    network_data = network_model_data._build_from_db(mock_con)

    # Verify sectors are included in efficiencyTuple
    techs = list(network_data.available_techs[(cast('Region', 'R1'), cast('Period', 2020))])
    assert len(techs) == 2
    # Fields: region, ic, tech, vintage, oc, lifetime, sector
    assert all(len(tech) == 7 for tech in techs)
    assert any(tech.sector == 'supply' for tech in techs)
    assert any(tech.sector == 'demand' for tech in techs)


def test_sector_handling_without_sectors() -> None:
    """Test that sectors are handled gracefully when they don't exist in the database."""
    # Mock database without sector column
    mock_con = MagicMock(name='mock_connection')
    mock_cursor = MagicMock(name='mock_cursor')
    mock_con.cursor.return_value = mock_cursor

    # Mock the sector column check to raise OperationalError (column doesn't exist)
    def dispatcher(query: str, *_: object) -> MagicMock:
        if 'sector FROM technology' in query:
            # Simulate column not existing
            raise sqlite3.OperationalError('no such column: sector')
        elif 'FROM main.efficiency' in query:
            # Return data without sector column
            mock = MagicMock()
            mock.fetchall.return_value = [
                ('R1', 's1', 't1', 2000, 'p1', 100),
                ('R1', 'p1', 't2', 2000, 'd1', 100),
            ]
            return mock
        elif 'FROM main.commodity' in query:
            m = MagicMock()
            m.fetchall.return_value = [('s1',), ('p1',), ('d1',)]
            return m
        elif 'technology WHERE retire==1' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif 'FROM survival_curve' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif 'FROM time_period' in query:
            m = MagicMock()
            m.fetchall.return_value = [(2020,), (2025,)]
            return m
        elif "commodity WHERE flag LIKE '%p%'" in query:
            m = MagicMock()
            m.fetchall.return_value = [('s1',), ('p1',), ('d1',)]
            return m
        elif "commodity WHERE flag LIKE '%w%'" in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif "commodity WHERE flag = 's'" in query:
            m = MagicMock()
            m.fetchall.return_value = [('s1',)]
            return m
        elif 'FROM main.demand' in query:
            m = MagicMock()
            m.fetchall.return_value = [('R1', 2020, 'd1')]
            return m
        elif 'FROM end_of_life_output' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif 'FROM construction_input' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif 'FROM main.linked_tech' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        elif 'FROM cost_variable' in query:
            m = MagicMock()
            m.fetchall.return_value = []
            return m
        raise ValueError(f'Mock database received unexpected query: {query}')

    mock_cursor.execute.side_effect = dispatcher

    # Build network data
    network_data = network_model_data._build_from_db(mock_con)

    # Verify sectors default to None
    techs = list(network_data.available_techs[(cast('Region', 'R1'), cast('Period', 2020))])
    assert len(techs) == 2
    # Fields: region, ic, tech, vintage, oc, lifetime, sector (sector None here)
    assert all(len(tech) == 7 for tech in techs)
    assert all(tech.sector is None for tech in techs)
