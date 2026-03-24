"""
A tabular summation of the results from an SVMGA run
"""
from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from collections.abc import Iterable

    from temoa.core.config import TemoaConfig


import tabulate  # type: ignore[import-untyped]


def summarize(config: TemoaConfig, orig_cost: float, option_cost: float) -> None:
    scenarios = (config.scenario + '-0', config.scenario + '-1')

    svmga_inputs = config.svmga_inputs or {}
    emission_labels = svmga_inputs.get('emission_labels', [])
    capacity_labels = svmga_inputs.get('capacity_labels', [])
    activity_labels = svmga_inputs.get('activity_labels', [])

    conn = sqlite3.connect(config.output_database)
    records: list[list[Any]] = [['Category', 'Label', 'Original', 'Option', 'Delta [%]']]
    total_delta = (option_cost - orig_cost) / orig_cost * 100
    records.append(['Cost', 'Total Cost', orig_cost, option_cost, total_delta])

    for item in sorted(cast('Iterable[Any]', emission_labels)):
        orig = poll_emission(
            conn,
            scenarios[0],
            item,
        )
        option = poll_emission(conn, scenarios[1], item)
        row_delta = float((option - orig) / orig * 100) if orig != 0.0 else None
        records.append(['Emission', item, orig, option, row_delta])
    for item in sorted(cast('Iterable[Any]', activity_labels)):
        orig = poll_activity(conn, scenarios[0], item)
        option = poll_activity(conn, scenarios[1], item)
        row_delta = (option - orig) / orig * 100 if orig != 0.0 else None

        records.append(['Activity', item, orig, option, row_delta])

    for item in sorted(cast('Iterable[Any]', capacity_labels)):
        orig = poll_capacity(conn, scenarios[0], item)
        option = poll_capacity(conn, scenarios[1], item)
        row_delta = (option - orig) / orig * 100 if orig != 0.0 else None

        records.append(['Capacity', item, orig, option, row_delta])

    print()
    print(tabulate.tabulate(records, headers='firstrow', tablefmt='outline', floatfmt='.2f'))
    print(
        '\nFor complete results, see the database records for:\n'
        f'\t{scenarios[0]}: Original\n'
        f'\t{scenarios[1]}: Option (relaxed cost)\n'
    )
    conn.close()


def poll_emission(conn: sqlite3.Connection, scenario: str, label: str) -> float:
    """
    poll the output database of selected iteration for the given emission label total
    """
    row = conn.execute(
        'SELECT sum(emission) FROM main.output_emission WHERE scenario=? AND emis_comm=?',
        (scenario, label),
    ).fetchone()
    return float(row[0] if row and row[0] is not None else 0.0)


def poll_activity(conn: sqlite3.Connection, scenario: str, label: str) -> float:
    """
    poll the Flow Out activity for the given emission label total
    """
    row = conn.execute(
        'SELECT sum(flow) FROM main.output_flow_out WHERE scenario=? AND tech=?',
        (scenario, label),
    ).fetchone()
    return float(row[0] if row and row[0] is not None else 0.0)


def poll_capacity(conn: sqlite3.Connection, scenario: str, label: str) -> float:
    """
    poll the built capacity for the given emission label total
    """
    row = conn.execute(
        'SELECT sum(capacity) FROM main.output_built_capacity WHERE scenario=? AND tech=?',
        (scenario, label),
    ).fetchone()
    return float(row[0] if row and row[0] is not None else 0.0)
