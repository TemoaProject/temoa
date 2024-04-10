"""
These tests are designed to check the construction of the numerous sets in the 2 exemplar models:
Utopia and Test System.

They construct all the pyomo Sets associated with the model and compare them with cached results that are stored
in json files

Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  9/26/23

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

import json
import pathlib

import pytest
from pyomo import environ as pyo

from definitions import PROJECT_ROOT
from temoa.temoa_model.temoa_sequencer import TemoaMode, TemoaSequencer

params = [
    ('utopia', 'config_utopia.toml', 'utopia_sets.json'),
    ('test_system', 'config_test_system.toml', 'test_system_sets.json'),
    ('mediumville', 'config_mediumville.toml', 'mediumville_sets.json'),
]


@pytest.mark.parametrize(
    argnames='data_name config_file set_file'.split(), argvalues=params, ids=[t[0] for t in params]
)
def test_set_consistency(data_name, config_file, set_file, tmp_path):
    """
    test the set membership of the utopia model against cached values to ensure consistency
    """
    config_file = pathlib.Path(PROJECT_ROOT, 'tests', 'testing_configs', config_file)
    options = {'silent': True, 'debug': True}
    ts = TemoaSequencer(
        config_file=config_file, output_path=tmp_path, mode_override=TemoaMode.BUILD_ONLY, **options
    )

    built_instance = ts.start()
    model_sets = built_instance.component_map(ctype=pyo.Set)
    model_sets = {k: set(v) for k, v in model_sets.items()}

    # retrieve the cache and convert the set values from list -> set (json can't store sets)
    cache_file = pathlib.Path(PROJECT_ROOT, 'tests', 'testing_data', set_file)
    with open(cache_file, 'r') as src:
        cached_sets = json.load(src)
    cached_sets = {
        k: set(tuple(t) if isinstance(t, list) else t for t in v) for (k, v) in cached_sets.items()
    }

    # compare sets where they exist in BOTH the cache and model
    overage_in_model = dict()
    shortage_in_model = dict()
    for set_name, s in model_sets.items():
        if cached_sets.get(set_name) != s:
            if cached_sets.get(set_name):
                overage_in_model[set_name] = s - cached_sets.get(set_name)
                shortage_in_model[set_name] = cached_sets.get(set_name) - s
    missing_in_model = cached_sets.keys() - model_sets.keys()
    # drop any set that has "_index" in the name as they are no longer reported by newer version of pyomo
    missing_in_model = {s for s in missing_in_model if '_index' not in s and '_domain' not in s}
    # assert not missing_in_model, f'one or more cached set not in model: {missing_in_model}'
    if overage_in_model:
        print('\nOverages compared to cache: ')
        for k, v in overage_in_model.items():
            if len(v) > 0:
                print(k, v)
    if shortage_in_model:
        print('\nShortages compared to cache: ')
        for k, v in shortage_in_model.items():
            if len(v) > 0:
                print(k, v)

    # look for new or dropped sets in either
    model_extra_sets = {
        k
        for k in model_sets.keys() - cached_sets.keys()
        if '_index' not in k and '_domain' not in k
    }
    cache_extra_sets = {
        k
        for k in cached_sets.keys() - model_sets.keys()
        if '_index' not in k and '_domain' not in k
    }
    if model_extra_sets:
        print('\nModel extra sets compared to cache: ')
        for k in model_extra_sets:
            print(f'{k}: {model_sets[k]}')
    if cache_extra_sets:
        print('\nCache extra sets compared to model: ')
        for k in cache_extra_sets:
            print(f'{k}: {cached_sets[k]}')

    assert (
        not overage_in_model and not shortage_in_model
    ), f'The {data_name} run-produced sets did not match cached values'
