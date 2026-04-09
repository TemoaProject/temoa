import logging
import sqlite3
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core import TemoaMode
from temoa.core.config import TemoaConfig

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def solved_connection(
    request: Any, tmp_path_factory: Any
) -> Generator[tuple[sqlite3.Connection, str, str, int, float, str], None, None]:
    """
    spin up the model, solve it, and hand over a connection to the results db
    """
    data_name = 'materials'
    mode = request.param['mode']
    logger.info('Setting up and solving: %s in %s mode', data_name, mode)
    filename = 'config_materials.toml'
    config_file = Path(__file__).parent / 'testing_configs' / filename
    tmp_path = tmp_path_factory.mktemp('data')
    config = TemoaConfig.build_config(
        config_file=config_file,
        output_path=tmp_path,
        silent=True,
    )
    config.scenario_mode = TemoaMode[mode.upper()]
    config.scenario = request.param['name']
    if mode == 'myopic':
        assert config.myopic_inputs is not None
        config.myopic_inputs['view_depth'] = request.param['view_depth']
        config.myopic_inputs['step_size'] = request.param['step_size']
    sequencer = TemoaSequencer(config=config)

    sequencer.start()

    con = sqlite3.connect(sequencer.config.output_database)
    try:
        # Pass all necessary params for this specific test
        yield (
            con,
            request.param['name'],
            request.param['tech'],
            request.param['period'],
            request.param['target'],
            mode,
        )
    finally:
        con.close()


# List of tech archetypes to test and their correct flowout value
# Parametrized for both perfect_foresight and myopic modes
flow_tests = [
    {
        'name': 'lithium import - perfect foresight',
        'tech': 'IMPORT_LI',
        'period': 2000,
        'target': 0.129291623,
        'mode': 'perfect_foresight',
    },
    {
        'name': 'lithium import - myopic 1-1',
        'tech': 'IMPORT_LI',
        'period': 2000,
        'target': 0.129291623,
        'mode': 'myopic',
        'view_depth': 1,
        'step_size': 1,
    },
    {
        'name': 'lithium import - myopic 2-1',
        'tech': 'IMPORT_LI',
        'period': 2000,
        'target': 0.129291623,
        'mode': 'myopic',
        'view_depth': 2,
        'step_size': 1,
    },
    {
        'name': 'lithium import - myopic 3-1',
        'tech': 'IMPORT_LI',
        'period': 2000,
        'target': 0.129291623,
        'mode': 'myopic',
        'view_depth': 3,
        'step_size': 1,
    },
    {
        'name': 'lithium import - myopic 2-2',
        'tech': 'IMPORT_LI',
        'period': 2000,
        'target': 0.129291623,
        'mode': 'myopic',
        'view_depth': 2,
        'step_size': 2,
    },
    {
        'name': 'lithium import - myopic 3-2',
        'tech': 'IMPORT_LI',
        'period': 2000,
        'target': 0.129291623,
        'mode': 'myopic',
        'view_depth': 3,
        'step_size': 2,
    },
    {
        'name': 'lithium import - myopic 3-3',
        'tech': 'IMPORT_LI',
        'period': 2000,
        'target': 0.129291623,
        'mode': 'myopic',
        'view_depth': 3,
        'step_size': 3,
    },
]


# Flows
@pytest.mark.parametrize(
    'solved_connection',
    argvalues=flow_tests,
    indirect=True,
    ids=[str(t['name']) for t in flow_tests],
)
def test_flows(solved_connection: tuple[sqlite3.Connection, str, str, int, float, str]) -> None:
    """
    Test that the flows from each technology archetype
    are correct in both perfect foresight and myopic modes
    """
    con, name, tech, period, flow_target, _mode = solved_connection
    cursor = con.cursor()
    row = cursor.execute(
        'SELECT SUM(flow) FROM main.output_flow_out WHERE tech = ? AND period = ? AND scenario = ?',
        (tech, period, name),
    ).fetchone()
    # If the query returns no rows, row will be None.
    # If it finds rows but the sum is NULL, row[0] will be None.
    flow = row[0] if row and row[0] is not None else 0.0

    assert flow == pytest.approx(
        flow_target,
        rel=1e-5,
    ), f'{name} flows were incorrect. Should be {flow_target}, got {flow}'
