"""
functions to check tables within a database for units compliance
"""

import logging
import re
import sqlite3
from typing import cast

from pint.registry import Unit

from temoa.model_checking.unit_checking import ureg
from temoa.model_checking.unit_checking.common import (
    ACCEPTABLE_CHARACTERS,
    RATIO_ELEMENT,
    SINGLE_ELEMENT,
    capacity_based_tables,
    consolidate_lines,
    ratio_capture_tables,
)
from temoa.model_checking.unit_checking.entry_checker import (
    gather_from_table,
    validate_units_expression,
    validate_units_format,
)

logger = logging.getLogger(__name__)


def check_table(conn: sqlite3.Connection, table_name: str) -> tuple[dict[str, Unit], list[str]]:
    """
    Check all entries in a table for format and registry compliance
    This "first pass" gathers common entries for efficiency"""
    errors = []
    res = {}
    format_type = RATIO_ELEMENT if table_name in ratio_capture_tables else SINGLE_ELEMENT

    # this function gathers all unique entries by row number for efficiency in larger tables
    entries = gather_from_table(conn, table_name)
    for expr, line_nums in entries.items():
        # mark the blanks
        if not expr:
            listed_lines = consolidate_lines(line_nums)
            errors.append(f'Blank units entry found at rows: {listed_lines}')
            continue

        # check characters
        valid_chars = re.search(ACCEPTABLE_CHARACTERS, expr)
        if not valid_chars:
            listed_lines = consolidate_lines(line_nums)
            errors.append(
                f'Invalid character(s): {expr if expr else "<no recognized entry>"} '
                f'[only letters, digits, underscore and "*, /, ^, ()" operators allowed] '
                f'at rows: {listed_lines}  '
            )
            continue

        # Check format
        valid_format, elements = validate_units_format(expr, format_type)
        if not valid_format:
            listed_lines = consolidate_lines(line_nums)
            if format_type == RATIO_ELEMENT:
                msg = (
                    f'Format violation at rows.  {listed_lines}:  {expr}.  '
                    f'Check illegal chars/operators and that denominator is isolated '
                    f'in parentheses.'
                )
            else:
                msg = (
                    f'Format violation at rows.  {listed_lines}:  {expr}.  '
                    f'Check for illegal characters or operators.'
                )
            errors.append(msg)
            continue
        elif elements is None:
            listed_lines = consolidate_lines(line_nums)
            errors.append(f'No units found for expression: {expr} at rows: {listed_lines}')
            continue

        # Check registry compliance
        converted_units = []
        for element in elements:
            if element:
                success, unit_obj = validate_units_expression(element)
                if not success or unit_obj is None:
                    listed_lines = consolidate_lines(line_nums)
                    errors.append(
                        f'Registry violation (UNK units): {element} at rows: {listed_lines}'
                    )
                else:
                    # Capacity table validation: check for inappropriate time dimensions
                    if table_name in capacity_based_tables and format_type == SINGLE_ELEMENT:
                        unit_dimensionality = unit_obj.dimensionality
                        time_exponent = unit_dimensionality.get('[time]', 0)

                        if float(cast('float', time_exponent)) > -3:  # cast needed to satisfy mypy
                            listed_lines = consolidate_lines(line_nums)
                            errors.append(
                                f'Energy units (not capacity) in capacity table: {element} '
                                f'at rows: {listed_lines}. '
                                f'Expected power units (e.g., GW, MW, kW), not energy units. '
                                f'Remove time component: use {unit_obj / ureg.year} instead?'
                            )
                    converted_units.append(unit_obj)

        # assemble a reference of item: units-relationship if we have a valid entry
        if len(converted_units) == format_type.groups:
            if format_type == SINGLE_ELEMENT:
                ref = {expr: converted_units[0]}
                res.update(ref)
            elif format_type == RATIO_ELEMENT:
                ref = {expr: converted_units[0] / converted_units[1]}
                res.update(ref)
            else:
                raise ValueError(f'Unknown units format: {format_type}')
    return res, errors
