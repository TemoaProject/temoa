"""
Test a couple full-runs to match objective function value and some internals
"""

import logging
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pyomo.core import Constraint, Var
from pyomo.environ import check_optimal_termination, value
from pyomo.opt import SolverResults

# from src.temoa_model.temoa_model import temoa_create_model
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel
from tests.legacy_test_values import ExpectedVals, test_vals

if TYPE_CHECKING:
    import pyomo.environ as pyo

logger = logging.getLogger(__name__)
# list of test scenarios for which we have captured results in legacy_test_values.py
legacy_config_files = [
    {'name': 'utopia', 'filename': 'config_utopia.toml'},
    {'name': 'test_system', 'filename': 'config_test_system.toml'},
    {'name': 'mediumville', 'filename': 'config_mediumville.toml'},
    {'name': 'seasonal_storage', 'filename': 'config_seasonal_storage.toml'},
    {'name': 'survival_curve', 'filename': 'config_survival_curve.toml'},
    {'name': 'annualised_demand', 'filename': 'config_annualised_demand.toml'},
]

myopic_files = [{'name': 'myopic utopia', 'filename': 'config_utopia_myopic.toml'}]


@pytest.mark.parametrize(
    'system_test_run',
    argvalues=legacy_config_files,
    indirect=True,
    ids=[d['name'] for d in legacy_config_files],
)
def test_against_legacy_outputs(
    system_test_run: tuple[str, SolverResults | None, TemoaModel | None, TemoaSequencer],
) -> None:
    """
    This test compares tests of legacy models to captured test results
    """
    data_name, res, mdl, _ = system_test_run
    logger.info('Starting output test on scenario: %s', data_name)

    # Defensive checks for test fixture results
    assert res is not None, f'No solver results for {data_name}'
    assert isinstance(res, SolverResults), (
        f'Expected SolverResults object for {data_name}, got {type(res)}'
    )
    assert mdl is not None, f'No model for {data_name}'

    expected_vals = test_vals.get(data_name)  # a dictionary of expected results
    assert expected_vals is not None, f'No expected values for {data_name}'

    # Inspect some summary results
    # Use check_optimal_termination instead of checking raw status string
    # Different solvers report status differently (e.g., HiGHS reports 'unknown' but is optimal)
    assert check_optimal_termination(res), f'Solver did not terminate optimally for {data_name}'

    # Get objective value from the model instance instead of results object
    # HiGHS doesn't populate the results object the same way as CBC
    obj_value = value(mdl.total_cost)
    assert obj_value == pytest.approx(expected_vals[ExpectedVals.OBJ_VALUE], 0.00001)

    # inspect a couple set sizes
    efficiency_param: pyo.Param = mdl.efficiency
    # check the set membership
    assert (
        len(tuple(efficiency_param.sparse_iterkeys())) == expected_vals[ExpectedVals.EFF_INDEX_SIZE]
    ), 'should match legacy numbers'

    # check the size of the domain.  NOTE:  The build of the domain here may be "expensive" for
    # large models
    assert (
        len(efficiency_param.index_set().domain) == expected_vals[ExpectedVals.EFF_DOMAIN_SIZE]
    ), 'should match legacy numbers'

    # inspect the total variable and constraint counts
    # gather some stats...
    c_count = 0
    v_count = 0
    for constraint in mdl.component_objects(ctype=Constraint):
        c_count += len(constraint)
    for var in mdl.component_objects(ctype=Var):
        v_count += len(var)

    # check the count of constraints & variables
    assert c_count == expected_vals[ExpectedVals.CONSTR_COUNT], 'should have this many constraints'
    assert v_count == expected_vals[ExpectedVals.VAR_COUNT], 'should have this many variables'


@pytest.mark.parametrize(
    'system_test_run', argvalues=myopic_files, indirect=True, ids=[d['name'] for d in myopic_files]
)
def test_myopic_utopia(
    system_test_run: tuple[str, SolverResults | None, TemoaModel | None, TemoaSequencer],
) -> None:
    """
    Some cursory tests to ensure Myopic is running...  This is a very weak/simple test
    It mostly just ensures that the mode runs correctly and only checks 1 output.  Much
    more can be done with some certified test values...
    """
    # the model itself is fairly useless here, because several were run
    # we just want a hook to the output database...
    _, _, _, sequencer = system_test_run
    con = sqlite3.connect(sequencer.config.output_database)
    cur = con.cursor()
    res = cur.execute('SELECT SUM(d_invest) FROM main.output_cost').fetchone()
    invest_sum = res[0]
    # reduced this target after storageinit rework
    # reduced after removing ancient 1-year shift bug from objective function
    # increased after rework of inter-season sequencing
    assert invest_sum == pytest.approx(11004.8335), 'sum of investment costs did not match expected'
    con.close()


def test_graphviz_integration(tmp_path: Path) -> None:
    """
    Test that graphviz diagrams are generated during a full run when enabled.
    """
    # Use utopia config as a base
    config_file = Path(__file__).parent / 'testing_configs' / 'config_utopia.toml'

    # Build config with graphviz output enabled
    config = TemoaConfig.build_config(
        config_file=config_file,
        output_path=tmp_path,
        silent=True,
    )

    # Enable graphviz output
    config.graphviz_output = True

    # Run the sequencer
    sequencer = TemoaSequencer(config=config)
    sequencer.start()

    # The graphviz generator creates a subdirectory like: {db_name}_{scenario}_graphviz
    # Find any directory matching the pattern *_graphviz
    graphviz_dirs = list(tmp_path.glob('*_graphviz'))
    assert len(graphviz_dirs) > 0, 'Graphviz output directory should be created'

    graphviz_dir = graphviz_dirs[0]
    assert graphviz_dir.is_dir(), 'Graphviz output should be a directory'

    # Check that at least some output files were generated (DOT or SVG files)
    output_files = list(graphviz_dir.rglob('*.svg')) + list(graphviz_dir.rglob('*.dot'))
    assert len(output_files) > 0, 'At least one diagram file should be generated'

    # Check that the files are not empty
    for output_file in output_files:
        assert output_file.stat().st_size > 0, f'{output_file.name} should not be empty'
