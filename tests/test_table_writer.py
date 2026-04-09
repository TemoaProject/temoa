from typing import TypedDict

import pytest

from temoa._internal.table_data_puller import loan_costs


class LoanCostInput(TypedDict):
    capacity: float
    invest_cost: float
    loan_life: float
    loan_rate: float
    global_discount_rate: float
    process_life: int
    p_0: int
    vintage: int
    p_e: int


class LoanCostTestCase(TypedDict):
    ID: str
    input: LoanCostInput
    expected_model_cost: float
    expected_undiscounted_cost: float


params: list[LoanCostTestCase] = [
    {
        'ID': 'near-zero GDR',
        'input': {
            'capacity': 100_000.0,  # units
            'invest_cost': 1.0,  # $/unit of capacity
            'loan_life': 40.0,
            'loan_rate': 0.10,
            'global_discount_rate': 0.000000000001,
            'process_life': 40,
            'p_0': 2020,  # the "myopic base year" to which all prices are discounted
            'vintage': 2020,  # the vintage of the new 'tech'
            'p_e': 2100,  # last year in the myopic view
        },
        'expected_model_cost': 409037.66,
        'expected_undiscounted_cost': 409037.66,
    },
    {
        'ID': 'shortened term',
        'input': {
            'capacity': 100_000.0,
            'invest_cost': 1.0,
            'loan_life': 40.0,
            'loan_rate': 0.08,
            'global_discount_rate': 0.05,
            'process_life': 50,
            'p_0': 2020,
            'vintage': 2030,
            'p_e': 2035,
        },
        'expected_model_cost': 20950.20952,
        'expected_undiscounted_cost': 33544.06,
    },
]
params_with_zero_gdr: list[LoanCostTestCase] = [
    {
        'ID': 'actual zero GDR',
        'input': {
            'capacity': 100_000.0,  # units
            'invest_cost': 1.0,  # $/unit of capacity
            'loan_life': 40.0,
            'loan_rate': 0.10,
            'global_discount_rate': 0,
            'process_life': 40,
            'p_0': 2020,  # the "myopic base year" to which all prices are discounted
            'vintage': 2020,  # the vintage of the new 'tech'
            'p_e': 2100,  # last year in the myopic view
        },
        'expected_model_cost': 409037.657,
        'expected_undiscounted_cost': 409037.657,
    }
]


@pytest.mark.parametrize('test_case', params, ids=[p['ID'] for p in params])
def test_loan_costs(test_case: LoanCostTestCase) -> None:
    """
    Test the loan cost calculations
    """
    # we will test with a 1% error to accommodate the approximation of GDR=0
    model_cost, undiscounted_cost = loan_costs(**test_case['input'])
    assert model_cost == pytest.approx(test_case['expected_model_cost'], rel=0.01)
    assert undiscounted_cost == pytest.approx(test_case['expected_undiscounted_cost'], rel=0.01)


@pytest.mark.parametrize(
    'test_case',
    params_with_zero_gdr,
    ids=[p['ID'] for p in params_with_zero_gdr],
)
def test_loan_costs_with_zero_gdr(test_case: LoanCostTestCase) -> None:
    """
    Test the formula with zero for GDR to make sure it is handled correctly.  The formula
    risks division by zero if this is not correct.
    """
    model_cost, undiscounted_cost = loan_costs(**test_case['input'])
    assert model_cost == pytest.approx(test_case['expected_model_cost'], abs=0.01)
    assert undiscounted_cost == pytest.approx(test_case['expected_undiscounted_cost'], abs=0.01)
