from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import MagicMock

import networkx as nx
import pytest

from temoa.core.config import TemoaConfig
from temoa.model_checking.commodity_graph import visualize_graph
from temoa.types.core_types import Period, Region


@pytest.fixture
def mock_config() -> MagicMock:
    config = MagicMock(spec=TemoaConfig)
    config.plot_commodity_network = True
    config.output_path = Path('./')
    config.cycle_count_limit = 100
    config.cycle_length_limit = 1
    return config


@pytest.fixture
def cycle_graph() -> nx.MultiDiGraph[str]:
    dg: nx.MultiDiGraph[str] = nx.MultiDiGraph()
    # Create two cycles: (A->B->A) length 2, (C->D->E->C) length 3
    dg.add_edge('A', 'B')
    dg.add_edge('B', 'A')
    dg.add_edge('C', 'D')
    dg.add_edge('D', 'E')
    dg.add_edge('E', 'C')
    # Add some other nodes/edges to make it look like a real graph
    dg.add_node('A', layer=1, sector='S1')
    dg.add_node('B', layer=2, sector='S1')
    dg.add_node('C', layer=1, sector='S2')
    dg.add_node('D', layer=2, sector='S2')
    dg.add_node('E', layer=3, sector='S2')
    return dg


def test_cycle_limits_logging(
    mock_config: MagicMock,
    cycle_graph: nx.MultiDiGraph[str],
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that cycles are logged according to length limit."""
    mock_config.cycle_length_limit = 3

    with caplog.at_level(logging.INFO):
        # We need to mock generate_commodity_graph to return our controlled graph
        import temoa.model_checking.commodity_graph as cg

        monkeypatch.setattr(
            cg, 'generate_commodity_graph', MagicMock(return_value=(cycle_graph, {}))
        )
        monkeypatch.setattr(cg, 'generate_technology_graph', MagicMock())
        monkeypatch.setattr(cg, 'nx_to_vis', MagicMock(return_value='path'))

        visualize_graph(
            region=Region('R1'),
            period=Period(2020),
            network_data=MagicMock(),
            demand_orphans=[],
            other_orphans=[],
            driven_techs=[],
            config=mock_config,
        )

    # Should only log cycles of length >= 3
    # (C->D->E->C) is length 3
    # (A->B->A) is length 2, should be skipped
    assert any(
        'Cycle detected' in record.message
        and 'C' in record.message
        and 'D' in record.message
        and 'E' in record.message
        for record in caplog.records
    )
    assert not any(
        'Cycle detected' in record.message and 'A' in record.message and 'B' in record.message
        for record in caplog.records
    )


def test_cycle_count_limit(
    mock_config: MagicMock,
    cycle_graph: nx.MultiDiGraph[str],
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that cycle detection stops after cycle_count_limit."""
    mock_config.cycle_count_limit = 1
    mock_config.cycle_length_limit = 1

    with caplog.at_level(logging.INFO):
        import temoa.model_checking.commodity_graph as cg

        monkeypatch.setattr(
            cg, 'generate_commodity_graph', MagicMock(return_value=(cycle_graph, {}))
        )
        monkeypatch.setattr(cg, 'generate_technology_graph', MagicMock())
        monkeypatch.setattr(cg, 'nx_to_vis', MagicMock(return_value='path'))

        visualize_graph(
            region=Region('R1'),
            period=Period(2020),
            network_data=MagicMock(),
            demand_orphans=[],
            other_orphans=[],
            driven_techs=[],
            config=mock_config,
        )

    # Should only log 1 cycle and then the warning
    # nx.simple_cycles might return them in different order depending on version/impl
    # but it should only log ONE of them.
    cycle_logs = [record.message for record in caplog.records if 'Cycle detected' in record.message]
    assert len(cycle_logs) == 1
    assert 'Cycle detection reached limit of 1 cycles. Stopping.' in caplog.text


def test_cycle_count_limit_zero(
    mock_config: MagicMock,
    cycle_graph: nx.MultiDiGraph[str],
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that cycle_count_limit=0 logs an error and stops immediately."""
    mock_config.cycle_count_limit = 0

    with caplog.at_level(logging.INFO):
        import temoa.model_checking.commodity_graph as cg

        monkeypatch.setattr(
            cg, 'generate_commodity_graph', MagicMock(return_value=(cycle_graph, {}))
        )
        monkeypatch.setattr(cg, 'generate_technology_graph', MagicMock())
        monkeypatch.setattr(cg, 'nx_to_vis', MagicMock(return_value='path'))

        visualize_graph(
            region=Region('R1'),
            period=Period(2020),
            network_data=MagicMock(),
            demand_orphans=[],
            other_orphans=[],
            driven_techs=[],
            config=mock_config,
        )

    assert any(
        'Cycles detected but cycle_count_limit is 0. Stopping.' in record.message
        for record in caplog.records
    )
    assert not any('Cycle detected:' in record.message for record in caplog.records)


def test_cycle_unbounded(
    mock_config: MagicMock,
    cycle_graph: nx.MultiDiGraph[str],
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that cycle_count_limit=-1 allows all cycles."""
    mock_config.cycle_count_limit = -1

    with caplog.at_level(logging.INFO):
        import temoa.model_checking.commodity_graph as cg

        monkeypatch.setattr(
            cg, 'generate_commodity_graph', MagicMock(return_value=(cycle_graph, {}))
        )
        monkeypatch.setattr(cg, 'generate_technology_graph', MagicMock())
        monkeypatch.setattr(cg, 'nx_to_vis', MagicMock(return_value='path'))

        visualize_graph(
            region=Region('R1'),
            period=Period(2020),
            network_data=MagicMock(),
            demand_orphans=[],
            other_orphans=[],
            driven_techs=[],
            config=mock_config,
        )

    assert any(
        'Cycle detected' in record.message and 'C' in record.message for record in caplog.records
    )
    assert any(
        'Cycle detected' in record.message and 'A' in record.message for record in caplog.records
    )
    assert not any('Stopping' in record.message for record in caplog.records)
