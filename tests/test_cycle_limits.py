import pathlib
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import networkx as nx
import pytest

from temoa.core.config import TemoaConfig
from temoa.model_checking.commodity_graph import detect_cycles


@pytest.fixture
def mock_logger() -> Generator[MagicMock, None, None]:
    """Fixture to safely mock and restore the commodity_graph logger."""
    import temoa.model_checking.commodity_graph as cg

    original_logger = cg.logger
    cg.logger = MagicMock()
    yield cg.logger
    cg.logger = original_logger


def test_detect_cycles_limit(mock_logger: MagicMock) -> None:
    """Test that cycle detection stops after the count limit."""
    # Setup graph with 3 cycles: (A,B), (B,C,D), (E,F)
    g: nx.DiGraph[str] = nx.DiGraph()
    g.add_edges_from([('A', 'B'), ('B', 'A')])
    g.add_edges_from([('B', 'C'), ('C', 'D'), ('D', 'B')])
    g.add_edges_from([('E', 'F'), ('F', 'E')])

    config = MagicMock()
    config.cycle_count_limit = 2
    config.cycle_length_limit = 1

    detect_cycles(g, config)

    # Should have 2 info logs for cycles and 1 warning about reaching the limit
    info_calls = [call for call in mock_logger.info.call_args_list if 'Cycle detected' in str(call)]
    warning_calls = [
        call
        for call in mock_logger.warning.call_args_list
        if 'Reached cycle detection limit' in str(call)
    ]

    assert len(info_calls) == 2
    assert len(warning_calls) == 1


def test_detect_cycles_zero(mock_logger: MagicMock) -> None:
    """Test that cycle detection logs errors when count limit is 0 (strictly not allow)."""
    # Use a graph with 2 cycles
    g: nx.DiGraph[str] = nx.DiGraph()
    g.add_edges_from([('A', 'B'), ('B', 'A')])
    g.add_edges_from([('C', 'D'), ('D', 'C')])

    config = MagicMock()
    config.cycle_count_limit = 0
    config.cycle_length_limit = 1

    detect_cycles(g, config)

    # Should have 1 warning about being in "strictly not allow" mode
    warning_calls = [call for call in mock_logger.warning.call_args_list if 'strictly' in str(call)]
    # Should have 2 ERROR logs for cycles
    error_calls = [
        call for call in mock_logger.error.call_args_list if 'Cycle detected' in str(call)
    ]
    # Should have 0 INFO logs for cycles
    info_calls = [call for call in mock_logger.info.call_args_list if 'Cycle detected' in str(call)]

    assert len(warning_calls) == 1
    assert len(error_calls) == 2
    assert len(info_calls) == 0


def test_detect_cycles_unbounded(mock_logger: MagicMock) -> None:
    """Test that cycle detection is unbounded when count limit is -1."""
    g: nx.DiGraph[str] = nx.DiGraph()
    g.add_edges_from([('A', 'B'), ('B', 'A')])
    g.add_edges_from([('C', 'D'), ('D', 'C')])

    config = MagicMock()
    config.cycle_count_limit = -1
    config.cycle_length_limit = 1

    detect_cycles(g, config)

    # Should have 1 warning for unbounded and 2 info logs for cycles
    unbounded_calls = [
        call for call in mock_logger.warning.call_args_list if 'unbounded' in str(call)
    ]
    info_calls = [call for call in mock_logger.info.call_args_list if 'Cycle detected' in str(call)]

    assert len(unbounded_calls) == 1
    assert len(info_calls) == 2


def test_detect_cycles_length_limit(mock_logger: MagicMock) -> None:
    """Test that cycles below the length limit are filtered out."""
    g: nx.DiGraph[str] = nx.DiGraph()
    g.add_edges_from([('A', 'B'), ('B', 'A')])  # Length 2
    g.add_edges_from([('C', 'D'), ('D', 'E'), ('E', 'C')])  # Length 3

    config = MagicMock()
    config.cycle_count_limit = 100
    config.cycle_length_limit = 2  # Skip cycles of length 2 or less

    detect_cycles(g, config)

    info_calls = [call for call in mock_logger.info.call_args_list if 'Cycle detected' in str(call)]
    assert len(info_calls) == 1
    expected_substrings = ['C -> D -> E -> C', 'C -> E -> D -> C', 'D -> E -> C -> D']
    assert any(s in str(info_calls[0]) for s in expected_substrings)


def test_detect_cycles_error(mock_logger: MagicMock) -> None:
    """Test that NetworkXError is caught and logged as a warning."""
    g: nx.DiGraph[str] = nx.DiGraph()
    config = MagicMock()
    config.cycle_count_limit = 100
    config.cycle_length_limit = 1

    with patch('networkx.simple_cycles', side_effect=nx.NetworkXError('Test Error')):
        detect_cycles(g, config)

    warning_calls = [
        call for call in mock_logger.warning.call_args_list if 'NetworkXError' in str(call)
    ]
    assert len(warning_calls) == 1


@patch('pathlib.Path.is_file', return_value=True)
def test_config_validation(mock_is_file: MagicMock) -> None:
    """Test that TemoaConfig validates cycle detection limits."""
    inp = pathlib.Path('in.sqlite')
    out = pathlib.Path('out.sqlite')
    out_p = pathlib.Path('out')

    # These should be valid
    TemoaConfig(
        scenario='test',
        scenario_mode='perfect_foresight',
        input_database=inp,
        output_database=out,
        output_path=out_p,
        solver_name='cbc',
        cycle_count_limit=100,
        cycle_length_limit=1,
    )
    TemoaConfig(
        scenario='test',
        scenario_mode='perfect_foresight',
        input_database=inp,
        output_database=out,
        output_path=out_p,
        solver_name='cbc',
        cycle_count_limit=-1,
        cycle_length_limit=0,
    )

    # These should raise ValueError
    with pytest.raises(ValueError, match='cycle_count_limit must be >= -1'):
        TemoaConfig(
            scenario='test',
            scenario_mode='perfect_foresight',
            input_database=inp,
            output_database=out,
            output_path=out_p,
            solver_name='cbc',
            cycle_count_limit=-2,
        )

    with pytest.raises(ValueError, match='cycle_length_limit must be >= 0'):
        TemoaConfig(
            scenario='test',
            scenario_mode='perfect_foresight',
            input_database=inp,
            output_database=out,
            output_path=out_p,
            solver_name='cbc',
            cycle_length_limit=-1,
        )
