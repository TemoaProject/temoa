"""
Test some emissions and curtailment results for some basic technology archetypes

Written by:  Ian David Elder
iandavidelder@gmail.com
Created on:  2025/05/01

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
from pathlib import Path

import pytest

from definitions import PROJECT_ROOT
from temoa.temoa_model.temoa_sequencer import TemoaSequencer

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def solved_connection(request, tmp_path_factory):
    """
    spin up the model, solve it, and hand over a connection to the results db
    """
    data_name = 'materials'
    logger.info('Setting up and solving: %s', data_name)
    filename = 'config_materials.toml'
    options = {'silent': True, 'debug': True}
    config_file = Path(PROJECT_ROOT, 'tests', 'testing_configs', filename)
    tmp_path = tmp_path_factory.mktemp('data')
    sequencer = TemoaSequencer(
        config_file=config_file,
        output_path=tmp_path,
        **options,
    )

    sequencer.start()
    # make connection here as in your code...
    con = sqlite3.connect(sequencer.config.output_database)
    yield con, request.param['name'], request.param['tech'], request.param['period'], request.param['target']
    con.close()


# List of tech archetypes to test and their correct flowout value
flow_tests = [
    {'name': 'lithium import', 'tech': 'IMPORT_LI', 'period': 2000, 'target': 0.129291623},
]

# Flows
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=flow_tests,
    indirect=True,
    ids=[t['name'] for t in flow_tests],
)
def test_flows(solved_connection):
    """
    Test that the emissions from each technology archetype are correct, and check total emissions
    """
    con, name, tech, period, flow_target = solved_connection
    flow = (
        con.cursor()
        .execute(f"SELECT SUM(flow) FROM main.OutputFlowOut WHERE tech == '{tech}' AND period == {period}")
        .fetchone()[0]
    )
    assert flow == pytest.approx(
        flow_target
    ), f'{name} flows were incorrect. Should be {flow_target}, got {flow}'