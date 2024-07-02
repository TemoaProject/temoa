"""
A quick & dirty graph of the commodity network for troubleshooting purposes.  Future
development may enhance this quite a bit.... lots of opportunity!
"""
import logging
from pathlib import Path
from typing import Iterable

import gravis as gv
import networkx as nx

from temoa.temoa_model.model_checking.network_model_data import NetworkModelData, Tech
from temoa.temoa_model.temoa_config import TemoaConfig

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
Created on:  2/14/24

"""

logger = logging.getLogger(__name__)


def generate_graph(
    region,
    period,
    network_data: NetworkModelData,
    demand_orphans: Iterable[Tech],
    other_orphans: Iterable[Tech],
    driven_techs: Iterable[Tech],
    config: TemoaConfig,
):
    """
    generate graph for region/period from network data
    :param region: region of interest
    :param period: period of interest
    :param network_data: the data showing all edges to be graphed.  "orphans" will be added, if they aren't included
    :param demand_orphans: container of orphans [orphanage ;)]
    :param other_orphans: container of orphans
    :param driven_techs: the "driven" techs in LinkedTech pairs
    :param config:
    :return:
    """
    layers = {}
    for c in network_data.all_commodities:
        layers[c] = 2  # physical
    for c in network_data.source_commodities:
        layers[c] = 1
    for c in network_data.demand_commodities[region, period]:
        layers[c] = 3

    edge_colors = {}
    edge_weights = {}
    # dev note:  the generators below do 2 things:  put the data in the format expected by the
    #            graphing code and reduce redundant vintages to 1 representation
    # Note that there is a heirarchy here and the latter loops may overwrite earlier color/weight
    # decisions, so primary stuff goes last!
    all_edges = {
        (tech.ic, tech.name, tech.oc) for tech in network_data.available_techs[region, period]
    }
    # troll through the tech_data and label things of low importance
    for edge in all_edges:
        tech = edge[1]
        characteristics = network_data.tech_data.get(tech, None)
        if characteristics and characteristics.get('neg_cost', False):
            edge_weights[edge] = 3
            edge_colors[edge] = 'green'
        # other growth here...
    # label other things of higher importance (these will override)
    for edge in ((tech.ic, tech.name, tech.oc) for tech in driven_techs):
        edge_colors[edge] = 'blue'
        edge_weights[edge] = 2
        all_edges.add(edge)
    for edge in ((tech.ic, tech.name, tech.oc) for tech in other_orphans):
        edge_colors[edge] = 'yellow'
        edge_weights[edge] = 3
        all_edges.add(edge)
    for edge in ((tech.ic, tech.name, tech.oc) for tech in demand_orphans):
        edge_colors[edge] = 'red'
        edge_weights[edge] = 5
        all_edges.add(edge)

    dg = make_nx_graph(all_edges, edge_colors, edge_weights, layers)

    # loop finder...
    try:
        cycles = nx.simple_cycles(G=dg)
        for cycle in cycles:
            cycle = list(cycle)
            if len(cycle) < 2:  # a storage item--not reportable
                continue
            logger.warning(
                'Found cycle in region %s, period %d.  No action needed if this is correct:',
                region,
                period,
            )
            res = '  '
            first = cycle[0]
            for node in cycle:
                res += f'{node} --> '
            res += first
            logger.info(res)
    except nx.NetworkXError as e:
        logger.warning('NetworkX exception encountered: %s.  Loop evaluation NOT performed.', e)
    if config.plot_commodity_network:
        filename_label = f'{region}_{period}'
        _graph_connections(
            directed_graph=dg,
            file_label=filename_label,
            output_path=config.output_path,
        )


def _graph_connections(
    directed_graph: nx.MultiDiGraph | nx.DiGraph,
    file_label: str,
    output_path: Path,
):
    """
    Make an HTML file containing the network graph
    :param file_label: the name of the output file
    :param output_path: the output directory
    :return:
    """
    try:
        fig = gv.d3(
            directed_graph,
            show_menu=True,
            show_node_label=True,
            node_label_data_source='label',
            show_edge_label=True,
            edge_label_data_source='label',
            edge_curvature=0.4,
            graph_height=1000,
            zoom_factor=1.0,
            node_drag_fix=True,
            node_label_size_factor=0.5,
            layout_algorithm_active=True,
        )
    except Exception as e:
        logger.error('Failed to create a figure for the network graph: %s', e)
        return
    filename = f'Commodity_Graph_{file_label}.html'
    output_path = output_path / filename
    try:
        fig.export_html(output_path, overwrite=True)
    except UnicodeEncodeError as e:
        logger.warning(
            'Failed to export the network graph into HTML.  Bad character in names of commodities or '
            'tech?\n  Error message: %s',
            e,
        )
    except Exception as e:
        logger.error('Failed to export the network graph into HTML.  Error message: %s', e)


def make_nx_graph(connections, edge_colors, edge_weights, layer_map) -> nx.MultiDiGraph:
    """
    Make a nx graph of the commodity network.  Additional info passed in to embed it within the nx data
    :param connections: an iterable container of connections of format (input_comm, tech, output_comm)
    :param edge_colors: An map of the layers.  1: source commodity, 2: physical commodity, 3: demand commodity
    :param edge_weights: color map of edges (technologies).  Non-entries default to black
    :param layer_map: weight map of edges (technologies).  Non-entries default to 1.0
    :return: a nx MultiDiGraph
    """
    dg = nx.MultiDiGraph()  # networkx multi(edge) directed graph
    layer_colors = {1: 'limegreen', 2: 'violet', 3: 'darkorange'}
    node_size = {1: 50, 2: 15, 3: 30}
    for ic, tech, oc in connections:
        dg.add_node(
            ic,
            name=ic,
            layer=layer_map[ic],
            label=ic,
            color=layer_colors[layer_map[ic]],
            size=node_size[layer_map[ic]],
        )
        dg.add_node(
            oc,
            name=oc,
            layer=layer_map[oc],
            label=oc,
            color=layer_colors[layer_map[oc]],
            size=node_size[layer_map[oc]],
        )
        dg.add_edge(
            ic,
            oc,
            label=tech,
            color=edge_colors.get((ic, tech, oc), 'black'),
            size=edge_weights.get((ic, tech, oc), 1),
        )
    return dg
