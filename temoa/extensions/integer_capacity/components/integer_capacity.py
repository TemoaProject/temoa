from __future__ import annotations

from typing import TYPE_CHECKING

import logging
logger = logging.getLogger(__name__)

from pyomo.environ import Constraint, quicksum, value

import temoa.components.geography as geography
import temoa.components.technology as technology

if TYPE_CHECKING:
    from temoa.extensions.integer_capacity.core.model import IntegerCapacityModel
    from temoa.types import ExprLike, Period, Region, Technology, Vintage


def limit_integer_new_capacity_indices(
    model: IntegerCapacityModel,
) -> set[tuple[Region, Technology, Vintage]]:
    indices = {
        (r, t, v)
        for r, t in model.limit_integer_new_capacity.sparse_keys()
        for v in model.vintage_optimize
    }
    return indices


def limit_integer_new_capacity_constraint_rule(
    model: IntegerCapacityModel, r: Region, t: Technology, v: Vintage
) -> ExprLike:
    r"""
    The limit_integer_new_capacity constraint requires the total new capacity
    for a technology (or technology group) in a region to be discrete, equal
    to some integer multiple of the specified capacity.

    .. math::
       :label: limit_integer_new_capacity

       \textbf{NCAP}_{r, t, v} = LINC_{r, t} \cdot \textbf{INCAP}_{r, v, t}

       \forall \{r, t, v\} \in \Theta_{\text{limit\_integer\_new\_capacity}}
    """

    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)
    unit_cap = value(model.limit_integer_new_capacity[r, t])

    new_capacity = quicksum(
        model.v_new_capacity[_r, _t, v]
        for _r in regions
        for _t in techs
        if (_r, _t, v) in model.process_periods
    )
    expr = new_capacity == unit_cap * model.v_integer_new_capacity[r, t, v]
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr


def limit_integer_net_capacity_indices(
    model: IntegerCapacityModel,
) -> set[tuple[Region, Period, Technology]]:
    indices = {
        (r, p, t)
        for r, t in model.limit_integer_net_capacity.sparse_keys()
        for p in model.time_optimize
    }
    return indices


def limit_integer_net_capacity_constraint_rule(
    model: IntegerCapacityModel, r: Region, p: Period, t: Technology
) -> ExprLike:
    r"""
    The limit_integer_net_capacity constraint requires the total available capacity
    for a technology (or technology group) in a region to be discrete, equal
    to some integer multiple of the specified capacity.

    .. math::
       :label: limit_integer_net_capacity

       \textbf{CAPAVL}_{r, p, t} = LIC_{r, t} \cdot \textbf{ICAP}_{r, p, t}

       \forall \{r, p, t\} \in \Theta_{\text{limit\_integer\_net\_capacity}}
    """

    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)
    capacity = value(model.limit_integer_net_capacity[r, t])

    net_capacity = quicksum(
        model.v_capacity_available_by_period_and_tech[_r, p, _t]
        for _r in regions
        for _t in techs
        if (_r, p, _t) in model.v_capacity_available_by_period_and_tech
    )
    expr = net_capacity == capacity * model.v_integer_net_capacity[r, p, t]
    if isinstance(expr, bool):
        return Constraint.Skip
    return expr
