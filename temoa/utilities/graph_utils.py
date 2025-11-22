# temoa/utilities/graph_utils.py
"""
Utility functions for calculating node positions for network graphs.

These functions provide deterministic starting positions for nodes based on
their layer (role) and sector, which helps the physics-based layout engine
in vis.js converge to a cleaner and more readable state faster.
"""

from __future__ import annotations

import json
import logging
import math
import random
import uuid
from typing import TYPE_CHECKING, Any, TypeVar, cast

import networkx as nx

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from temoa.model_checking.network_model_data import EdgeTuple
    from temoa.types.core_types import Commodity, Sector, Technology

    GraphType = TypeVar(
        'GraphType',
        nx.Graph[Commodity | Technology | str],
        nx.DiGraph[Commodity | Technology | str],
        nx.MultiGraph[Commodity | Technology | str],
        nx.MultiDiGraph[Commodity | Technology | str],
    )
else:
    # At runtime, use the base types which are not subscripted.
    # The TypeVar still enforces that the graph type is one of these.
    GraphType = TypeVar('GraphType', nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)


def convert_graph_to_json[GraphType: (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)](
    nx_graph: GraphType,
    override_node_properties: dict[str, Any] | None,
    override_edge_properties: dict[str, Any] | None,
    verbosity: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Helper to convert a single NetworkX graph to JSON-serializable lists."""
    nodes_data: list[dict[str, Any]] = []
    node_ids_map: dict[Any, str] = {}

    for node_obj, attrs in nx_graph.nodes(data=True):
        node_id_str = str(node_obj)
        node_ids_map[node_obj] = node_id_str
        node_entry: dict[str, Any] = {'id': node_id_str}
        if 'label' not in attrs:
            node_entry['label'] = node_id_str
        for key, value in attrs.items():
            try:
                # Test if the value is JSON serializable
                json.dumps(value)
                node_entry[key] = value
            except (TypeError, OverflowError):
                # If not, fall back to a string representation
                if verbosity >= 2:
                    logger.debug(
                        "Node %s attr '%s' not JSON serializable, converting to string.",
                        node_id_str,
                        key,
                    )
                node_entry[key] = str(value)
        if override_node_properties:
            node_entry.update({k: v for k, v in override_node_properties.items() if k != 'id'})
        nodes_data.append(node_entry)

    edges_data: list[dict[str, Any]] = []
    for u_obj, v_obj, attrs in nx_graph.edges(data=True):
        edge_entry: dict[str, Any] = {
            'from': node_ids_map[u_obj],
            'to': node_ids_map[v_obj],
        }
        if 'id' not in attrs and nx_graph.is_multigraph():
            edge_entry['id'] = str(uuid.uuid4())
        for key, value in attrs.items():
            try:
                # Test if the value is JSON serializable
                json.dumps(value)
                edge_entry[key] = value
            except (TypeError, OverflowError):
                # If not, fall back to a string representation
                if verbosity >= 2:
                    logger.debug(
                        "Edge (%s-%s) attr '%s' not JSON serializable, converting to string.",
                        u_obj,
                        v_obj,
                        key,
                    )
                edge_entry[key] = str(value)
        if override_edge_properties:
            edge_entry.update(
                {k: v for k, v in override_edge_properties.items() if k not in {'id', 'from', 'to'}}
            )

        edges_data.append(edge_entry)

    return nodes_data, edges_data


def calculate_source_positions(
    node_layer_map: dict[str, int],
    x_pos: int = 0,
    y_separation: int = 500,
) -> dict[str, dict[str, Any]]:
    """
    Calculates fixed (x, y) positions for SOURCE nodes (Layer 1) only.

    Args:
        node_layer_map: Mapping from commodity name to layer ID (1, 2, or 3).
        x_pos: The fixed horizontal coordinate for all source nodes.
        y_separation: The vertical distance between source nodes.

    Returns:
        A dictionary mapping only source node names to their position attributes.
        e.g., {'SourceA': {'x': 0, 'y': 0, 'fixed': True}}
    """
    positions = {}
    # Filter for source nodes (layer 1) and sort them for consistent layout
    source_nodes = sorted([node for node, layer in node_layer_map.items() if layer == 1])

    if not source_nodes:
        return {}

    # Calculate a starting y-offset to center the group vertically
    num_nodes = len(source_nodes)
    start_y = -((num_nodes - 1) * y_separation) / 2

    for i, node_name in enumerate(source_nodes):
        y_pos = start_y + i * y_separation
        # Set fixed position only for these source nodes
        positions[node_name] = {'x': x_pos, 'y': y_pos, 'fixed': True}

    return positions


def calculate_initial_positions(
    node_layer_map: dict[str, int],
    commodity_to_primary_sector: dict[Commodity, Sector],
    unique_sectors: Sequence[Sector] | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Calculates an initial (x, y) layout for all nodes to provide a better
    starting point for the physics engine.

    - Source nodes (Layer 1) are fixed on the left.
    - Other nodes are arranged in clusters based on their primary sector,
      with the clusters themselves arranged in a large circle.
    """
    positions: dict[str, dict[str, Any]] = {}

    # Prepare to lay out the remaining (non-fixed) nodes: all layers except 1
    nodes_to_place = {cast('Commodity', n) for n, layer in node_layer_map.items() if layer != 1}
    if not nodes_to_place:
        return positions

    # Use provided unique_sectors if available; else derive from mapping
    sectors_to_place = (
        sorted(unique_sectors)
        if unique_sectors
        else sorted({s for c, s in commodity_to_primary_sector.items() if c in nodes_to_place})
    )
    # ------------------------------------

    if not sectors_to_place:
        return positions

    # Arrange sector "anchors" in a large circle
    layout_radius = 2000  # The radius of the main circle for sectors
    jitter_radius = 1000  # How far nodes can be from their sector anchor
    sector_anchors = {}
    num_sectors = len(sectors_to_place)

    for i, sector in enumerate(sectors_to_place):
        angle = (i / num_sectors) * 2 * math.pi
        cx = layout_radius * math.cos(angle)
        cy = layout_radius * math.sin(angle)
        sector_anchors[sector] = (cx, cy)

    # Place each remaining node near its sector's anchor point
    for node_name in nodes_to_place:
        primary_sector = commodity_to_primary_sector.get(node_name)
        if not primary_sector or primary_sector not in sector_anchors:
            # Place nodes without a sector or a new sector at the center
            cx, cy = 0, 0
        else:
            cx, cy = sector_anchors[primary_sector]

        # Stable jitter derived from node name
        seed = uuid.uuid5(uuid.NAMESPACE_DNS, node_name).int
        rand_angle = ((seed % 3600) / 3600.0) * 2 * math.pi
        rand_radius = (seed // 3600) % jitter_radius
        x = cx + rand_radius * math.cos(rand_angle)
        y = cy + rand_radius * math.sin(rand_angle)

        # Add the position but DO NOT set 'fixed: True'
        positions[node_name] = {'x': x, 'y': y}

    return positions


def calculate_tech_graph_positions(
    all_edges: Iterable[EdgeTuple],
) -> dict[Technology, dict[str, Any]]:
    """
    Calculates an initial (x, y) layout for the technology graph.
    All technologies are arranged in clusters by sector, with clusters
    arranged in a large circle. No nodes are fixed.
    """
    positions = {}

    # 1. Identify all unique sectors present in the technology list
    sectors_to_place = sorted({tech.sector for tech in all_edges if tech.sector})

    if not sectors_to_place:
        # If no sectors, just return empty positions and let physics handle it
        return {}

    # 2. Arrange sector "anchors" in a large circle
    layout_radius = 2500  # Use a large radius to ensure initial separation
    jitter_radius = 600  # Controls the size of the initial clusters
    sector_anchors = {}
    num_sectors = len(sectors_to_place)

    for i, sector in enumerate(sectors_to_place):
        angle = (i / num_sectors) * 2 * math.pi
        cx = layout_radius * math.cos(angle)
        cy = layout_radius * math.sin(angle)
        sector_anchors[sector] = (cx, cy)

    # 3. Place each technology node near its sector's anchor point with jitter
    for edge_tuple in all_edges:
        primary_sector = edge_tuple.sector
        if not primary_sector or primary_sector not in sector_anchors:
            # Place nodes without a defined sector at the center
            cx, cy = 0, 0
        else:
            cx, cy = sector_anchors[primary_sector]

        # Apply deterministic "jitter" to prevent stacking (stable per-tech)
        seed = uuid.uuid5(uuid.NAMESPACE_DNS, str(edge_tuple.tech)).int
        rng = random.Random(seed)
        rand_angle = rng.uniform(0, 2 * math.pi)
        rand_radius = rng.uniform(0, jitter_radius)
        x = cx + rand_radius * math.cos(rand_angle)
        y = cy + rand_radius * math.sin(rand_angle)

        positions[edge_tuple.tech] = {'x': x, 'y': y}

    return positions
