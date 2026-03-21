"""
Quick utility to capture set values from a pyomo model to enable later comparison.

This file should not need to be run again unless model schema changes
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pyomo.environ as pyo

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode
from tests.conftest import refresh_databases

print(
    'WARNING:  Continuing to execute this file will '
    'update the cached values in the testing_data folder'
    'from the sqlite databases in the same folder. '
    'This should only need to be done if the schema or '
    'model have changed and that database has been updated.'
    '\nRunning this basically resets the expected value sets'
    'for Utopia, TestSystem, and Mediumville'
)

t = 'Y'  # automated run
if t not in {'y', 'Y'}:
    sys.exit(0)

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

    def hash_set(s: Any) -> str:
        try:
            sorted_elements = sorted(s)
        except TypeError:
            sorted_elements = sorted([str(e) for e in s])
        s_bytes = json.dumps(sorted_elements).encode('utf-8')
        return hashlib.sha256(s_bytes).hexdigest()

    model_sets = built_instance.component_map(ctype=pyo.Set)
    sets_dict = {
        k: hash_set(v) for k, v in model_sets.items() if '_index' not in k and '_domain' not in k
    }

    # stash the result in a json file...
    with open(scenario['output_file'], 'w') as f_out:
        json.dump(sets_dict, f_out, indent=2)
