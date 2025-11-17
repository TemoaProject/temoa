"""
a container for test values from legacy code (Python 3.7 / Pyomo 5.5) captured for
continuity/development testing

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
        # reduced 2025/07/25 by 504 after annualising demands
        # increased 2025/08/19 after making annual demands optional
        ExpectedVals.CONSTR_COUNT: 2810,
        # reduced by 6 when reworking storageinit.
        # increased after making annualretirement derived var
        # reduced 2025/07/21 after removing existing vintage v_new_capacity indices
        # reduced 2025/07/25 by 420 after annualising demands
        # increased 2025/08/19 after making annual demands optional
        ExpectedVals.VAR_COUNT: 1960,
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
        # reduced 2025/07/25 by 225 after annualising demands
        # increased 2025/08/19 after making annual demands optional
        ExpectedVals.CONSTR_COUNT: 1486,
        # reduced 3/27:  unlim_cap techs now employed.
        # reduced by 4 in storageinit rework.
        # increased after making annualretirement derived var
        # reduced 2025/07/21 after removing existing vintage v_new_capacity indices
        # reduced 2025/07/25 by 200 after annualising demands
        # increased 2025/08/19 after making annual demands optional
        ExpectedVals.VAR_COUNT: 1095,
    },
    'mediumville': {
        # added 2025/06/12 prior to addition of dynamic reserve margin
        # reduced 2025/06/16 after fixing bug in db
        ExpectedVals.OBJ_VALUE: 7035.7275,
        ExpectedVals.EFF_DOMAIN_SIZE: 2800,
        ExpectedVals.EFF_INDEX_SIZE: 18,
        # increased after reviving RampSeason constraints
        # reduced 2025/07/25 by 24 after annualising demands
        # increased 2025/08/19 after making annual demands optional
        ExpectedVals.CONSTR_COUNT: 240,
        # reduced 2025/07/25 by 18 after annualising demands
        # increased 2025/08/19 after making annual demands optional
        ExpectedVals.VAR_COUNT: 146,
    },
    'seasonal_storage': {
        # added 2025/06/16 after addition of seasonal storage
        ExpectedVals.OBJ_VALUE: 76661.0231,
        ExpectedVals.EFF_DOMAIN_SIZE: 24,
        ExpectedVals.EFF_INDEX_SIZE: 4,
        # reduced 2025/07/25 by 7 after annualising demands
        # increased 2025/08/19 after making annual demands optional
        ExpectedVals.CONSTR_COUNT: 183,
        # reduced 2025/07/25 by 7 after annualising demands
        # increased 2025/08/19 after making annual demands optional
        ExpectedVals.VAR_COUNT: 91,
    },
    'survival_curve': {
        # added 2025/06/19 after addition of survival curves
        # reduced after changing fixed costs from MLP to PL
        # increased after adding Periodsurvival_curve
        ExpectedVals.OBJ_VALUE: 31.9423,
        ExpectedVals.EFF_DOMAIN_SIZE: 64,
        ExpectedVals.EFF_INDEX_SIZE: 8,
        ExpectedVals.CONSTR_COUNT: 127,
        # reduced 2025/07/21 after removing existing vintage v_new_capacity indices
        ExpectedVals.VAR_COUNT: 127,
    },
    'annualised_demand': {
        # added 2025/06/19 after addition of survival curves
        # reduced after changing fixed costs from MLP to PL
        # increased after adding Periodsurvival_curve
        ExpectedVals.OBJ_VALUE: 1.9524,
        ExpectedVals.EFF_DOMAIN_SIZE: 36,
        ExpectedVals.EFF_INDEX_SIZE: 10,
        ExpectedVals.CONSTR_COUNT: 15,
        # reduced 2025/07/21 after removing existing vintage v_new_capacity indices
        ExpectedVals.VAR_COUNT: 21,
    },
}
