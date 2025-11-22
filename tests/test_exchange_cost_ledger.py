from typing import TYPE_CHECKING, Any, cast

import pytest

from temoa._internal.exchange_tech_cost_ledger import CostType, ExchangeTechCostLedger
from tests.utilities.namespace_mock import Namespace

if TYPE_CHECKING:
    from temoa.types.core_types import Period, Region, Technology, Vintage

# Module-level typed constants
TEST_REGION_A = cast('Region', 'A')
TEST_REGION_B = cast('Region', 'B')
TEST_REGION_AB = cast('Region', 'A-B')
TEST_PERIOD_1 = cast('Period', 1)
TEST_PERIOD_2000 = cast('Period', 2000)
TEST_TECH_T1 = cast('Technology', 't1')
TEST_VINTAGE_2000 = cast('Vintage', 2000)

# these are the necessary Temoa elements to make the ledger work
data = {
    'time_season': {2000: [1]},
    'time_of_day': {1},
    'tech_annual': set(),
    'lifetime_process': {('A-B', 't1', 2000): 30, ('B-A', 't1', 2000): 30},
    'process_inputs': {('A-B', 2000, 't1', 2000): ('c1',), ('B-A', 2000, 't1', 2000): ('c1',)},
    'process_outputs_by_input': {
        ('A-B', 2000, 't1', 2000, 'c1'): ('c1',),
        ('B-A', 2000, 't1', 2000, 'c1'): ('c1',),
    },
    'v_flow_out': {
        ('A-B', 2000, 1, 1, 'c1', 't1', 2000, 'c1'): 60,
        ('B-A', 2000, 1, 1, 'c1', 't1', 2000, 'c1'): 40,
    },
}


@pytest.fixture
def fake_model() -> Namespace:
    """make a fake Temoa Model from data"""
    fake_model = Namespace(**data)
    return fake_model


def test_add_cost_record(fake_model: Namespace) -> None:
    """test adding a record to the ledger"""
    ledger = ExchangeTechCostLedger(fake_model)
    ledger.add_cost_record(
        TEST_REGION_AB,
        TEST_PERIOD_1,
        TEST_TECH_T1,
        TEST_VINTAGE_2000,
        1.99,
        CostType.FIXED,
    )
    assert len(ledger.cost_records) == 1, 'should have 1 entry in the ledger'


params: list[dict[str, Any]] = [
    {
        'name': 'no usage splitting',
        'records': [
            ('A-B', 2000, 't1', 2000, 300, CostType.FIXED),
            ('B-A', 2000, 't1', 2000, 100, CostType.FIXED),
        ],
        'B_ratio': 0.6,
        'A_ratio': 0.4,
        'cost_entries': 2,  # both should get a cost entry
        'A_cost': 100,  # A should get the full value of the cost entry (as importer)
        'B_cost': 300,  # B should get full value also as importer
    },
    {
        'name': 'usage splitting',
        'records': [
            ('A-B', 2000, 't1', 2000, 100, CostType.FIXED),
        ],
        'B_ratio': 0.6,
        'A_ratio': 0.4,
        'cost_entries': 1,  # both should get a cost entry
        'A_cost': 40,  # A should get 40% of the cost, based on use
        'B_cost': 60,  # B should get 60% of the cost...
    },
]


@pytest.mark.parametrize('costs', argvalues=params, ids=[d['name'] for d in params])
def test_cost_allocation(fake_model: Namespace, costs: dict[str, Any]) -> None:
    """Test the accurate"""
    ledger = ExchangeTechCostLedger(fake_model)
    for record in costs['records']:
        ledger.add_cost_record(*record)
    assert len(ledger.cost_records[CostType.FIXED]) == costs['cost_entries']

    # test for ratio...
    ratio = ledger.get_use_ratio(
        TEST_REGION_A,
        TEST_REGION_B,
        TEST_PERIOD_2000,
        TEST_TECH_T1,
        TEST_VINTAGE_2000,
    )
    assert ratio == pytest.approx(costs['B_ratio']), (
        'B should get 60% of cost as it receives 60% of flow'
    )
    ratio = ledger.get_use_ratio(
        TEST_REGION_B,
        TEST_REGION_A,
        TEST_PERIOD_2000,
        TEST_TECH_T1,
        TEST_VINTAGE_2000,
    )
    assert ratio == pytest.approx(costs['A_ratio']), (
        'A should get 40% of cost as it receives 40% of flow'
    )

    # test the outpt cost entries...
    entries = ledger.get_entries()
    assert len(entries) == 2, 'should produce 2 entries for A, B'
    assert (
        entries[TEST_REGION_A, TEST_PERIOD_2000, TEST_TECH_T1, TEST_VINTAGE_2000][CostType.FIXED]
        == costs['A_cost']
    ), "costs didn't match"
    assert (
        entries[TEST_REGION_B, TEST_PERIOD_2000, TEST_TECH_T1, TEST_VINTAGE_2000][CostType.FIXED]
        == costs['B_cost']
    ), "costs didn't match"
