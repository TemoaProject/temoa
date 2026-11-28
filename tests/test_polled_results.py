import dataclasses
import logging
import pickle
import shutil
import sqlite3
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from temoa._internal.run_actions import build_instance, solve_instance
from temoa._internal.table_writer import TableWriter, check_flow_balance, dual_values
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode
from temoa.data_io.hybrid_loader import HybridLoader
from temoa.extensions.modeling_to_generate_alternatives.worker import (
    SOLVE_FAILED,
    WORKER_CONTEXT,
    Worker,
)
from temoa.types.core_types import (
    Commodity,
    Period,
    Region,
    Season,
    Technology,
    TimeOfDay,
    Vintage,
)
from temoa.types.model_types import FI, FlowType

TESTING_OUTPUTS = Path(__file__).parent / 'testing_outputs'
TABLES = (
    'output_built_capacity',
    'output_net_capacity',
    'output_retired_capacity',
    'output_cost',
    'output_emission',
    'output_flow_in',
    'output_flow_out',
    'output_curtailment',
    'output_storage_level',
)


def _gurobi_available() -> bool:
    try:
        import gurobipy

        gurobipy.Model().dispose()
    except Exception:
        return False
    return True


def _rows(con: sqlite3.Connection, table: str, scenario: str) -> list[tuple[object, ...]]:
    columns = [row[1] for row in con.execute(f'PRAGMA table_info({table})') if row[1] != 'scenario']
    query = f'SELECT {", ".join(columns)} FROM {table} WHERE scenario = ?'
    return sorted(con.execute(query, (scenario,)).fetchall(), key=repr)


def _config(tmp_path: Path, db_name: str, solver: str, save_duals: bool = False) -> TemoaConfig:
    db = tmp_path / db_name
    shutil.copy(TESTING_OUTPUTS / db_name, db)
    config = TemoaConfig(
        scenario='polled',
        scenario_mode=TemoaMode.PERFECT_FORESIGHT,
        input_database=db,
        output_database=db,
        output_path=tmp_path,
        solver=solver,
        time_sequencing='seasonal_timeslices',
        save_storage_levels=True,
        save_duals=save_duals,
        silent=True,
    )
    return config


def _solve(config: TemoaConfig, suffixes: list[str] | None = None) -> tuple[Any, Any]:
    con = sqlite3.connect(config.input_database)
    try:
        portal = HybridLoader(db_connection=con, config=config).load_data_portal(myopic_index=None)
    finally:
        con.close()
    return solve_instance(
        build_instance(portal, silent=True),
        config.solver_name,
        silent=True,
        solver_suffixes=suffixes,
    )


@pytest.mark.parametrize('db_name', ['utopia.sqlite', 'materials.sqlite'])
def test_polled_results_match_write_results(tmp_path: Path, db_name: str) -> None:
    """The results polled in a worker are written exactly as the TableWriter writes a model"""
    config = _config(tmp_path, db_name, 'appsi_highs')
    model, _ = _solve(config)

    with TableWriter(config) as writer:
        poller = pickle.loads(pickle.dumps(writer.result_poller()))
        results = pickle.loads(pickle.dumps(poller(model)))
        assert results.duals is None
        writer.write_results(model, save_storage_levels=True, append=True, iteration=1)
        writer.write_polled_results(results, iteration=2)
        for table in TABLES:
            expected = _rows(writer.connection, table, 'polled-1')
            assert _rows(writer.connection, table, 'polled-2') == expected, table
        assert _rows(writer.connection, 'output_flow_out', 'polled-2')
        if db_name == 'utopia.sqlite':
            assert _rows(writer.connection, 'output_storage_level', 'polled-2')


@pytest.mark.skipif(not _gurobi_available(), reason='needs a licensed Gurobi')
def test_polled_duals_match_write_results(tmp_path: Path) -> None:
    """The duals polled in a worker are written exactly as the TableWriter writes them"""
    config = _config(tmp_path, 'utopia.sqlite', 'gurobi', save_duals=True)
    model, solver_results = _solve(config, suffixes=['dual'])

    with TableWriter(config) as writer:
        results = pickle.loads(pickle.dumps(writer.result_poller()(model)))
        writer.write_dual_variables(solver_results, iteration=1)
        writer.write_polled_optional(results, iteration=2)
        expected = _rows(writer.connection, 'output_dual_variable', 'polled-1')
        assert expected
        assert _rows(writer.connection, 'output_dual_variable', 'polled-2') == expected


def _build(config: TemoaConfig) -> Any:
    con = sqlite3.connect(config.input_database)
    try:
        portal = HybridLoader(db_connection=con, config=config).load_data_portal(myopic_index=None)
    finally:
        con.close()
    return build_instance(portal, silent=True)


def _fi(i: str | None, t: str, o: str | None) -> FI:
    return FI(
        Region('R'),
        Period(2020),
        Season('s'),
        TimeOfDay('d'),
        Commodity(i) if i else None,
        Technology(t),
        Vintage(2020),
        Commodity(o) if o else None,
    )


def test_flow_balance(caplog: pytest.LogCaptureFixture) -> None:
    flows = {
        _fi('a', 'balanced', 'b'): {FlowType.IN: 10.0, FlowType.OUT: 9.0, FlowType.LOST: 1.0},
        _fi('a', 'storage', 'b'): {FlowType.IN: 10.0},
        _fi(None, 'no_input', 'b'): {FlowType.OUT: 10.0},
    }
    assert check_flow_balance(flows, {'storage'})
    flows[_fi('a', 'imbalanced', 'b')] = {FlowType.IN: 10.0, FlowType.OUT: 5.0}
    flows[_fi('a', 'zero_input', 'b')] = {FlowType.OUT: 1.0}
    with caplog.at_level(logging.WARNING):
        assert not check_flow_balance(flows, {'storage'})
    assert 'Flow imbalance > 2%' in caplog.text
    assert 'Flow imbalance (zero input)' in caplog.text


def test_dual_values() -> None:
    results: Any = {'Solution': SimpleNamespace(Constraint={'c1': {'Dual': 1.5}})}
    assert dual_values(results) == {'c1': 1.5}


def test_write_polled_capacity_and_optional(tmp_path: Path) -> None:
    config = _config(tmp_path, 'utopia.sqlite', 'appsi_highs')
    model, _ = _solve(config)

    with TableWriter(config) as writer:
        results = writer.result_poller(check_balance=True)(model)
        results = dataclasses.replace(results, duals={'some_constraint': 2.0})
        writer.write_polled_capacity(results, iteration=1)
        writer.write_polled_optional(results, iteration=1)
        assert _rows(writer.connection, 'output_net_capacity', 'polled-1')
        assert _rows(writer.connection, 'output_storage_level', 'polled-1')
        assert _rows(writer.connection, 'output_dual_variable', 'polled-1') == [
            ('some_constraint', 2.0)
        ]


def _failing_extractor(model: Any) -> Any:
    raise RuntimeError('extraction failed')


def _run_worker(config: TemoaConfig, extractor: Any) -> list[Any]:
    model_queue: Any = WORKER_CONTEXT.Queue()
    results_queue: Any = WORKER_CONTEXT.Queue()
    log_queue: Any = WORKER_CONTEXT.Queue()
    worker = Worker(
        model_queue=model_queue,
        results_queue=results_queue,
        log_root_name='test_polled_results',
        log_queue=log_queue,
        result_extractor=extractor,
    )
    if worker._extractor_queue is not None:
        worker._extractor_queue.put(extractor)
    model_queue.put(_build(config))
    model_queue.put('ZEBRA')
    worker.run()
    received: list[Any] = []
    while True:
        item = results_queue.get(timeout=60)
        if isinstance(item, str) and item == 'COYOTE':
            return received
        received.append(item)


def test_worker_extraction_in_process(tmp_path: Path) -> None:
    config = _config(tmp_path, 'utopia.sqlite', 'appsi_highs')
    with TableWriter(config) as writer:
        poller = writer.result_poller()

    extracted = _run_worker(config, poller)
    assert len(extracted) == 1
    assert extracted[0].flows

    models = _run_worker(config, None)
    assert len(models) == 1
    assert hasattr(models[0], 'total_cost')

    assert _run_worker(config, _failing_extractor) == [SOLVE_FAILED]
