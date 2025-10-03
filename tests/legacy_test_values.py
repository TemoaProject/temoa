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


class ExpectedVals(Enum):
    OBJ_VALUE = 'obj_value'
    EFF_DOMAIN_SIZE = 'eff_domain_size'
    EFF_INDEX_SIZE = 'eff_index_size'
    VAR_COUNT = 'count of variables in model'
    CONSTR_COUNT = 'count of constraints in model'


# these values were captured on base level runs of the .dat files in the tests/testing_data folder
test_vals = {
    'test_system': {
        # reduced after removing ancient 1-year-shift obj function bug
        ExpectedVals.OBJ_VALUE: 468550.1905,
        ExpectedVals.EFF_DOMAIN_SIZE: 30720,
        ExpectedVals.EFF_INDEX_SIZE: 74,
        # increased by 2 when reworking storageinit.
        # increased after making annualretirement derived var
        ExpectedVals.CONSTR_COUNT: 2834,
        # reduced by 6 when reworking storageinit.
        # increased after making annualretirement derived var
        # reduced 2025/07/21 after removing existing vintage V_NewCapacity indices
        ExpectedVals.VAR_COUNT: 1900,
    },
    'utopia': {
        # reduced after reworking storageinit -> storage was less constrained
        # reduced after removing ancient 1-year-shift obj function bug
        # increased after rework of inter-season sequencing
        # reduced after changing fixed costs from MLP to PL
        ExpectedVals.OBJ_VALUE: 34711.5173,
        ExpectedVals.EFF_DOMAIN_SIZE: 12312,
        ExpectedVals.EFF_INDEX_SIZE: 64,
        # reduced 3/27:  unlim_cap techs now employed.
        # increased after making annualretirement derived var
        ExpectedVals.CONSTR_COUNT: 1471,
        # reduced 3/27:  unlim_cap techs now employed.
        # reduced by 4 in storageinit rework.
        # increased after making annualretirement derived var
        # reduced 2025/07/21 after removing existing vintage V_NewCapacity indices
        ExpectedVals.VAR_COUNT: 1055, 
    },
    'mediumville': {
        # added 2025/06/12 prior to addition of dynamic reserve margin
        # reduced 2025/06/16 after fixing bug in db
        ExpectedVals.OBJ_VALUE: 7035.7275,
        ExpectedVals.EFF_DOMAIN_SIZE: 2800,
        ExpectedVals.EFF_INDEX_SIZE: 18,
        # increased after reviving RampSeason constraints
        ExpectedVals.CONSTR_COUNT: 240,
        ExpectedVals.VAR_COUNT: 140, 
    },
    'seasonal_storage': {
        # added 2025/06/16 after addition of seasonal storage
        ExpectedVals.OBJ_VALUE: 76661.0231,
        ExpectedVals.EFF_DOMAIN_SIZE: 24,
        ExpectedVals.EFF_INDEX_SIZE: 4,
        ExpectedVals.CONSTR_COUNT: 182,
        ExpectedVals.VAR_COUNT: 90, 
    },
    'survival_curve': {
        # added 2025/06/19 after addition of survival curves
        # reduced after changing fixed costs from MLP to PL
        # increased after adding PeriodSurvivalCurve
        ExpectedVals.OBJ_VALUE: 31.9423,
        ExpectedVals.EFF_DOMAIN_SIZE: 64,
        ExpectedVals.EFF_INDEX_SIZE: 8,
        ExpectedVals.CONSTR_COUNT: 101,
        # reduced 2025/07/21 after removing existing vintage V_NewCapacity indices
        ExpectedVals.VAR_COUNT: 101, 
    },
}
