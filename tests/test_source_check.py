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
Created on:  2/6/24

"""

from temoa.model_checking.commodity_network import _mark_good_connections, _visited_dfs


def test_network_analysis():
    """
    tests of the dfs connection maker
    :return:
    """
    # s = source commodity
    # p = physical commodity
    # d = demand commodity (starts for DFS)
    # t = techs

    # s1 -> t1 -> p1 -> t2 -> d1
    start_nodes = {'d1'}
    end_nodes = {'s1'}
    connections = {'d1': {('p1', 't2')}, 'p1': {('s1', 't1')}}
    good_tech = {('s1', 't1', 'p1'), ('p1', 't2', 'd1')}
    discovered_sources, visited = _visited_dfs(
        start_nodes=start_nodes, end_nodes=end_nodes, connections=connections
    )
    t = _mark_good_connections(discovered_sources, visited)
    assert t == good_tech, 'should match up!'

    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -

    start_nodes = {'d1'}
    end_nodes = {'s1'}
    connections = {'d1': {('p1', 't2'), ('p2', 't3')}, 'p1': {('s1', 't1')}}
    good_tech = {('s1', 't1', 'p1'), ('p1', 't2', 'd1')}
    discovered_sources, visited = _visited_dfs(
        start_nodes=start_nodes, end_nodes=end_nodes, connections=connections
    )
    t = _mark_good_connections(discovered_sources, visited)
    assert t == good_tech, 'should match up!'

    #                 - t4  -
    #               /        \
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -

    start_nodes = {'d1'}
    end_nodes = {'s1'}
    connections = {'d1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')}, 'p1': {('s1', 't1')}}
    good_tech = {('s1', 't1', 'p1'), ('p1', 't2', 'd1'), ('p1', 't4', 'd1')}
    discovered_sources, visited = _visited_dfs(
        start_nodes=start_nodes, end_nodes=end_nodes, connections=connections
    )
    t = _mark_good_connections(discovered_sources, visited)
    assert t == good_tech, 'should match up!'

    #                 - t4  -
    #               /        \
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    #
    #             s2 -> t5 -> d2

    start_nodes = {'d1', 'd2'}
    end_nodes = {'s1', 's2'}
    connections = {
        'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
        'p1': {('s1', 't1')},
        'd2': {('s2', 't5')},
    }
    good_tech = {('s1', 't1', 'p1'), ('p1', 't2', 'd1'), ('p1', 't4', 'd1'), ('s2', 't5', 'd2')}
    discovered_sources, visited = _visited_dfs(
        start_nodes=start_nodes, end_nodes=end_nodes, connections=connections
    )
    t = _mark_good_connections(discovered_sources, visited)
    assert t == good_tech, 'should match up!'

    # demand 2 (d2) with no path back to any source...
    #                 - t4  -
    #               /        \
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    #
    #             p3 -> t5 -> d2

    start_nodes = {'d1', 'd2'}
    end_nodes = {'s1'}
    connections = {
        'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
        'p1': {('s1', 't1')},
        'd2': {('p3', 't5')},
    }
    good_tech = {('s1', 't1', 'p1'), ('p1', 't2', 'd1'), ('p1', 't4', 'd1')}
    discovered_sources, visited = _visited_dfs(
        start_nodes=start_nodes, end_nodes=end_nodes, connections=connections
    )
    t = _mark_good_connections(discovered_sources, visited)
    assert t == good_tech, 'should match up!'

    # test with loop: t4 is like storage with I/O the same
    #           - t4 -
    #            \  /
    # s1 -> t1 -> p1 -> t2 -> d1
    #                        /
    #             p2 -> t3  -
    #

    start_nodes = {'d1'}
    end_nodes = {'s1', 's2'}
    connections = {
        'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
        'p1': {('s1', 't1'), ('p1', 't4')},
    }
    good_tech = {('s1', 't1', 'p1'), ('p1', 't2', 'd1'), ('p1', 't4', 'd1'), ('p1', 't4', 'p1')}
    discovered_sources, visited = _visited_dfs(
        start_nodes=start_nodes, end_nodes=end_nodes, connections=connections
    )
    t = _mark_good_connections(discovered_sources, visited)
    assert t == good_tech, 'should match up!'

    # no good tech
    start_nodes = {'d1', 'd2'}
    end_nodes = set()
    connections = {
        'd1': {('p1', 't2'), ('p2', 't3'), ('p1', 't4')},
        'p1': {('s1', 't1')},
        'd2': {('s2', 't5')},
    }
    good_tech = set()
    discovered_sources, visited = _visited_dfs(
        start_nodes=start_nodes, end_nodes=end_nodes, connections=connections
    )
    t = _mark_good_connections(discovered_sources, visited)
    assert t == good_tech, 'should match up!'
