"""
Tests for the MGA axes, which select the quantity (activity, capacity, emission) that is
diversified across technology categories.
"""

from __future__ import annotations

import contextlib
import shutil
import sqlite3
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import pytest
from pyomo.environ import value

from temoa._internal.table_data_puller import poll_emissions
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.extensions.modeling_to_generate_alternatives.manager_factory import get_manager
from temoa.extensions.modeling_to_generate_alternatives.mga_constants import MgaAxis, MgaWeighting
from temoa.extensions.modeling_to_generate_alternatives.tech_activity_vector_manager import (
    TechActivityVectorManager,
)

if TYPE_CHECKING:
    from pyomo.opt import SolverResults

    from temoa.core.model import TemoaModel

UTOPIA_DB = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'

utopia_pf = [{'name': 'utopia', 'filename': 'config_utopia.toml'}]

CONFIG_TEMPLATE = """
scenario = "mga_axis"
scenario_mode = "mga"
input_database = "{db}"
output_database = "{db}"
neos = false
solver = "appsi_highs"
time_sequencing = "seasonal_timeslices"
days_per_period = 365
reserve_margin = "static"

[MGA]
cost_epsilon = 0.03
iteration_limit = {iteration_limit}
time_limit_hrs = 1
weighting = "hull_expansion"
{mga_options}
"""


def _manager(
    model: TemoaModel,
    sequencer: TemoaSequencer,
    axis: MgaAxis,
    mga_inputs: dict[str, object] | None = None,
) -> tuple[TechActivityVectorManager, sqlite3.Connection]:
    con = sqlite3.connect(sequencer.config.output_database)
    config = SimpleNamespace(mga_inputs=mga_inputs or {}, output_path=sequencer.config.output_path)
    manager = get_manager(
        axis=axis,
        weighting=MgaWeighting.HULL_EXPANSION,
        model=model,
        con=con,
        optimal_cost=1.0,
        cost_relaxation=0.03,
        config=config,
    )
    assert isinstance(manager, TechActivityVectorManager)
    return manager, con


def _categories(con: sqlite3.Connection) -> dict[str, str]:
    return dict(con.execute('SELECT tech, category FROM Technology').fetchall())


@pytest.mark.parametrize('system_test_run', utopia_pf, indirect=True, ids=['utopia'])
def test_category_values_match_model_results(
    system_test_run: tuple[str, SolverResults | None, TemoaModel | None, TemoaSequencer],
) -> None:
    """
    The value of each category (the coordinates of the solution in the space explored by MGA)
    should match the results of the solved model, for each axis
    """
    _, _, model, sequencer = system_test_run
    assert model is not None
    scenario = sequencer.config.scenario

    manager, con = _manager(model, sequencer, MgaAxis.TECH_CATEGORY_ACTIVITY)
    with contextlib.closing(con):
        expected = dict(
            con.execute(
                'SELECT t.category, SUM(f.flow) FROM output_flow_out f '
                'JOIN Technology t ON t.tech = f.tech WHERE f.scenario = ? GROUP BY t.category',
                (scenario,),
            ).fetchall()
        )
        point = dict(zip(manager.groups, manager.process_results(model), strict=True))
        assert set(expected) <= set(point)
        assert len(point) > 1
        for cat, val in point.items():
            assert val == pytest.approx(expected.get(cat, 0), rel=1e-3, abs=1e-2), (
                f'activity of {cat}'
            )

    manager, con = _manager(model, sequencer, MgaAxis.TECH_CATEGORY_CAPACITY)
    with contextlib.closing(con):
        categories = _categories(con)
        expected_cap: dict[str, float] = defaultdict(float)
        for (_r, _p, t), var in model.v_capacity_available_by_period_and_tech.items():
            expected_cap[categories[t]] += value(var)
        point = dict(zip(manager.groups, manager.process_results(model), strict=True))
        assert set(point) == set(expected_cap)
        assert len(point) > 1
        for cat, val in point.items():
            assert val == pytest.approx(expected_cap[cat]), f'capacity of {cat}'
        assert sum(point.values()) > 0

    for commodities in (['co2'], ['co2', 'nox']):
        manager, con = _manager(
            model,
            sequencer,
            MgaAxis.TECH_CATEGORY_EMISSION,
            {'axis_emission_commodities': commodities},
        )
        with contextlib.closing(con):
            categories = _categories(con)
            _, e_flows = poll_emissions(model=model, p_0=None, epsilon=0)
            expected_emis: dict[str, float] = defaultdict(float)
            for ei, val in e_flows.items():
                if ei.e in commodities:
                    expected_emis[categories[ei.t]] += val
            point = dict(zip(manager.groups, manager.process_results(model), strict=True))
            assert len(point) > 1
            assert set(point) <= set(expected_emis)
            for cat, val in point.items():
                assert val == pytest.approx(expected_emis[cat], rel=1e-6), f'{commodities} {cat}'
            assert sum(point.values()) == pytest.approx(sum(expected_emis.values()), rel=1e-6)


@pytest.mark.parametrize('system_test_run', utopia_pf, indirect=True, ids=['utopia'])
def test_emission_axis_requires_valid_commodities(
    system_test_run: tuple[str, SolverResults | None, TemoaModel | None, TemoaSequencer],
) -> None:
    _, _, model, sequencer = system_test_run
    assert model is not None
    bad_inputs: list[tuple[dict[str, object], str]] = [
        ({}, 'requires the "axis_emission_commodities" option'),
        ({'axis_emission_commodities': []}, 'requires the "axis_emission_commodities" option'),
        ({'axis_emission_commodities': ['unobtainium']}, 'are not emission commodities'),
        # only 1 category emits nox in Utopia, which is not enough to define a space
        ({'axis_emission_commodities': ['nox']}, 'needs at least 2 technology categories'),
    ]
    for inputs, message in bad_inputs:
        con = sqlite3.connect(sequencer.config.output_database)
        with contextlib.closing(con), pytest.raises(ValueError, match=message):
            get_manager(
                axis=MgaAxis.TECH_CATEGORY_EMISSION,
                weighting=MgaWeighting.HULL_EXPANSION,
                model=model,
                con=con,
                optimal_cost=1.0,
                cost_relaxation=0.03,
                config=cast('Any', SimpleNamespace(mga_inputs=inputs)),
            )


@pytest.mark.parametrize('system_test_run', utopia_pf, indirect=True, ids=['utopia'])
def test_uncategorized_technologies_are_not_part_of_the_axis(
    system_test_run: tuple[str, SolverResults | None, TemoaModel | None, TemoaSequencer],
) -> None:
    _, _, model, sequencer = system_test_run
    assert model is not None
    con = sqlite3.connect(':memory:')
    with contextlib.closing(sqlite3.connect(sequencer.config.output_database)) as source:
        source.backup(con)
    with contextlib.closing(con):
        con.execute("UPDATE Technology SET category = NULL WHERE category = 'petroleum'")
        uncategorized = {
            t for (t,) in con.execute('SELECT tech FROM Technology WHERE category IS NULL')
        }
        assert uncategorized
        for axis in (MgaAxis.TECH_CATEGORY_ACTIVITY, MgaAxis.TECH_CATEGORY_CAPACITY):
            manager = get_manager(
                axis=axis,
                weighting=MgaWeighting.HULL_EXPANSION,
                model=model,
                con=con,
                optimal_cost=1.0,
                cost_relaxation=0.03,
                config=cast('Any', SimpleNamespace(mga_inputs={})),
            )
            assert isinstance(manager, TechActivityVectorManager)
            members = {t for g in manager.groups for t in manager.group_members(g)}
            assert len(list(manager.groups)) > 1
            assert set(manager.groups) <= {'coal', 'electric', 'hydro', 'nuclear'}
            assert members.isdisjoint(uncategorized)
            assert len(manager.var_vector(model)) == sum(
                manager.technology_size[t] for t in members
            )
            assert len(manager.process_results(model)) == len(list(manager.groups))


def _mga_config(tmp_path: Path, mga_options: str, iteration_limit: int = 8) -> TemoaConfig:
    db = tmp_path / 'utopia_mga_axis.sqlite'
    shutil.copy(UTOPIA_DB, db)
    config_file = tmp_path / 'config.toml'
    config_file.write_text(
        CONFIG_TEMPLATE.format(
            db=db.as_posix(), iteration_limit=iteration_limit, mga_options=mga_options
        )
    )
    return TemoaConfig.build_config(config_file=config_file, output_path=tmp_path, silent=True)


@pytest.mark.parametrize(
    'mga_options',
    [
        'axis = "tech_category_capacity"',
        'axis = "tech_category_emission"\naxis_emission_commodities = ["co2"]',
    ],
    ids=['capacity', 'emission'],
)
def test_mga_run_with_axis(mga_options: str, tmp_path: Path) -> None:
    """Full MGA runs, long enough to get past the basis solves and into hull expansion"""
    config = _mga_config(tmp_path, mga_options, iteration_limit=14)
    TemoaSequencer(config=config).start()

    with contextlib.closing(sqlite3.connect(config.output_database)) as con:
        capacities = con.execute(
            'SELECT scenario, SUM(capacity) FROM output_net_capacity '
            "WHERE scenario LIKE 'mga_axis-%' GROUP BY scenario"
        ).fetchall()
    scenarios = {row[0] for row in capacities}
    assert 'mga_axis-0' in scenarios
    assert len(scenarios) >= 14
    assert len({round(row[1], 3) for row in capacities}) > 3
