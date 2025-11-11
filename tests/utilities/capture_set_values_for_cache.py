"""
Quick utility to capture set values from a pyomo model to enable later comparison.

This file should not need to be run again unless model schema changes
"""

import json
import sys
from pathlib import Path

import pyomo.environ as pyo

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from tests.conftest import refresh_databases

print(
    'WARNING:  Continuing to execute this file will '
    'update the cached values in the testing_data folder'
    'from the sqlite databases in the same folder.  '
    'This should only need to be done if the schema or'
    'model have changed and that database has been updated.'
    '\nRunning this basically resets the expected value sets'
    'for Utopia, TestSystem, and Mediumville'
)

t = input('Type "Y" to continue, any other key to exit now.')
if t not in {'y', 'Y'}:
    sys.exit(0)

output_path = Path(__file__).parent.parent / 'testing_log'  # capture the log here
output_path.mkdir(parents=True, exist_ok=True)

scenarios = [
    {
        'output_file': Path(__file__).parent.parent / 'testing_data' / 'utopia_sets.json',
        'config_file': Path(__file__).parent / 'config_utopia.toml',
    },
    {
        'output_file': Path(__file__).parent.parent / 'testing_data' / 'test_system_sets.json',
        'config_file': Path(__file__).parent / 'config_test_system.toml',
    },
    {
        'output_file': Path(__file__).parent.parent / 'testing_data' / 'mediumville_sets.json',
        'config_file': Path(__file__).parent / 'config_mediumville.toml',
    },
]
# make new copies of the DB's from source...
refresh_databases()

for scenario in scenarios:
    config = TemoaConfig.build_config(
        config_file=scenario['config_file'], output_path=output_path, silent=True
    )
    ts = TemoaSequencer(config=config)

    built_instance = ts.build_model()  # catch the built model

    model_sets = built_instance.component_map(ctype=pyo.Set)
    sets_dict = {k: list(v) for k, v in model_sets.items()}

    # stash the result in a json file...
    with open(scenario['output_file'], 'w') as f_out:
        json.dump(sets_dict, f_out, indent=2)
