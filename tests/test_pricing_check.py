from typing import TYPE_CHECKING, cast

import pytest
from pyomo.environ import Any, ConcreteModel, Param, Set

from temoa.model_checking.pricing_check import check_tech_uncap

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


@pytest.fixture
def mock_model() -> ConcreteModel:
    """let's see how tough this is to work with..."""
    model = ConcreteModel('mock')
    model.tech_uncap = Set(initialize=['refinery'])
    model.time_optimize = Set(initialize=[2000, 2010, 2020, 2030])
    model.lifetime_process = Param(Any, Any, Any, initialize={('CA', 'refinery', 2020): 30})
    model.efficiency = Param(
        Any, Any, Any, Any, Any, initialize={('CA', 0, 'refinery', 2020, 0): 1.0}
    )

    model.existing_capacity = Param(Any, Any, Any, mutable=True)
    model.cost_fixed = Param(Any, Any, Any, Any, mutable=True)
    model.cost_invest = Param(Any, Any, Any, mutable=True)
    model.cost_variable = Param(Any, Any, Any, Any, mutable=True)
    model.max_capacity = Param(Any, Any, Any, mutable=True)
    model.min_capacity = Param(Any, Any, Any, mutable=True)
    return model


def test_check_tech_uncap(
    mock_model: ConcreteModel,
) -> None:
    """
    test the fault checking for unlimited capacity techs
    :param mock_model:
    :return:
    """
    model = cast('TemoaModel', mock_model)

    assert check_tech_uncap(model), 'should pass for no fixed/invest/variable costs'
    model.cost_variable[('CA', 2020, 'refinery', 2020)] = 42
    assert not check_tech_uncap(model), 'should fail.  Has cost in 2020, but missing in 2030'
    # add in missing cost...
    model.cost_variable[('CA', 2030, 'refinery', 2020)] = 42
    assert check_tech_uncap(model), 'should pass for all periods having var cost'


def test_detect_fixed_cost(
    mock_model: ConcreteModel,
) -> None:
    """
    test the fault checking for unlimited capacity techs
    :param mock_model:
    :return:
    """
    model = cast('TemoaModel', mock_model)
    assert check_tech_uncap(model), 'should have cleared and passed again'
    model.cost_fixed[('CA', 2020, 'refinery', 2020)] = 42
    assert not check_tech_uncap(model), 'should fail with any fixed cost'


def test_detect_invest_cost(
    mock_model: ConcreteModel,
) -> None:
    """
    test the fault checking for unlimited capacity techs
    :param mock_model:
    :return:
    """
    model = cast('TemoaModel', mock_model)
    model.cost_invest['CA', 'refinery', 2020] = 42
    assert not check_tech_uncap(model), 'should fail with any investment cost'
