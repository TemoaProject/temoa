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

logger = logging.getLogger(__name__)
# suitable scenarios for storage testing....singleton for now.
storage_config_files = [
    {'name': 'storageville', 'filename': 'config_storageville.toml'},
    {'name': 'test_system', 'filename': 'config_test_system.toml'},
]


@pytest.mark.skip(reason='known not working...fix deferred')
@pytest.mark.parametrize(
    'system_test_run',
    argvalues=storage_config_files,
    indirect=True,
    ids=[d['name'] for d in storage_config_files],
)
def test_initialization_in_last_period(system_test_run):
    """
    The last period should end up back at the initialization value
    """
    model: TemoaModel  # helps with typing for some reason...
    data_name, results, model, _ = system_test_run
    assert len(model.V_StorageInit.index_set()) > 0, (
        'This model does not appear to haveany available storage components'
    )
    # get references to last timeslot for each prtv combo in things with storage
    last_slots = {
        (r, p, s, d, t, v)
        for r, p, s, d, t, v in model.StorageLevel_rpsdtv
        if s == model.time_season.last() and d == model.time_of_day.last()
    }
    # test that the last day/season combo ends up at the initialization value
    # devnote:  the Level variable is assessed at the end of the timeperiod
    for r, p, s, d, t, v in last_slots:
        assert model.V_StorageLevel[r, p, s, d, t, v].value == pytest.approx(
            model.V_StorageInit[r, t, v].value, rel=1e-3
        ), f'model fails to align last season/day slot with initialization value for {r, t, v}'


@pytest.mark.parametrize(
    'system_test_run',
    argvalues=storage_config_files,
    indirect=True,
    ids=[d['name'] for d in storage_config_files],
)
def test_initialization_in_first_period(system_test_run):
    """
    The level at the end of the first period should be the initialization ± flows
    """

    model: TemoaModel  # helps with typing for some reason...
    data_name, results, model, _ = system_test_run
    assert len(model.V_StorageInit.index_set()) > 0, (
        'This model does not appear to haveany available storage components'
    )
    # test the first periods
    # get references to first timeslot for each prtv combo in things with storage
    first_slots = {
        (r, p, s, d, t, v)
        for r, p, s, d, t, v in model.StorageLevel_rpsdtv
        if s == model.time_season.first() and d == model.time_of_day.first()
    }
    # test that the last day/season combo starts up at the initialization value
    # devnote:  the Level variable is assessed at the end of the timeperiod, so the init ± flows
    #           should total the end value
    for r, p, s, d, t, v in first_slots:
        inflow_indices = {
            (rr, pp, ss, dd, ii, tt, vv, oo)
            for rr, pp, ss, dd, ii, tt, vv, oo in model.FlowInStorage_rpsditvo
            if all((rr == r, pp == p, ss == s, dd == d, tt == t, vv == v))
        }
        outflow_indices = {
            (rr, pp, ss, dd, ii, tt, vv, oo)
            for (rr, pp, ss, dd, ii, tt, vv, oo) in model.FlowVar_rpsditvo
            if all((rr == r, pp == p, ss == s, dd == d, tt == t, vv == v))
        }

        # calculate the inflow and outflow.  Inflow is taxed by efficiency in the model,
        # so we need to do that here as well
        inflow = sum(
            model.V_FlowIn[r, p, s, d, i, t, v, o].value * model.Efficiency[r, i, t, v, o]
            for (r, p, s, d, i, t, v, o) in inflow_indices
        )
        outflow = sum(model.V_FlowOut[idx].value for idx in outflow_indices)
        start = model.V_StorageInit[r, t, v].value
        assert model.V_StorageInit[r, t, v].value + inflow - outflow == pytest.approx(
            model.V_StorageLevel[r, p, s, d, t, v].value, rel=1e-3
        ), f'model fails to align last season/day slot with initialization value for {r, t, v}'


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
    assert len(model.V_StorageInit.index_set()) > 0, (
        'This model does not appear to haveany available storage components'
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
        assert inflow == pytest.approx(outflow, rel=1e-3), (
            f'the inflow and outflow of storage tech {s_tech} do not match'
        )


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
