# temoa/components/utils.py
"""
This module contains generic, reusable utility functions for the Temoa model.

These helpers are used by various components to perform common tasks like
building Pyomo expressions from strings or calculating time-variable efficiencies.
"""

from enum import Enum
from logging import getLogger
from typing import TYPE_CHECKING, Any

from pyomo.core import Expression
from pyomo.environ import value

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types import Commodity, Period, Region, Season, Technology, TimeOfDay, Vintage


logger = getLogger(__name__)


class Operator(str, Enum):
    EQUAL = 'e'
    LESS_EQUAL = 'le'
    GREATER_EQUAL = 'ge'


def operator_expression(lhs: Expression, operator: Operator, rhs: Expression) -> Any:
    match operator:
        case Operator.EQUAL:
            return lhs == rhs
        case Operator.LESS_EQUAL:
            return lhs <= rhs
        case Operator.GREATER_EQUAL:
            return lhs >= rhs
    raise ValueError(f'Invalid operator: {operator!r}')


def get_variable_efficiency(
    M: 'TemoaModel',
    r: 'Region',
    p: 'Period',
    s: 'Season',
    d: 'TimeOfDay',
    i: 'Commodity',
    t: 'Technology',
    v: 'Vintage',
    o: 'Commodity',
) -> float:
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
