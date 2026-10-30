"""
Check that duals are fetched and written when save_duals is on, and not fetched at all when it is
off, on a myopic run of utopia
"""

import contextlib
import shutil
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from pyomo.environ import Suffix
from pyomo.opt import SolverResults

from temoa._internal import run_actions
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel

# unmodified utopia, built from utopia_data.sql by conftest
UTOPIA_DB = Path(__file__).parent / 'testing_outputs' / 'utopia_valid_units.sqlite'

# appsi_highs does not return duals.  utopia is small enough for the size-limited licence that
# comes with gurobipy
SOLVER = 'gurobi'


def run_myopic_utopia(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, save_duals: bool
) -> tuple[Path, list[tuple[int, int]]]:
    """
    Run utopia in myopic mode and return the output database and, for each solve, the number of
    duals in the model and the number of solutions in the results object
    """
    if not UTOPIA_DB.exists():
        pytest.skip('Utopia database not available')
    is_available, _location = TemoaConfig._check_solver_availability(SOLVER)
    if not is_available:
        pytest.skip(f'Solver {SOLVER} not available')

    db = tmp_path / 'utopia_duals.sqlite'
    shutil.copy(UTOPIA_DB, db)
    # Use as_posix() to ensure forward slashes, avoiding escape sequence issues on Windows in TOML
    config_content = (
        f'scenario = "duals"\n'
        f'scenario_mode = "myopic"\n'
        f'input_database = "{db.as_posix()}"\n'
        f'output_database = "{db.as_posix()}"\n'
        f'solver_name = "{SOLVER}"\n'
        f'save_excel = false\n'
        f'save_duals = {"true" if save_duals else "false"}\n'
        f'save_lp_file = false\n'
        f'time_sequencing = "seasonal_timeslices"\n'
        f'days_per_period = 365\n'
        f'reserve_margin = "static"\n'
        f'\n'
        f'[myopic]\n'
        f'view_depth = 2\n'
        f'step_size = 1\n'
        f'evolving = false\n'
        f"evolution_script = ''\n"
    )
    config_file = tmp_path / 'config_duals.toml'
    config_file.write_text(config_content)

    solves: list[tuple[int, int]] = []
    solve_instance = run_actions.solve_instance

    def recording_solve_instance(*args: Any, **kwargs: Any) -> tuple[TemoaModel, SolverResults]:
        model, results = solve_instance(*args, **kwargs)
        dual_suffix = model.component('dual')
        assert isinstance(dual_suffix, Suffix)
        solves.append((len(dual_suffix), len(results.solution)))
        return model, results

    monkeypatch.setattr(run_actions, 'solve_instance', recording_solve_instance)

    config = TemoaConfig.build_config(config_file=config_file, output_path=tmp_path, silent=True)
    TemoaSequencer(config=config).start()

    return db, solves


def test_myopic_save_duals_on_writes_duals(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db, solves = run_myopic_utopia(tmp_path, monkeypatch, save_duals=True)

    assert len(solves) > 1, 'expected more than one myopic step'
    with contextlib.closing(sqlite3.connect(db)) as con:
        written = con.execute(
            "SELECT COUNT(*) FROM output_dual_variable WHERE scenario LIKE 'duals-%'"
        ).fetchone()[0]
        steps_written = con.execute(
            'SELECT COUNT(DISTINCT scenario) FROM output_dual_variable '
            "WHERE scenario LIKE 'duals-%'"
        ).fetchone()[0]

    for n_duals, _n_solutions in solves:
        assert n_duals > 0, 'every myopic step should fetch duals'
    assert steps_written == len(solves), 'every myopic step should write its duals'
    assert written == sum(n_duals for n_duals, _ in solves), 'every fetched dual should be written'


def test_myopic_save_duals_off_fetches_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db, solves = run_myopic_utopia(tmp_path, monkeypatch, save_duals=False)

    assert len(solves) > 1, 'expected more than one myopic step'
    for n_duals, n_solutions in solves:
        assert n_duals == 0, 'no duals should be loaded into the model'
        assert n_solutions == 0, 'the solution should not be copied into the results object'
    with contextlib.closing(sqlite3.connect(db)) as con:
        written = con.execute('SELECT COUNT(*) FROM output_dual_variable').fetchone()[0]
    assert written == 0
