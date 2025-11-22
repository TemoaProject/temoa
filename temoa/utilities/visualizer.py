# temoa/utilities/visualizer.py
"""
Tools for converting NetworkX graphs to interactive vis.js visualizations.

This module provides the `nx_to_vis` function which takes one or two
NetworkX graphs and generates a self-contained HTML file for exploration.
It includes features for toggling between views, filtering by sector or node
name, and an interactive configuration panel.

This code is designed to replace previous graphing dependencies like `gravis`.
"""

from __future__ import annotations

import copy
import json
import logging
import uuid
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

import networkx as nx

from temoa.utilities.graph_utils import (
    GraphType,
    convert_graph_to_json,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from temoa.types.core_types import Commodity, Sector, Technology

logger = logging.getLogger(__name__)


def deep_merge_dicts(source: dict[str, Any], destination: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries."""
    for key, source_value in source.items():
        dest_value = destination.get(key)
        if isinstance(source_value, dict) and isinstance(dest_value, dict):
            deep_merge_dicts(source_value, dest_value)
        else:
            destination[key] = source_value
    return destination


def make_nx_graph(
    connections: Iterable[tuple[Commodity, Technology, Commodity, Sector | None]],
    edge_attributes_map: dict[tuple[str, str, str, str | None], dict[str, Any]],
    node_layer_map: dict[str, int],
    node_positions: dict[str, dict[str, Any]],
    commodity_to_primary_sector: dict[Commodity, Sector],
    driven_tech_names: set[Technology],
    other_orphan_names: set[Technology],
    demand_orphan_names: set[Technology],
    driven_commodities: set[Commodity],
    other_orphan_commodities: set[Commodity],
    demand_orphan_commodities: set[Commodity],
) -> nx.MultiDiGraph[str]:
    """
    Make an nx graph, grouping parallel edges to prevent label overlap.
    """

    dg: nx.MultiDiGraph[str] = nx.MultiDiGraph()
    connections = tuple(connections)  # Freeze for multiple iterations

    node_styles_by_layer = {
        1: {'size': 25, 'shape': 'ellipse'},
        2: {'size': 15, 'shape': 'dot'},
        3: {'size': 20, 'shape': 'box'},
    }
    default_node_style = {'size': 15, 'shape': 'dot'}

    # 1. Add all nodes first to ensure they exist before adding edges
    all_nodes_in_connections = {c[0] for c in connections} | {c[2] for c in connections}
    for node_name in sorted(all_nodes_in_connections):  # Sort for consistency
        if node_name in dg:
            continue
        layer = node_layer_map.get(node_name, 2)
        style = node_styles_by_layer.get(layer, default_node_style)
        pos_attrs = node_positions.get(node_name, {})
        group_name = commodity_to_primary_sector.get(node_name)

        # Start with the base attributes for the node.
        node_attrs: dict[str, Any] = {
            'label': node_name,
            'title': f'Commodity: {node_name}\nLayer: {layer}\nSector: {group_name or "N/A"}',
            'group': group_name,
            'size': style.get('size'),
            'shape': style.get('shape'),
            'borderWidth': 2,  # Default
            'color': {},  # Initialize the color object
            **pos_attrs,
        }

        # Now, conditionally modify the attributes
        color_obj = node_attrs['color']

        # Set background color and alwaysVisible flag based on layer
        if layer == 1:
            color_obj['background'] = '#2ca02c'
            node_attrs['alwaysVisible'] = True  # Now this is safe to do
        elif layer == 3:
            color_obj['background'] = '#78facf'

        # Set border color based on special status
        if node_name in demand_orphan_commodities:
            color_obj['border'] = '#d62728'
            node_attrs['borderWidth'] = 4
        elif node_name in other_orphan_commodities:
            color_obj['border'] = '#ff7f0e'
            node_attrs['borderWidth'] = 4
        elif node_name in driven_commodities:
            color_obj['border'] = '#1f77b4'
            node_attrs['borderWidth'] = 4

        # Add shadow and update title for highlighted nodes
        if node_attrs['borderWidth'] > 2:
            node_attrs['shadow'] = {'enabled': True, 'color': 'rgba(0,0,0,0.5)', 'x': 2, 'y': 2}
            status = 'Unknown'
            if node_name in demand_orphan_commodities:
                status = 'Connected to Demand Orphan'
            elif node_name in other_orphan_commodities:
                status = 'Connected to Other Orphan'
            elif node_name in driven_commodities:
                status = 'Connected to Driven Tech'
            node_attrs['title'] += f'\nStatus: {status}'

        dg.add_node(node_name, **node_attrs)

    # 2. Group technologies by their input/output commodity pair
    grouped_edges: dict[tuple[Commodity, Commodity], list[dict[str, Any]]] = defaultdict(list)
    for ic, tech, oc, sector in connections:
        edge_key = (ic, tech, oc, sector)
        attrs = edge_attributes_map.get(edge_key, {})
        grouped_edges[(ic, oc)].append({'tech': tech, 'sector': sector, 'attrs': attrs})

    # 3. Create a single, combined edge for each group
    for (ic, oc), techs_info in grouped_edges.items():
        combined_attrs: dict[str, Any] = {}
        tech_names = [info['tech'] for info in techs_info]

        # Combine labels: Show up to 2 names, then "X techs"
        if len(tech_names) <= 2:
            combined_attrs['label'] = ', '.join(tech_names)
        else:
            combined_attrs['label'] = f'{len(tech_names)} technologies'

        # Combine tooltips (titles) to list all techs
        tooltip_lines = []
        # Sort by tech name for a consistent order in the tooltip
        for info in sorted(techs_info, key=lambda x: x['tech']):
            tech_name = info['tech']
            sector_name = info.get('sector', 'N/A')

            tech_type_info = ''
            if tech_name in demand_orphan_names:
                tech_type_info = ' [Demand Orphan]'
            elif tech_name in other_orphan_names:
                tech_type_info = ' [Other Orphan]'
            elif tech_name in driven_tech_names:
                tech_type_info = ' [Driven Tech]'

            tooltip_lines.append(f'- {tech_name} (Sector: {sector_name}){tech_type_info}')

        combined_attrs['title'] = f'Technologies ({ic} → {oc}):\n' + '\n'.join(tooltip_lines)

        # Combine visual properties
        all_sectors = {info['sector'] for info in techs_info if info['sector']}
        if len(all_sectors) > 1:
            combined_attrs['color'] = '#888888'
        elif len(all_sectors) == 1:
            # Find a tech that actually has the sector
            tech_with_sector = next((info for info in techs_info if info['sector']), techs_info[0])
            combined_attrs['color'] = tech_with_sector['attrs'].get('color', '#888888')

        # If any underlying edge is dashed, the combined edge is dashed.
        if any(info['attrs'].get('dashes', False) for info in techs_info):
            combined_attrs['dashes'] = True

        combined_attrs['value'] = sum(info['attrs'].get('value', 1) for info in techs_info)
        multi_edge_key = f'{ic}-{oc}-{uuid.uuid4().hex[:8]}'
        dg.add_edge(ic, oc, key=multi_edge_key, **combined_attrs)

    return dg


def nx_to_vis(
    nx_graph: GraphType,
    output_filename: Path,
    html_title: str = 'NetworkX to vis.js Graph',
    vis_options: dict[str, Any] | None = None,
    override_node_properties: dict[str, Any] | None = None,
    override_edge_properties: dict[str, Any] | None = None,
    sectors: Sequence[Sector] | None = None,
    color_legend_map: dict[str, str] | None = None,
    style_legend_map: list[dict[str, Any]] | None = None,
    secondary_graph: GraphType | None = None,
    primary_view_name: str = 'Commodity View',
    secondary_view_name: str = 'Technology View',
    *,
    show_browser: bool = True,
) -> str | None:
    """
    Generates an interactive HTML file and its assets (CSS, JS) for graph visualization.
    """
    nodes_data_primary, edges_data_primary = convert_graph_to_json(
        nx_graph, override_node_properties, override_edge_properties, 0
    )
    nodes_data_secondary: list[dict[str, Any]] = []
    edges_data_secondary: list[dict[str, Any]] = []
    if secondary_graph:
        nodes_data_secondary, edges_data_secondary = convert_graph_to_json(
            secondary_graph, override_node_properties, override_edge_properties, 0
        )

    current_options = copy.deepcopy(DEFAULT_VIS_OPTIONS)
    if vis_options:
        deep_merge_dicts(vis_options, current_options)

    try:
        template_dir = Path(__file__).parent / 'network_vis_templates'
        html_template = (template_dir / 'graph_template.html').read_text(encoding='utf-8')
        css_template = (template_dir / 'graph_styles.css').read_text(encoding='utf-8')
        js_template = (template_dir / 'graph_script.js').read_text(encoding='utf-8')
    except FileNotFoundError:
        logger.exception(
            "Template files not found. Ensure the 'network_vis_templates' directory exists next to "
            'visualizer.py.'
        )
        return None

    # Prepare all data for injection into the HTML
    graph_data = {
        'nodes_json_primary': nodes_data_primary,
        'edges_json_primary': edges_data_primary,
        'nodes_json_secondary': nodes_data_secondary,
        'edges_json_secondary': edges_data_secondary,
        'options_json_str': current_options,
        'sectors_json_str': sorted(sectors) if sectors else [],
        'color_legend_json_str': color_legend_map or {},
        'style_legend_json_str': style_legend_map or [],
        'primary_view_name': primary_view_name,
        'secondary_view_name': secondary_view_name,
    }

    try:
        output_filename.parent.mkdir(parents=True, exist_ok=True)
        output_filename.with_name('graph_styles.css').write_text(css_template, encoding='utf-8')
        output_filename.with_name('graph_script.js').write_text(js_template, encoding='utf-8')

        html_content = html_template.replace('__HTML_PAGE_TITLE__', html_title).replace(
            '__GRAPH_DATA_JSON__', json.dumps(graph_data)
        )
        output_filename.write_text(html_content, encoding='utf-8')
        abs_path = str(output_filename.resolve())
    except OSError:
        logger.exception('Failed to write graph visualization files.')
        return None
    else:
        logger.info('Generated graph HTML at: %s', abs_path)
        if show_browser:
            import webbrowser

            webbrowser.open('file://' + abs_path)
        return abs_path


DEFAULT_VIS_OPTIONS = {
    'autoResize': True,
    'nodes': {
        'shape': 'dot',
        'size': 16,
        'font': {'size': 14, 'color': '#333'},
        'borderWidth': 2,
    },
    'edges': {
        'width': 2,
        'smooth': {'type': 'continuous', 'roundness': 0.5},
        'arrows': {'to': {'enabled': False, 'scaleFactor': 1}},
    },
    'physics': {
        'enabled': False,
        'barnesHut': {
            'gravitationalConstant': -15000,
            'springConstant': 0.04,
            'springLength': 200,
            'damping': 0.09,
            'avoidOverlap': 0.1,
        },
        'solver': 'barnesHut',
        'minVelocity': 0.75,
        'timestep': 0.05,
        'stabilization': {'enabled': False},
    },
    'interaction': {
        'hover': True,
        'dragNodes': True,
        'dragView': True,
        'zoomView': True,
        'tooltipDelay': 200,
        'navigationButtons': False,
        'keyboard': {'enabled': True, 'bindToWindow': False},
    },
    'layout': {'randomSeed': None, 'improvedLayout': True},
    'configure': {
        'enabled': True,
        'showButton': False,  # We have our own header, so hide the default floating button
        'container': None,  # We will set this dynamically in the HTML
    },
}
