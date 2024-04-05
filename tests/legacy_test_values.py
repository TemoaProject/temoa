"""
a container for test values from legacy code (Python 3.7 / Pyomo 5.5) captured for
continuity/development testing

Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  6/27/23

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
"""

from enum import Enum


class TestVals(Enum):
    OBJ_VALUE = 'obj_value'
    EFF_DOMAIN_SIZE = 'eff_domain_size'
    EFF_INDEX_SIZE = 'eff_index_size'
    VAR_COUNT = 'count of variables in model'
    CONSTR_COUNT = 'count of constraints in model'


# these values were captured on base level runs of the .dat files in the tests/testing_data folder
test_vals = {
    'test_system': {
        TestVals.OBJ_VALUE: 491977.7000753,
        TestVals.EFF_DOMAIN_SIZE: 30720,
        TestVals.EFF_INDEX_SIZE: 74,
        TestVals.CONSTR_COUNT: 2826,
        TestVals.VAR_COUNT: 1904,
    },
    'utopia': {
        TestVals.OBJ_VALUE: 36535.631200,
        TestVals.EFF_DOMAIN_SIZE: 12312,
        TestVals.EFF_INDEX_SIZE: 64,
        TestVals.CONSTR_COUNT: 1452,  # reduced 3/27:  unlim_cap techs now employed
        TestVals.VAR_COUNT: 1055,  # reduced 3/27:  unlim_cap techs now employed
    },
}
