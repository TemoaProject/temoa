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
Created on:  3/14/24

"""

from pathlib import Path

import pytest

from definitions import PROJECT_ROOT
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.modes import TemoaMode

params = [
    {'name': 'build-only', 'mode': TemoaMode.BUILD_ONLY},
    {'name': 'check', 'mode': TemoaMode.CHECK},
    {'name': 'pf', 'mode': TemoaMode.PERFECT_FORESIGHT},
    {'name': 'myopic', 'mode': TemoaMode.MYOPIC},
    {'name': 'MGA', 'mode': TemoaMode.MGA},
]
# using the myopic config file for now below, becuase (a) it is most current db, (b) it is self-referencing
# for the database, which is needed for myopic, and (c) the mode is overriden anyhow!
config_file = Path(PROJECT_ROOT, 'tests', 'testing_configs', 'config_utopia_myopic.toml')


@pytest.mark.parametrize('run_data', params, ids=lambda p: p['name'])
def test_start(run_data, tmp_path):
    options = {'silent': True, 'debug': True, 'mode_override': run_data['mode']}
    sequencer = TemoaSequencer(
        config_file=config_file,
        output_path=tmp_path,
        **options,
    )
    sequencer.start()
