import shutil
import sqlite3
from importlib import resources
from pathlib import Path
from typing import Any

import pyomo.environ as pyo
import pytest
from pyomo.opt import SolverResults

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode
from temoa.extensions.multi_objective_optimization.moo_constants import MooObjective
from temoa.extensions.multi_objective_optimization.moo_sequencer import is_suboptimal

TESTING_OUTPUTS = Path(__file__).parent / 'testing_outputs'


def _gurobi_available() -> bool:
    try:
        import gurobipy

        gurobipy.Model().dispose()
    except Exception:
        return False
    return True


def run_moo(
    tmp_path: Path,
    db_name: str,
    moo_inputs: dict[str, Any],
    extensions: list[str] | None = None,
    **options: Any,
) -> dict[str, dict[str, float]]:
    db = tmp_path / db_name
    if not db.exists():
        shutil.copy(TESTING_OUTPUTS / db_name, db)
    config = TemoaConfig(
        scenario='moo',
        scenario_mode=TemoaMode.MOO,
        input_database=db,
        output_database=db,
        output_path=tmp_path,
        time_sequencing='seasonal_timeslices',
        silent=True,
        MOO=moo_inputs,
        extensions=extensions or [],
        **{'solver': 'appsi_highs', **options},
    )
    TemoaSequencer(config=config).start()
    con = sqlite3.connect(db)
    try:
        rows = con.execute(
            'SELECT scenario, objective_name, total_system_cost FROM output_objective '
            "WHERE scenario LIKE 'moo-%'"
        ).fetchall()
    finally:
        con.close()
    res: dict[str, dict[str, float]] = {}
    for scenario, name, val in rows:
        res.setdefault(scenario, {})[name] = val
    return res


moo_params = [
    pytest.param(
        'utopia.sqlite',
        {'f1': 'cost', 'f2': 'emission', 'ncaps': 4, 'emission_commodities': ['co2']},
        id='utopia_cost_emission',
    ),
    pytest.param(
        'materials.sqlite',
        {'f1': 'cost', 'f2': 'construction_input', 'ncaps': 4},
        id='materials_cost_construction_input',
    ),
    pytest.param(
        'materials.sqlite',
        {
            'f1': 'emission',
            'f2': 'construction_input',
            'ncaps': 3,
            'construction_input_commodities': ['battery_nmc'],
        },
        id='materials_emission_construction_input',
    ),
]


@pytest.mark.parametrize(('db_name', 'moo_inputs'), moo_params)
def test_pareto_front(tmp_path: Path, db_name: str, moo_inputs: dict[str, Any]) -> None:
    res = run_moo(tmp_path, db_name, moo_inputs)
    ncaps = moo_inputs['ncaps']
    assert set(res) == {f'moo-{n}' for n in range(ncaps)}
    f1 = [res[f'moo-{n}'][moo_inputs['f1']] for n in range(ncaps)]
    f2 = [res[f'moo-{n}'][moo_inputs['f2']] for n in range(ncaps)]
    for point in res.values():
        assert set(point) == {objective.value for objective in MooObjective}
    assert f2[0] > f2[-1], 'the objectives should be conflicting in the test data'
    for n in range(ncaps - 1):
        assert f2[n] > f2[n + 1], 'f2 should decrease with the cap'
        assert f1[n] < f1[n + 1], 'f1 should increase as the cap on f2 is tightened'


def _scenarios(db: Path, table: str) -> dict[str, int]:
    con = sqlite3.connect(db)
    try:
        rows = con.execute(f'SELECT scenario, COUNT(*) FROM {table} GROUP BY scenario')
        return dict(rows.fetchall())
    finally:
        con.close()


@pytest.mark.parametrize('save_storage_levels', [True, False])
def test_storage_levels(tmp_path: Path, save_storage_levels: bool) -> None:
    inputs = {'f1': 'cost', 'f2': 'emission', 'ncaps': 3, 'emission_commodities': ['co2']}
    res = run_moo(tmp_path, 'utopia.sqlite', inputs, save_storage_levels=save_storage_levels)
    assert set(res) == {'moo-0', 'moo-1', 'moo-2'}
    storage = _scenarios(tmp_path / 'utopia.sqlite', 'output_storage_level')
    assert set(storage) == (set(res) if save_storage_levels else set())


@pytest.mark.skipif(not _gurobi_available(), reason='needs a licensed Gurobi')
def test_duals(tmp_path: Path) -> None:
    """Every solution has its duals, and the dual of the cap on f2 is the slope of the front"""
    inputs = {'f1': 'cost', 'f2': 'emission', 'ncaps': 5, 'emission_commodities': ['co2']}
    res = run_moo(tmp_path, 'utopia.sqlite', inputs, solver='gurobi', save_duals=True)
    db = tmp_path / 'utopia.sqlite'
    assert set(_scenarios(db, 'output_dual_variable')) == set(res)
    con = sqlite3.connect(db)
    try:
        cap_duals = dict(
            con.execute(
                'SELECT scenario, dual FROM output_dual_variable '
                "WHERE constraint_name = 'moo_f2_cap'"
            ).fetchall()
        )
    finally:
        con.close()
    points = [res[f'moo-{n}'] for n in range(5)]
    slopes = [
        (b['cost'] - a['cost']) / (b['emission'] - a['emission'])
        for a, b in zip(points[:-1], points[1:], strict=True)
    ]
    for n in range(1, 4):
        dual = cap_duals[f'moo-{n}']
        low, high = sorted((slopes[n - 1], slopes[n]))
        assert low - 1e-6 * abs(dual) <= dual <= high + 1e-6 * abs(dual)


def test_workers(tmp_path: Path) -> None:
    inputs = {'f1': 'cost', 'f2': 'emission', 'ncaps': 4, 'emission_commodities': ['co2']}
    (tmp_path / 'serial').mkdir()
    (tmp_path / 'parallel').mkdir()
    serial = run_moo(tmp_path / 'serial', 'utopia.sqlite', {**inputs, 'num_workers': 1})
    parallel = run_moo(
        tmp_path / 'parallel',
        'utopia.sqlite',
        {**inputs, 'num_workers': 3, 'solver_options': {'threads': 1}},
    )
    assert set(serial) == {f'moo-{n}' for n in range(4)}
    assert set(parallel) == set(serial)
    for scenario, values in serial.items():
        for name, val in values.items():
            assert parallel[scenario][name] == pytest.approx(val, rel=1e-4, abs=1e-4)


def test_integer_model(tmp_path: Path) -> None:
    """The workers solve mixed-integer models, which have no duals"""
    db = tmp_path / 'utopia.sqlite'
    shutil.copy(TESTING_OUTPUTS / 'utopia.sqlite', db)
    tables = resources.files('temoa.extensions.discrete_capacity') / 'tables.sql'
    con = sqlite3.connect(db)
    try:
        con.executescript(tables.read_text(encoding='utf-8'))
        con.execute(
            "INSERT INTO limit_discrete_new_capacity VALUES ('utopia', 'E21', 1.5, 'GW', NULL)"
        )
        con.commit()
    finally:
        con.close()
    inputs = {'f1': 'cost', 'f2': 'emission', 'ncaps': 3, 'emission_commodities': ['co2']}
    res = run_moo(tmp_path, 'utopia.sqlite', {**inputs, 'num_workers': 2}, ['discrete_capacity'])
    assert set(res) == {f'moo-{n}' for n in range(3)}


def test_unknown_commodity(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match='not found in the model'):
        run_moo(
            tmp_path,
            'utopia.sqlite',
            {'f1': 'cost', 'f2': 'emission', 'emission_commodities': ['not_a_commodity']},
        )


def test_same_objectives(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match='must be different'):
        run_moo(tmp_path, 'utopia.sqlite', {'f1': 'cost', 'f2': 'cost'})


def add_weight_tables(db: Path) -> None:
    schema = resources.files('temoa.extensions.multi_objective_optimization') / 'tables.sql'
    con = sqlite3.connect(db)
    try:
        con.executescript(schema.read_text(encoding='utf-8'))
        con.commit()
    finally:
        con.close()


def test_custom_objective(tmp_path: Path) -> None:
    """An objective mixing weighted activity, built capacity and net capacity (TXD is a demand
    technology, with both time-sliced and annual flow variables)"""
    tech, w_act, w_built, w_net = 'E01', 1.0, 2.0, 0.5
    db = tmp_path / 'utopia.sqlite'
    run_moo(tmp_path, 'utopia.sqlite', {'f1': 'cost', 'f2': 'emission', 'ncaps': 2})
    add_weight_tables(db)
    con = sqlite3.connect(db)
    try:
        con.execute(
            'INSERT INTO moo_activity_weight '
            "SELECT DISTINCT 'coal', region, period, tech, vintage, ?, NULL "
            'FROM output_flow_out WHERE tech IN (?, ?)',
            (w_act, tech, 'TXD'),
        )
        con.execute(
            'INSERT INTO moo_built_capacity_weight '
            "SELECT DISTINCT 'coal', region, tech, vintage, ?, NULL "
            'FROM output_built_capacity WHERE tech = ?',
            (w_built, tech),
        )
        con.execute(
            'INSERT INTO moo_net_capacity_weight '
            "SELECT DISTINCT 'coal', region, period, tech, vintage, ?, NULL "
            'FROM output_net_capacity WHERE tech = ?',
            (w_net, tech),
        )
        con.commit()
    finally:
        con.close()

    ncaps = 4
    res = run_moo(tmp_path, 'utopia.sqlite', {'f1': 'cost', 'f2': 'coal', 'ncaps': ncaps})
    assert set(res) == {f'moo-{n}' for n in range(ncaps)}
    coal = [res[f'moo-{n}']['coal'] for n in range(ncaps)]
    cost = [res[f'moo-{n}']['cost'] for n in range(ncaps)]
    for n in range(ncaps - 1):
        assert coal[n] > coal[n + 1]
        assert cost[n] < cost[n + 1]

    con = sqlite3.connect(db)
    try:
        for n in range(ncaps):
            expected = con.execute(
                'SELECT '
                '(SELECT COALESCE(SUM(f.flow * w.weight), 0) * 10 FROM output_flow_out f '
                ' JOIN moo_activity_weight w USING (region, period, tech, vintage) '
                ' WHERE f.scenario = :s) + '
                '(SELECT COALESCE(SUM(c.capacity * w.weight), 0) FROM output_built_capacity c '
                ' JOIN moo_built_capacity_weight w USING (region, tech, vintage) '
                ' WHERE c.scenario = :s) + '
                '(SELECT COALESCE(SUM(c.capacity * w.weight), 0) FROM output_net_capacity c '
                ' JOIN moo_net_capacity_weight w USING (region, period, tech, vintage) '
                ' WHERE c.scenario = :s)',
                {'s': f'moo-{n}'},
            ).fetchone()[0]
            assert coal[n] == pytest.approx(expected, rel=1e-3, abs=1e-3)
    finally:
        con.close()


def test_custom_objective_without_tables(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match='none of the tables'):
        run_moo(tmp_path, 'utopia.sqlite', {'f1': 'cost', 'f2': 'coal'})


def test_custom_objective_not_defined(tmp_path: Path) -> None:
    db = tmp_path / 'utopia.sqlite'
    shutil.copy(TESTING_OUTPUTS / 'utopia.sqlite', db)
    add_weight_tables(db)
    with pytest.raises(ValueError, match='no weights are defined'):
        run_moo(tmp_path, 'utopia.sqlite', {'f1': 'cost', 'f2': 'coal'})


def test_custom_objective_bad_index(tmp_path: Path) -> None:
    db = tmp_path / 'utopia.sqlite'
    shutil.copy(TESTING_OUTPUTS / 'utopia.sqlite', db)
    add_weight_tables(db)
    con = sqlite3.connect(db)
    try:
        con.execute(
            "INSERT INTO moo_built_capacity_weight VALUES ('coal', 'utopia', 'E01', 1960, 1, NULL)"
        )
        con.commit()
    finally:
        con.close()
    with pytest.raises(ValueError, match='do not exist in the model'):
        run_moo(tmp_path, 'utopia.sqlite', {'f1': 'cost', 'f2': 'coal'})


@pytest.mark.parametrize(
    ('status', 'termination', 'message', 'expected'),
    [
        (
            pyo.SolverStatus.warning,
            pyo.TerminationCondition.other,
            'Unable to satisfy optimality tolerances; a sub-optimal solution is available.',
            True,
        ),
        (pyo.SolverStatus.ok, pyo.TerminationCondition.feasible, '', True),
        (
            pyo.SolverStatus.warning,
            pyo.TerminationCondition.infeasible,
            'Model is infeasible',
            False,
        ),
        (pyo.SolverStatus.error, pyo.TerminationCondition.other, 'error', False),
    ],
)
def test_suboptimal_boundary_solves(
    status: Any, termination: Any, message: str, expected: bool
) -> None:
    res = SolverResults()
    res.solver.status = status
    res.solver.termination_condition = termination
    res.solver.message = message
    assert is_suboptimal(res) is expected
