# temoa/components/utils.py
"""
This module contains generic, reusable utility functions for the Temoa model.

These helpers are used by various components to perform common tasks like
building Pyomo expressions from strings or calculating time-variable efficiencies.
"""

from __future__ import annotations

from enum import Enum
from logging import getLogger
from typing import TYPE_CHECKING

from pyomo.environ import value

if TYPE_CHECKING:
    from pyomo.core import Expression

    from temoa.core.model import TemoaModel
    from temoa.types import (
        Commodity,
        ExprLike,
        Period,
        Region,
        Season,
        Technology,
        TimeOfDay,
        Vintage,
    )


logger = getLogger(__name__)


class Operator(str, Enum):
    EQUAL = 'e'
    LESS_EQUAL = 'le'
    GREATER_EQUAL = 'ge'


def operator_expression(lhs: Expression, operator: Operator, rhs: Expression) -> ExprLike:
    match operator:
        case Operator.EQUAL:
            return lhs == rhs
        case Operator.LESS_EQUAL:
            return lhs <= rhs
        case Operator.GREATER_EQUAL:
            return lhs >= rhs
    raise ValueError(f'Invalid operator: {operator!r}')


def get_variable_efficiency(
    model: TemoaModel,
    r: Region,
    _p: Period,
    s: Season,
    d: TimeOfDay,
    i: Commodity,
    t: Technology,
    v: Vintage,
    o: Commodity,
) -> float:
    """
    Calculates the effective efficiency for a process in a specific time slice.

    This function handles time-varying efficiencies. It checks a pre-computed boolean,
    `M.is_efficiency_variable`, to determine if a variable efficiency is defined for
    the given process.

    - If True, it returns `efficiency * efficiency_variable`.
    - If False, it returns the base `efficiency`.

    This dictionary-lookup approach is used for performance, as it is much faster
    than repeatedly checking the indices of a large Pyomo parameter during model build.
    """
    if model.is_efficiency_variable[r, i, t, v, o]:
        return value(model.efficiency[r, i, t, v, o]) * value(
            model.efficiency_variable[r, s, d, i, t, v, o]
        )
    return value(model.efficiency[r, i, t, v, o])


def get_capacity_factor(
    model: TemoaModel, r: Region, s: Season, d: TimeOfDay, t: Technology, v: Vintage
) -> float:
    if model.is_capacity_factor_process[r, t, v]:
        return value(model.capacity_factor_process[r, s, d, t, v])
    return value(model.capacity_factor_tech[r, s, d, t])
