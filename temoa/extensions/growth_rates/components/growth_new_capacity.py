from __future__ import annotations

from typing import TYPE_CHECKING, cast

from pyomo.environ import Constraint, quicksum, value

import temoa.components.geography as geography
import temoa.components.technology as technology
from temoa.components import capacity
from temoa.components.utils import Operator, operator_expression

if TYPE_CHECKING:
    from temoa.extensions.growth_rates.core.model import GrowthRatesModel
    from temoa.types import ExprLike, Period, Region, Technology, Vintage


def limit_growth_new_capacity_indices(
    model: GrowthRatesModel,
) -> set[tuple[Region, Period, Technology, str]]:
    return {
        (r, p, t, op)
        for r, t, op in model.limit_growth_new_capacity.sparse_keys()
        for p in model.time_optimize
    }


def limit_degrowth_new_capacity_indices(
    model: GrowthRatesModel,
) -> set[tuple[Region, Period, Technology, str]]:
    return {
        (r, p, t, op)
        for r, t, op in model.limit_degrowth_new_capacity.sparse_keys()
        for p in model.time_optimize
    }


def limit_growth_new_capacity_constraint_rule(
    model: GrowthRatesModel, r: Region, p: Period, t: Technology, op: str
) -> ExprLike:
    return limit_growth_new_capacity(model, r, p, t, op, False)


def limit_degrowth_new_capacity_constraint_rule(
    model: GrowthRatesModel, r: Region, p: Period, t: Technology, op: str
) -> ExprLike:
    return limit_growth_new_capacity(model, r, p, t, op, True)


def limit_growth_new_capacity(
    model: GrowthRatesModel,
    r: Region,
    p: Period,
    t: Technology,
    op: str,
    degrowth: bool = False,
) -> ExprLike:
    r"""
    Constrain the change of new capacity deployed between periods.
    Forces the model to ramp up and down the deployment of new technologies
    more smoothly. Has constant (seed, :math:`S_{r,t}`) and proportional
    (rate, :math:`R_{r,t}`) terms. This can be defined for a technology group
    instead of one technology, in which case, new capacity is summed over
    all technologies in the group. In the first period, previous new capacity
    :math:`\mathbf{NCAP}_{r,t,v_prev}` is replaced by previous existing capacity,
    if any can be found.

    .. math::
        :label: Limit (De)Growth New Capacity

            \begin{aligned}\text{Growth:}\\
            &\mathbf{NCAP}_{r,t,v}
            \quad \le, \ge, \text{or} = \quad
            S_{r,t} + (1+R_{r,t}) \cdot \mathbf{NCAP}_{r,t,v_{prev}}
            \text{ where } v=p
            \end{aligned}

            \qquad \forall \{r, p, t\} \in \Theta_{\text{limit\_growth\_capacity}}

            \begin{aligned}\text{Degrowth:}\\
            &\mathbf{NCAP}_{r,t,v_{prev}}
            \quad \le, \ge, \text{or} = \quad S_{r,t} + (1+R_{r,t}) \cdot \mathbf{NCAP}_{r,t,v}
            \text{ where } v=p
            \end{aligned}

            \qquad \forall \{r, p, t\} \in \Theta_{\text{limit\_degrowth\_capacity}}
    """

    growth = model.limit_degrowth_new_capacity if degrowth else model.limit_growth_new_capacity
    rate = 1 + value(growth[r, t, op][0])
    seed = value(growth[r, t, op][1])

    new_cap = quicksum(
        model.v_new_capacity[_r, _t, p]
        for _r, _t in capacity.gather_group_built_processes(model, r, t, cast('Vintage', p))
    )

    new_cap_prev = 0.0

    if p == model.time_optimize.first():
        if model.time_exist:
            regions = geography.gather_group_regions(model, r)
            techs = technology.gather_group_techs(model, t)
            p_prev = model.time_exist.last()
            new_cap_prev = quicksum(
                value(model.existing_capacity[_r, _t, _v])
                for _r, _t, _v in model.existing_capacity.sparse_keys()
                if _r in regions and _t in techs and _v == p_prev
            )
    else:
        p_prev = model.time_optimize.prev(p)
        new_cap_prev = quicksum(
            model.v_new_capacity[_r, _t, p_prev]
            for _r, _t in capacity.gather_group_built_processes(
                model, r, t, cast('Vintage', p_prev)
            )
        )

    if degrowth:
        expr = operator_expression(new_cap_prev, Operator(op), seed + new_cap * rate)
    else:
        expr = operator_expression(new_cap, Operator(op), seed + new_cap_prev * rate)

    if isinstance(expr, bool):
        return Constraint.Skip
    return expr
