"""
Copyright (c) 2015 J. F. Hyink
Copyright (c) 2025 Anil Radhakrishnan

SPDX-License-Identifier: MIT

A quick & dirty graph of the commodity network for troubleshooting purposes.  Future
development may enhance this quite a bit.... lots of opportunity!
"""
import logging
from pathlib import Path
from typing import Iterable

import networkx as nx
from nx_vis_visualizer.core import nx_to_vis

from temoa.temoa_model.model_checking.network_model_data import (
    NetworkModelData,
    Tech,
)
from temoa.temoa_model.temoa_config import TemoaConfig

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
    :param network_data: the data showing all edges to be graphed.
                            "orphans" will be added, if they aren't included.
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
        (tech.ic, tech.name, tech.oc)
        for tech in network_data.available_techs[region, period]
    }
    # troll through the tech_data and label things of low importance
    for edge in all_edges:
        tech = edge[1]
        characteristics = network_data.tech_data.get(tech, None)
        if characteristics and characteristics.get("neg_cost", False):
            edge_weights[edge] = 3
            edge_colors[edge] = "green"
        # other growth here...
    # label other things of higher importance (these will override)
    for edge in ((tech.ic, tech.name, tech.oc) for tech in driven_techs):
        edge_colors[edge] = "blue"
        edge_weights[edge] = 2
        all_edges.add(edge)
    for edge in ((tech.ic, tech.name, tech.oc) for tech in other_orphans):
        edge_colors[edge] = "yellow"
        edge_weights[edge] = 3
        all_edges.add(edge)
    for edge in ((tech.ic, tech.name, tech.oc) for tech in demand_orphans):
        edge_colors[edge] = "red"
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
                "Found cycle in region %s, period %d.  No action needed if this is correct:",
                region,
                period,
            )
            res = "  "
            first = cycle[0]
            for node in cycle:
                res += f"{node} --> "
            res += first
            logger.info(res)
    except nx.NetworkXError as e:
        logger.warning(
            "NetworkX exception encountered: %s.  Loop evaluation NOT performed.",
            e,
        )
    if config.plot_commodity_network:
        filename_label = f"{region}_{period}"
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
    Make an HTML file containing the network graph using nx-vis-visualizer.
    Uses a physics-based layout.
    :param directed_graph: The NetworkX graph to plot.
    :param file_label: A label for the output file and title.
    :param output_path: The output directory.
    """
    # Define vis.js options for a force-directed layout similar to gravis.
    vis_options = {
        "configure": {"enabled": True},  # Mimics gravis' show_menu=True
        "edges": {
            # This mimics gravis' edge_curvature=0.4
            "smooth": {"type": "continuous", "roundness": 0.4},
            "font": {"size": 12, "align": "middle"},
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.7}},
        },
        "nodes": {
            "font": {"size": 14}  # Corresponds to node_label_size_factor
        },
        "interaction": {
            "navigationButtons": True,  # Show zoom/fit buttons
            "hover": True,
            "dragNodes": True,  # Mimics gravis' node_drag_fix=True
        },
        # Use a physics-based layout engine, which is the default for gravis.
        "physics": {
            "enabled": True,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "springConstant": 0.04,
                "springLength": 150,
            },
            "stabilization": {"iterations": 1500},
        },

        "layout": {"hierarchical": False}, # heirarchical may be better but this replicates gravis
    }

    filename = f"Commodity_Graph_{file_label}.html"
    full_output_path = output_path / filename
    html_title = f"Commodity Graph - {file_label}"

    try:
        # nx_to_vis handles file writing and logging internally
        nx_to_vis(
            nx_graph=directed_graph,
            output_filename=str(full_output_path),
            html_title=html_title,
            vis_options=vis_options,
            graph_height="1000px",  # Matches original gravis height
            show_browser=False,
            verbosity=1,
        )
    except Exception as e:
        logger.error(
            "Failed to generate or export the network graph into HTML. Error message: %s",
            e,
        )


def make_nx_graph(
    connections, edge_colors, edge_weights, layer_map
) -> nx.MultiDiGraph:
    """
    Make a nx graph of the commodity network. Additional info passed in to embed it
    within the nx data
    :param connections: an iterable container of connections of format
        (input_comm, tech, output_comm)
    :param edge_colors: An map of the layers.  1: source commodity, 2: physical commodity,
        3: demand commodity
    :param edge_weights: color map of edges (technologies).  Non-entries default to black
    :param layer_map: weight map of edges (technologies).  Non-entries default to 1.0
    :return: a nx MultiDiGraph
    """
    dg = nx.MultiDiGraph()  # networkx multi(edge) directed graph
    layer_colors = {1: "limegreen", 2: "violet", 3: "darkorange"}
    node_size = {1: 50, 2: 15, 3: 30}
    for ic, tech, oc in connections:
        # vis.js can take color as a dictionary for more control
        dg.add_node(
            ic,
            name=ic,
            layer=layer_map[ic],
            label=ic,
            color={"background": layer_colors[layer_map[ic]]},
            size=node_size[layer_map[ic]],
        )
        dg.add_node(
            oc,
            name=oc,
            layer=layer_map[oc],
            label=oc,
            color={"background": layer_colors[layer_map[oc]]},
            size=node_size[layer_map[oc]],
        )
        dg.add_edge(
            ic,
            oc,
            label=tech,
            color=edge_colors.get((ic, tech, oc), "black"),
            # IMPORTANT: Changed 'size' to 'width' for vis.js compatibility
            width=edge_weights.get((ic, tech, oc), 1),
        )
    return dg