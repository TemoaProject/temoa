"""
Utility to capture the set sizes for inspection/comparison
"""

import json
import logging
import sys
from pathlib import Path

import pyomo.environ as pyo

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig

logger = logging.getLogger(__name__)

print(
    'WARNING:  Continuing to execute this file will update the cached values for the set sizes '
    'for US_9R model in the testing_data folder from the sqlite databases in the same folder.  '
    'This should only need to be done if the schema or model have changed and that database has '
    'been updated.'
)

t = input('Type "Y" to continue, any other key to exit now.')
if t not in {'y', 'Y'}:
    sys.exit(0)
output_file = Path(__file__).parent.parent / 'testing_data' / 'US_9R_8D_set_sizes.json'
config_file_path = Path(__file__).parent / 'config_US_9R_8D.toml'
output_path = Path(__file__).parent.parent / 'testing_log'
output_path.mkdir(parents=True, exist_ok=True)

options = {'silent': True}
config = TemoaConfig.build_config(
    config_file=config_file_path, output_path=output_path, silent=options['silent']
)
sequencer = TemoaSequencer(config=config)
instance = sequencer.build_model()  # catch the built model

model_sets = instance.component_map(ctype=pyo.Set)
sets_dict = {k: len(v) for k, v in model_sets.items() if '_index' not in k}

# stash the result in a json file...
with open(output_file, 'w') as f_out:
    json.dump(sets_dict, f_out, indent=2)
