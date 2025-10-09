# temoa/components/utils.py
"""
This module contains generic, reusable utility functions for the Temoa model.

These helpers are used by various components to perform common tasks like
building Pyomo expressions from strings or calculating time-variable efficiencies.
"""

from logging import getLogger
from typing import TYPE_CHECKING

from pyomo.core import Expression
from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel


logger = getLogger(__name__)


def operator_expression(lhs: Expression | None, operator: str | None, rhs: Expression | None):
    """Returns an expression, applying a configured operator"""
    if any((lhs is None, operator is None, rhs is None)):
        msg = ('Tried to build a constraint using a bad expression or operator: {} {} {}').format(
            lhs, operator, rhs
        )
        logger.error(msg)
        raise ValueError(msg)
    try:
        match operator:
            case 'e':
                expr = lhs == rhs
            case 'le':
                expr = lhs <= rhs
            case 'ge':
                expr = lhs >= rhs
            case _:
                msg = (
                    'Tried to build a constraint using a bad operator. Allowed operators are "e","le", or "ge". Got "{}": {} {} {}'
                ).format(operator, lhs, operator, rhs)
                logger.error(msg)
                raise ValueError(msg)
    except Exception as e:
        print(e)
        msg = ('Tried to build a constraint using a bad expression or operator: {} {} {}').format(
            lhs, operator, rhs
        )
        logger.error(msg)
        raise ValueError(msg) from e

    return expr


def get_variable_efficiency(M: 'TemoaModel', r, p, s, d, i, t, v, o) -> float:
    """
    Calculates the effective efficiency for a process in a specific time slice.

    This function handles time-varying efficiencies. It checks a pre-computed boolean,
    `M.isEfficiencyVariable`, to determine if a variable efficiency is defined for
    the given process.

    - If True, it returns `Efficiency * EfficiencyVariable`.
    - If False, it returns the base `Efficiency`.

    This dictionary-lookup approach is used for performance, as it is much faster
    than repeatedly checking the indices of a large Pyomo parameter during model build.
    """
    if M.isEfficiencyVariable.get((r, p, i, t, v, o), False):
        return value(M.Efficiency[r, i, t, v, o]) * value(
            M.EfficiencyVariable[r, p, s, d, i, t, v, o]
        )
    else:
        return value(M.Efficiency[r, i, t, v, o])
