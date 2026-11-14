"""
Annual technologies report their flows once a year, in the yearly flow tables
(output_flow_in_summary and output_flow_out_summary), and not in the per-time-slice tables
(output_flow_in and output_flow_out). Every technology's flows are in the yearly tables, so
each per-slice flow summed over the year equals its yearly row. Annual flex technologies keep
their per-slice rows, because their flex is reported per time slice in output_curtailment.
"""

import contextlib
import shutil
import sqlite3
from collections import defaultdict
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig

SCENARIO = 'annual_flow_output'

# (config file, an annual technology that must run, an annual flex technology or None)
cases = [
    ('config_materials.toml', 'MANUFAC_NMC', None),
    ('config_emissions.toml', 'TechAnnual', 'TechAnnualFlex'),
]

FlowKey = tuple[str, int, str | None, str, int, str | None]


@pytest.fixture(scope='module', params=cases, ids=[c[0] for c in cases])
def solved(
    request: Any, tmp_path_factory: Any
) -> Generator[tuple[sqlite3.Connection, str, str | None], None, None]:
    config_file, annual_tech, flex_tech = request.param
    tmp_path = tmp_path_factory.mktemp('data')
    config = TemoaConfig.build_config(
        config_file=Path(__file__).parent / 'testing_configs' / config_file,
        output_path=tmp_path,
        silent=True,
    )
    # a copy, so this scenario's results stay out of the database other tests read
    db = tmp_path / Path(config.input_database).name
    shutil.copyfile(config.input_database, db)
    config.input_database = db
    config.output_database = db
    config.scenario = SCENARIO
    sequencer = TemoaSequencer(config=config)
    sequencer.start()
    with contextlib.closing(sqlite3.connect(sequencer.config.output_database)) as con:
        yield con, annual_tech, flex_tech


def _techs(con: sqlite3.Connection, annual: int, flex: int) -> set[str]:
    rows = con.execute(
        'SELECT tech FROM technology WHERE annual = ? AND flex = ?', (annual, flex)
    ).fetchall()
    return {r[0] for r in rows}


def _flows(con: sqlite3.Connection, table: str) -> dict[FlowKey, float]:
    """Each flow summed over the time slices (if any) of its period."""
    totals: dict[FlowKey, float] = defaultdict(float)
    rows = con.execute(
        f'SELECT region, period, input_comm, tech, vintage, output_comm, flow FROM {table} '
        'WHERE scenario = ?',
        (SCENARIO,),
    ).fetchall()
    for r, p, i, t, v, o, flow in rows:
        totals[r, p, i, t, v, o] += flow
    return totals


def test_annual_flows_only_in_yearly_tables(
    solved: tuple[sqlite3.Connection, str, str | None],
) -> None:
    con, annual_tech, _flex_tech = solved
    annual = _techs(con, annual=1, flex=0)
    assert annual_tech in annual
    for table in ('output_flow_in', 'output_flow_out'):
        per_slice = {key[3] for key in _flows(con, table)}
        assert not per_slice & annual, f'annual technologies in {table}: {per_slice & annual}'
    yearly_out = _flows(con, 'output_flow_out_summary')
    assert sum(flow for key, flow in yearly_out.items() if key[3] == annual_tech) > 0, (
        f'{annual_tech} must run for this test to mean anything'
    )


def test_yearly_tables_equal_summed_slice_tables(
    solved: tuple[sqlite3.Connection, str, str | None],
) -> None:
    con, _annual_tech, _flex_tech = solved
    annual = _techs(con, annual=1, flex=0)
    for per_slice_table, yearly_table in (
        ('output_flow_in', 'output_flow_in_summary'),
        ('output_flow_out', 'output_flow_out_summary'),
    ):
        per_slice = _flows(con, per_slice_table)
        yearly = {k: v for k, v in _flows(con, yearly_table).items() if k[3] not in annual}
        assert per_slice, f'{per_slice_table} is empty'
        assert set(per_slice) == set(yearly), f'{per_slice_table} and {yearly_table} differ'
        for key, flow in per_slice.items():
            assert yearly[key] == pytest.approx(flow, rel=1e-5), key


def test_annual_tech_yearly_input(solved: tuple[sqlite3.Connection, str, str | None]) -> None:
    """An annual technology's yearly input is its yearly output over its efficiency."""
    con, annual_tech, _flex_tech = solved
    efficiency = {
        (r, i, t, v, o): eff
        for r, i, t, v, o, eff in con.execute(
            'SELECT region, input_comm, tech, vintage, output_comm, efficiency FROM efficiency '
            'WHERE tech = ?',
            (annual_tech,),
        )
    }
    flow_in = _flows(con, 'output_flow_in_summary')
    flow_out = _flows(con, 'output_flow_out_summary')
    checked = 0
    for (r, p, i, t, v, o), out in flow_out.items():
        if t != annual_tech:
            continue
        assert flow_in[r, p, i, t, v, o] == pytest.approx(out / efficiency[r, i, t, v, o], rel=1e-5)
        checked += 1
    assert checked > 0


def test_annual_flex_tech_keeps_slice_rows(
    solved: tuple[sqlite3.Connection, str, str | None],
) -> None:
    con, _annual_tech, flex_tech = solved
    if flex_tech is None:
        pytest.skip('no annual flex technology in this model')
    assert flex_tech in _techs(con, annual=1, flex=1)
    per_slice = _flows(con, 'output_flow_out')
    assert sum(flow for key, flow in per_slice.items() if key[3] == flex_tech) > 0, (
        f'{flex_tech} must run for this test to mean anything'
    )


def test_database_made_before_the_yearly_flow_in_table(tmp_path: Path) -> None:
    """A database whose schema predates output_flow_in_summary, and the units column of
    output_flow_out_summary, gets both before the yearly flows are written."""
    config = TemoaConfig.build_config(
        config_file=Path(__file__).parent / 'testing_configs' / 'config_materials.toml',
        output_path=tmp_path,
        silent=True,
    )
    db = tmp_path / 'older_schema.sqlite'
    shutil.copyfile(config.input_database, db)
    with contextlib.closing(sqlite3.connect(db)) as con:
        con.executescript(
            'DROP TABLE output_flow_in_summary; DROP TABLE output_flow_out_summary; '
            'CREATE TABLE output_flow_out_summary (scenario TEXT, region TEXT, sector TEXT, '
            'period INTEGER, input_comm TEXT, tech TEXT, vintage INTEGER, output_comm TEXT, '
            'flow REAL, PRIMARY KEY (scenario, region, period, input_comm, tech, vintage, '
            'output_comm));'
        )
    config.input_database = db
    config.output_database = db
    config.scenario = SCENARIO
    TemoaSequencer(config=config).start()
    with contextlib.closing(sqlite3.connect(db)) as con:
        for table in ('output_flow_in_summary', 'output_flow_out_summary'):
            columns = {row[1] for row in con.execute(f'PRAGMA table_info({table})')}
            assert 'units' in columns, f'{table} has no units column'
            rows = con.execute(
                f'SELECT count(*) FROM {table} WHERE scenario = ?', (SCENARIO,)
            ).fetchone()[0]
            assert rows > 0, f'{table} is empty'
