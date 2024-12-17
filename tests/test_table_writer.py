"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.


Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  3/1/24

"""

import pytest

from temoa.temoa_model.table_data_puller import loan_costs

params = [
    {
        'ID': 'near-zero GDR',
        'capacity': 100_000,  # units
        'invest_cost': 1,  # $/unit of capacity
        'loan_life': 40,
        'loan_rate': 0.10,
        'global_discount_rate': 0.000000000001,
        'process_life': 40,
        'p_0': 2020,  # the "myopic base year" to which all prices are discounted
        'vintage': 2020,  # the vintage of the new 'tech'
        'p_e': 2100,  # last year in the myopic view
        'model_cost': 409037.69,
        'undiscounted_cost': 409037.69,
    },
    {
        'ID': 'shortened term',
        'capacity': 100_000,
        'invest_cost': 1,
        'loan_life': 40,
        'loan_rate': 0.08,
        'global_discount_rate': 0.05,
        'process_life': 50,
        'p_0': 2020,
        'vintage': 2030,
        'p_e': 2035,
        'model_cost': 23403.85,
        'undiscounted_cost': 41930.08,
    },
]
params_with_zero_GDR = [
    {
        'ID': 'actual zero GDR',
        'capacity': 100_000,  # units
        'invest_cost': 1,  # $/unit of capacity
        'loan_life': 40,
        'loan_rate': 0.10,
        'global_discount_rate': 0,
        'process_life': 40,
        'p_0': 2020,  # the "myopic base year" to which all prices are discounted
        'vintage': 2020,  # the vintage of the new 'tech'
        'p_e': 2100,  # last year in the myopic view
        'model_cost': 409037.657,
        'undiscounted_cost': 409037.657,
    }
]


@pytest.mark.parametrize('param', params, ids=(param['ID'] for param in params))
def test_loan_costs(param):
    """
    Test the loan cost calculations
    """
    # we will test with a 1% error to accommodate the approximation of GDR=0
    model_cost, undiscounted_cost = loan_costs(**param)
    assert model_cost == pytest.approx(param['model_cost'], rel=0.01)
    assert undiscounted_cost == pytest.approx(param['undiscounted_cost'], rel=0.01)


@pytest.mark.parametrize(
    'param', params_with_zero_GDR, ids=(param['ID'] for param in params_with_zero_GDR)
)
def test_loan_costs_with_zero_GDR(param):
    """
    Test the formula with zero for GDR to make sure it is handled correctly.  The formula
    risks division by zero if this is not correct.
    """
    model_cost, undiscounted_cost = loan_costs(**param)
    assert model_cost == pytest.approx(param['model_cost'], abs=0.01)
    assert undiscounted_cost == pytest.approx(param['undiscounted_cost'], abs=0.01)
