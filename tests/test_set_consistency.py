"""
These tests are designed to check the construction of the numerous sets in the 2 exemplar models:
Utopia and Test System.
"""

import json
import pathlib

import pytest
from pyomo import environ as pyo

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode

TESTING_CONFIGS_DIR = pathlib.Path(__file__).parent / 'testing_configs'

# Update params to just be filenames, we will construct the path inside the test
params = [
    ('utopia', 'config_utopia.toml', 'utopia_sets.json'),
    ('test_system', 'config_test_system.toml', 'test_system_sets.json'),
    ('mediumville', 'config_mediumville.toml', 'mediumville_sets.json'),
]


@pytest.mark.parametrize(
    argnames='data_name config_file set_file'.split(), argvalues=params, ids=[t[0] for t in params]
)
def test_set_consistency(
    data_name: str, config_file: str, set_file: str, tmp_path: pathlib.Path
) -> None:
    """
    test the set membership of the utopia model against cached values to ensure consistency
    """
    full_config_path = TESTING_CONFIGS_DIR / config_file

    config = TemoaConfig.build_config(
        config_file=full_config_path, output_path=tmp_path, silent=True
    )
    ts = TemoaSequencer(config=config, mode_override=TemoaMode.BUILD_ONLY)

    built_instance = ts.build_model()

    model_sets = built_instance.component_map(ctype=pyo.Set)
    model_sets = {k: set(v) for k, v in model_sets.items()}

    # retrieve the cache and convert the set values from list -> set (json can't store sets)
    cache_file = pathlib.Path(__file__).parent / 'testing_data' / set_file
    with open(cache_file) as src:
        cached_sets = json.load(src)
    cached_sets = {
        k: {tuple(t) if isinstance(t, list) else t for t in v} for (k, v) in cached_sets.items()
    }

    # compare sets where they exist in the model.
    overage_in_model = {}
    shortage_in_model = {}
    for set_name, s in model_sets.items():
        if set_name == 'cost_emission_rpe':
            pass
        if cached_sets.get(set_name) != s:
            cached_set = cached_sets.get(set_name, set())
            overage_in_model[set_name] = s - cached_set
            shortage_in_model[set_name] = cached_set - s
    missing_in_model = cached_sets.keys() - model_sets.keys()
    # drop any set that has "_index" in the name as they are no longer reported by newer version of
    # pyomo
    missing_in_model = {s for s in missing_in_model if '_index' not in s and '_domain' not in s}

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

    # look for new or dropped sets in EITHER
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

    assert not missing_in_model, f'one or more cached set not in model: {missing_in_model}'
    assert not overage_in_model and not shortage_in_model, (
        f'The {data_name} run-produced sets did not match cached values'
    )
    if cache_extra_sets:
        assert False, 'Cache has extra sets'  # noqa B011
    if model_extra_sets:
        assert False, 'Model has extra sets'  # noqa B011
