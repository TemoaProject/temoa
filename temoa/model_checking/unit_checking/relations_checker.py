"""
A systematic check of expected relationships between tables to ensure units are consistent

"""

import dataclasses
import logging
import sqlite3
from collections import defaultdict
from collections.abc import Iterable

from pint.registry import Unit

from temoa.model_checking.unit_checking import ureg
from temoa.model_checking.unit_checking.common import (
    RATIO_ELEMENT,
    SINGLE_ELEMENT,
    CostTableData,
    RelationType,
    activity_based_tables,
    capacity_based_tables,
    commodity_based_tables,
    consolidate_lines,
)
from temoa.model_checking.unit_checking.entry_checker import (
    validate_units_expression,
    validate_units_format,
)

logger = logging.getLogger(__name__)


def make_commodity_lut(conn: sqlite3.Connection) -> dict[str, Unit]:
    """Get a dictionary of the units for each commodity entry"""
    res: dict[str, Unit] = {}
    cursor = conn.cursor()
    query = 'SELECT name, units FROM commodity'
    cursor.execute(query)
    rows = cursor.fetchall()
    for comm, units in rows:
        valid, group = validate_units_format(units, SINGLE_ELEMENT)
        if valid and group is not None:
            valid, unit_obj = validate_units_expression(group[0])
            if valid and unit_obj is not None:
                res[comm] = unit_obj
    return res


def make_c2a_lut(conn: sqlite3.Connection) -> dict[str, Unit]:
    """Get a dictionary of the units for each capacity to activity entry"""
    res: dict[str, Unit] = {}
    cursor = conn.cursor()
    query = 'SELECT tech, units FROM capacity_to_activity'
    cursor.execute(query)
    rows = cursor.fetchall()
    for tech, units in rows:
        valid, group = validate_units_format(units, SINGLE_ELEMENT)
        if valid and group is not None:
            valid, unit_obj = validate_units_expression(group[0])
            if valid and unit_obj is not None:
                res[tech] = unit_obj
    return res


@dataclasses.dataclass(frozen=True)
class IOUnits:
    input_units: Unit
    output_units: Unit


def check_efficiency_table(
    conn: sqlite3.Connection, comm_units: dict[str, Unit]
) -> tuple[dict[str, IOUnits], list[str]]:
    """
    Check the technology units for Efficiency table entries

    Returns a dictionary of technology : IOUnits and a list of error messages

    """

    query = 'SELECT tech, input_comm, output_comm, units FROM efficiency'
    rows = conn.execute(query).fetchall()
    res: dict[str, IOUnits] = {}
    error_msgs = []
    invalid_rows = []
    for idx, (tech, ic, oc, units) in enumerate(rows, start=1):
        input_units: Unit | None = None
        output_units: Unit | None = None
        valid, located_units = validate_units_format(units, RATIO_ELEMENT)
        if valid and located_units is not None and len(located_units) >= 2:
            valid, output_units = validate_units_expression(located_units[0])
        if valid and located_units is not None and len(located_units) >= 2:
            valid, input_units = validate_units_expression(located_units[1])
        if not valid or input_units is None or output_units is None:
            invalid_rows.append(idx)
            # we give up early.  The specifics of why this failed should be evident in earlier tests
            continue

        # check that our tech matches the units of the connected commodities
        expected_input = comm_units.get(ic)
        expected_output = comm_units.get(oc)
        if expected_input is None or expected_output is None:
            invalid_rows.append(idx)
            logger.warning(
                'Missing commodity units for input_comm=%s or output_comm=%s in efficiency row %d',
                ic,
                oc,
                idx,
            )
            continue

        invalid_input_flag = input_units != expected_input
        invalid_output_flag = output_units != expected_output
        if invalid_input_flag or invalid_output_flag:
            logger.warning(
                'Efficiency units conflict with associated commodity for Technology %s near row %d',
                tech,
                idx,
            )
            msg = (
                f'\n  Expected:  {f"{ic} [{expected_input}]":^25} ----> '
                f'{tech:^20} ----> {f"{oc} [{expected_output}]": ^25}'
            )
            if invalid_input_flag:
                msg += f'\n    Invalid input units: {input_units}'
            if invalid_output_flag:
                msg += f'\n    Invalid output units: {output_units}'
            error_msgs.append(msg)

        # check that the output of this technology is consistent in units with
        # other instances of same tech
        if tech in res:
            if res[tech].output_units != output_units:
                logger.warning(
                    'Efficiency units conflict with same-name tech for Technology %s near row %d',
                    tech,
                    idx,
                )
                msg = (
                    f'\n  Found:  {f"{ic} [{input_units}]":^25} ----> '
                    f'{tech:^20} ----> {f"{oc} [{output_units}]": ^25}'
                )
                msg += f'\n    Conflicting output units: {res[tech].output_units} vs {output_units}'
                error_msgs.append(msg)

        else:
            res[tech] = IOUnits(input_units, output_units)

    # we gather all non-processed rows in one statement here due to size of table
    # vs. individual reporting
    if invalid_rows:
        listed_lines = consolidate_lines(invalid_rows)
        line_error_msg = f'Non-processed rows (see earlier tests): {listed_lines}'
        error_msgs.append(line_error_msg)

    return res, error_msgs


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """Check if a column exists in a table."""
    try:
        cursor = conn.execute(f'PRAGMA table_info({table})')
        columns = [row[1] for row in cursor.fetchall()]
        return column in columns
    except sqlite3.Error:
        return False


def check_inter_table_relations(
    conn: sqlite3.Connection,
    table_name: str,
    tech_lut: dict[str, IOUnits],
    comm_lut: dict[str, Unit],
    relation_type: RelationType,
) -> list[str]:
    """Check the tech and units in the given table vs. baseline (expected) values for the tech.

    Fixed: Made SQL queries more robust to handle:
    - Missing columns (e.g., 'region' may not exist in all tables)
    - Missing tables (e.g., some databases may not have all limit tables)
    - Schema variations between v3.1 and v4.0
    """
    # Validate table_name against known safe tables
    valid_tables = activity_based_tables + capacity_based_tables + commodity_based_tables
    if table_name not in valid_tables:
        raise ValueError(f'Invalid table name: {table_name}')

    grouped_errors: defaultdict[str, list[int]] = defaultdict(list)

    # Build query based on relation type, with robustness checks
    match relation_type:
        case RelationType.CAPACITY:
            # Check if required tables and columns exist
            has_c2a = _column_exists(conn, 'capacity_to_activity', 'tech')
            has_region = _column_exists(conn, table_name, 'region')

            # Some tables use 'tech_or_group' instead of 'tech' (e.g., limit tables)
            tech_column = 'tech' if _column_exists(conn, table_name, 'tech') else 'tech_or_group'

            if has_c2a:
                # Use LEFT JOIN to handle missing matches gracefully
                join_condition = f'{table_name}.{tech_column} = ca.tech'
                if has_region:
                    join_condition += f' AND {table_name}.region = ca.region'

                query = (
                    f'SELECT {table_name}.{tech_column}, {table_name}.units, ca.units '
                    f'FROM {table_name} '
                    f'LEFT JOIN capacity_to_activity ca ON {join_condition}'
                )
            else:
                # Fallback: no C2A table available, just check the table itself
                query = f'SELECT {tech_column}, units, NULL FROM {table_name}'
                logger.warning(
                    'capacity_to_activity table not available for %s, skipping C2A verification',
                    table_name,
                )
        case RelationType.ACTIVITY:
            # Activity tables may also have tech_or_group
            tech_column = 'tech' if _column_exists(conn, table_name, 'tech') else 'tech_or_group'
            query = f'SELECT {tech_column}, units, NULL FROM {table_name}'
        case RelationType.COMMODITY:
            query = f'SELECT commodity, units, NULL FROM {table_name}'
        case _:
            raise ValueError(f'Unexpected relation type: {relation_type}')

    try:
        rows = conn.execute(query).fetchall()
    except sqlite3.OperationalError as _:
        # Log the error but don't fail the entire check
        logger.exception('failed to process query: %s when processing table %s', query, table_name)
        msg = (
            f'Failed to process table {table_name} due to SQL error. '
            f'This may indicate missing columns or incompatible schema. '
            f'See log for details.'
        )
        return [msg]

    # process the rows
    for idx, (tech_or_comm, table_units, c2a_units) in enumerate(rows, start=1):
        expected_units = None
        match relation_type:
            case RelationType.CAPACITY:
                io_units = tech_lut.get(tech_or_comm)
                if not io_units:
                    grouped_errors[
                        f'Unprocessed row (missing reference for tech '
                        f'"{tech_or_comm}" --see earlier tests)'
                    ].append(idx)
                    continue
                expected_units = io_units.output_units
            case RelationType.ACTIVITY:
                io_units = tech_lut.get(tech_or_comm)
                if not io_units:
                    grouped_errors[
                        f'Unprocessed row (missing reference for tech '
                        f'"{tech_or_comm}" --see earlier tests)'
                    ].append(idx)
                    continue
                expected_units = io_units.output_units
            case RelationType.COMMODITY:
                expected_units = comm_lut.get(tech_or_comm)
            case _:
                raise ValueError(f'Unexpected relation type: {relation_type}')
        if not expected_units:
            entity = 'commodity' if relation_type is RelationType.COMMODITY else 'tech'
            grouped_errors[
                f'Unprocessed row (missing reference for {entity} "{tech_or_comm}"'
            ].append(idx)

            continue

        # validate the units in the table...
        entry_format_valid, units_data = validate_units_format(table_units, SINGLE_ELEMENT)
        if entry_format_valid and units_data is not None and len(units_data) >= 1:
            _is_valid, valid_table_units = validate_units_expression(units_data[0])
        else:
            valid_table_units = None

        # validate the c2a units, if needed
        if c2a_units:
            c2a_valid, units_data = validate_units_format(c2a_units, SINGLE_ELEMENT)
            if c2a_valid and units_data is not None and len(units_data) >= 1:
                # further ensure the conversion is valid and retain the appropriate units object
                _is_valid, valid_c2a_units = validate_units_expression(units_data[0])
                if not valid_c2a_units:
                    grouped_errors[
                        f'Invalid units or unit format for c2a table: {c2a_units}'
                    ].append(idx)
                    continue
            else:
                grouped_errors[f'Invalid units or unit format for c2a table: {c2a_units}'].append(
                    idx
                )
                continue
        else:
            valid_c2a_units = None

        if not valid_table_units:
            grouped_errors[f'Invalid units or unit format: {table_units}'].append(idx)
            continue

        # if we have valid c2a units, combine them to get the units of activity
        if valid_c2a_units:
            res_units = valid_table_units * (valid_c2a_units * ureg.year)
        else:
            res_units = valid_table_units

        # check that the res_units match the expectation from the tech
        if expected_units != res_units:
            label = f'Units do not match expectation for tech/comm: {tech_or_comm}'
            conversions = []
            if valid_c2a_units:
                conversions.append(f'C2A Factor: {valid_c2a_units}')
                conversions.append(f'Nominal Period: {ureg.year}')
            detail = _ding_label(
                table_entry=table_units,
                focus=f'Converted Measure: {valid_table_units}',
                conversions=conversions,
                result=res_units,
                expectation=expected_units,
            )
            msg = label + detail + '\n'
            grouped_errors[msg].append(idx)

    # gather into list format
    res = []
    for msg, line_nums in grouped_errors.items():
        res.append(f'{msg}  at rows: {consolidate_lines(line_nums)}')

    return res


def _ding_label(
    table_entry: str,
    focus: str,
    result: Unit | None,
    expectation: Unit | None,
    conversions: list[str] | None = None,
) -> str:
    """Make a standardized 'ding' label to use in error reporting"""
    res = ['']
    res.append(f'|        Table Entry: {table_entry}')
    res.append(f'|    Focused Portion: {focus}')
    if conversions:
        for conversion in conversions:
            res.append(f'|         Conversion: {conversion}')
    res.append(f'|             Result: {result}')
    res.append(f'|        Expectation: {expectation}')
    return '\n  '.join(res)


def check_cost_tables(
    conn: sqlite3.Connection,
    cost_tables: Iterable[CostTableData],
    tech_lut: dict[str, IOUnits],
    c2a_lut: dict[str, Unit],
    commodity_lut: dict[str, Unit],
) -> list[str]:
    """
    Check all cost tables for (a) alignment of units to tech output (the denominator)
    and (b) 100% commonality in the cost units (numerator)
    Note:  we'll *assume* the first passing entry in the first table establishes
           the common cost units and check for consistency
    """
    common_cost_unit = None  # Expectation:  MUSD.  Something with a prefix and currency dimension
    error_msgs = []
    for ct in cost_tables:
        table_grouped_errors = defaultdict(list)
        if ct.commodity_reference and ct.capacity_based:
            raise ValueError(
                f'Table that is "capacity based" {ct.table_name} flagged as '
                'having commodity field--expecting tech field.  Check data.'
            )
        query = (
            f'SELECT {ct.commodity_reference if ct.commodity_reference else "tech"}, '
            f'units FROM {ct.table_name}'
        )
        try:
            rows = conn.execute(query).fetchall()
        except sqlite3.OperationalError:
            logger.exception(
                'failed to process query: %s when processing table %s', query, ct.table_name
            )
            msg = f'Failed to process table {ct.table_name}.  See log for failed query.'
            error_msgs.append(msg)
            continue
        for idx, (tech, raw_units_expression) in enumerate(rows, start=1):
            # convert to pint expression
            cost_units, measure_units = None, None
            # screen for empty/missing raw inputs
            if not raw_units_expression:
                label = f'{ct.table_name}:  Unprocessed row (missing units): {raw_units_expression}'
                table_grouped_errors[label].append(idx)
                continue
            valid, elements = validate_units_format(raw_units_expression, RATIO_ELEMENT)
            if valid and elements is not None and len(elements) >= 2:
                cost_valid, cost_units = validate_units_expression(elements[0])
                units_valid, measure_units = validate_units_expression(elements[1])
            else:
                cost_valid, units_valid = False, False
            if not (cost_valid and units_valid):
                label = (
                    f'{ct.table_name}:  Unprocessed row '
                    f'(invalid units--see earlier tests): {raw_units_expression}'
                )
                table_grouped_errors[label].append(idx)
                continue

            # Test 1: Look for cost commonality
            # extract the cost units
            if not cost_units:
                label = (
                    f'{ct.table_name}:  Unprocessed row '
                    f'(missing cost units): {raw_units_expression}'
                )
                table_grouped_errors[label].append(idx)
                continue

            # Get cost unit object
            # cost_units is already a pint Unit object from validate_units_expression(elements[0])
            cost_unit_obj = cost_units

            # Check for currency dimension
            if '[currency]' not in cost_unit_obj.dimensionality:
                label = (
                    f'{ct.table_name}:  Cost units must have currency dimension. '
                    f'Found: {cost_unit_obj}'
                )
                table_grouped_errors[label].append(idx)
                continue

            # Initialize common_cost_unit on first valid row
            if common_cost_unit is None:
                common_cost_unit = cost_unit_obj
                # No need to continue here, as we still need to check measure units
            else:
                # Validate subsequent rows against the established common unit
                if cost_unit_obj != common_cost_unit:
                    # Try to see if they're equivalent but differently expressed
                    try:
                        # Attempt conversion to check if they're compatible
                        (1.0 * cost_unit_obj).to(common_cost_unit)
                    except (ValueError, AttributeError, TypeError) as e:
                        # Not compatible - this is an error
                        label = (
                            f'{ct.table_name}:  Inconsistent cost units: {cost_unit_obj} '
                            f'does not match common cost unit {common_cost_unit}. Error: {e}'
                        )
                        table_grouped_errors[label].append(idx)
                        continue
                    # If compatible but not strictly equal, we still flag it as non-standard
                    label = (
                        f'{ct.table_name}:  Non-standard cost found '
                        f'(expected common cost units of {common_cost_unit}) got '
                        f'{cost_unit_obj}'
                    )
                    table_grouped_errors[label].append(idx)

            # Test 2:  Check the units of measure to ensure alignment with the
            # tech's output units. Find the referenced commodity units from the tech
            # or commodity depending on table structure...
            expected_measure_units: Unit | None = None
            if ct.commodity_reference:
                expected_measure_units = commodity_lut.get(tech)
                if not expected_measure_units:
                    label = f'{ct.table_name}:  Unprocessed row (unknown commodity: {tech}) '
                    table_grouped_errors[label].append(idx)
                    continue
            else:
                tech_io = tech_lut.get(tech)
                if tech_io:
                    # If capacity-based, we need to multiply by C2A and nominal period
                    if ct.capacity_based:
                        c2a_unit = c2a_lut.get(tech)
                        if c2a_unit:
                            expected_measure_units = tech_io.output_units * c2a_unit * ureg.year
                        else:
                            label = (
                                f'{ct.table_name}:  Unprocessed row (missing C2A for tech: {tech}) '
                            )
                            table_grouped_errors[label].append(idx)
                            continue
                    else:
                        expected_measure_units = tech_io.output_units
                else:
                    label = f'{ct.table_name}:  Unprocessed row (unknown tech: {tech}) '
                    table_grouped_errors[label].append(idx)
                    continue

            # Now adjust for period-based if needed
            if ct.period_based and expected_measure_units is not None:
                expected_measure_units = expected_measure_units / ureg.year

            # Handle case where both are None (could indicate data issue)
            if measure_units is None and expected_measure_units is None:
                label = f'{ct.table_name}:  Unable to determine measure units for tech/comm: {tech}'
                table_grouped_errors[label].append(idx)
                continue

            # Check if measure_units matches expected
            matched = (
                measure_units == expected_measure_units
                if (measure_units and expected_measure_units)
                else False
            )

            if not matched:
                label = f'{ct.table_name}:  Non-matching measure unit for tech/comm: {tech}'
                # Simplified detail without c2a_units/oring_measure_units
                detail = (
                    f'\n  Table entry: {raw_units_expression}'
                    f'\n  Expected: {expected_measure_units}'
                    f'\n  Found: {measure_units}'
                )
                label += detail

                table_grouped_errors[label].append(idx)

        for label, listed_lines in table_grouped_errors.items():
            error_msgs.append(f'{label}  at rows: {consolidate_lines(listed_lines)}\n')
    return error_msgs
