"""Full HiGHS solves and input-contract regressions for period/cohort utilization."""

from __future__ import annotations

import contextlib
import hashlib
import sqlite3
from typing import TYPE_CHECKING, Any

import pytest
from pyomo.environ import Constraint, Var, check_optimal_termination, value

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.data_io.hybrid_loader import HybridLoader
from temoa.utilities.master_migration import migrate_database
from tests.conftest import SCHEMA_PATH, TEST_DATA_PATH, _build_test_db

if TYPE_CHECKING:
    from pathlib import Path

    from pyomo.opt import SolverResults

    from temoa.core.model import TemoaModel

    type Run = tuple[str, SolverResults | None, TemoaModel | None, TemoaSequencer]

TOL = 1e-7
INSERT = (
    'INSERT INTO limit_annual_capacity_factor '
    '(region, period, tech_or_group, vintage, output_comm, operator, factor) '
    'VALUES (?, ?, ?, ?, ?, ?, ?)'
)
type Modification = tuple[str, tuple[Any, ...]]


def _case(
    annual: int,
    factors: list[tuple[int | None, int, str, float]],
    modifications: list[Modification] | None = None,
    *,
    myopic: bool = False,
) -> dict[str, Any]:
    """Build isolated variations of the small, shared SQL fixture."""
    mods: list[Modification] = [
        ('UPDATE technology SET annual=?', (annual,)),
        ('DELETE FROM limit_annual_capacity_factor', ()),
    ]
    mods.extend((INSERT, ('R1', p, 'vehicle', v, 'service', op, f)) for p, v, op, f in factors)
    mods.extend(modifications or [])
    suffix = '_myopic' if myopic else ''
    return {
        'name': f'annual={annual}, factors={factors}, myopic={myopic}',
        'filename': f'config_annual_capacity_factor{suffix}.toml',
        'modifications': mods,
    }


def _output(model: TemoaModel, r: str, p: int, t: str, v: int, o: str) -> float:
    """Sum annual service output on either temporal path, without period scaling."""
    component = model.v_flow_out_annual if t in model.tech_annual else model.v_flow_out
    return sum(
        value(flow)
        for key, flow in component.items()
        if key[0] == r and key[1] == p and key[-3:] == (t, v, o)
    )


def _assert_residuals(model: TemoaModel) -> None:
    for constraint in model.limit_annual_capacity_factor_constraint.values():
        body = value(constraint.body)
        if constraint.lower is not None:
            assert body >= value(constraint.lower) - TOL
        if constraint.upper is not None:
            assert body <= value(constraint.upper) + TOL


@pytest.mark.parametrize(
    ('system_test_run', 'last_factor', 'expected_capacity'),
    [
        (
            _case(
                a,
                [(2025, 2025, 'le', 0.5), (2030, 2025, 'le', f)],
                [
                    # Remove cost-free oversupply degeneracy without another binding limit.
                    (
                        'INSERT INTO cost_variable (region, period, tech, vintage, cost) '
                        "VALUES ('R1',2025,'vehicle',2025,0.001), ('R1',2030,'vehicle',2025,0.001)",
                        (),
                    ),
                ],
            ),
            f,
            cap,
        )
        for a in (0, 1)
        for f, cap in ((0.25, 4), (0.5, 2))
    ],
    indirect=['system_test_run'],
)
def test_period_capacity_optimum(
    system_test_run: Run, last_factor: float, expected_capacity: float
) -> None:
    """Changing only the second operating-period factor doubles required capacity."""
    _, results, model, _ = system_test_run
    assert model is not None and check_optimal_termination(results)
    assert value(model.v_new_capacity['R1', 'vehicle', 2025]) == pytest.approx(
        expected_capacity, rel=0, abs=TOL
    )
    assert len(model.limit_annual_capacity_factor_constraint) == 2
    for p, factor in ((2025, 0.5), (2030, last_factor)):
        key = ('R1', p, 'vehicle', 2025, 'service', 'le')
        # This assertion also detects last-row-wins vintage-only broadcasting.
        assert value(model.limit_annual_capacity_factor[key]) == factor
        assert value(model.process_life_frac['R1', p, 'vehicle', 2025]) == 1
        capacity = value(model.v_capacity['R1', p, 'vehicle', 2025])
        assert capacity == pytest.approx(expected_capacity, rel=0, abs=TOL)
        assert _output(model, 'R1', p, 'vehicle', 2025, 'service') == pytest.approx(
            1, rel=0, abs=TOL
        )
        assert value(model.capacity_to_activity['R1', 'vehicle']) == 1
        if not model.tech_annual:
            # Independent hourly availability stays at 1, above either annual limit.
            for s in model.time_season:
                for d in model.time_of_day:
                    assert value(model.capacity_factor_process['R1', s, d, 'vehicle', 2025]) == 1
    _assert_residuals(model)


COHORT_MODS: list[Modification] = [
    (
        'INSERT INTO efficiency (region, input_comm, tech, vintage, output_comm, efficiency) '
        "VALUES ('R1', 'source', 'vehicle', 2030, 'service', 1)",
        (),
    ),
    ("INSERT INTO cost_invest (region, tech, vintage, cost) VALUES ('R1','vehicle',2030,1)", ()),
    (
        'INSERT INTO loan_lifetime_process (region, tech, vintage, lifetime) '
        "VALUES ('R1','vehicle',2030,5)",
        (),
    ),
]
COHORT_FACTORS: list[tuple[int | None, int, str, float]] = [
    (2025, 2025, 'e', 0.5),
    (2030, 2025, 'e', 0.25),
    (2030, 2030, 'e', 0.75),
]


@pytest.mark.parametrize(
    'system_test_run',
    [_case(a, COHORT_FACTORS, COHORT_MODS) for a in (0, 1)],
    indirect=True,
)
def test_two_cohorts(system_test_run: Run) -> None:
    """Both cohorts operate in 2030 with separate factors; 2025 remains independent."""
    _, results, model, _ = system_test_run
    assert model is not None and check_optimal_termination(results)
    assert value(model.v_new_capacity['R1', 'vehicle', 2025]) == pytest.approx(2, rel=0, abs=TOL)
    assert value(model.v_new_capacity['R1', 'vehicle', 2030]) == pytest.approx(
        2 / 3, rel=0, abs=TOL
    )
    assert len(model.limit_annual_capacity_factor_constraint) == 3
    for p, v, factor in ((2025, 2025, 0.5), (2030, 2025, 0.25), (2030, 2030, 0.75)):
        output = _output(model, 'R1', p, 'vehicle', v, 'service')
        capacity = value(model.v_capacity['R1', p, 'vehicle', v])
        assert output / capacity == pytest.approx(factor, rel=0, abs=TOL)
    _assert_residuals(model)


@pytest.mark.parametrize(
    'system_test_run',
    [
        _case(
            a,
            [(2025, 2025, op, 0.5), (2030, 2025, op, 0.25)],
            [
                ('UPDATE demand SET demand=CASE period WHEN 2025 THEN 1 ELSE 0.5 END', ()),
                (
                    'INSERT INTO limit_new_capacity '
                    '(region, tech_or_group, vintage, operator, new_cap) '
                    "VALUES ('R1','vehicle',2025,'e',2)",
                    (),
                ),
                (
                    'INSERT INTO cost_variable (region, period, tech, vintage, cost) '
                    "VALUES ('R1',2025,'vehicle',2025,1), ('R1',2030,'vehicle',2025,1)",
                    (),
                ),
            ],
        )
        for a in (0, 1)
        for op in ('ge', 'e')
    ],
    indirect=True,
)
def test_lower_bound_and_equality(system_test_run: Run) -> None:
    _, results, model, _ = system_test_run
    assert model is not None and check_optimal_termination(results)
    assert _output(model, 'R1', 2025, 'vehicle', 2025, 'service') == pytest.approx(
        1, rel=0, abs=TOL
    )
    assert _output(model, 'R1', 2030, 'vehicle', 2025, 'service') == pytest.approx(
        0.5, rel=0, abs=TOL
    )
    _assert_residuals(model)


@pytest.mark.parametrize(
    ('system_test_run', 'built', 'available'),
    [
        (
            _case(a, [(2025, 2025, 'le', 0.5), (2030, 2025, 'le', 0.25)], [mod]),
            built,
            available,
        )
        for a in (0, 1)
        for mod, built, available in (
            (('UPDATE capacity_to_activity SET c2a=2', ()), 2, 2),
            (('UPDATE lifetime_tech SET lifetime=7', ()), 10, 4),
        )
    ],
    indirect=['system_test_run'],
)
def test_available_capacity_and_c2a(system_test_run: Run, built: float, available: float) -> None:
    """The denominator uses available capacity and C2A once, including partial lifetime."""
    _, results, model, _ = system_test_run
    assert model is not None and check_optimal_termination(results)
    assert value(model.v_new_capacity['R1', 'vehicle', 2025]) == pytest.approx(
        built, rel=0, abs=TOL
    )
    assert value(model.v_capacity['R1', 2030, 'vehicle', 2025]) == pytest.approx(
        available, rel=0, abs=TOL
    )
    ratio = _output(model, 'R1', 2030, 'vehicle', 2025, 'service') / (
        available * value(model.capacity_to_activity['R1', 'vehicle'])
    )
    assert ratio == pytest.approx(0.25, rel=0, abs=TOL)
    _assert_residuals(model)


GROUP_MODS: list[Modification] = [
    ("INSERT INTO region (region) VALUES ('R2')", ()),
    ("INSERT INTO commodity (name, flag) VALUES ('service2','d')", ()),
    ("INSERT INTO technology (tech,flag,sector) VALUES ('other','p','transport')", ()),
    ("INSERT INTO tech_group (group_name) VALUES ('fleet')", ()),
    ("INSERT INTO tech_group_member VALUES ('fleet','vehicle'), ('fleet','other')", ()),
    (
        'INSERT INTO efficiency (region,input_comm,tech,vintage,output_comm,efficiency) '
        "VALUES ('R1','source','vehicle',2025,'service2',1), "
        "('R2','source','other',2025,'service',1), ('R2','source','other',2025,'service2',1)",
        (),
    ),
    ("INSERT INTO capacity_to_activity (region,tech,c2a) VALUES ('R2','other',1)", ()),
    ("INSERT INTO cost_invest (region,tech,vintage,cost) VALUES ('R2','other',2025,1)", ()),
    ("INSERT INTO lifetime_tech (region,tech,lifetime) VALUES ('R2','other',10)", ()),
    (
        'INSERT INTO limit_new_capacity (region,tech_or_group,vintage,operator,new_cap) '
        "VALUES ('R1','vehicle',2025,'e',1), ('R2','other',2025,'e',1)",
        (),
    ),
    ('UPDATE demand SET demand=CASE period WHEN 2025 THEN 0.5 ELSE 0.25 END', ()),
    (
        'INSERT INTO demand (region,period,commodity,demand) '
        "VALUES ('R2',2025,'service',0.5), ('R2',2030,'service',0.25), "
        "('R1',2025,'service2',0.25), ('R1',2030,'service2',0.5), "
        "('R2',2025,'service2',0.25), ('R2',2030,'service2',0.5)",
        (),
    ),
]


@pytest.mark.parametrize(
    'system_test_run',
    [
        _case(
            1,
            [],
            GROUP_MODS
            + [
                (INSERT, (r, p, 'fleet', 2025, o, 'e', f))
                for p, o, f in (
                    (2025, 'service', 0.5),
                    (2030, 'service', 0.25),
                    (2025, 'service2', 0.25),
                    (2030, 'service2', 0.5),
                )
            ]
            + [(INSERT, (r, 2030, 'fleet', 2025, 'service2', 'le', 0.9))],
        )
        for r in ('global', 'R1+R2')
    ],
    indirect=True,
)
def test_groups_regions_and_outputs(system_test_run: Run) -> None:
    """Aggregate a mixed annual/timeslice group while retaining outputs and operators."""
    _, results, model, _ = system_test_run
    assert model is not None and check_optimal_termination(results)
    assert len(model.limit_annual_capacity_factor_constraint) == 5
    for p, o, expected in (
        (2025, 'service', 1),
        (2030, 'service', 0.5),
        (2025, 'service2', 0.5),
        (2030, 'service2', 1),
    ):
        output = sum(
            _output(model, r, p, t, 2025, o) for r, t in [('R1', 'vehicle'), ('R2', 'other')]
        )
        assert output == pytest.approx(expected, rel=0, abs=TOL)
    _assert_residuals(model)


@pytest.mark.parametrize(
    'system_test_run',
    [_case(a, COHORT_FACTORS, COHORT_MODS, myopic=True) for a in (0, 1)],
    indirect=True,
)
def test_myopic_cohort_factors(system_test_run: Run) -> None:
    """A retained cohort receives the later period's factor in the next solve."""
    _, _, _, sequencer = system_test_run
    with contextlib.closing(sqlite3.connect(sequencer.config.output_database)) as con:
        rows = con.execute(
            'SELECT period, vintage, SUM(flow) FROM output_flow_out '
            "WHERE tech='vehicle' AND output_comm='service' GROUP BY period, vintage"
        ).fetchall()
    assert {(p, v): f for p, v, f in rows} == pytest.approx(
        {(2025, 2025): 1, (2030, 2025): 0.5, (2030, 2030): 0.5}, rel=0, abs=TOL
    )


@pytest.mark.parametrize(
    'system_test_run',
    [_case(1, [(None, 2025, 'le', 0.5)], myopic=True)],
    indirect=True,
)
def test_myopic_legacy_broadcast(system_test_run: Run) -> None:
    """A NULL-period row must survive both window filters for the retained cohort."""
    _, _, _, sequencer = system_test_run
    with contextlib.closing(sqlite3.connect(sequencer.config.output_database)) as con:
        rows = con.execute(
            "SELECT period, capacity FROM output_net_capacity WHERE tech='vehicle' ORDER BY period"
        ).fetchall()
    assert rows == [
        (2025, pytest.approx(2, rel=0, abs=TOL)),
        (2030, pytest.approx(2, rel=0, abs=TOL)),
    ]


def _config(db: Path) -> TemoaConfig:
    return TemoaConfig(
        scenario='annual_factor',
        scenario_mode='perfect_foresight',
        input_database=db,
        output_database=db,
        output_path=db.parent / db.stem,
        solver='appsi_highs',
        time_sequencing='seasonal_timeslices',
        silent=True,
    )


def _load(db: Path) -> TemoaModel:
    with contextlib.closing(sqlite3.connect(db)) as con:
        loader = HybridLoader(con, _config(db))
        return loader.model.create_instance(loader.load_data_portal())


@pytest.fixture
def factor_db(tmp_path: Path) -> Path:
    db = tmp_path / 'factor.sqlite'
    _build_test_db(db, [TEST_DATA_PATH / 'annual_capacity_factor.sql'])
    return db


@pytest.mark.parametrize('period', [2020, 2027, 2035, 'all'])
def test_invalid_operating_period(factor_db: Path, period: object) -> None:
    with sqlite3.connect(factor_db) as con:
        con.execute('UPDATE limit_annual_capacity_factor SET period=?', (period,))
    with pytest.raises(ValueError, match='Invalid operating period'):
        _load(factor_db)


def test_inactive_process(factor_db: Path) -> None:
    with sqlite3.connect(factor_db) as con:
        con.execute('UPDATE lifetime_tech SET lifetime=5')
        con.execute('UPDATE limit_annual_capacity_factor SET period=2030')
    with pytest.raises(ValueError, match='No active process'):
        _load(factor_db)


@pytest.mark.parametrize(
    ('column', 'bad_value'),
    [
        ('region', 'unknown'),
        ('tech_or_group', 'missing'),
        ('vintage', 2027),
        ('output_comm', 'missing'),
        ('operator', 'eq'),
    ],
)
def test_invalid_keys(factor_db: Path, column: str, bad_value: object) -> None:
    with sqlite3.connect(factor_db) as con:
        con.execute(f'UPDATE limit_annual_capacity_factor SET {column}=?', (bad_value,))
    with pytest.raises(ValueError, match='Invalid limit_annual_capacity_factor key'):
        _load(factor_db)


@pytest.mark.parametrize(
    'system_test_run',
    [_case(1, [(2025, 2025, 'le', 0.5)])],
    indirect=True,
)
def test_missing_period_row_is_unconstrained(system_test_run: Run) -> None:
    _, results, model, _ = system_test_run
    assert model is not None and check_optimal_termination(results)
    assert set(model.limit_annual_capacity_factor_constraint) == {
        ('R1', 2025, 'vehicle', 2025, 'service', 'le')
    }
    assert value(model.v_new_capacity['R1', 'vehicle', 2025]) == pytest.approx(2, rel=0, abs=TOL)


@pytest.mark.parametrize('reverse', [False, True])
def test_overlap_rejected_before_filtering(factor_db: Path, reverse: bool) -> None:
    with sqlite3.connect(factor_db) as con:
        con.execute('DELETE FROM limit_annual_capacity_factor')
        for p in [2030, None] if reverse else [None, 2030]:
            con.execute(INSERT, ('R1', p, 'vehicle', 2025, 'service', 'le', 0.5))
    with pytest.raises(ValueError, match='Overlapping NULL and explicit periods'):
        _load(factor_db)


def test_myopic_overlap_outside_first_window(factor_db: Path) -> None:
    from temoa.core.modes import TemoaMode

    with sqlite3.connect(factor_db) as con:
        con.execute(INSERT, ('R1', 2030, 'vehicle', 2025, 'service', 'le', 0.25))
    config = _config(factor_db)
    config.scenario_mode = TemoaMode.MYOPIC
    config.myopic_inputs = {'view_depth': 1, 'step_size': 1, 'evolving': False}
    with pytest.raises(ValueError, match='Overlapping NULL and explicit periods'):
        TemoaSequencer(config).start()


def test_malformed_optional_table_is_not_silently_skipped(factor_db: Path) -> None:
    with sqlite3.connect(factor_db) as con:
        con.execute('ALTER TABLE limit_annual_capacity_factor RENAME COLUMN vintage TO wrong')
    with pytest.raises(sqlite3.OperationalError, match='vintage'):
        _load(factor_db)


@pytest.mark.parametrize('period', [None, 2025])
def test_duplicate_keys(factor_db: Path, period: int | None) -> None:
    with sqlite3.connect(factor_db) as con:
        con.execute('UPDATE limit_annual_capacity_factor SET period=?', (period,))
        with pytest.raises(sqlite3.IntegrityError, match='UNIQUE'):
            con.execute(INSERT, ('R1', period, 'vehicle', 2025, 'service', 'le', 0.5))
        # An externally produced table without SQL keys must also fail in the loader.
        con.execute('CREATE TABLE raw_factors AS SELECT * FROM limit_annual_capacity_factor')
        con.execute('DROP TABLE limit_annual_capacity_factor')
        con.execute('ALTER TABLE raw_factors RENAME TO limit_annual_capacity_factor')
        con.execute(INSERT, ('R1', period, 'vehicle', 2025, 'service', 'le', 0.25))
    with pytest.raises(ValueError, match='Duplicate'):
        _load(factor_db)


@pytest.mark.parametrize('factor', [-0.1, 1.1, None])
def test_factor_bounds(factor_db: Path, factor: float | None) -> None:
    with sqlite3.connect(factor_db) as con:
        with pytest.raises(sqlite3.IntegrityError):
            con.execute('UPDATE limit_annual_capacity_factor SET factor=?', (factor,))
        con.execute('CREATE TABLE raw_factors AS SELECT * FROM limit_annual_capacity_factor')
        con.execute('DROP TABLE limit_annual_capacity_factor')
        con.execute('ALTER TABLE raw_factors RENAME TO limit_annual_capacity_factor')
        con.execute('UPDATE limit_annual_capacity_factor SET factor=?', (factor,))
    with pytest.raises(ValueError, match=r'factor must be in \[0, 1\]'):
        _load(factor_db)


def _solve_snapshot(db: Path) -> dict[str, Any]:
    sequencer = TemoaSequencer(_config(db))
    sequencer.start()
    assert check_optimal_termination(sequencer.pf_results)
    model = sequencer.pf_solved_instance
    assert model is not None
    _assert_residuals(model)
    return {
        'values': {
            f'{component.name}{key}': value(component[key])
            for component in model.component_objects(Var)
            for key in component
        },
        'objective': value(model.total_cost),
        'coverage': {
            (component.name, str(key))
            for component in model.component_objects(Constraint)
            for key in component
        },
    }


def test_vintageless_migration_requires_mapping(factor_db: Path) -> None:
    """Never relabel an operating period as vintage, or publish a partial migration."""
    with sqlite3.connect(factor_db) as con:
        con.execute(
            'CREATE TABLE old_factors AS SELECT region, 2025 AS period, tech_or_group, '
            'output_comm, operator, factor, notes FROM limit_annual_capacity_factor'
        )
        con.execute('DROP TABLE limit_annual_capacity_factor')
        con.execute('ALTER TABLE old_factors RENAME TO limit_annual_capacity_factor')
    before = factor_db.read_bytes()
    target = factor_db.with_name('target.sqlite')
    target.write_bytes(b'Existing destination must survive a failed migration')
    with pytest.raises(ValueError, match='explicit cohort mapping'):
        migrate_database(factor_db, SCHEMA_PATH, target)
    assert factor_db.read_bytes() == before
    assert target.read_bytes() == b'Existing destination must survive a failed migration'
    assert not list(factor_db.parent.glob('temp_migration_*.sqlite'))


@pytest.mark.parametrize('annual', [0, 1])
def test_legacy_migration_solver_equivalence(factor_db: Path, annual: int) -> None:
    """Old physical schema, migrated NULL rows and explicit broadcasts solve identically."""
    with sqlite3.connect(factor_db) as con:
        con.execute('UPDATE technology SET annual=?', (annual,))
        con.execute('ALTER TABLE limit_annual_capacity_factor RENAME TO new_factors')
        con.execute(
            'CREATE TABLE limit_annual_capacity_factor '
            '(region TEXT, tech_or_group TEXT, vintage INTEGER, output_comm TEXT, '
            'operator TEXT NOT NULL DEFAULT "le", factor REAL, notes TEXT, '
            'PRIMARY KEY (region, tech_or_group, vintage, output_comm, operator))'
        )
        con.execute(
            'INSERT INTO limit_annual_capacity_factor '
            'SELECT region, tech_or_group, vintage, output_comm, operator, factor, notes '
            'FROM new_factors'
        )
        con.execute('DROP TABLE new_factors')
    legacy = _solve_snapshot(factor_db)
    assert legacy['objective'] == pytest.approx(2, rel=0, abs=TOL)
    source_hash = hashlib.sha256(factor_db.read_bytes()).hexdigest()
    migrated = factor_db.with_name('migrated.sqlite')
    migrate_database(factor_db, SCHEMA_PATH, migrated)
    assert hashlib.sha256(factor_db.read_bytes()).hexdigest() == source_hash
    current = _solve_snapshot(migrated)
    with sqlite3.connect(migrated) as con:
        assert con.execute('SELECT period FROM limit_annual_capacity_factor').fetchall() == [
            (None,)
        ]
        # Old named-column INSERTs retain broadcast semantics after migration.
        con.execute('DELETE FROM limit_annual_capacity_factor')
        con.execute(
            'INSERT INTO limit_annual_capacity_factor '
            '(region, tech_or_group, vintage, output_comm, factor) '
            "VALUES ('R1', 'vehicle', 2025, 'service', 0.5)"
        )
        assert con.execute('SELECT period FROM limit_annual_capacity_factor').fetchone() == (None,)
        with pytest.raises(sqlite3.OperationalError, match='8 columns but 7 values'):
            con.execute(
                "INSERT INTO limit_annual_capacity_factor VALUES ('R1','vehicle',2025,"
                "'service','le',0.5,NULL)"
            )
        con.execute('UPDATE limit_annual_capacity_factor SET period=2025')
        con.execute(INSERT, ('R1', 2030, 'vehicle', 2025, 'service', 'le', 0.5))
    explicit = _solve_snapshot(migrated)
    for result in (current, explicit):
        assert result['objective'] == pytest.approx(legacy['objective'], rel=0, abs=TOL)
        assert result['values'] == pytest.approx(legacy['values'], rel=0, abs=TOL)
        assert result['coverage'] == legacy['coverage']
