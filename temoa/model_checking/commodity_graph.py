from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, cast

import networkx as nx

from temoa.utilities.graph_utils import (
    calculate_initial_positions,
    calculate_tech_graph_positions,
)
from temoa.utilities.visualizer import make_nx_graph, nx_to_vis

if TYPE_CHECKING:
    from collections.abc import Iterable

    from temoa.core.config import TemoaConfig
    from temoa.model_checking.network_model_data import EdgeTuple, NetworkModelData
    from temoa.types.core_types import Commodity, Period, Region, Sector, Technology

logger = logging.getLogger(__name__)


def generate_technology_graph(
    all_edges: Iterable[EdgeTuple],
    source_commodities: set[Commodity],
    demand_commodities: set[Commodity],
    sector_colors: dict[Sector, str],
) -> nx.MultiDiGraph[str]:
    """
    Generates a technology-centric graph with a pre-computed initial layout.
    """
    tg: nx.MultiDiGraph[str] = nx.MultiDiGraph()
    tech_positions = calculate_tech_graph_positions(all_edges)

    # Pass 1: Aggregate information for each unique technology.
    tech_info: dict[str, dict[str, Any]] = defaultdict(
        lambda: {'is_source': False, 'is_demand': False, 'sector': None}
    )
    for tech_tuple in all_edges:
        info = tech_info[tech_tuple.tech]
        if tech_tuple.input_comm in source_commodities:
            info['is_source'] = True
        if tech_tuple.output_comm in demand_commodities:
            info['is_demand'] = True
        # Use the sector from the first tuple we see for a given tech
        if not info['sector']:
            info['sector'] = tech_tuple.sector

    # Pass 2: Create a single, correctly styled node for each unique technology.
    for tech_name, info in tech_info.items():
        pos_attrs = tech_positions.get(cast('Technology', tech_name)) or {}
        sector = info['sector']

        color_obj: dict[str, str] = {}
        if sector and (bg := sector_colors.get(sector)):
            color_obj['background'] = bg
        border_width = 1
        title = f'Tech: {tech_name}'

        # Apply styles based on the aggregated status
        if info['is_source']:
            color_obj['border'] = '#2ca02c'  # Green border
            border_width = 4
            title += '\nType: Source Technology'
        if info['is_demand']:
            color_obj['border'] = '#e377c2'  # Magenta/Pink border
            border_width = 4
            title += '\nType: Demand Technology'

        node_attrs: dict[str, Any] = {
            'label': tech_name,
            'title': title + (f'\nSector: {sector}' if sector else ''),
            'shape': 'box',
            'color': color_obj,
            'borderWidth': border_width,
            **pos_attrs,
        }
        tg.add_node(tech_name, **node_attrs)

    # Create edges representing commodity flows
    commodity_map: defaultdict[str, dict[str, set[str]]] = defaultdict(
        lambda: {'producers': set(), 'consumers': set()}
    )
    for tech_tuple in all_edges:
        commodity_map[tech_tuple.output_comm]['producers'].add(tech_tuple.tech)
        commodity_map[tech_tuple.input_comm]['consumers'].add(tech_tuple.tech)

    for commodity, roles in commodity_map.items():
        if commodity in source_commodities or commodity in demand_commodities:
            continue
        for producer in roles['producers']:
            for consumer in roles['consumers']:
                if producer != consumer:
                    tg.add_edge(
                        producer,
                        consumer,
                        label=commodity,
                        title=f'Commodity Flow: {commodity}',
                        arrows='to',
                        color='#555555',
                    )
    return tg


def generate_commodity_graph(
    region: Region,
    period: Period,
    network_data: NetworkModelData,
    demand_orphans: Iterable[EdgeTuple],
    other_orphans: Iterable[EdgeTuple],
    driven_techs: Iterable[EdgeTuple],
) -> tuple[nx.MultiDiGraph[str], dict[Sector, str]]:
    """
    Generates the commodity-centric graph and its associated color scheme.
    In this view, commodities are nodes and technologies are grouped into edges.
    """
    all_edge_tuples = (
        set(network_data.available_techs.get((region, period), set()))
        | set(demand_orphans)
        | set(other_orphans)
        | set(driven_techs)
    )

    # 1. Prepare sector-based mappings for coloring
    unique_sectors = sorted({tech.sector for tech in all_edge_tuples if tech.sector})
    color_palette = [
        '#1f77b4',
        '#ff7f0e',
        '#2ca02c',
        '#d62728',
        '#9467bd',
        '#8c564b',
        '#e377c2',
        '#7f7f7f',
        '#bcbd22',
        '#17becf',
    ]
    sector_colors = {
        sector: color_palette[i % len(color_palette)] for i, sector in enumerate(unique_sectors)
    }
    default_color = '#A9A9A9'

    commodity_sector_counts: defaultdict[Commodity, defaultdict[Sector, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    for tech in all_edge_tuples:
        if tech.sector:
            commodity_sector_counts[tech.input_comm][tech.sector] += 1
            commodity_sector_counts[tech.output_comm][tech.sector] += 1

    commodity_to_primary_sector: dict[Commodity, Sector] = {
        comm: max(counts, key=lambda k: counts[k])
        for comm, counts in commodity_sector_counts.items()
        if counts
    }

    # 2. Define node layers (1: source, 2: intermediate, 3: sink)
    layer_map: dict[str, int] = dict.fromkeys(
        network_data.physical_commodities, 2
    )  # all intermediates
    for c in network_data.source_commodities.get((region, period), []):
        layer_map[c] = 1
    for c in network_data.demand_commodities.get((region, period), []):
        layer_map[c] = 3

    node_positions = calculate_initial_positions(
        layer_map,
        commodity_to_primary_sector,
        unique_sectors,
    )

    # 3. Prepare edge attributes with sector-based coloring
    edge_attributes_map: dict[tuple[str, str, str, str | None], dict[str, Any]] = {}
    all_connections: set[tuple[Commodity, Technology, Commodity, Sector | None]] = {
        (edge_tuple.input_comm, edge_tuple.tech, edge_tuple.output_comm, edge_tuple.sector)
        for edge_tuple in all_edge_tuples
    }

    driven_names = {t.tech for t in driven_techs}
    other_orphan_names = {t.tech for t in other_orphans}
    demand_orphan_names = {t.tech for t in demand_orphans}

    driven_commodities: set[Commodity] = set()
    other_orphan_commodities: set[Commodity] = set()
    demand_orphan_commodities: set[Commodity] = set()

    for ic, tech_name, oc, sector in all_connections:
        key = (ic, tech_name, oc, sector)
        color = default_color
        if sector:
            color = sector_colors.get(sector, default_color)

        attrs: dict[str, Any] = {
            'color': color,
            'value': 1,  # Default thickness
        }

        tech_data = network_data.tech_data.get(tech_name, {})
        if tech_data.get('neg_cost', False):
            attrs['value'] = 3

        if tech_name in driven_names:
            attrs.update({'color': '#1f77b4', 'value': 3, 'dashes': True})
            driven_commodities.update({ic, oc})
        elif tech_name in other_orphan_names:
            attrs.update({'color': '#ff7f0e', 'value': 4, 'dashes': True})
            other_orphan_commodities.update({ic, oc})
        elif tech_name in demand_orphan_names:
            attrs.update({'color': '#d62728', 'value': 6, 'dashes': True})
            demand_orphan_commodities.update({ic, oc})

        edge_attributes_map[key] = attrs

    # 4. Create the NetworkX graph using the utility function
    dg = make_nx_graph(
        all_connections,
        edge_attributes_map,
        layer_map,
        node_positions,
        commodity_to_primary_sector,
        driven_names,
        other_orphan_names,
        demand_orphan_names,
        driven_commodities=driven_commodities,
        other_orphan_commodities=other_orphan_commodities,
        demand_orphan_commodities=demand_orphan_commodities,
    )

    return dg, sector_colors


def visualize_graph(
    region: Region,
    period: Period,
    network_data: NetworkModelData,
    demand_orphans: Iterable[EdgeTuple],
    other_orphans: Iterable[EdgeTuple],
    driven_techs: Iterable[EdgeTuple],
    config: TemoaConfig,
) -> None:
    """
    Generates and saves an interactive HTML file with two graph views if
    config.plot_commodity_network is True.
    """
    # 1. Check the configuration flag first. If false, do nothing.
    if not config.plot_commodity_network:
        logger.info("Skipping network graph generation because 'plot_commodity_network' is false.")
        return

    # --- All generation logic now only runs if the flag is True ---

    # 2. Generate the primary (commodity-centric) graph and its color legend
    commodity_graph, sector_colors = generate_commodity_graph(
        region, period, network_data, demand_orphans, other_orphans, driven_techs
    )

    # 3. Collect all technology tuples needed for the secondary graph
    all_techs_for_period = (
        set(network_data.available_techs.get((region, period), set()))
        | set(demand_orphans)
        | set(other_orphans)
        | set(driven_techs)
    )

    # 4. Generate the secondary (technology-centric) graph
    tech_graph = generate_technology_graph(
        all_techs_for_period,
        network_data.source_commodities.get((region, period), set()),
        network_data.demand_commodities.get((region, period), set()),
        sector_colors,
    )

    # 5. Define the style legend data
    style_legend_map = [
        # Styles for the Commodity View
        {'label': 'Connected to Demand Orphan', 'borderColor': '#d62728', 'borderWidth': 4},
        {'label': 'Connected to Other Orphan', 'borderColor': '#ff7f0e', 'borderWidth': 4},
        {'label': 'Connected to Driven Tech', 'borderColor': '#1f77b4', 'borderWidth': 4},
        # Styles for the Technology View
        {'label': 'Source Technology', 'borderColor': '#2ca02c', 'borderWidth': 4},
        {'label': 'Demand Technology', 'borderColor': '#e377c2', 'borderWidth': 4},
    ]

    # 6. Create the interactive HTML visualization
    output_file = config.output_path / f'Network_Graph_{region}_{period}.html'
    unique_sectors = sorted(sector_colors)

    graph_path = nx_to_vis(
        nx_graph=commodity_graph,
        secondary_graph=tech_graph,
        output_filename=output_file,
        html_title=f'Network Graphs - {region} {period}',
        sectors=unique_sectors,
        color_legend_map=cast('dict[str, str]', sector_colors),
        style_legend_map=style_legend_map,
        show_browser=False,
    )

    if graph_path:
        logger.info('Generated network graphs at: %s', graph_path)
    else:
        logger.error('Failed to generate network graphs')

    # 8. Perform cycle detection on the commodity graph
    try:
        for cycle in nx.simple_cycles(G=commodity_graph):
            if len(cycle) < 2:
                continue
            cycle_str = ' -> '.join(cycle) + f' -> {cycle[0]}'
            logger.info('Cycle detected: %s', cycle_str)
    except nx.NetworkXError as e:
        logger.warning('NetworkXError during cycle detection: %s', e, exc_info=True)
