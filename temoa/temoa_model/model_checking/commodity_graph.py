"""
A quick & dirty graph of the commodity network for troubleshooting purposes.  Future
development may enhance this quite a bit.... lots of opportunity!
"""

import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import networkx as nx
import plotly.graph_objects as go

from temoa.temoa_model.model_checking.network_model_data import (
    NetworkModelData,
    Tech,
)
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
GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.


Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  2/14/24

"""

logger = logging.getLogger(__name__)

# --- Constants for Styling (Consider moving to config or a dedicated style module) ---
NODE_LAYER_COLORS = {1: 'limegreen', 2: 'violet', 3: 'darkorange'}
NODE_LAYER_SIZES = {1: 20, 2: 10, 3: 15}  # Adjusted for Plotly's scale
DEFAULT_EDGE_COLOR = 'black'
DEFAULT_EDGE_WIDTH = 1
NEG_COST_EDGE_COLOR = 'green'
NEG_COST_EDGE_WIDTH = 2  # Plotly uses width, not weight for thickness
DRIVEN_TECH_EDGE_COLOR = 'blue'
DRIVEN_TECH_EDGE_WIDTH = 1.5
OTHER_ORPHAN_EDGE_COLOR = 'yellow'  # May need adjustment for visibility
OTHER_ORPHAN_EDGE_WIDTH = 2
DEMAND_ORPHAN_EDGE_COLOR = 'red'
DEMAND_ORPHAN_EDGE_WIDTH = 2.5


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
    Generate graph for region/period from network data.
    :param region: Region of interest.
    :param period: Period of interest.
    :param network_data: Data showing all edges to be graphed.
    :param demand_orphans: Iterable of demand orphan technologies.
    :param other_orphans: Iterable of other orphan technologies.
    :param driven_techs: Iterable of "driven" technologies in LinkedTech pairs.
    :param config: Temoa configuration object.
    """
    # Determine node layers based on commodity type
    # Layer 1: Source commodities
    # Layer 2: Physical/Intermediate commodities
    # Layer 3: Demand commodities
    node_layers: Dict[str, int] = {}
    for commodity_name in network_data.all_commodities:
        node_layers[commodity_name] = 2  # Default to physical
    for commodity_name in network_data.source_commodities:
        node_layers[commodity_name] = 1
    for commodity_name in network_data.demand_commodities.get((region, period), []):
        node_layers[commodity_name] = 3

    edge_attributes: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

    # Process all available technologies
    all_tech_connections = {
        (tech.ic, tech.name, tech.oc)
        for tech in network_data.available_techs.get((region, period), [])
    }

    for ic, tech_name, oc in all_tech_connections:
        edge_key = (ic, tech_name, oc)
        attributes = {'color': DEFAULT_EDGE_COLOR, 'width': DEFAULT_EDGE_WIDTH}
        characteristics = network_data.tech_data.get(tech_name, {})
        if characteristics.get('neg_cost', False):
            attributes['color'] = NEG_COST_EDGE_COLOR
            attributes['width'] = NEG_COST_EDGE_WIDTH
        edge_attributes[edge_key] = attributes

    # Override for driven techs
    for tech in driven_techs:
        edge_key = (tech.ic, tech.name, tech.oc)
        edge_attributes[edge_key] = {
            'color': DRIVEN_TECH_EDGE_COLOR,
            'width': DRIVEN_TECH_EDGE_WIDTH,
        }
        all_tech_connections.add(edge_key)  # Ensure it's in the set

    # Override for other orphans
    for tech in other_orphans:
        edge_key = (tech.ic, tech.name, tech.oc)
        edge_attributes[edge_key] = {
            'color': OTHER_ORPHAN_EDGE_COLOR,
            'width': OTHER_ORPHAN_EDGE_WIDTH,
        }
        all_tech_connections.add(edge_key)

    # Override for demand orphans (highest precedence for styling)
    for tech in demand_orphans:
        edge_key = (tech.ic, tech.name, tech.oc)
        edge_attributes[edge_key] = {
            'color': DEMAND_ORPHAN_EDGE_COLOR,
            'width': DEMAND_ORPHAN_EDGE_WIDTH,
        }
        all_tech_connections.add(edge_key)

    dg = make_nx_graph(
        connections=all_tech_connections,
        edge_attributes_map=edge_attributes,
        node_layer_map=node_layers,
    )

    # Loop finder
    try:
        for cycle in nx.simple_cycles(G=dg):
            if len(cycle) < 2:  # Ignore self-loops if not meaningful
                continue
            logger.warning(
                'Found cycle in region %s, period %d. No action needed if this is correct:',
                region,
                period,
            )
            cycle_path = ' --> '.join(cycle) + f' --> {cycle[0]}'
            logger.info('  %s', cycle_path)
    except nx.NetworkXError as e:
        logger.warning(
            'NetworkX exception encountered during cycle detection: %s. '
            'Loop evaluation NOT performed.',
            e,
        )

    if config.plot_commodity_network:
        filename_label = f'{region}_{period}'
        _graph_connections(
            directed_graph=dg,
            file_label=filename_label,
            output_path=config.output_path,
            graph_title=f'Commodity Network: {region} - Period {period}',
        )


def make_nx_graph(
    connections: Iterable[Tuple[str, str, str]],
    edge_attributes_map: Dict[Tuple[str, str, str], Dict[str, Any]],
    node_layer_map: Dict[str, int],
) -> nx.MultiDiGraph:
    """
    Make a NetworkX MultiDiGraph of the commodity network.

    :param connections: An iterable of connections (input_comm, tech_name, output_comm).
    :param edge_attributes_map: A dictionary mapping edge keys (ic, tech, oc)
                                to their attributes (e.g., {'color': 'red', 'width': 2}).
    :param node_layer_map: A dictionary mapping commodity names to their layer index (1, 2, or 3).
    :return: A NetworkX MultiDiGraph.
    """
    dg = nx.MultiDiGraph()

    for ic, tech_name, oc in connections:
        # Add input commodity node
        if ic not in dg:
            layer_ic = node_layer_map.get(ic, 2)  # Default to layer 2 if not found
            dg.add_node(
                ic,
                label=ic,  # For display
                layer=layer_ic,
                color=NODE_LAYER_COLORS.get(layer_ic, 'gray'),
                size=NODE_LAYER_SIZES.get(layer_ic, 10),
                title=f'Commodity: {ic}\nLayer: {layer_ic}',  # Tooltip
            )
        # Add output commodity node
        if oc not in dg:
            layer_oc = node_layer_map.get(oc, 2)  # Default to layer 2 if not found
            dg.add_node(
                oc,
                label=oc,
                layer=layer_oc,
                color=NODE_LAYER_COLORS.get(layer_oc, 'gray'),
                size=NODE_LAYER_SIZES.get(layer_oc, 10),
                title=f'Commodity: {oc}\nLayer: {layer_oc}',
            )

        edge_attrs = edge_attributes_map.get(
            (ic, tech_name, oc),
            {'color': DEFAULT_EDGE_COLOR, 'width': DEFAULT_EDGE_WIDTH, 'label': tech_name},
        )
        # Ensure label is present for the edge
        edge_attrs.setdefault('label', tech_name)

        dg.add_edge(
            ic,
            oc,
            key=tech_name,  # Useful for MultiDiGraph if multiple techs connect same commodities
            label=edge_attrs['label'],  # For display
            color=edge_attrs['color'],
            width=edge_attrs.get('width', DEFAULT_EDGE_WIDTH),  # Plotly uses 'width'
            title=f'Technology: {tech_name}',  # Tooltip
        )
    return dg


def _graph_connections(
    directed_graph: nx.MultiDiGraph,
    file_label: str,
    output_path: Path,
    graph_title: str = 'Commodity Network',
    graph_height: int = 1000,
):
    """
    Make an HTML file containing the network graph using Plotly.

    :param directed_graph: The NetworkX graph to plot.
    :param file_label: The base name for the output file.
    :param output_path: The output directory.
    :param graph_title: Title for the graph.
    :param graph_height: Height of the graph in pixels.
    """
    if not directed_graph.nodes:
        logger.warning('Graph is empty. Skipping Plotly visualization.')
        return

    # Use a layout algorithm from NetworkX for node positions
    # Spring layout is common, but others (kamada_kawai, fruchterman_reingold) can be tried
    try:
        # For layered graphs, shell_layout or multipartite_layout might be better
        # if you can define shells/layers explicitly for positioning.
        # For now, let's try to use the 'layer' attribute if possible,
        # otherwise fall back to spring_layout.

        # A simple way to use layers for y-positioning:
        pos = {}
        layer_nodes = {layer: [] for layer in NODE_LAYER_COLORS.keys()}
        for node, data in directed_graph.nodes(data=True):
            layer_nodes.get(data.get('layer', 2), []).append(node)

        # Spread nodes within layers, and separate layers along y-axis
        y_coords = {1: 0.8, 2: 0.5, 3: 0.2}  # Layer 1 at top, 3 at bottom
        x_spacing = 1.0 / (max(len(n_list) for n_list in layer_nodes.values()) + 1)

        for layer, nodes_in_layer in layer_nodes.items():
            for i, node in enumerate(nodes_in_layer):
                pos[node] = ((i + 1) * x_spacing, y_coords.get(layer, 0.5))

        # If pos is empty or something went wrong, fallback to spring_layout
        if not pos or len(pos) != len(directed_graph.nodes()):
            logger.info('Using spring_layout as layered positioning was incomplete.')
            pos = nx.spring_layout(directed_graph, k=0.5, iterations=50, seed=42)

    except Exception as e:
        logger.warning('Failed to compute spring layout, falling back to random: %s', e)
        pos = nx.random_layout(directed_graph, seed=42)

    edge_traces = []

    for edge in directed_graph.edges(data=True, keys=True):
        u, v, key, data = edge
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        # Create a trace for each edge to customize color, width, and hover
        edge_trace = go.Scatter(
            x=[x0, x1, None],  # x-coordinates of the edge
            y=[y0, y1, None],  # y-coordinates of the edge
            line=dict(
                width=data.get('width', DEFAULT_EDGE_WIDTH),
                color=data.get('color', DEFAULT_EDGE_COLOR),
            ),
            hoverinfo='text',
            text=data.get('title', data.get('label', '')),  # Edge tooltip
            mode='lines',
        )
        edge_traces.append(edge_trace)

    node_x = []
    node_y = []
    node_colors = []
    node_sizes = []
    node_texts = []  # For hover text
    node_labels = []  # For visible labels

    for node, data in directed_graph.nodes(data=True):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_colors.append(data.get('color', 'grey'))
        node_sizes.append(data.get('size', 10))
        node_texts.append(data.get('title', data.get('label', node)))
        node_labels.append(data.get('label', node))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',  # Show markers and text labels
        hoverinfo='text',
        text=node_texts,  # Text for hover
        textfont=dict(size=10),
        textposition='top center',  # Position of the visible labels
        marker=dict(
            showscale=False,
            color=node_colors,
            size=node_sizes,
            line_width=1,
            line_color='black',
        ),
        customdata=node_labels,  # Store labels here if needed for callbacks
        # Or directly use node_labels for 'text' if hover is sufficient
    )
    # For visible labels directly on nodes
    node_trace.text = node_labels

    fig = go.Figure(
        data=edge_traces + [node_trace],  # Combine edge traces and node trace
        layout=go.Layout(
            title=graph_title,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text='Graph generated using Plotly and NetworkX',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0.005,
                    y=-0.002,
                )
            ]
            if not directed_graph.edges()  # Add annotation only if there are edges
            else [],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=graph_height,
            plot_bgcolor='white',  # Set background color
        ),
    )

    # Add edge labels (as annotations for better control)
    # This can get crowded for dense graphs.
    annotations = []
    for u, v, _key, data in directed_graph.edges(data=True, keys=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        label = data.get('label', '')
        if label:  # Only add annotation if label exists
            annotations.append(
                dict(
                    x=(x0 + x1) / 2,
                    y=(y0 + y1) / 2,
                    xref='x',
                    yref='y',
                    text=label,
                    showarrow=False,
                    font=dict(size=8, color=data.get('color', DEFAULT_EDGE_COLOR)),
                    bgcolor='rgba(255,255,255,0.6)',  # Slight background for readability
                )
            )
    fig.update_layout(annotations=annotations)

    filename = f'Commodity_Graph_{file_label}.html'
    output_file_path = output_path / filename
    output_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure dir exists

    try:
        fig.write_html(str(output_file_path), auto_open=False)
        logger.info('Successfully exported graph to %s', output_file_path)
    except Exception as e:
        # Catching a generic Exception as Plotly can raise various errors
        logger.error(
            'Failed to export the network graph to HTML using Plotly. Error: %s',
            e,
        )
