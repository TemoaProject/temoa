"""
The intent of this file is to test the storage relationships in the model

Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  12/29/23
"""

import logging
import pathlib

import pytest

from definitions import PROJECT_ROOT
from temoa.temoa_model.temoa_mode import TemoaMode
from temoa.temoa_model.temoa_model import TemoaModel
from temoa.temoa_model.temoa_sequencer import TemoaSequencer
from temoa.temoa_model.temoa_rules import (
    link_season_next_timeslice,
    loop_season_next_timeslice
)

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
def test_storage_fraction(system_test_run):
    """
    Level at the start of the time slice should equal the forced fraction
    """

    model: TemoaModel  # helps with typing for some reason...
    data_name, results, model, _ = system_test_run
    assert len(model.StorageFractionConstraint_rpsdtv) > 0, (
        'This model does not appear to have any StorageFraction constraints to test'
    )

    for r, p, s, d, t, v in model.StorageFractionConstraint_rpsdtv:

        energy = (
            model.StorageFraction[r, p, s, d, t, v]
            * model.V_Capacity[r, p, t, v].value
            * model.CapacityToActivity[r, t]
            * (model.StorageDuration[r, t] / 8760)
            * model.SegFracPerSeason[s]
            * 365
            * model.ProcessLifeFrac[r, p, t, v]
        )

        assert model.V_StorageLevel[r, p, s, d, t, v].value == pytest.approx(
            energy, rel=1e-3
        ), f'model fails to initialise storage state at start of season {r, p, s, d, t, v}'


@pytest.mark.parametrize(
    'system_test_run',
    argvalues=storage_config_files,
    indirect=True,
    ids=[d['name'] for d in storage_config_files],
)
def test_state_sequencing(system_test_run):
    """
    Make sure that everything is looping properly
    """

    model: TemoaModel  # helps with typing for some reason...
    data_name, results, model, _ = system_test_run
    assert len(model.StorageLevel_rpsdtv) > 0, (
        'This model does not appear to have any available storage components'
    )
    
    for r, p, s, d, t, v in model.StorageLevel_rpsdtv:

        charge = sum(
            model.V_FlowIn[r, p, s, d, S_i, t, v, S_o].value * model.Efficiency[r, S_i, t, v, S_o]
            for S_i in model.processInputs[r, p, t, v]
            for S_o in model.ProcessOutputsByInput[r, p, t, v, S_i]
        )
        discharge = sum(
            model.V_FlowOut[r, p, s, d, S_i, t, v, S_o].value
            for S_o in model.processOutputs[r, p, t, v]
            for S_i in model.ProcessInputsByOutput[r, p, t, v, S_o]
        )

        if model.link_seasons: s_next, d_next = link_season_next_timeslice(model, s, d)
        else: s_next, d_next = loop_season_next_timeslice(model, s, d)

        state = model.V_StorageLevel[r, p, s, d, t, v].value
        next_state = model.V_StorageLevel[r, p, s_next, d_next, t, v].value
    
        assert state + charge - discharge == pytest.approx(
           next_state, rel=1e-3
        ), f'model fails to correctly sequence storage states {r, p, s, t, v}'


@pytest.mark.parametrize(
    'system_test_run',
    argvalues=storage_config_files,
    indirect=True,
    ids=[d['name'] for d in storage_config_files],
)
def test_storage_flow_balance(system_test_run):
    """
    Test the balance of all inflows vs. all outflows.
    Note:  inflows are taxed by efficiency, so that is replicated here
    """
    model: TemoaModel  # helps with typing for some reason...
    data_name, results, model, _ = system_test_run
    assert len(model.StorageLevel_rpsdtv) > 0, (
        'This model does not appear to have' 'any available storage components'
    )
    for s_tech in model.tech_storage:
        inflow_indices = {
            (r, p, s, d, i, t, v, o)
            for r, p, s, d, i, t, v, o in model.FlowInStorage_rpsditvo
            if t == s_tech
        }
        outflow_indices = {
            (r, p, s, d, i, t, v, o)
            for r, p, s, d, i, t, v, o in model.FlowVar_rpsditvo
            if t == s_tech
        }

        # calculate the inflow and outflow.  Inflow is taxed by efficiency in the model,
        # so we need to do that here as well
        inflow = sum(
            model.V_FlowIn[r, p, s, d, i, t, v, o].value * model.Efficiency[r, i, t, v, o]
            for (r, p, s, d, i, t, v, o) in inflow_indices
        )
        outflow = sum(model.V_FlowOut[idx].value for idx in outflow_indices)
        
        assert inflow == pytest.approx(
            outflow, rel=1e-3
        ), (f'total inflow and outflow of storage tech {s_tech} do not match',
            ' - there is a discontinuity of storage states')


@pytest.mark.skip('not ready for primetime')
def test_hard_initialization():
    filename = 'config_storageville.toml'
    options = {'silent': True, 'debug': True}
    config_file = pathlib.Path(PROJECT_ROOT, 'tests', 'testing_configs', filename)

    sequencer = TemoaSequencer(
        config_file=config_file,
        output_path=tmp_path,
        mode_override=TemoaMode.BUILD_ONLY,
        **options,
    )
    # get a built, unsolved model
    model = sequencer.start()
    model.V_StorageInit['electricville', 'batt', 2025] = 0.5
