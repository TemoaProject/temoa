"""
A linked technology produces only what its own primary vintage captures. In
linked_tech_vintages.sql, CCS has unlimited capacity and no cost, so any CCS vintage without
its PLANT vintage would supply CO2_CAP for free:

- the 1995 PLANT has no existing capacity, so Temoa skips it while keeping the 1995 CCS
- in myopic runs, the 2000 and 2005 PLANT vintages are never built and are dropped from later
  windows, while CCS, having unlimited capacity, keeps them

PLANT is first worth building in 2010, when BACKUP's price rises.
"""

import contextlib
import shutil
import sqlite3
from collections import defaultdict
from pathlib import Path

import pytest

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig

CAPTURE_PER_ELC = 3.0  # PLANT's emission_activity for CO2 is -3 per unit of ELC
DEMAND = {2000: 1.0, 2005: 100.0, 2010: 100.0}  # CO2_CAP

config_files = ['config_linked_tech_vintages.toml', 'config_linked_tech_vintages_myopic.toml']


@pytest.fixture(scope='module', params=config_files)
def output_db(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory) -> Path:
    tmp_path = tmp_path_factory.mktemp('data')
    config = TemoaConfig.build_config(
        config_file=Path(__file__).parent / 'testing_configs' / request.param,
        output_path=tmp_path,
        silent=True,
    )
    db = tmp_path / Path(config.input_database).name
    shutil.copyfile(config.input_database, db)
    config.input_database = db
    config.output_database = db
    TemoaSequencer(config=config).start()
    return db


def _flow_out(db: Path, tech: str) -> dict[tuple[int, int], float]:
    """A technology's output by (period, vintage), summed over time slices."""
    totals: dict[tuple[int, int], float] = defaultdict(float)
    with contextlib.closing(sqlite3.connect(db)) as con:
        for p, v, flow in con.execute(
            'SELECT period, vintage, flow FROM output_flow_out WHERE tech = ?', (tech,)
        ):
            totals[p, v] += flow
    return totals


def test_linked_output_equals_own_vintage_capture(output_db: Path) -> None:
    plant = _flow_out(output_db, 'PLANT')
    ccs = _flow_out(output_db, 'CCS')
    for p, v in set(plant) | set(ccs):
        assert ccs.get((p, v), 0.0) == pytest.approx(
            CAPTURE_PER_ELC * plant.get((p, v), 0.0), abs=1e-5
        ), f'CCS vintage {v} in {p}'


def test_backup_supplies_the_rest(output_db: Path) -> None:
    ccs = _flow_out(output_db, 'CCS')
    backup = _flow_out(output_db, 'BACKUP')
    for p, demand in DEMAND.items():
        captured = sum(flow for (period, _), flow in ccs.items() if period == p)
        supplied = sum(flow for (period, _), flow in backup.items() if period == p)
        assert captured + supplied == pytest.approx(demand, rel=1e-5), p
        if p < 2010:
            assert supplied == pytest.approx(demand, rel=1e-5), f'BACKUP in {p}'


def test_plant_and_link_run_in_2010(output_db: Path) -> None:
    """PLANT must run for the equality above to test a working link."""
    plant = _flow_out(output_db, 'PLANT')
    assert sum(flow for (p, _), flow in plant.items() if p == 2010) > 0
