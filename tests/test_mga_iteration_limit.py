"""
Test that an MGA run records exactly the number of alternative solutions requested with the
iteration_limit option, regardless of the number of workers solving in parallel.
"""

import contextlib
import shutil
import sqlite3
from pathlib import Path

import pytest

from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig

UTOPIA_DB = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'

CONFIG_TEMPLATE = """
scenario = "mga_limit"
scenario_mode = "mga"
input_database = "{db}"
output_database = "{db}"
neos = false
solver = "appsi_highs"
time_sequencing = "seasonal_timeslices"
days_per_period = 365
reserve_margin = "static"

[MGA]
cost_epsilon = 0.03
iteration_limit = {iteration_limit}
time_limit_hrs = 1
axis = "tech_category_activity"
weighting = "hull_expansion"
"""


@pytest.mark.parametrize('iteration_limit', [1, 4])
def test_mga_iteration_limit_is_exact(iteration_limit: int, tmp_path: Path) -> None:
    db = tmp_path / 'utopia_mga_limit.sqlite'
    shutil.copy(UTOPIA_DB, db)
    config_file = tmp_path / 'config.toml'
    config_file.write_text(
        CONFIG_TEMPLATE.format(db=db.as_posix(), iteration_limit=iteration_limit)
    )

    config = TemoaConfig.build_config(config_file=config_file, output_path=tmp_path, silent=True)
    TemoaSequencer(config=config).start()

    with contextlib.closing(sqlite3.connect(db)) as con:
        scenarios = {
            row[0]
            for row in con.execute(
                'SELECT DISTINCT scenario FROM output_net_capacity '
                "WHERE scenario LIKE 'mga_limit-%'"
            ).fetchall()
        }

    assert 'mga_limit-0' in scenarios
    assert len(scenarios) == iteration_limit + 1, (
        f'expected the base solve + {iteration_limit} alternatives, got: {sorted(scenarios)}'
    )
