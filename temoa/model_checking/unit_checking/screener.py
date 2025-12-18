"""
The main executable to screen for units
"""

import logging
import sqlite3
from pathlib import Path
from typing import Any

from temoa.model_checking.unit_checking.common import (
    RelationType,
    activity_based_tables,
    capacity_based_tables,
    commodity_based_tables,
    cost_based_tables,
    input_tables_with_units,
)
from temoa.model_checking.unit_checking.relations_checker import (
    check_cost_tables,
    check_efficiency_table,
    check_inter_table_relations,
    make_c2a_lut,
    make_commodity_lut,
)
from temoa.model_checking.unit_checking.table_checker import check_table

logger = logging.getLogger(__name__)


def _check_db_version(conn: sqlite3.Connection, report_entries: list[str]) -> tuple[bool, int, int]:
    """
    Check the database version and return success/failure indicator and version info
    :param conn: sqlite3 database connection
    :param report_entries: list to append report messages to
    :return: tuple of (success_indicator, major_version, minor_version)
    """
    msg = '========  Units Check 1 (DB Version):  Started ========'
    report_entries.extend((msg, '\n'))
    logger.info(msg)

    data = conn.execute('SELECT element, value FROM metadata').fetchall()
    meta_data = dict(data)
    major = int(meta_data.get('DB_MAJOR', 0))
    minor = int(meta_data.get('DB_MINOR', 0))

    if major >= 4:
        msg = 'Units Check 1 (DB Version):  Passed'
        report_entries.extend((msg, '\n'))
        logger.info(msg)
        return True, major, minor
    else:
        msg = 'Units Check 1 (DB Version):  Failed.  DB must be v4.0 or greater for units checking'
        report_entries.extend((msg, '\n'))
        logger.warning(msg)
        return False, major, minor


def _check_units_entries(conn: sqlite3.Connection, report_entries: list[str]) -> bool:
    """
    Check units entries in all tables and return success/failure indicator
    :param conn: sqlite3 database connection
    :param report_entries: list to append report messages to
    :return: True if all units entries are valid, False otherwise
    """
    report_entries.append('\n')
    msg = '======== Units Check 2 (Units Entries in Tables):  Started ========'
    logger.info(msg)
    report_entries.extend((msg, '\n'))

    tables_to_check = input_tables_with_units.copy()

    errors_test2 = False
    for table in tables_to_check:
        _, table_errors = check_table(conn, table)
        if table_errors:
            errors_test2 = True
            for error in table_errors:
                logger.info('%s: %s', table, error)
                report_entries.extend((f'{table}:  {error}', '\n'))

    if not errors_test2:
        msg = 'Units Check 2 (Units Entries in Tables):  Passed'
        logger.info(msg)
        report_entries.extend((msg, '\n'))

    report_entries.append('\n')
    return not errors_test2


def _check_efficiency_table(
    conn: sqlite3.Connection, report_entries: list[str], comm_units: dict[str, Any]
) -> tuple[dict[str, Any], bool]:
    """
    Check efficiency table and return tech_io_lut and success/failure indicator
    :param conn: sqlite3 database connection
    :param report_entries: list to append report messages to
    :param comm_units: commodity units lookup table
    :return: tuple of (tech_io_lut, success_indicator)
    """
    report_entries.append('\n')
    msg = '======== Units Check 3 (Tech I/O via Efficiency Table):  Started ========'
    report_entries.extend((msg, '\n'))
    logger.info(msg)

    tech_io_lut, efficiency_errors = check_efficiency_table(conn, comm_units=comm_units)

    if efficiency_errors:
        report_entries.append('Efficiency:  \n')
        for error in efficiency_errors:
            report_entries.append(error)
            report_entries.append('\n')
        logger.warning('Unit conflicts found in Efficiency table. See report.')
        return tech_io_lut, False
    else:
        msg = 'Units Check 3 (Efficiency):  Passed'
        report_entries.extend((msg, '\n'))
        logger.info(msg)
        return tech_io_lut, True


def _check_related_tables(
    conn: sqlite3.Connection,
    report_entries: list[str],
    tech_io_lut: dict[str, Any],
    comm_units: dict[str, Any],
) -> bool:
    """
    Check related tables and return success/failure indicator
    :param conn: sqlite3 database connection
    :param report_entries: list to append report messages to
    :param tech_io_lut: technology I/O units lookup table
    :param comm_units: commodity units lookup table
    :return: True if all related tables are valid, False otherwise
    """
    report_entries.append('\n')
    msg = '======== Units Check 4 (Related Tables):  Started ========'
    report_entries.extend((msg, '\n'))
    logger.info(msg)

    errors_test4 = False

    # Activity-based
    for table in activity_based_tables:
        activity_errors = check_inter_table_relations(
            conn=conn,
            table_name=table,
            tech_lut=tech_io_lut,
            comm_lut=comm_units,
            relation_type=RelationType.ACTIVITY,
        )
        if activity_errors:
            errors_test4 = True
            report_entries.append(f'{table}:  \n')
            for error in activity_errors:
                report_entries.append(error)
                report_entries.append('\n')
                logger.info('%s: %s', table, error)

    # Capacity-based
    for table in capacity_based_tables:
        capacity_errors = check_inter_table_relations(
            conn=conn,
            table_name=table,
            tech_lut=tech_io_lut,
            comm_lut=comm_units,
            relation_type=RelationType.CAPACITY,
        )
        if capacity_errors:
            errors_test4 = True
            report_entries.append(f'{table}:  \n')
            for error in capacity_errors:
                report_entries.append(error)
                report_entries.append('\n')
                logger.info('%s: %s', table, error)

    # Commodity-based
    for table in commodity_based_tables:
        commodity_errors = check_inter_table_relations(
            conn=conn,
            table_name=table,
            tech_lut=tech_io_lut,
            comm_lut=comm_units,
            relation_type=RelationType.COMMODITY,
        )
        if commodity_errors:
            errors_test4 = True
            report_entries.append(f'{table}:  \n')
            for error in commodity_errors:
                report_entries.append(error)
                report_entries.append('\n')
                logger.info('%s: %s', table, error)

    if not errors_test4:
        msg = 'Units Check 4: (Related Tables):  Passed'
        logger.info(msg)
        report_entries.extend((msg, '\n'))

    report_entries.append('\n')
    return not errors_test4


def _check_cost_tables(
    conn: sqlite3.Connection,
    report_entries: list[str],
    tech_io_lut: dict[str, Any],
    c2a_units: dict[str, Any],
    comm_units: dict[str, Any],
) -> bool:
    """
    Check cost tables and return success/failure indicator
    :param conn: sqlite3 database connection
    :param report_entries: list to append report messages to
    :param tech_io_lut: technology I/O units lookup table
    :param c2a_units: capacity to activity units lookup table
    :param comm_units: commodity units lookup table
    :return: True if all cost tables are valid, False otherwise
    """
    msg = '======== Units Check 5 (Cost Tables):  Started ========'
    logger.info(msg)
    report_entries.extend((msg, '\n'))

    errors = check_cost_tables(
        conn,
        cost_tables=cost_based_tables,
        tech_lut=tech_io_lut,
        c2a_lut=c2a_units,
        commodity_lut=comm_units,
    )

    if errors:
        for error in errors:
            logger.info('Cost Tables: %s', error)
            report_entries.extend(('Cost Tables:  ', error, '\n'))

        return False
    else:
        msg = 'Units Check 5 (Cost Tables):  Passed'
        logger.info(msg)
        report_entries.extend((msg, '\n'))

        return True


def screen(*db_paths: Path, report_dir: Path | None = None) -> bool:
    """
    Run series of units screens on the database
    :param db_paths: the abs path(S) to the database(s)
    :param report_dir: directory to write the report to. If None, no report is written
    :return: indicator of whether all checks passed "cleanly" or not
    """
    all_clear = True
    report_entries = []

    for db_path in db_paths:
        if not db_path.is_file():
            raise FileNotFoundError(f'Database file not found: {db_path}')
        initialization_msg = f'\n========  Units Check on DB: {db_path}:  Started ========\n\n'
        report_entries.append(initialization_msg)
        logger.info('Starting Units Check on DB: %s', db_path)

        with sqlite3.connect(db_path) as conn:
            # test 1: DB version
            db_version_ok, _major_version, _minor_version = _check_db_version(conn, report_entries)
            if not db_version_ok:
                # we are non-viable, write the (very short) report and return
                if report_dir:
                    _write_report(report_dir, report_entries)
                return False

            # test 2: Units in tables
            comm_units = make_commodity_lut(conn)
            c2a_units = make_c2a_lut(conn)

            units_entries_ok = _check_units_entries(conn, report_entries)
            if not units_entries_ok:
                all_clear = False

            # test 3: efficiency table
            tech_io_lut, efficiency_ok = _check_efficiency_table(conn, report_entries, comm_units)
            if not efficiency_ok:
                all_clear = False

            # test 4: related tables
            related_tables_ok = _check_related_tables(conn, report_entries, tech_io_lut, comm_units)
            if not related_tables_ok:
                all_clear = False

            # test 5: Cost-Based Tables
            cost_tables_ok = _check_cost_tables(
                conn, report_entries, tech_io_lut, c2a_units, comm_units
            )
            if not cost_tables_ok:
                all_clear = False

    # wrap it up
    if report_dir:
        _write_report(report_dir, report_entries)
    logger.info('Finished Units Check')
    return all_clear


def _write_report(report_dir: Path, report_entries: list[str]) -> None:
    """write out a report if the path is specified"""
    import datetime

    timestamp = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d_%H%M%S')
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file_path = report_dir / f'units_check_{timestamp}.txt'
    with open(report_file_path, 'w', encoding='utf-8') as report_file:
        report_file.writelines(report_entries)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
        screen(db_path, report_dir=Path('temp'))
    else:
        print('Usage: python screener.py <path_to_database.sqlite>')
