"""Investment hurdles affect choices while all reported costs use real financing."""

import contextlib
import logging
import queue
import sqlite3
import tomllib
from pathlib import Path

import pytest
from pyomo.environ import value

from temoa._internal.data_brick import data_brick_factory
from temoa._internal.table_writer import TableWriter
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode
from temoa.data_io.hybrid_loader import HybridLoader
from temoa.extensions.method_of_morris.morris_evaluate import evaluate
from tests.conftest import TEST_DATA_PATH, _build_test_db
from tests.legacy_test_values import ExpectedVals, test_vals

gurobipy = pytest.importorskip('gurobipy')


def crf(rate: float, years: int) -> float:
    return rate / (1 - (1 + rate) ** -years) if rate else 1 / years


def present_value(years: int, rate: float = 0.02) -> float:
    return sum((1 + rate) ** -year for year in range(1, years + 1))


def example_config(tmp_path: Path, hurdle: float, *, myopic: bool = False) -> TemoaConfig:
    db = tmp_path / 'example.sqlite'
    _build_test_db(db, [TEST_DATA_PATH / 'hurdle_rate.sql'])
    with contextlib.closing(sqlite3.connect(db)) as con:
        if myopic:
            con.executemany(
                'INSERT INTO time_period(sequence, period, flag) VALUES (?, ?, ?)',
                [(2, 2050, 'f'), (3, 2065, 'f')],
            )
            for year in [2035, 2050]:
                for table in ['cost_invest', 'loan_lifetime_process']:
                    con.execute(
                        f'INSERT INTO {table} SELECT region, tech, ?, '
                        + ('cost' if table == 'cost_invest' else 'lifetime')
                        + f', units, notes FROM {table} WHERE vintage = 2020',
                        (year,),
                    )
                con.execute(
                    'INSERT INTO efficiency SELECT region, input_comm, tech, ?, output_comm, '
                    'efficiency, units, notes FROM efficiency WHERE vintage = 2020',
                    (year,),
                )
                con.execute(
                    'INSERT INTO cost_variable SELECT region, ?, tech, ?, cost, units, notes '
                    'FROM cost_variable WHERE vintage = 2020',
                    (year, year),
                )
                con.execute(
                    'INSERT INTO demand SELECT region, ?, commodity, demand, units, notes '
                    'FROM demand WHERE period = 2020',
                    (year,),
                )
        con.execute(
            'INSERT INTO hurdle_rate(region, tech, vintage, rate) '
            'SELECT region, tech, vintage, ? FROM cost_invest',
            (hurdle,),
        )
        con.commit()
    return TemoaConfig(
        scenario='hurdle',
        scenario_mode='myopic' if myopic else 'perfect_foresight',
        input_database=db,
        output_database=db,
        output_path=tmp_path,
        solver={'name': 'gurobi_direct', 'options': {'Threads': 1, 'Method': 1}},
        time_sequencing='seasonal_timeslices',
        reserve_margin='static',
        silent=True,
        myopic={'view_depth': 2, 'step_size': 1, 'evolving': False} if myopic else None,
    )


def totals(config: TemoaConfig) -> dict[str, float]:
    with contextlib.closing(sqlite3.connect(config.output_database)) as con:
        return dict(con.execute('SELECT objective_name, total_system_cost FROM output_objective'))


@pytest.mark.parametrize('zero_mode', ['empty', 'missing', 'explicit'])
def test_zero_hurdle_leaves_utopia_unchanged(tmp_path: Path, zero_mode: str) -> None:
    """An empty, missing or all-zero hurdle table gives utopia's recorded cost and no score row."""
    db = tmp_path / 'utopia.sqlite'
    _build_test_db(db, [TEST_DATA_PATH / 'utopia_data.sql'])
    with contextlib.closing(sqlite3.connect(db)) as con:
        if zero_mode == 'missing':
            con.execute('DROP TABLE hurdle_rate')
        elif zero_mode == 'explicit':
            con.execute(
                'INSERT INTO hurdle_rate(region, tech, vintage, rate) '
                'SELECT region, tech, vintage, 0 FROM cost_invest'
            )
        con.commit()
    settings = tomllib.loads(
        (Path(__file__).parent / 'testing_configs' / 'config_utopia.toml').read_text()
    )
    settings.pop('solver_name', None)
    settings.update(
        input_database=db,
        output_database=db,
        solver={'name': 'gurobi_direct', 'options': {'Threads': 1, 'Method': 1}},
    )
    config = TemoaConfig(output_path=tmp_path, silent=True, **settings)
    TemoaSequencer(config).start()

    expected = test_vals['utopia'][ExpectedVals.OBJ_VALUE]
    assert totals(config) == {'total_cost': pytest.approx(expected, rel=1e-5)}


@pytest.mark.parametrize(
    'hurdle,chosen,price,operation',
    [
        (0, 'efficient', 1500, 240),
        (0.10, 'standard', 1000, 300),
    ],
)
@pytest.mark.parametrize('myopic', [False, True])
@pytest.mark.parametrize('eos', [False, True])
def test_worked_example(
    tmp_path: Path,
    hurdle: float,
    chosen: str,
    price: float,
    operation: float,
    myopic: bool,
    eos: bool,
) -> None:
    config = example_config(tmp_path, hurdle, myopic=myopic)
    if eos:
        config.extensions = ('eos',)
        with contextlib.closing(sqlite3.connect(config.input_database)) as con:
            con.execute('DELETE FROM cost_invest')
            con.executemany(
                'INSERT INTO cost_invest_eos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                [
                    ('region', tech, 1, 0, 10, 0, 10 * cost, None, None)
                    for tech, cost in [('standard', 1000), ('efficient', 1500)]
                ],
            )
            con.commit()
    sequencer = TemoaSequencer(config)
    sequencer.start()
    years = [2020, 2035, 2050] if myopic else [2020]
    discount = sum(1.02 ** -(year - 2020) for year in years)
    real = (price * crf(0.05, 15) + operation) * present_value(15) * discount
    penalty = price * (crf(0.05 + hurdle, 15) - crf(0.05, 15)) * present_value(15) * discount
    reported = totals(config)
    assert reported['total_cost'] == pytest.approx(real, rel=1e-5)
    if hurdle:
        assert reported['choice_score'] == pytest.approx(real + penalty, rel=1e-5)
        if not myopic:
            assert real == pytest.approx(5092.71, abs=0.005)
            assert real + penalty == pytest.approx(6052.22, abs=0.005)
            assert penalty == pytest.approx(959.52, abs=0.005)
    else:
        assert set(reported) == {'total_cost'}
    with contextlib.closing(sqlite3.connect(config.output_database)) as con:
        built = con.execute('SELECT tech, vintage, capacity FROM output_built_capacity').fetchall()
        assert [(tech, vintage) for tech, vintage, _ in sorted(built)] == [
            (chosen, year) for year in years
        ]
        assert [capacity for _, _, capacity in built] == pytest.approx([1] * len(years), rel=1e-5)
        invest, discounted = con.execute(
            'SELECT SUM(invest), SUM(d_invest) FROM output_cost'
        ).fetchone()
        assert invest == pytest.approx(len(years) * price * crf(0.05, 15) * 15, rel=1e-5)
        assert discounted == pytest.approx(price * crf(0.05, 15) * present_value(15) * discount)
    if not myopic:
        model = sequencer.pf_solved_instance
        assert model is not None
        assert value(model.total_cost) == pytest.approx(real + penalty)
        assert value(model.loan_rate['region', chosen, 2020]) == 0.05
        assert value(model.global_discount_rate) == 0.02
        if not eos:
            shadow_price = model.dual[model.demand_constraint['region', 2020, 'demand']]
            assert shadow_price == pytest.approx(real + penalty)


@pytest.mark.parametrize('survival', [False, True])
@pytest.mark.parametrize('loan_rate,loan_life,discount_rate', [(0.05, 5, 0.02), (0, 20, 0)])
def test_investment_horizon_and_lifetimes(
    tmp_path: Path, survival: bool, loan_rate: float, loan_life: int, discount_rate: float
) -> None:
    """A truncated horizon and unequal lives retain their original financing treatment."""
    config = example_config(tmp_path, 0.1)
    with contextlib.closing(sqlite3.connect(config.input_database)) as con:
        con.execute('UPDATE time_period SET period = ? WHERE period = ?', (2030, 2035))
        con.execute('UPDATE loan_lifetime_process SET lifetime = ?', (loan_life,))
        con.execute(
            "UPDATE metadata_real SET value = ? WHERE element = 'default_loan_rate'", (loan_rate,)
        )
        con.execute(
            "UPDATE metadata_real SET value = ? WHERE element = 'global_discount_rate'",
            (discount_rate,),
        )
        if survival:
            con.executemany(
                'INSERT INTO lifetime_survival_curve(region, period, tech, vintage, fraction) '
                'VALUES (?, ?, ?, ?, ?)',
                [
                    ('region', year, tech, 2020, fraction)
                    for tech in ['standard', 'efficient']
                    for year, fraction in [(2020, 1), (2025, 0.8), (2035, 0)]
                ],
            )
        con.commit()
    sequencer = TemoaSequencer(config)
    sequencer.start()
    model = sequencer.pf_solved_instance
    assert model is not None
    full_loan_pv = present_value(loan_life, discount_rate)
    if survival:
        fractions = [
            1 - year * 0.04 if year <= 5 else 0.8 - (year - 5) * 0.08 for year in range(15)
        ]
        pv = [f * (1 + discount_rate) ** -(year + 1) for year, f in enumerate(fractions)]
        horizon_share = sum(pv[:10]) / sum(pv)
    else:
        horizon_share = present_value(10, discount_rate) / present_value(15, discount_rate)
    capital = sum(
        value(model.v_new_capacity['region', tech, 2020]) * price
        for tech, price in [('standard', 1000), ('efficient', 1500)]
    )
    expected_invest = capital * crf(loan_rate, loan_life) * full_loan_pv * horizon_share
    weight = crf(loan_rate + 0.1, loan_life) / crf(loan_rate, loan_life)
    with contextlib.closing(sqlite3.connect(config.output_database)) as con:
        investment, operating = con.execute(
            'SELECT SUM(d_invest), SUM(d_var) FROM output_cost'
        ).fetchone()
    assert investment == pytest.approx(expected_invest, rel=1e-5)
    assert value(model.real_cost) == pytest.approx(investment + operating, rel=1e-5)
    assert value(model.total_cost) == pytest.approx(investment * weight + operating, rel=1e-5)


def test_negative_hurdle_rejected(tmp_path: Path) -> None:
    config = example_config(tmp_path, -0.1)
    with pytest.raises(RuntimeError, match='hurdle_rate'):
        TemoaSequencer(config).build_model()


@pytest.mark.parametrize('myopic', [False, True])
@pytest.mark.parametrize('hurdle', [0, 0.1])
def test_total_includes_links_and_all_operating_costs(
    tmp_path: Path, myopic: bool, hurdle: float
) -> None:
    config = example_config(tmp_path, hurdle, myopic=myopic)
    years = [2020, 2035, 2050] if myopic else [2020]
    with contextlib.closing(sqlite3.connect(config.input_database)) as con:
        con.execute('INSERT INTO region(region) VALUES (?)', ('upstream',))
        con.executemany(
            'INSERT INTO commodity(name, flag) VALUES (?, ?)', [('fuel', 'p'), ('co2', 'e')]
        )
        con.execute('UPDATE efficiency SET input_comm = ?', ('fuel',))
        con.executemany(
            'INSERT INTO technology(tech, flag, sector, unlim_cap, exchange) '
            'VALUES (?, ?, ?, ?, ?)',
            [('supply', 'p', 'equipment', 1, 0), ('link', 'p', 'equipment', 0, 1)],
        )
        for year in years:
            for region, tech, input_comm, operating in [
                ('upstream', 'supply', 'source', 7),
                ('upstream-region', 'link', 'fuel', 3),
                ('region-upstream', 'link', 'fuel', 3),
            ]:
                con.execute(
                    'INSERT INTO efficiency(region, input_comm, tech, vintage, '
                    'output_comm, efficiency) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (region, input_comm, tech, year, 'fuel', 1),
                )
                con.execute(
                    'INSERT INTO lifetime_process(region, tech, vintage, lifetime) '
                    'VALUES (?, ?, ?, ?)',
                    (region, tech, year, 15),
                )
                con.execute(
                    'INSERT INTO cost_variable(region, period, tech, vintage, cost) '
                    'VALUES (?, ?, ?, ?, ?)',
                    (region, year, tech, year, operating),
                )
            con.execute(
                'INSERT INTO cost_emission(region, period, emis_comm, cost) VALUES (?, ?, ?, ?)',
                ('region', year, 'co2', 4),
            )
            for tech in ['standard', 'efficient']:
                con.execute(
                    'INSERT INTO cost_fixed(region, period, tech, vintage, cost) '
                    'VALUES (?, ?, ?, ?, ?)',
                    ('region', year, tech, year, 10),
                )
                con.execute(
                    'INSERT INTO emission_activity(region, emis_comm, input_comm, tech, vintage, '
                    'output_comm, activity) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    ('region', 'co2', 'fuel', tech, year, 'demand', 2),
                )
        con.commit()
    discount = sum(1.02 ** -(year - 2020) for year in years)
    price, operating = (1000, 300) if hurdle else (1500, 240)
    # Includes fixed (10), fuel (7), link (3), and emissions (2 * 4).
    expected = (price * crf(0.05, 15) + operating + 28) * present_value(15) * discount
    sequencer = TemoaSequencer(config)
    sequencer.start()
    assert totals(config)['total_cost'] == pytest.approx(expected, rel=1e-5)
    with contextlib.closing(sqlite3.connect(config.output_database)) as con:
        link_cost = con.execute(
            'SELECT SUM(d_var) FROM output_cost WHERE tech = ?', ('link',)
        ).fetchone()[0]
        if myopic:
            reported_total = con.execute(
                'SELECT SUM(d_invest)+SUM(d_fixed)+SUM(d_var)+SUM(d_emiss) FROM output_cost '
                'WHERE scenario = ?',
                (config.scenario,),
            ).fetchone()[0]
            assert totals(config)['total_cost'] == pytest.approx(reported_total, rel=1e-5)
    assert link_cost == pytest.approx(3 * present_value(15) * discount)
    # Preserve myopic's output sum; perfect foresight and choice scores use the model.
    config.output_threshold_cost = 1e9
    TemoaSequencer(config).start()
    with contextlib.closing(sqlite3.connect(config.output_database)) as con:
        assert con.execute('SELECT COUNT(*) FROM output_cost').fetchone()[0] == 0
    assert totals(config)['total_cost'] == pytest.approx(0 if myopic else expected, rel=1e-5)
    if hurdle:
        penalty = price * (crf(0.15, 15) - crf(0.05, 15)) * present_value(15) * discount
        assert totals(config)['choice_score'] == pytest.approx(expected + penalty, rel=1e-5)


def test_existing_capacity_has_no_hurdle(tmp_path: Path) -> None:
    config = example_config(tmp_path, 0.1)
    config.source_trace = True
    with contextlib.closing(sqlite3.connect(config.input_database)) as con:
        con.execute('INSERT INTO time_period VALUES (?, ?, ?)', (-1, 2005, 'e'))
        con.execute(
            'INSERT INTO efficiency(region, input_comm, tech, vintage, output_comm, efficiency) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            ('region', 'source', 'standard', 2005, 'demand', 1),
        )
        con.execute(
            'INSERT INTO lifetime_process(region, tech, vintage, lifetime) VALUES (?, ?, ?, ?)',
            ('region', 'standard', 2005, 30),
        )
        con.execute(
            'INSERT INTO existing_capacity(region, tech, vintage, capacity) VALUES (?, ?, ?, ?)',
            ('region', 'standard', 2005, 1),
        )
        for table, column, amount in [('hurdle_rate', 'rate', 1), ('cost_invest', 'cost', 1000)]:
            con.execute(
                f'INSERT INTO {table}(region, tech, vintage, {column}) VALUES (?, ?, ?, ?)',
                ('region', 'standard', 2005, amount),
            )
        con.execute(
            'INSERT INTO cost_variable(region, period, tech, vintage, cost) VALUES (?, ?, ?, ?, ?)',
            ('region', 2020, 'standard', 2005, 12),
        )
        con.commit()
    sequencer = TemoaSequencer(config)
    sequencer.start()
    model = sequencer.pf_solved_instance
    assert model is not None
    assert ('region', 'standard', 2005) not in model.hurdle_rate
    assert value(model.real_cost) == pytest.approx(12 * present_value(15))
    assert value(model.total_cost) == pytest.approx(value(model.real_cost), rel=1e-5)


def test_monte_carlo_reports_both_metrics(tmp_path: Path) -> None:
    config = example_config(tmp_path, 0.1)
    sequencer = TemoaSequencer(config)
    sequencer.start()
    model = sequencer.pf_solved_instance
    assert model is not None
    brick = data_brick_factory(model)
    with TableWriter(config) as writer:
        writer.write_mc_results(brick, iteration=1)
    with contextlib.closing(sqlite3.connect(config.output_database)) as con:
        reported = dict(
            con.execute(
                'SELECT objective_name, total_system_cost FROM output_objective WHERE scenario = ?',
                ('hurdle-1',),
            )
        )
    assert reported['total_cost'] == pytest.approx(value(model.real_cost), rel=1e-5)
    assert reported['choice_score'] == pytest.approx(value(model.total_cost), rel=1e-5)


def test_morris_cost_response_excludes_hurdle(tmp_path: Path) -> None:
    config = example_config(tmp_path, 0.1)
    with contextlib.closing(sqlite3.connect(config.input_database)) as con:
        data = HybridLoader(con, config).create_data_dict()
    response = evaluate({}, [], data, 0, config, queue.Queue(), logging.WARNING)
    expected = (1000 * crf(0.05, 15) + 300) * present_value(15)
    assert response == pytest.approx([expected, 0])


@pytest.mark.parametrize('epsilon,chosen', [(0, 'standard'), (0.1, 'efficient')])
def test_single_vector_mga_caps_choice_score_and_reports_real_cost(
    tmp_path: Path, epsilon: float, chosen: str
) -> None:
    config = example_config(tmp_path, 0.1)
    config.scenario_mode = TemoaMode.SVMGA
    config.svmga_inputs = {'cost_epsilon': epsilon, 'capacity_labels': ['standard']}
    with contextlib.closing(sqlite3.connect(config.input_database)) as con:
        con.executemany(
            'INSERT INTO limit_new_capacity(region, tech_or_group, vintage, new_cap) '
            'VALUES (?, ?, ?, ?)',
            [('region', tech, 2020, 1) for tech in ['standard', 'efficient']],
        )
        con.commit()
    TemoaSequencer(config).start()
    with contextlib.closing(sqlite3.connect(config.output_database)) as con:
        reported = dict(
            con.execute(
                'SELECT objective_name, total_system_cost FROM output_objective WHERE scenario = ?',
                ('hurdle-1',),
            )
        )
        built = con.execute(
            'SELECT tech, capacity FROM output_built_capacity WHERE scenario = ?', ('hurdle-1',)
        ).fetchall()
    assert [tech for tech, _ in built] == [chosen]
    assert [capacity for _, capacity in built] == pytest.approx([1], rel=1e-5)
    price, operation = (1000, 300) if chosen == 'standard' else (1500, 240)
    assert reported['total_cost'] == pytest.approx(
        (price * crf(0.05, 15) + operation) * present_value(15)
    )
    assert reported['choice_score'] == pytest.approx(
        (price * crf(0.15, 15) + operation) * present_value(15)
    )
    assert reported['svmga_obj'] == (1 if chosen == 'standard' else 0)
