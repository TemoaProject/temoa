"""
module to check all units entries in database for...
    (1) existence :)
    (2) general format (e.g. as a singleton or a ratio expression like Lumens / (Watt))
    (3) membership in units registry

"""

import logging
import re
import sqlite3
from collections import defaultdict

from pint import UndefinedUnitError, Unit

from temoa.model_checking.unit_checking import ureg
from temoa.model_checking.unit_checking.common import (
    UnitsFormat,
)

logger = logging.getLogger(__name__)


def validate_units_format(
    expr: str, unit_format: UnitsFormat
) -> tuple[bool, tuple[str, ...] | None]:
    """
    validate against the format
    return boolean for validity and tuple of elements if valid
    """
    if not expr:
        return False, None
    elements = re.search(unit_format.format, expr)
    if elements:
        return True, tuple(elements.groups())
    return False, None


def validate_units_expression(expr: str) -> tuple[bool, Unit | None]:
    """
    validate an entry against the units registry
    :param expr: the expression to validate
    :return: tuple of the validity and the converted expression
    """
    try:
        units = ureg.parse_units(expr)
        return True, units
    except UndefinedUnitError:
        return False, None


def gather_from_table(conn: sqlite3.Connection, table: str) -> dict[str, list[int]]:
    """gather all unique "units" entries from a table and collect the row indices"""

    res = defaultdict(list)
    with conn:
        cur = conn.cursor()

        try:
            cur.execute(f'SELECT units FROM {table}')
        except sqlite3.OperationalError as exc:
            # e.g. "no such column: units" for a table that hasn't been upgraded
            logger.error(
                'Table %s does not contain a "units" column required for units checking: %s',
                table,
                exc,
            )
            # Let the caller decide how to treat this (e.g., mark Check 2 as failed)
            return {}

        for idx, result in enumerate(cur.fetchall(), start=1):
            # note:  this will put in "blank" entries which is OK, we want to mark blank rows too
            entry = result[0]
            res[entry].append(idx)

    return res
