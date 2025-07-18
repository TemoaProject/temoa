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
Created on:  3/11/24

"""

from itertools import chain
from unittest.mock import MagicMock

import pytest

from temoa.temoa_model.model_checking import network_model_data
from temoa.temoa_model.model_checking.commodity_network import CommodityNetwork

# a couple of test cases with diagrams in the flow...
params = [
    # let's model this basic faulty network as a trial:
    #     - t4(2) -> p3
    #   /
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    #
    #             p2 -> t5 -> d2
    # the above should produce:
    # 2 valid techs, t1, t2
    # 2 supply-side orphans (both instances of t4 of differing vintage)
    # 1 demand-side orphan: t3
    {
        'name': 'basic',
        'data': [
            [(t,) for t in ['s1', 'p1', 'p2', 'p3', 'd1', 'd2']],  # all commodities
            [
                (t,)
                for t in [
                    's1',
                ]
            ],  # sources
            [('R1', 2020, 'd1'), ('R1', 2020, 'd2')],  # demands
            [
                ('R1', 's1', 't4', 2000, 'p3', 100),
                ('R1', 's1', 't4', 1990, 'p3', 100),
                ('R1', 's1', 't1', 2000, 'p1', 100),
                ('R1', 'p1', 't2', 2000, 'd1', 100),
                ('R1', 'p2', 't3', 2000, 'd1', 100),
                ('R1', 'p2', 't5', 2000, 'd2', 100),
            ],  # techs
            [
                (2020,),
                (2025,),
            ],  # periods
            [],  # no linked techs
            [],  # no negative cost techs
        ],
        'res': {
            'demands': 2,
            'techs': 6,
            'valid_techs': 2,
            'demand_orphans': 2,
            'other_orphans': 2,
            'unsupported_demands': {'d2'},
        },
    },
    #  p1 -> driven -> d2
    #        |
    #     - t4 -> p3
    #   /
    # s1 -> t1 -> d1
    #
    # bad link tech set.  t4 should be other orphan and the linked "driven" should be a demand side orphan
    {
        'name': 'bad linked tech',
        'data': [
            [(t,) for t in ['s1', 'p3', 'd1', 'd2']],  # all commodities
            [
                (t,)
                for t in [
                    's1',
                ]
            ],  # sources
            [('R1', 2020, 'd1'), ('R1', 2020, 'd2')],  # demands
            [
                ('R1', 's1', 't4', 2000, 'p3', 100),
                ('R1', 'p1', 'driven', 1990, 'd2', 100),
                ('R1', 's1', 't1', 2000, 'd1', 100),
            ],  # techs
            [
                (2020,),
                (2025,),
            ],  # periods
            [('R1', 't4', 'nox', 'driven')],  # t4 drives 'driven' with 'nox' emission
            [],  # no negative cost techs
        ],
        'res': {
            'demands': 2,
            'techs': 3,
            'valid_techs': 1,
            'demand_orphans': 0,
            'other_orphans': 2,  # driven and t4 will both be culled as "other orphans" because t4 is a supply-orphan
            'unsupported_demands': {'d2'},
        },
    },
    {
        # iteration with a "good linked tech"
        # system should give a synthetic link from t4's input to driven
        #  s2 -> driven -> d2
        #        |
        #     - t4 -> d2
        #   /
        # s1 -> t1 -> d1
        #
        #
        'name': 'good linked tech',
        'data': [
            [(t,) for t in ['s1', 'd1', 'd2', 's2']],  # all commodities
            [(t,) for t in ['s1', 's2']],  # sources
            [('R1', 2020, 'd1'), ('R1', 2020, 'd2')],  # demands
            [
                ('R1', 's1', 't4', 2000, 'd2', 100),
                ('R1', 's2', 'driven', 1990, 'd2', 100),
                ('R1', 's1', 't1', 2000, 'd1', 100),
            ],  # techs
            [
                (2020,),
                (2025,),
            ],  # periods
            [('R1', 't4', 'nox', 'driven')],  # t4 drives 'driven' with 'nox' emission
            [],  # no negative cost techs
        ],
        'res': {
            'demands': 2,
            'techs': 3,
            'valid_techs': 3,
            'demand_orphans': 0,
            'other_orphans': 0,
            'unsupported_demands': set(),
        },
    },
]


# we need a small fixture to simulate the database here
@pytest.fixture()
def mock_db_connection(request):
    mock_con = MagicMock()
    mock_cursor = MagicMock()
    mock_con.cursor.return_value = mock_cursor
    mock_execute = MagicMock()
    mock_cursor.execute.return_value = mock_execute
    mock_execute.fetchall.side_effect = request.param['data']
    return mock_con, request.param['res']


@pytest.mark.parametrize(
    'mock_db_connection', params, indirect=True, ids=[d['name'] for d in params]
)
def test_build_from_db(mock_db_connection):
    """test a couple values in the load"""
    conn, expected = mock_db_connection
    network_data = network_model_data._build_from_db(conn)
    assert len(tuple(chain(*network_data.demand_commodities.values()))) == expected['demands'], (
        'demand count failed'
    )
    assert len(network_data.available_techs['R1', 2020]) == expected['techs'], (
        '6 techs are available'
    )


@pytest.mark.parametrize(
    'mock_db_connection', params, indirect=True, ids=[d['name'] for d in params]
)
def test_source_trace(mock_db_connection):
    """analyze the network and check results"""
    conn, expected = mock_db_connection
    network_data = network_model_data._build_from_db(conn)
    cn = CommodityNetwork(region='R1', period=2020, model_data=network_data)
    cn.analyze_network()

    # test the outputs
    assert len(cn.get_valid_tech()) == expected['valid_techs'], 'should have this many valid techs'
    assert len(cn.get_demand_side_orphans()) == expected['demand_orphans'], 'demand orphans'
    assert len(cn.get_other_orphans()) == expected['other_orphans'], 'other orphans'
    assert cn.unsupported_demands() == expected['unsupported_demands'], 'unsupported demands'


@pytest.mark.parametrize(
    'mock_db_connection',
    [
        params[0],
    ],
    indirect=True,
)
def test_clone(mock_db_connection):
    """quick test to ensure cloning is working OK"""
    conn, expected = mock_db_connection
    network_data = network_model_data._build_from_db(conn)
    clone = network_data.clone()
    assert clone is not network_data, 'should be different objects'
    assert network_data.available_techs == clone.available_techs, 'should be a direct copy'
    clone.available_techs.pop(('R1', 2020))  # remove a known region-period
    assert network_data.available_techs != clone.available_techs, 'should be different now'
