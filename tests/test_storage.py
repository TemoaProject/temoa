"""
The intent of this file is to test the storage relationships in the model

"""

import logging
from typing import Any

import pytest

from temoa.core.model import TemoaModel

logger = logging.getLogger(__name__)
# suitable scenarios for storage testing....singleton for now.
storage_config_files = [
    {'name': 'storageville', 'filename': 'config_storageville.toml'},
    {'name': 'test_system', 'filename': 'config_test_system.toml'},
]


@pytest.mark.parametrize(
    'system_test_run',
    argvalues=storage_config_files,
    indirect=True,
    ids=[d['name'] for d in storage_config_files],
)
def test_storage_fraction(system_test_run: tuple[str, Any, TemoaModel, Any]) -> None:
    """
    Level at the start of the time slice should equal the forced fraction
    """

    model: TemoaModel  # helps with typing for some reason...
    data_name, results, model, _ = system_test_run
    assert len(model.limit_storage_fraction_constraint_rpsdtv) > 0, (
        'This model does not appear to have any StorageFraction constraints to test'
    )

    for r, p, s, d, t, v, op in model.limit_storage_fraction_constraint_rpsdtv:
        energy = (
            model.limit_storage_fraction[r, p, s, d, t, v, op]
            * model.v_capacity[r, p, t, v].value  # type: ignore [attr-defined] # I can't figure out how to get mypy to see value through the pyomo stubs
            * model.capacity_to_activity[r, t]
            * (model.storage_duration[r, t] / 8760)
            * model.segment_fraction_per_season[p, s]
            * model.days_per_period
            * model.process_life_frac[r, p, t, v]
        )

        assert model.v_storage_level[r, p, s, d, t, v].value == pytest.approx(energy, abs=1e-5), (  # type: ignore [attr-defined] # I can't figure out how to get mypy to see value through the pyomo stubs
            f'model fails to initialise storage state at start of season {r, p, s, d, t, v}'
        )


@pytest.mark.parametrize(
    'system_test_run',
    argvalues=storage_config_files,
    indirect=True,
    ids=[d['name'] for d in storage_config_files],
)
def test_state_sequencing(system_test_run: tuple[str, Any, TemoaModel, Any]) -> None:
    """
    Make sure that everything is looping properly
    """

    model: TemoaModel  # helps with typing for some reason...
    data_name, results, model, _ = system_test_run
    assert len(model.storage_level_rpsdtv) > 0, (
        'This model does not appear to have any available storage components'
    )

    for r, p, s, d, t, v in model.storage_level_rpsdtv:
        charge = sum(
            model.v_flow_in[r, p, s, d, S_i, t, v, S_o].value * model.efficiency[r, S_i, t, v, S_o]  # type: ignore [attr-defined] # I can't figure out how to get mypy to see value through the pyomo stubs
            for S_i in model.process_inputs[r, p, t, v]
            for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
        )
        discharge = sum(
            model.v_flow_out[r, p, s, d, S_i, t, v, S_o].value  # type: ignore [attr-defined] # I can't figure out how to get mypy to see value through the pyomo stubs
            for S_o in model.process_outputs[r, p, t, v]
            for S_i in model.process_inputs_by_output[r, p, t, v, S_o]
        )

        s_next, d_next = model.time_next[p, s, d]

        state = model.v_storage_level[r, p, s, d, t, v].value  # type: ignore [attr-defined] # I can't figure out how to get mypy to see value through the pyomo stubs
        next_state = model.v_storage_level[r, p, s_next, d_next, t, v].value  # type: ignore [attr-defined] # I can't figure out how to get mypy to see value through the pyomo stubs

        assert state + charge - discharge == pytest.approx(next_state, abs=1e-5), (
            f'model fails to correctly sequence storage states {r, p, s, t, v} sequenced {s, d} '
            f'to {s_next, d_next}'
        )


@pytest.mark.parametrize(
    'system_test_run',
    argvalues=storage_config_files,
    indirect=True,
    ids=[d['name'] for d in storage_config_files],
)
def test_storage_flow_balance(system_test_run: tuple[str, Any, TemoaModel, Any]) -> None:
    """
    Test the balance of all inflows vs. all outflows.
    Note:  inflows are taxed by efficiency, so that is replicated here
    """
    model: TemoaModel  # helps with typing for some reason...
    data_name, results, model, _ = system_test_run
    assert len(model.storage_level_rpsdtv) > 0, (
        'This model does not appear to haveany available storage components'
    )
    for s_tech in model.tech_storage:
        inflow_indices = {
            (r, p, s, d, i, t, v, o)
            for r, p, s, d, i, t, v, o in model.flow_in_storage_rpsditvo
            if t == s_tech
        }
        outflow_indices = {
            (r, p, s, d, i, t, v, o)
            for r, p, s, d, i, t, v, o in model.flow_var_rpsditvo
            if t == s_tech
        }

        # calculate the inflow and outflow.  Inflow is taxed by efficiency in the model,
        # so we need to do that here as well
        inflow = sum(
            model.v_flow_in[r, p, s, d, i, t, v, o].value * model.efficiency[r, i, t, v, o]  # type: ignore [attr-defined] # I can't figure out how to get mypy to see value through the pyomo stubs
            for (r, p, s, d, i, t, v, o) in inflow_indices
        )
        outflow = sum(model.v_flow_out[idx].value for idx in outflow_indices)  # type: ignore [attr-defined] # I can't figure out how to get mypy to see value through the pyomo stubs

        assert inflow == pytest.approx(outflow, abs=1e-5), (
            f'total inflow and outflow of storage tech {s_tech} do not match',
            ' - there is a discontinuity of storage states',
        )


# devnote: the storage_init constraint was reworked into LimitStorageLevelFraction
# @pytest.mark.skip('not ready for primetime')
# def test_hard_initialization():
#     filename = 'config_storageville.toml'
#     options = {'silent': True, 'debug': True}
#     config_file = pathlib.Path(PROJECT_ROOT, 'tests', 'testing_configs', filename)

#     sequencer = TemoaSequencer(
#         config_file=config_file,
#         output_path=tmp_path,
#         mode_override=TemoaMode.BUILD_ONLY,
#         **options,
#     )
#     # get a built, unsolved model
#     model = sequencer.start()
#     model.v_storage_init['electricville', 'batt', 2025] = 0.5
