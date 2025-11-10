"""
A series of tests focused on the model entity.
"""

import pathlib
import pickle

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode


def test_serialization() -> None:
    """
    Test to ensure the model pickles properly. This is used when employing mpi4py which requires
    that jobs passed are pickle-able.
    """
    config_filename = 'config_utopia.toml'
    config_file_path = pathlib.Path(__file__).parent / 'testing_configs' / config_filename
    output_path = pathlib.Path(__file__).parent / 'testing_outputs'

    config = TemoaConfig.build_config(
        config_file=config_file_path, output_path=output_path, silent=True
    )
    ts = TemoaSequencer(config=config, mode_override=TemoaMode.BUILD_ONLY)

    # Use the correct method for build-only mode
    built_instance = ts.build_model()

    # The actual test: try to pickle the model
    pickle.dumps(built_instance)
