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
Created on:  6/22/24

A quick test on Linked Tech.  The scenario is described in an image in the testing_data folder:
simple_linked_tech_description.jpg

"""

import logging
import sqlite3
from pathlib import Path

import pytest

from definitions import PROJECT_ROOT

logger = logging.getLogger(__name__)
config_files = [
    {'name': 'link', 'filename': 'config_link_test.toml'},
]


@pytest.mark.parametrize(
    'system_test_run',
    argvalues=config_files,
    indirect=True,
    ids=[d['name'] for d in config_files],
)
def test_linked_tech(system_test_run):
    """Check a few known values.  See the note above in header regarding scenario reference"""
    data_name, res, mdl, _ = system_test_run
    # test emission of CO2
    output_db_path = Path(PROJECT_ROOT, 'tests', 'testing_outputs', 'simple_linked_tech.sqlite')
    print(output_db_path)
    conn = sqlite3.connect(str(output_db_path))
    co2_emiss = conn.execute(
        "SELECT emission FROM output_emissionn WHERE emis_comm = 'CO2'"
    ).fetchall()
    assert len(co2_emiss) == 1
    co2_emiss = co2_emiss[0][0]
    # check the total emission
    assert co2_emiss == pytest.approx(-30.0), (
        'the linked processes should remove have an aggregate -30 units of co2 emissions'
    )

    # check the flow out of captured carbon from the driven tech, which should output the captured carbon
    flow_out = conn.execute(
        "SELECT SUM(flow) FROM output_flow_out WHERE tech = 'CCS' and output_comm = 'CO2_CAP'"
    ).fetchone()[0]
    assert flow_out == pytest.approx(30.0)
