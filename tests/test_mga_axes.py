"""
Tests for the MGA axes, which select the quantity that is diversified across technology
categories.
"""

from __future__ import annotations

import contextlib
import sqlite3
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import pytest

from temoa.extensions.modeling_to_generate_alternatives.manager_factory import get_manager
from temoa.extensions.modeling_to_generate_alternatives.mga_constants import MgaAxis, MgaWeighting

if TYPE_CHECKING:
    from pyomo.opt import SolverResults

    from temoa._internal.temoa_sequencer import TemoaSequencer
    from temoa.core.model import TemoaModel

utopia_pf = [{'name': 'utopia', 'filename': 'config_utopia.toml'}]


@pytest.mark.parametrize('system_test_run', utopia_pf, indirect=True, ids=['utopia'])
def test_activity_category_values_match_model_results(
    system_test_run: tuple[str, SolverResults | None, TemoaModel | None, TemoaSequencer],
) -> None:
    """
    The activity of each category (the coordinates of the solution in the space explored by MGA)
    should match the output flows of the solved model
    """
    _, _, model, sequencer = system_test_run
    assert model is not None
    con = sqlite3.connect(sequencer.config.output_database)
    with contextlib.closing(con):
        manager = get_manager(
            axis=MgaAxis.TECH_CATEGORY_ACTIVITY,
            weighting=MgaWeighting.HULL_EXPANSION,
            model=model,
            con=con,
            optimal_cost=1.0,
            cost_relaxation=0.03,
            config=cast('Any', SimpleNamespace()),
        )
        expected = dict(
            con.execute(
                'SELECT t.category, SUM(f.flow) FROM output_flow_out f '
                'JOIN Technology t ON t.tech = f.tech WHERE f.scenario = ? GROUP BY t.category',
                (sequencer.config.scenario,),
            ).fetchall()
        )
        point = dict(zip(manager.groups, manager.process_results(model), strict=True))
        assert set(expected) <= set(point)
        for cat, val in point.items():
            assert val == pytest.approx(expected.get(cat, 0), rel=1e-3, abs=1e-2), (
                f'activity of {cat}'
            )
