from pathlib import Path

import pytest

from temoa.core.solver_spec import (
    SolverSpec,
    mode_solver_options,
    read_options_file,
    resolve_num_workers,
    resolve_solver_options,
)


def test_option_layers() -> None:
    spec = SolverSpec('gurobi', {'Threads': 8, 'BarConvTol': 1e-5})
    options = resolve_solver_options(
        spec,
        {'Threads': 2},
        fallback_options={'Threads': 20, 'BarConvTol': 1e-2, 'FeasibilityTol': 1e-2},
    )
    assert options['Threads'] == 2
    assert options['BarConvTol'] == 1e-5
    assert options['FeasibilityTol'] == 1e-2
    assert options['Method'] == 2


def test_num_workers() -> None:
    assert resolve_num_workers({'num_workers': 3}, {'num_workers': 6}, 'MGA') == 3
    assert resolve_num_workers({}, {'num_workers': 6}, 'MGA') == 6
    assert resolve_num_workers(None, {}, 'MGA') == 1
    with pytest.raises(ValueError, match='at least 1'):
        resolve_num_workers({'num_workers': 0}, {}, 'MGA')
    with pytest.raises(ValueError, match='must be an integer'):
        resolve_num_workers({'num_workers': 'many'}, {}, 'MGA')


def test_mode_solver_options() -> None:
    assert mode_solver_options({'solver_options': {'Threads': 2}}, 'MOO') == {'Threads': 2}
    assert mode_solver_options(None, 'MOO') == {}
    with pytest.raises(ValueError, match='table of solver options'):
        mode_solver_options({'solver_options': 'options.toml'}, 'MOO')


def test_missing_options_file(tmp_path: Path) -> None:
    assert read_options_file(tmp_path / 'missing.toml') == {}


def test_options_file(tmp_path: Path) -> None:
    source = tmp_path / 'options.toml'
    source.write_text('num_workers = 3\n\n[gurobi]\nThreads = 2\n')
    assert read_options_file(source) == {'num_workers': 3, 'gurobi': {'Threads': 2}}
