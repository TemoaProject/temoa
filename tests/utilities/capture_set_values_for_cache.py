"""
Quick utility to capture set values from a pyomo model to enable later comparison.

This file should not need to be run again unless model schema changes
"""

import json
from pathlib import Path

import pyomo.environ as pyo

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode
from tests.conftest import refresh_databases
from tests.utilities.hash_utils import hash_set

output_path = Path(__file__).parent.parent / 'testing_log'  # capture the log here
output_path.mkdir(parents=True, exist_ok=True)

scenarios = [
    {
        'output_file': Path(__file__).parent.parent / 'testing_data' / 'utopia_sets.json',
        'config_file': Path(__file__).parent.parent / 'testing_configs' / 'config_utopia.toml',
    },
    {
        'output_file': Path(__file__).parent.parent / 'testing_data' / 'test_system_sets.json',
        'config_file': Path(__file__).parent.parent / 'testing_configs' / 'config_test_system.toml',
    },
    {
        'output_file': Path(__file__).parent.parent / 'testing_data' / 'mediumville_sets.json',
        'config_file': Path(__file__).parent.parent / 'testing_configs' / 'config_mediumville.toml',
    },
]
# make new copies of the DB's from source...
refresh_databases()

for scenario in scenarios:
    config = TemoaConfig.build_config(
        config_file=scenario['config_file'], output_path=output_path, silent=True
    )
    ts = TemoaSequencer(config=config, mode_override=TemoaMode.BUILD_ONLY)

    built_instance = ts.build_model()  # catch the built model

    model_sets = built_instance.component_map(ctype=pyo.Set)
    sets_dict = {
        k: hash_set(v) for k, v in model_sets.items() if '_index' not in k and '_domain' not in k
    }

    # stash the result in a json file...
    with open(scenario['output_file'], 'w') as f_out:
        json.dump(sets_dict, f_out, indent=2, sort_keys=True)
