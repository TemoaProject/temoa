import contextlib
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from pyomo.environ import SolverFactory, check_optimal_termination, value

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.components.reserves import _available_activity_dynamic
from temoa.core.config import TemoaConfig
from temoa.types.core_types import Period, Region, Season, TimeOfDay

if TYPE_CHECKING:
    from temoa.extensions.unit_commitment.core.model import UnitCommitmentModel


def test_dynamic_reserve_counts_offline_capacity(tmp_path: Path) -> None:
    """An offline committed plant still provides derated planning capacity."""
    database = tmp_path / 'reserves.sqlite'
    root = Path(__file__).resolve().parents[1]
    with contextlib.closing(sqlite3.connect(database)) as connection:
        connection.executescript((root / 'temoa/db_schema/temoa_schema_v4.sql').read_text())
        connection.executescript((root / 'temoa/extensions/unit_commitment/tables.sql').read_text())
        connection.execute('INSERT INTO region (region) VALUES (?)', ('R',))
        connection.executemany(
            'INSERT INTO time_period (sequence, period, flag) VALUES (?, ?, ?)',
            [(0, 2020, 'e'), (1, 2025, 'f'), (2, 2030, 'f')],
        )
        connection.execute(
            'INSERT INTO time_season (sequence, season, segment_fraction) VALUES (?, ?, ?)',
            (1, 'year', 1.0),
        )
        connection.executemany(
            'INSERT INTO time_of_day (sequence, tod, hours) VALUES (?, ?, ?)',
            [(1, 'day', 12), (2, 'night', 12)],
        )
        connection.executemany(
            'INSERT INTO commodity (name, flag) VALUES (?, ?)', [('fuel', 's'), ('ELC', 'd')]
        )
        connection.execute(
            'INSERT INTO demand (region, period, commodity, demand) VALUES (?, ?, ?, ?)',
            ('R', 2025, 'ELC', 80.0),
        )
        connection.execute(
            'INSERT INTO planning_reserve_margin (region, margin) VALUES (?, ?)', ('R', 0.3)
        )
        for tech, capacity, cost, cf, derate in [
            ('base', 100.0, 1.0, 1.0, 1.0),
            ('backup', 20.0, 10.0, 0.8, 0.5),
        ]:
            connection.execute(
                'INSERT INTO technology (tech, flag, reserve) VALUES (?, ?, ?)', (tech, 'p', 1)
            )
            connection.execute(
                'INSERT INTO efficiency (region, input_comm, tech, vintage, output_comm, '
                'efficiency) VALUES (?, ?, ?, ?, ?, ?)',
                ('R', 'fuel', tech, 2020, 'ELC', 1.0),
            )
            connection.execute(
                'INSERT INTO existing_capacity (region, tech, vintage, capacity) '
                'VALUES (?, ?, ?, ?)',
                ('R', tech, 2020, capacity),
            )
            connection.execute(
                'INSERT INTO capacity_to_activity (region, tech, c2a) VALUES (?, ?, ?)',
                ('R', tech, 1.0),
            )
            connection.execute(
                'INSERT INTO cost_variable (region, period, tech, vintage, cost) '
                'VALUES (?, ?, ?, ?, ?)',
                ('R', 2025, tech, 2020, cost),
            )
            connection.execute(
                'INSERT INTO reserve_capacity_derate (region, season, tech, vintage, factor) '
                'VALUES (?, ?, ?, ?, ?)',
                ('R', 'year', tech, 2020, derate),
            )
            connection.executemany(
                'INSERT INTO capacity_factor_process (region, season, tod, tech, vintage, '
                'factor) VALUES (?, ?, ?, ?, ?, ?)',
                [('R', 'year', tod, tech, 2020, cf) for tod in ('day', 'night')],
            )
            connection.execute(
                'INSERT INTO unit_commitment (region, tech, unit_capacity, min_output_fraction) '
                'VALUES (?, ?, ?, ?)',
                ('R', tech, 10.0, 0.5),
            )
        connection.commit()

    config = TemoaConfig(
        scenario='reserves',
        scenario_mode='build_only',
        input_database=database,
        output_database=database,
        output_path=tmp_path,
        solver='gurobi_direct',
        time_sequencing='seasonal_timeslices',
        reserve_margin='dynamic',
        extensions=['unit_commitment'],
        silent=True,
    )
    model = cast('UnitCommitmentModel', TemoaSequencer(config).build_model())
    results = SolverFactory('gurobi_direct').solve(model)
    assert check_optimal_termination(results)
    assert value(model.v_capacity['R', 2025, 'backup', 2020]) == pytest.approx(20.0, rel=1e-5)
    for tod in ('day', 'night'):
        assert value(model.v_uc_online['R', 2025, 'year', tod, 'backup', 2020]) == pytest.approx(
            0.0, abs=1e-5
        )
        assert value(
            model.v_flow_out['R', 2025, 'year', tod, 'fuel', 'backup', 2020, 'ELC']
        ) == pytest.approx(0.0, abs=1e-5)
        available = _available_activity_dynamic(
            model, Region('R'), Period(2025), Season('year'), TimeOfDay(tod)
        )
        # (100 + 20 * 0.8 * 0.5) * C2A * SEG = 54, exceeding 80 * 1.3 / 2 = 52.
        assert value(available) == pytest.approx(54.0, rel=1e-5)
