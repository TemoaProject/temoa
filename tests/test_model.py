"""
A series of tests focused on the model entity.

Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  12/6/23

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

import pathlib
import pickle

from definitions import PROJECT_ROOT
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.modes import TemoaMode


def test_serialization():
    """
    Test to ensure the model pickles properly.  This is used when employing mpi4py which requires
    that jobs passed are pickle-able
    """
    config_file = 'config_utopia.toml'
    config_file = pathlib.Path(PROJECT_ROOT, 'tests', 'testing_configs', config_file)
    output_path = pathlib.Path(PROJECT_ROOT, 'tests', 'testing_outputs')
    options = {'silent': True, 'debug': True}
    ts = TemoaSequencer(
        config_file=config_file,
        output_path=output_path,
        mode_override=TemoaMode.BUILD_ONLY,
        **options,
    )

    built_instance = ts.start()

    pickled_model = pickle.dumps(built_instance)
    assert pickled_model, 'model should have pickled successfully, but did not.'

    recovered_model = pickle.loads(pickled_model)
    assert recovered_model, 'unable to recover model.'
