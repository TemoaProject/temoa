"""
A tabular summation of the results from an SVMGA run
"""

import sqlite3
from sqlite3 import Connection

import tabulate

from temoa.core.config import TemoaConfig


def summarize(config: TemoaConfig, orig_cost: float, option_cost: float) -> None:
    scenarios = (config.scenario + '-0', config.scenario + '-1')

    emission_labels = config.svmga_inputs.get('emission_labels', [])
    capacity_labels = config.svmga_inputs.get('capacity_labels', [])
    activity_labels = config.svmga_inputs.get('activity_labels', [])

    conn = sqlite3.connect(config.output_database)
    records = [['Category', 'Label', 'Original', 'Option', 'Delta [%]']]
    delta = (option_cost - orig_cost) / orig_cost * 100
    records.append(['Cost', 'Total Cost', orig_cost, option_cost, delta])

    for item in sorted(emission_labels):
        orig = poll_emission(
            conn,
            scenarios[0],
            item,
        )
        option = poll_emission(conn, scenarios[1], item)
        delta = float((option - orig) / orig * 100) if all((orig, option)) else None
        records.append(['Emission', item, orig, option, delta])
    for item in sorted(activity_labels):
        orig = poll_activity(conn, scenarios[0], item)
        option = poll_activity(conn, scenarios[1], item)
        delta = (option - orig) / orig * 100 if all((orig, option)) else None

        records.append(['Activity', item, orig, option, delta])

    for item in sorted(capacity_labels):
        orig = poll_capacity(conn, scenarios[0], item)
        option = poll_capacity(conn, scenarios[1], item)
        delta = (option - orig) / orig * 100 if all((orig, option)) else None

        records.append(['Capacity', item, orig, option, delta])

    print()
    print(tabulate.tabulate(records, headers='firstrow', tablefmt='outline', floatfmt='.2f'))
    print(
        '\nFor complete results, see the database records for:\n'
        f'\t{scenarios[0]}: Original\n'
        f'\t{scenarios[1]}: Option (relaxed cost)\n'
    )
    conn.close()


def poll_emission(conn: Connection, scenario: str, label: str) -> float:
    """
    poll the output database of selected iteration for the given emission label total
    """
    raw = conn.execute(
        'SELECT sum(emission) FROM main.output_emissionn WHERE scenario=? AND emis_comm=?',
        (scenario, label),
    ).fetchone()[0]
    return raw


def poll_activity(conn: Connection, scenario: str, label: str) -> float:
    """
    poll the Flow Out activity for the given emission label total
    """
    raw = conn.execute(
        'SELECT sum(flow) FROM main.output_flow_out WHERE scenario=? AND tech=?',
        (scenario, label),
    ).fetchone()[0]
    return raw


def poll_capacity(conn: Connection, scenario: str, label: str) -> float:
    """
    poll the built capacity for the given emission label total
    """
    raw = conn.execute(
        'SELECT sum(capacity) FROM main.output_built_capacity WHERE scenario=? AND tech=?',
        (scenario, label),
    ).fetchone()[0]
    return raw
