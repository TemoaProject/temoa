"""
Test a couple full-runs to match objective function value and some internals

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

import logging
import sqlite3

import pyomo.environ as pyo
import pytest
from pyomo.core import Constraint, Var

# from src.temoa_model.temoa_model import temoa_create_model
from tests.legacy_test_values import ExpectedVals, test_vals

logger = logging.getLogger(__name__)
# list of test scenarios for which we have captured results in legacy_test_values.py
legacy_config_files = [
    {'name': 'utopia', 'filename': 'config_utopia.toml'},
    {'name': 'test_system', 'filename': 'config_test_system.toml'},
]

myopic_files = [{'name': 'myopic utopia', 'filename': 'config_utopia_myopic.toml'}]


@pytest.mark.parametrize(
    'system_test_run',
    argvalues=legacy_config_files,
    indirect=True,
    ids=[d['name'] for d in legacy_config_files],
)
def test_against_legacy_outputs(system_test_run):
    """
    This test compares tests of legacy models to captured test results
    """
    data_name, res, mdl, _ = system_test_run
    logger.info('Starting output test on scenario: %s', data_name)
    expected_vals = test_vals.get(data_name)  # a dictionary of expected results

    # inspect some summary results
    assert res['Solution'][0]['Status'] == 'optimal'
    assert res['Solution'][0]['Objective']['TotalCost']['Value'] == pytest.approx(
        expected_vals[ExpectedVals.OBJ_VALUE], 0.00001
    )

    # inspect a couple set sizes
    efficiency_param: pyo.Param = mdl.Efficiency
    # check the set membership
    assert (
        len(tuple(efficiency_param.sparse_iterkeys())) == expected_vals[ExpectedVals.EFF_INDEX_SIZE]
    ), 'should match legacy numbers'

    # check the size of the domain.  NOTE:  The build of the domain here may be "expensive" for large models
    assert (
        len(efficiency_param.index_set().domain) == expected_vals[ExpectedVals.EFF_DOMAIN_SIZE]
    ), 'should match legacy numbers'

    # inspect the total variable and constraint counts
    # gather some stats...
    c_count = 0
    v_count = 0
    for constraint in mdl.component_objects(ctype=Constraint):
        c_count += len(constraint)
    for var in mdl.component_objects(ctype=Var):
        v_count += len(var)

    # check the count of constraints & variables
    assert c_count == expected_vals[ExpectedVals.CONSTR_COUNT], 'should have this many constraints'
    assert v_count == expected_vals[ExpectedVals.VAR_COUNT], 'should have this many variables'


@pytest.mark.parametrize(
    'system_test_run', argvalues=myopic_files, indirect=True, ids=[d['name'] for d in myopic_files]
)
def test_myopic_utopia(system_test_run):
    """
    Some cursory tests to ensure Myopic is running...  This is a very weak/simple test
    It mostly just ensures that the mode runs correctly and only checks 1 output.  Much
    more can be done with some certified test values...
    """
    # the model itself is fairly useless here, because several were run
    # we just want a hook to the output database...
    _, _, _, sequencer = system_test_run
    con = sqlite3.connect(sequencer.config.output_database)
    cur = con.cursor()
    res = cur.execute('SELECT SUM(d_invest) FROM main.OutputCost').fetchone()
    invest_sum = res[0]
    # reduced this target after storageinit rework
    assert invest_sum == pytest.approx(11525.19), 'sum of investment costs did not match expected'
    con.close()
