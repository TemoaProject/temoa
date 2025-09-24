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
Created on:  3/3/24

"""

import pytest

from temoa.temoa_model.exchange_tech_cost_ledger import CostType, ExchangeTechCostLedger
from tests.utilities.namespace_mock import Namespace

# these are the necessary Temoa elements to make the ledger work
data = {
    'time_season': {1},
    'time_of_day': {1},
    'tech_annual': set(),
    'LifetimeProcess': {('A-B', 't1', 2000): 30, ('B-A', 't1', 2000): 30},
    'processInputs': {('A-B', 2000, 't1', 2000): ('c1',), ('B-A', 2000, 't1', 2000): ('c1',)},
    'processOutputsByInput': {
        ('A-B', 2000, 't1', 2000, 'c1'): ('c1',),
        ('B-A', 2000, 't1', 2000, 'c1'): ('c1',),
    },
    'V_FlowOut': {
        ('A-B', 2000, 1, 1, 'c1', 't1', 2000, 'c1'): 60,
        ('B-A', 2000, 1, 1, 'c1', 't1', 2000, 'c1'): 40,
    },
}


@pytest.fixture
def fake_model():
    """make a fake Temoa Model from data"""
    fake_model = Namespace(**data)
    return fake_model


def test_add_cost_record(fake_model):
    """test adding a record to the ledger"""
    ledger = ExchangeTechCostLedger(fake_model)
    ledger.add_cost_record('A-B', 1, 't1', 2000, 1.99, CostType.FIXED)
    assert len(ledger.cost_records) == 1, 'should have 1 entry in the ledger'


params = [
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
def test_cost_allocation(fake_model, costs):
    """Test the accurate"""
    ledger = ExchangeTechCostLedger(fake_model)
    for record in costs['records']:
        ledger.add_cost_record(*record)
    assert len(ledger.cost_records[CostType.FIXED]) == costs['cost_entries']

    # test for ratio...
    ratio = ledger.get_use_ratio('A', 'B', 2000, 't1', 2000)
    assert ratio == pytest.approx(
        costs['B_ratio']
    ), 'B should get 60% of cost as it receives 60% of flow'
    ratio = ledger.get_use_ratio('B', 'A', 2000, 't1', 2000)
    assert ratio == pytest.approx(
        costs['A_ratio']
    ), 'A should get 40% of cost as it receives 40% of flow'

    # test the outpt cost entries...
    entries = ledger.get_entries()
    assert len(entries) == 2, 'should produce 2 entries for A, B'
    assert entries['A', 2000, 't1', 2000][CostType.FIXED] == costs['A_cost'], "costs didn't match"
    assert entries['B', 2000, 't1', 2000][CostType.FIXED] == costs['B_cost'], "costs didn't match"
