"""
Unit commitment startups must be counted once for every day a season stands for.

uc_starts.sql describes an 8-day period as two seasons: 'a' stands for 2 days and 'b' for 6.
The same 8 days are also solved as 8 one-day seasons. On every a-day 2 MW start, on every
b-day 1 MW starts, so both representations must start 10 MW per period-year and give the same
startup cost, emissions, inputs and objective.
"""

import contextlib
import shutil
import sqlite3
from pathlib import Path

import pytest
from pyomo.environ import check_optimal_termination, value

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel
from temoa.extensions.unit_commitment.components import startup
from temoa.types.core_types import Commodity, Period, Region, Technology, Vintage

CONFIG_FILE = Path(__file__).parent / 'testing_configs' / 'config_uc_starts.toml'
SOURCE_DB = Path(__file__).parent / 'testing_outputs' / 'uc_starts.sqlite'

REPRESENTATIONS = ['multi_day_seasons', 'one_day_seasons']

# Values from uc_starts.sql
STARTED_PER_YEAR = 10.0  # MW started: 2 MW x 2 a-days + 1 MW x 6 b-days
PERIOD_LENGTH = 5
STARTUP_COST_PER_CAP = 3.0
STARTUP_EMISSIONS_PER_CAP = 5.0
STARTUP_INPUT_PER_CAP = 7.0
COST_EMISSION = 2.0
DEMAND = 120.0

R = Region('region')
P = Period(2020)


def _split_into_one_day_seasons(db: Path) -> None:
    """Replace seasons a (2 days) and b (6 days) with the same 8 days as one-day seasons."""
    day_dsd = [('a1', 0.2), ('a2', 0.2)] + [(f'b{i}', 0.1) for i in range(1, 7)]
    with contextlib.closing(sqlite3.connect(db)) as con:
        con.execute('DELETE FROM demand_specific_distribution')
        con.execute('DELETE FROM time_season')
        con.executemany(
            'INSERT INTO time_season VALUES (?, ?, ?, NULL)',
            [(i, s, 1 / 8) for i, (s, _) in enumerate(day_dsd, start=1)],
        )
        con.executemany(
            'INSERT INTO demand_specific_distribution '
            "VALUES ('region', 2020, ?, ?, 'elc', ?, NULL)",
            [
                (s, tod, dsd if tod == 'day' else 0.0)
                for s, dsd in day_dsd
                for tod in ('day', 'night')
            ],
        )
        con.commit()


@pytest.fixture(scope='module')
def runs(tmp_path_factory: pytest.TempPathFactory) -> dict[str, tuple[TemoaModel, Path]]:
    """Solve both representations, each on its own copy of the database."""
    solved = {}
    for representation in REPRESENTATIONS:
        tmp_path = tmp_path_factory.mktemp(representation)
        db = tmp_path / SOURCE_DB.name
        shutil.copyfile(SOURCE_DB, db)
        if representation == 'one_day_seasons':
            _split_into_one_day_seasons(db)

        config = TemoaConfig.build_config(
            config_file=CONFIG_FILE, output_path=tmp_path, silent=True
        )
        config.input_database = db
        config.output_database = db
        sequencer = TemoaSequencer(config=config)
        sequencer.start()

        assert sequencer.pf_results is not None
        assert check_optimal_termination(sequencer.pf_results)
        assert sequencer.pf_solved_instance is not None
        solved[representation] = (sequencer.pf_solved_instance, db)
    return solved


@pytest.mark.parametrize('representation', REPRESENTATIONS)
def test_startup_model_terms(runs: dict[str, tuple[TemoaModel, Path]], representation: str) -> None:
    """The startup terms in the objective and constraints count every represented day."""
    model, _ = runs[representation]

    cost = startup.uc_startup_cost_rptv(model, R, P, Technology('gen'), Vintage(2020))
    emissions = startup.uc_startup_emissions_rpe(model, R, P, Commodity('co2'))
    startup_input = startup.uc_startup_input_rpc(model, R, P, Commodity('fuel'))

    assert value(cost) == pytest.approx(STARTED_PER_YEAR * STARTUP_COST_PER_CAP)
    assert value(emissions) == pytest.approx(STARTED_PER_YEAR * STARTUP_EMISSIONS_PER_CAP)
    assert value(startup_input) == pytest.approx(STARTED_PER_YEAR * STARTUP_INPUT_PER_CAP)


@pytest.mark.parametrize('representation', REPRESENTATIONS)
def test_startup_outputs(runs: dict[str, tuple[TemoaModel, Path]], representation: str) -> None:
    """Output tables report the startup cost, emissions and input of every represented day."""
    model, db = runs[representation]

    with contextlib.closing(sqlite3.connect(db)) as con:
        var_cost, emiss_cost = con.execute(
            "SELECT SUM(var), SUM(emiss) FROM output_cost WHERE tech = 'gen'"
        ).fetchone()
        emission = con.execute(
            "SELECT SUM(emission) FROM output_emission WHERE tech = 'gen' AND emis_comm = 'co2'"
        ).fetchone()[0]
        startup_input = con.execute(
            'SELECT SUM(flow) FROM output_flow_in '
            "WHERE tech = 'gen' AND input_comm = 'fuel' AND output_comm IS NULL"
        ).fetchone()[0]
        fuel_supplied = con.execute(
            "SELECT SUM(flow) FROM output_flow_out WHERE tech = 'imp_fuel'"
        ).fetchone()[0]
        summed_costs = con.execute(
            'SELECT SUM(d_invest + d_fixed + d_var + d_emiss) FROM output_cost'
        ).fetchone()[0]

    # gen has no cost_variable, so its variable cost is all startup cost
    assert var_cost == pytest.approx(STARTED_PER_YEAR * STARTUP_COST_PER_CAP * PERIOD_LENGTH)
    assert emiss_cost == pytest.approx(
        STARTED_PER_YEAR * STARTUP_EMISSIONS_PER_CAP * COST_EMISSION * PERIOD_LENGTH
    )
    assert emission == pytest.approx(STARTED_PER_YEAR * STARTUP_EMISSIONS_PER_CAP)
    assert startup_input == pytest.approx(STARTED_PER_YEAR * STARTUP_INPUT_PER_CAP)
    # the fuel commodity balance makes imp_fuel supply the generator's fuel plus its startup fuel
    assert fuel_supplied == pytest.approx(DEMAND + STARTED_PER_YEAR * STARTUP_INPUT_PER_CAP)
    assert summed_costs == pytest.approx(value(model.total_cost), rel=1e-10)


@pytest.mark.parametrize('representation', REPRESENTATIONS)
def test_start_cap_is_per_represented_day(
    runs: dict[str, tuple[TemoaModel, Path]], representation: str
) -> None:
    """output_unit_commitment holds the commitment schedule of one day of each season."""
    _, db = runs[representation]

    with contextlib.closing(sqlite3.connect(db)) as con:
        start_cap_by_season = con.execute(
            "SELECT season, SUM(start_cap) FROM output_unit_commitment WHERE tech = 'gen' "
            'GROUP BY season'
        ).fetchall()

    expected_seasons = 2 if representation == 'multi_day_seasons' else 8
    assert len(start_cap_by_season) == expected_seasons
    for season, start_cap in start_cap_by_season:
        assert start_cap == pytest.approx(2.0 if season.startswith('a') else 1.0)


def test_objective_matches_across_representations(
    runs: dict[str, tuple[TemoaModel, Path]],
) -> None:
    """Describing the same days as one-day seasons must not change the objective."""
    multi_day, _ = runs['multi_day_seasons']
    one_day, _ = runs['one_day_seasons']
    assert value(multi_day.total_cost) == pytest.approx(value(one_day.total_cost), rel=1e-9)
