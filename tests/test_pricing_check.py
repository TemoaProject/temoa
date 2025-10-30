"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.


Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  2/2/24

"""

import pytest
from pyomo.environ import Any, ConcreteModel, Param, Set

from temoa.model_checking.pricing_check import check_tech_uncap


@pytest.fixture
def mock_model():
    """let's see how tough this is to work with..."""
    model = ConcreteModel('mock')
    model.tech_uncap = Set(initialize=['refinery'])
    model.time_optimize = Set(initialize=[2000, 2010, 2020, 2030])
    model.LifetimeProcess = Param(Any, Any, Any, initialize={('CA', 'refinery', 2020): 30})
    model.Efficiency = Param(
        Any, Any, Any, Any, Any, initialize={('CA', 0, 'refinery', 2020, 0): 1.0}
    )

    model.ExistingCapacity = Param(Any, Any, Any, mutable=True)
    model.CostFixed = Param(Any, Any, Any, Any, mutable=True)
    model.CostInvest = Param(Any, Any, Any, mutable=True)
    model.CostVariable = Param(Any, Any, Any, Any, mutable=True)
    model.MaxCapacity = Param(Any, Any, Any, mutable=True)
    model.MinCapacity = Param(Any, Any, Any, mutable=True)
    return model


def test_check_tech_uncap(mock_model):
    """
    test the fault checking for unlimited capacity techs
    :param mock_model:
    :return:
    """
    model = mock_model

    assert check_tech_uncap(model), 'should pass for no fixed/invest/variable costs'
    model.CostVariable[('CA', 2020, 'refinery', 2020)] = 42
    assert not check_tech_uncap(model), 'should fail.  Has cost in 2020, but missing in 2030'
    # add in missing cost...
    model.CostVariable[('CA', 2030, 'refinery', 2020)] = 42
    assert check_tech_uncap(model), 'should pass for all periods having var cost'


def test_detect_fixed_cost(mock_model):
    """
    test the fault checking for unlimited capacity techs
    :param mock_model:
    :return:
    """
    model = mock_model
    assert check_tech_uncap(model), 'should have cleared and passed again'
    model.CostFixed[('CA', 2020, 'refinery', 2020)] = 42
    assert not check_tech_uncap(model), 'should fail with any fixed cost'


def test_detect_invest_cost(mock_model):
    """
    test the fault checking for unlimited capacity techs
    :param mock_model:
    :return:
    """
    model = mock_model
    model.CostInvest['CA', 'refinery', 2020] = 42
    assert not check_tech_uncap(model), 'should fail with any investment cost'
