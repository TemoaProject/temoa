import logging
import os
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from pyomo.opt import SolverResults

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel

logger = logging.getLogger(__name__)

# set the target folder for output from testing
output_path = Path(__file__).parent / 'testing_log'
if not output_path.exists():
    output_path.mkdir()

# set up logger in conftest.py so that it is properly anchored in the test folder.
filename = 'testing.log'
logging.basicConfig(
    filename=output_path / filename,
    filemode='w',
    format='%(asctime)s | %(module)s | %(levelname)s | %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.DEBUG,  # <-- global change for testing activities is here
)

logging.getLogger('pyomo').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('pyutilib').setLevel(logging.WARNING)


def refresh_databases() -> None:
    """make new databases from source for testing...  removes possibility of contamination by earlier runs"""
    data_output_path = Path(__file__).parent / 'testing_outputs'
    data_source_path = Path(__file__).parent / 'testing_data'
    databases = (
        ('utopia.sql', 'utopia.sqlite'),
        ('utopia.sql', 'myo_utopia.sqlite'),
        ('test_system.sql', 'test_system.sqlite'),
        ('storageville.sql', 'storageville.sqlite'),
        ('mediumville.sql', 'mediumville.sqlite'),
        ('emissions.sql', 'emissions.sqlite'),
        ('materials.sql', 'materials.sqlite'),
        ('simple_linked_tech.sql', 'simple_linked_tech.sqlite'),
        ('seasonal_storage.sql', 'seasonal_storage.sqlite'),
        ('survival_curve.sql', 'survival_curve.sqlite'),
        ('annualised_demand.sql', 'annualised_demand.sqlite'),
    )
    for src, db in databases:
        if Path.exists(data_output_path / db):
            os.remove(data_output_path / db)
        # make a new one and fill it
        con = sqlite3.connect(data_output_path / db)
        with open(data_source_path / src) as script:
            con.executescript(script.read())
        con.close()


refresh_databases()


@pytest.fixture()
def system_test_run(
    request: Any, tmp_path: Path
) -> tuple[Any, SolverResults | None, TemoaModel | None, TemoaSequencer]:
    """
    spin up the model, solve it, and hand over the model and result for inspection
    """
    data_name = request.param['name']
    logger.info('Setting up and solving: %s', data_name)
    filename = request.param['filename']
    config_file = Path(__file__).parent / 'testing_configs' / filename

    config = TemoaConfig.build_config(
        config_file=config_file,
        output_path=tmp_path,
        silent=True,
    )

    sequencer = TemoaSequencer(config=config)

    sequencer.start()

    # The rest of the fixture returns the solved instance from the sequencer
    return (
        data_name,
        sequencer.pf_results,
        sequencer.pf_solved_instance,
        sequencer,
    )
