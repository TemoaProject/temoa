from pathlib import Path
from typing import Any

import pytest
from pyomo.environ import ConcreteModel

# Import the new dependencies
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode

# Define the config file path once
TESTING_CONFIGS_DIR = Path(__file__).parent / 'testing_configs'
UTOPIA_MYOPIC_CONFIG = TESTING_CONFIGS_DIR / 'config_utopia_myopic.toml'

# Define test parameters
# Note: Separated BUILD_ONLY as it uses a different method now
run_params = [
    {'name': 'check', 'mode': TemoaMode.CHECK},
    {'name': 'pf', 'mode': TemoaMode.PERFECT_FORESIGHT},
    {'name': 'myopic', 'mode': TemoaMode.MYOPIC},
    {'name': 'MGA', 'mode': TemoaMode.MGA},
]


def id_func(p: dict[str, Any]) -> str:
    return p['name']


# Suppress mypy error for pytest.mark.parametrize by using a more specific ignore
@pytest.mark.parametrize('run_data', run_params, ids=id_func)
def test_sequencer_start(run_data: dict[str, Any], tmp_path: Path) -> None:
    """
    Tests the main `start()` method for various run modes.
    """
    # Step 1: Create the TemoaConfig object first.
    # The 'silent' flag is now part of the config.
    config = TemoaConfig.build_config(
        config_file=UTOPIA_MYOPIC_CONFIG,
        output_path=tmp_path,
        silent=True,
    )

    # Step 2: Instantiate the sequencer with the config object.
    # The mode is passed as an override.
    sequencer = TemoaSequencer(
        config=config,
        mode_override=run_data['mode'],
    )

    # Step 3: Call the `start()` method.
    # Any failure will raise an exception, which pytest will catch.
    sequencer.start()


def test_sequencer_build_model(tmp_path: Path) -> None:
    """
    Tests the dedicated `build_model()` method for the BUILD_ONLY mode.
    """
    # Step 1: Create the config object.
    config = TemoaConfig.build_config(
        config_file=UTOPIA_MYOPIC_CONFIG,
        output_path=tmp_path,
        silent=True,
    )

    # Step 2: Instantiate the sequencer.
    sequencer = TemoaSequencer(
        config=config,
        mode_override=TemoaMode.BUILD_ONLY,
    )

    # Step 3: Call the `build_model()` method and check the return value.
    model = sequencer.build_model()
    assert model is not None, 'sequencer.build_model() should return a model'
    assert isinstance(model, ConcreteModel), 'Should return a Pyomo ConcreteModel'
