"""
Myopic unit commitment startup costs must be discounted to the same year as every other cost.

In a myopic run the core cost rule discounts every cost to the run's first period
(myopic_discounting_year), not to the first period of each myopic window. uc_myopic_discount.sql
solves 2030 and 2040 as one window each at a 2% discount rate. In the 2040 window a start must
carry the same discount weight as a 2040 variable cost; discounted to 2040 instead of 2030 it
would weigh 1.02 ** 10 = 1.219 times as much.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest
from pyomo.common.collections import ComponentMap
from pyomo.environ import check_optimal_termination, value
from pyomo.repn import generate_standard_repn

from temoa._internal import run_actions
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel
from temoa.extensions.unit_commitment.components import startup
from temoa.types.core_types import Commodity, Period, Region, Technology, Vintage

if TYPE_CHECKING:
    from pyomo.core.base.objective import ObjectiveData

CONFIG_FILE = Path(__file__).parent / 'testing_configs' / 'config_uc_myopic_discount.toml'

R = Region('region')
GEN = Technology('gen')
V = Vintage(2030)
CO2 = Commodity('co2')


def test_myopic_startup_costs_use_core_discount_year(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """In every myopic window a start is discounted like a variable cost of its period."""
    solved: list[TemoaModel] = []
    solve_instance = run_actions.solve_instance

    def solve_and_keep(*args: Any, **kwargs: Any) -> tuple[TemoaModel, Any]:
        model, results = solve_instance(*args, **kwargs)
        assert check_optimal_termination(results)
        solved.append(model)
        return model, results

    monkeypatch.setattr(run_actions, 'solve_instance', solve_and_keep)

    config = TemoaConfig.build_config(config_file=CONFIG_FILE, output_path=tmp_path, silent=True)
    TemoaSequencer(config=config).start()

    assert [min(model.time_optimize) for model in solved] == [2030, 2040]
    for model in solved:
        p = Period(min(model.time_optimize))
        assert value(model.myopic_discounting_year) == 2030

        objective = generate_standard_repn(cast('ObjectiveData', model.total_cost).expr)
        objective_coefs = ComponentMap(
            zip(objective.linear_vars, objective.linear_coefs, strict=True)
        )

        # discount weight the core cost rule gives a variable cost in period p
        flow = model.v_flow_out[R, p, 's', 'day', 'ethos', GEN, V, 'power']
        core_weight = objective_coefs[flow] / value(model.cost_variable[R, p, GEN, V])

        # undiscounted annual startup cost and startup emission cost per start variable
        startup_cost = startup.uc_startup_cost_rptv(model, R, p, GEN, V)
        startup_emission_cost = value(
            model.cost_emission[R, p, CO2]
        ) * startup.uc_startup_emissions_rpe(model, R, p, CO2)
        assert value(startup_cost) > 0
        annual = generate_standard_repn(startup_cost + startup_emission_cost)

        for started, annual_coef in zip(annual.linear_vars, annual.linear_coefs, strict=True):
            assert objective_coefs[started] == pytest.approx(annual_coef * core_weight, rel=1e-5)
