"""
Copyright (c) 2015 J. F. Hyink
Copyright (c) 2025 Anil Radhakrishnan

SPDX-License-Identifier: MIT

A utility to generate a graph of the commodity network for troubleshooting and
visualization purposes.
"""

import logging
from pathlib import Path
from typing import Iterable, NamedTuple

import networkx as nx
from nx_vis_visualizer.core import nx_to_vis

from temoa.temoa_model.model_checking.network_model_data import (
    NetworkModelData,
    Tech,
)
from temoa.temoa_model.temoa_config import TemoaConfig

logger = logging.getLogger(__name__)

# ==============================================================================
# Graph Styling Constants
# ==============================================================================

# Layer definitions for hierarchical layout
SOURCE_LAYER = 1
PHYSICAL_LAYER = 2
DEMAND_LAYER = 3

# Node styling based on layer
NODE_LAYER_COLORS = {
    SOURCE_LAYER: 'limegreen',
    PHYSICAL_LAYER: 'violet',
    DEMAND_LAYER: 'darkorange',
}
NODE_LAYER_SIZES = {SOURCE_LAYER: 50, PHYSICAL_LAYER: 15, DEMAND_LAYER: 30}

# Edge styling for different technology types
# Colors
DEMAND_ORPHAN_COLOR = 'red'
OTHER_ORPHAN_COLOR = 'yellow'
DRIVEN_TECH_COLOR = 'blue'
NEG_COST_TECH_COLOR = 'green'
DEFAULT_EDGE_COLOR = 'black'

# Weights (rendered as width in the graph)
DEMAND_ORPHAN_WEIGHT = 5
OTHER_ORPHAN_WEIGHT = 3
NEG_COST_TECH_WEIGHT = 3
DRIVEN_TECH_WEIGHT = 2
DEFAULT_EDGE_WEIGHT = 1


class GraphEdge(NamedTuple):
    """Represents a directed connection from an input commodity to an output
    commodity via a technology."""

    ic: str
    tech: str
    oc: str


def _prepare_graph_elements(
    region: str,
    period: int,
    network_data: NetworkModelData,
    demand_orphans: Iterable[Tech],
    other_orphans: Iterable[Tech],
    driven_techs: Iterable[Tech],
) -> tuple[dict[str, int], set[GraphEdge], dict[GraphEdge, dict]]:
    """
    Prepares all necessary data structures for graph generation.

    This function consolidates all technologies, assigns layers to commodities,
    and determines the visual properties (color, width) for each edge based on
    a defined hierarchy.

    Args:
        region: The region of interest.
        period: The period of interest.
        network_data: The data showing all edges to be graphed.
        demand_orphans: A container of demand orphan technologies.
        other_orphans: A container of other orphan technologies.
        driven_techs: The "driven" technologies in LinkedTech pairs.

    Returns:
        A tuple containing:
        - A dictionary mapping commodities to their layer number.
        - A set of all unique GraphEdge objects to be included in the graph.
        - A dictionary mapping each GraphEdge to its visual attributes.
    """
    # 1. Determine layers for all commodities
    layers = {c: PHYSICAL_LAYER for c in network_data.all_commodities}
    layers.update({c: SOURCE_LAYER for c in network_data.source_commodities})
    layers.update({c: DEMAND_LAYER for c in network_data.demand_commodities[region, period]})

    # 2. Consolidate all unique edges to be graphed
    def to_graph_edge(tech: Tech) -> GraphEdge:
        return GraphEdge(ic=tech.ic, tech=tech.name, oc=tech.oc)

    # Create sets for efficient lookups
    demand_orphan_edges = {to_graph_edge(t) for t in demand_orphans}
    other_orphan_edges = {to_graph_edge(t) for t in other_orphans}
    driven_tech_edges = {to_graph_edge(t) for t in driven_techs}
    available_tech_edges = {to_graph_edge(t) for t in network_data.available_techs[region, period]}

    all_edges = available_tech_edges.union(
        demand_orphan_edges, other_orphan_edges, driven_tech_edges
    )

    # 3. Determine attributes for each edge based on a defined hierarchy
    edge_attributes = {}
    for edge in all_edges:
        # The hierarchy is: Demand Orphan > Other Orphan > Driven > Default
        if edge in demand_orphan_edges:
            color, width = DEMAND_ORPHAN_COLOR, DEMAND_ORPHAN_WEIGHT
        elif edge in other_orphan_edges:
            color, width = OTHER_ORPHAN_COLOR, OTHER_ORPHAN_WEIGHT
        elif edge in driven_tech_edges:
            color, width = DRIVEN_TECH_COLOR, DRIVEN_TECH_WEIGHT
        else:
            # Default case for regular technologies
            tech_chars = network_data.tech_data.get(edge.tech, {})
            if tech_chars.get('neg_cost', False):
                color, width = NEG_COST_TECH_COLOR, NEG_COST_TECH_WEIGHT
            else:
                color, width = DEFAULT_EDGE_COLOR, DEFAULT_EDGE_WEIGHT

        edge_attributes[edge] = {'color': color, 'width': width}

    return layers, all_edges, edge_attributes


def generate_graph(
    region: str,
    period: int,
    network_data: NetworkModelData,
    demand_orphans: Iterable[Tech],
    other_orphans: Iterable[Tech],
    driven_techs: Iterable[Tech],
    config: TemoaConfig,
):
    """
    Generates and optionally saves a graph for a specific region and period.

    Args:
        region: The region of interest.
        period: The period of interest.
        network_data: The data showing all edges to be graphed.
        demand_orphans: A container of demand orphan technologies.
        other_orphans: A container of other orphan technologies.
        driven_techs: The "driven" technologies in LinkedTech pairs.
        config: The Temoa configuration object.
    """
    layers, all_edges, edge_attributes = _prepare_graph_elements(
        region, period, network_data, demand_orphans, other_orphans, driven_techs
    )

    dg = make_nx_graph(all_edges, edge_attributes, layers)

    # Find and log any cycles in the graph
    try:
        for cycle in nx.simple_cycles(G=dg):
            if len(cycle) < 2:  # Ignore self-loops (e.g., storage)
                continue
            logger.warning(
                'Found cycle in region %s, period %d. No action needed if this is intentional:',
                region,
                period,
            )
            path = ' --> '.join(cycle) + f' --> {cycle[0]}'
            logger.info('  %s', path)
    except nx.NetworkXError as e:
        logger.warning(
            'NetworkX exception encountered: %s. Loop evaluation NOT performed.',
            e,
        )

    if config.plot_commodity_network:
        filename_label = f'{region}_{period}'
        _graph_connections(
            directed_graph=dg,
            file_label=filename_label,
            output_path=config.output_path,
        )


def make_nx_graph(
    connections: Iterable[GraphEdge],
    edge_attributes: dict[GraphEdge, dict],
    layer_map: dict[str, int],
) -> nx.MultiDiGraph:
    """
    Creates a NetworkX MultiDiGraph from prepared graph elements.

    Args:
        connections: An iterable of GraphEdge objects.
        edge_attributes: A dictionary mapping each GraphEdge to its attributes
                         (e.g., color, width).
        layer_map: A dictionary mapping each commodity to its layer number.

    Returns:
        A NetworkX MultiDiGraph object with all nodes and edges populated.
    """
    dg = nx.MultiDiGraph()
    for edge in connections:
        # Add nodes. NetworkX handles duplicates gracefully.
        for commodity in (edge.ic, edge.oc):
            layer = layer_map[commodity]
            dg.add_node(
                commodity,
                name=commodity,
                layer=layer,
                label=commodity,
                color={'background': NODE_LAYER_COLORS[layer]},
                size=NODE_LAYER_SIZES[layer],
            )

        # Add the edge with its pre-calculated attributes
        attributes = edge_attributes[edge]
        dg.add_edge(
            edge.ic,
            edge.oc,
            label=edge.tech,
            color=attributes['color'],
            width=attributes['width'],
        )
    return dg


def _graph_connections(directed_graph: nx.MultiDiGraph, file_label: str, output_path: Path):
    """
    Generates an HTML file containing the network graph using nx-vis-visualizer.

    Args:
        directed_graph: The NetworkX graph to plot.
        file_label: A label for the output file and title.
        output_path: The output directory.
    """
    vis_options = {
        'configure': {'enabled': True},
        'edges': {
            'smooth': {'type': 'continuous', 'roundness': 0.4},
            'font': {'size': 12, 'align': 'middle'},
            'arrows': {'to': {'enabled': True, 'scaleFactor': 0.7}},
        },
        'nodes': {'font': {'size': 14}},
        'interaction': {
            'navigationButtons': True,
            'hover': True,
            'dragNodes': True,
        },
        'physics': {
            'enabled': True,
            'barnesHut': {
                'gravitationalConstant': -8000,
                'springConstant': 0.04,
                'springLength': 150,
            },
            'stabilization': {'iterations': 1500},
        },
        'layout': {'hierarchical': False},
    }

    filename = f'Commodity_Graph_{file_label}.html'
    full_output_path = output_path / filename
    html_title = f'Commodity Graph - {file_label}'

    try:
        nx_to_vis(
            nx_graph=directed_graph,
            output_filename=str(full_output_path),
            html_title=html_title,
            vis_options=vis_options,
            graph_height='1000px',
            show_browser=False,
            verbosity=1,
        )
    except Exception as e:
        logger.error('Failed to generate or export the network graph. Error: %s', e)
