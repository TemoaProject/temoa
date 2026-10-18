"""Capture every output row for zero-hurdle regression against d5148dbb.

Run in a fresh process with PYTHONHASHSEED=0 for reproducible model ordering.
The reference was captured before changing model or reporting code.
"""

import argparse
import contextlib
import gzip
import json
import sqlite3
import tomllib
from pathlib import Path
from typing import Any

from pyomo.environ import value

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from tests.conftest import TEST_DATA_PATH, _build_test_db

CASES = {
    'utopia': ('utopia_data', 'utopia'),
    'test_system': ('test_system', 'test_system'),
    'mediumville': ('mediumville', 'mediumville'),
    'seasonal_storage': ('seasonal_storage', 'seasonal_storage'),
    'survival_curve': ('survival_curve', 'survival_curve'),
    'annualised_demand': ('annualised_demand', 'annualised_demand'),
    'myopic_utopia': ('utopia_data', 'utopia_myopic'),
}


def capture_outputs(db_path: Path) -> dict[str, Any]:
    """Read all output tables, including empty ones, in column order."""
    with contextlib.closing(sqlite3.connect(db_path)) as con:
        tables = con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name GLOB 'output_*' "
            'ORDER BY name'
        ).fetchall()
        outputs = {}
        for (table,) in tables:
            columns = [row[1] for row in con.execute(f'PRAGMA table_info("{table}")')]
            order = ', '.join(str(i + 1) for i in range(len(columns)))
            rows = con.execute(f'SELECT * FROM "{table}" ORDER BY {order}').fetchall()
            outputs[table] = {'columns': columns, 'rows': rows}
        return outputs


def capture_cases(
    work_dir: Path, zero_mode: str, *, skip_size_limited: bool = False
) -> dict[str, Any]:
    """Solve existing cases with Gurobi and capture their complete outputs."""
    from gurobipy import GRB, GurobiError

    work_dir.mkdir(parents=True, exist_ok=True)
    snapshots: dict[str, Any] = {}
    for name, (source, config_name) in CASES.items():
        db_path = work_dir / f'{name}.sqlite'
        _build_test_db(db_path, [TEST_DATA_PATH / f'{source}.sql'])
        with contextlib.closing(sqlite3.connect(db_path)) as con:
            if zero_mode == 'missing':
                con.execute('DROP TABLE IF EXISTS hurdle_rate')
            elif zero_mode == 'explicit':
                con.execute(
                    'INSERT INTO hurdle_rate(region, tech, vintage, rate) '
                    'SELECT region, tech, vintage, 0 FROM cost_invest'
                )
            con.commit()
        config_path = Path(__file__).parent / 'testing_configs' / f'config_{config_name}.toml'
        settings = tomllib.loads(config_path.read_text())
        settings.pop('solver_name', None)
        settings.update(
            input_database=db_path,
            output_database=db_path,
            solver={'name': 'gurobi_direct', 'options': {'Threads': 1, 'Method': 1}},
        )
        config = TemoaConfig(output_path=work_dir, silent=True, **settings)
        sequencer = TemoaSequencer(config)
        try:
            sequencer.start()
        except GurobiError as error:
            if not skip_size_limited or error.errno != GRB.Error.SIZE_LIMIT_EXCEEDED:
                raise
            snapshots[name] = {
                'skip_reason': f'{name} exceeds the Gurobi size-limited license: {error}'
            }
            continue
        snapshots[name] = {
            'objective': float(value(sequencer.pf_solved_instance.total_cost))
            if sequencer.pf_solved_instance is not None
            else None,
            'tables': capture_outputs(db_path),
        }
    return snapshots


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('work_dir', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument(
        '--zero-mode', choices=['default', 'explicit', 'missing'], default='default'
    )
    parser.add_argument('--skip-size-limited', action='store_true')
    args = parser.parse_args()
    result = capture_cases(args.work_dir, args.zero_mode, skip_size_limited=args.skip_size_limited)
    with gzip.open(args.output, 'wt', encoding='utf-8') as stream:
        json.dump(result, stream, sort_keys=True)
