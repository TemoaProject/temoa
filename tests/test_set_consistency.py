"""
These tests are designed to check the construction of the numerous sets in the 2 exemplar models:
Utopia and Test System.
"""

import hashlib
import json
import pathlib
from typing import Any

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

    def hash_set(s: Any) -> str:
        try:
            sorted_elements = sorted(s)
        except TypeError:
            sorted_elements = sorted([str(e) for e in s])
        s_bytes = json.dumps(sorted_elements).encode('utf-8')
        return hashlib.sha256(s_bytes).hexdigest()

    # retrieve the cache which now stores hashes
    cache_file = pathlib.Path(__file__).parent / 'testing_data' / set_file
    with open(cache_file) as src:
        cached_sets = json.load(src)

    # compare hashes where they exist in the model.
    mismatched_sets = {}
    for set_name, s in model_sets.items():
        if set_name == 'cost_emission_rpe':
            pass
        if '_index' in set_name or '_domain' in set_name:
            continue

        model_hash = hash_set(s)
        cached_hash = cached_sets.get(set_name)
        if cached_hash is not None and cached_hash != model_hash:
            mismatched_sets[set_name] = {'cached': cached_hash, 'model': model_hash}

    missing_in_model = cached_sets.keys() - model_sets.keys()
    # drop any set that has "_index" in the name as they are no longer reported by newer version of
    # pyomo
    missing_in_model = {s for s in missing_in_model if '_index' not in s and '_domain' not in s}

    if mismatched_sets:
        print('\nMismatched sets compared to cache (hashes differ): ')
        for k, hashes in mismatched_sets.items():
            print(f'{k}: cached={hashes["cached"]}, model={hashes["model"]}')

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
    assert not mismatched_sets, (
        f'The {data_name} run-produced sets did not match cached values (hashes differ)'
    )
    if cache_extra_sets:
        assert False, 'Cache has extra sets'  # noqa B011
    if model_extra_sets:
        assert False, 'Model has extra sets'  # noqa B011
