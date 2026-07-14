from __future__ import annotations

from typing import TYPE_CHECKING

from pyomo.environ import Constraint, quicksum, value

import temoa.components.geography as geography
import temoa.components.technology as technology
from temoa.components import capacity
from temoa.components.utils import Operator, get_adjusted_existing_capacity, operator_expression

if TYPE_CHECKING:
    from temoa.extensions.growth_rates.core.model import GrowthRatesModel
    from temoa.types import ExprLike, Period, Region, Technology


def limit_growth_capacity_indices(
    model: GrowthRatesModel,
) -> set[tuple[Region, Period, Technology, str]]:
    return {
        (r, p, t, op)
        for r, t, op in model.limit_growth_capacity.sparse_keys()
        for p in model.time_optimize
    }


def limit_degrowth_capacity_indices(
    model: GrowthRatesModel,
) -> set[tuple[Region, Period, Technology, str]]:
    return {
        (r, p, t, op)
        for r, t, op in model.limit_degrowth_capacity.sparse_keys()
        for p in model.time_optimize
    }


def limit_growth_capacity_constraint_rule(
    model: GrowthRatesModel, r: Region, p: Period, t: Technology, op: str
) -> ExprLike:
    return limit_growth_capacity(model, r, p, t, op, False)


def limit_degrowth_capacity_constraint_rule(
    model: GrowthRatesModel, r: Region, p: Period, t: Technology, op: str
) -> ExprLike:
    return limit_growth_capacity(model, r, p, t, op, True)


def limit_growth_capacity(
    model: GrowthRatesModel,
    r: Region,
    p: Period,
    t: Technology,
    op: str,
    degrowth: bool = False,
) -> ExprLike:
    r"""
    Constrain the change of capacity available between periods.
    Forces the model to ramp up and down the availability of new technologies
    more smoothly. Has constant (seed, :math:`S_{r,t}`) and proportional
    (rate, :math:`R_{r,t}`) terms. This can be defined for a technology group
    instead of one technology, in which case, capacity available is summed over
    all technologies in the group. In the first period, previous available
    capacity :math:`\mathbf{CAPAVL}_{r,p,t}` is replaced by previous existing
    capacity, if any can be found.

    .. math::
        :label: Limit (De)Growth Capacity

            \begin{aligned}\text{Growth:}\\
            &\mathbf{CAPAVL}_{r,p,t}
            \quad \le, \ge, \text{or} = \quad
            S_{r,t} + (1+R_{r,t}) \cdot \mathbf{CAPAVL}_{r,p_{prev},t}
            \end{aligned}

            \qquad \forall \{r, p, t\} \in \Theta_{\text{limit\_growth\_capacity}}


            \begin{aligned}\text{Degrowth:}\\
            &\mathbf{CAPAVL}_{r,p_{prev},t}
            \quad \le, \ge, \text{or} = \quad S_{r,t} + (1+R_{r,t}) \cdot \mathbf{CAPAVL}_{r,p,t}
            \end{aligned}

            \qquad \forall \{r, p, t\} \in \Theta_{\text{limit\_degrowth\_capacity}}
    """

    regions = geography.gather_group_regions(model, r)
    techs = technology.gather_group_techs(model, t)

    growth = model.limit_degrowth_capacity if degrowth else model.limit_growth_capacity
    rate = 1 + value(growth[r, t, op][0])
    seed = value(growth[r, t, op][1])

    cap = quicksum(
        model.v_capacity_available_by_period_and_tech[_r, p, _t]
        for _r, _t in capacity.gather_group_active_processes(model, r, p, t)
    )

    capacity_prev = 0.0

    if p == model.time_optimize.first():
        if model.time_exist:
            p_prev = model.time_exist.last()
            capacity_prev = quicksum(
                get_adjusted_existing_capacity(model, _r, _t, _v)
                * value(model.process_life_frac[_r, p_prev, _t, _v])
                for _r, _t, _v in model.existing_capacity.sparse_keys()
                if _r in regions
                and _t in techs
                and _v + value(model.lifetime_process[_r, _t, _v]) > p_prev
            )
    else:
        p_prev = model.time_optimize.prev(p)
        capacity_prev = quicksum(
            model.v_capacity_available_by_period_and_tech[_r, p_prev, _t]
            for _r, _t in capacity.gather_group_active_processes(model, r, p_prev, t)
        )

    if degrowth:
        expr = operator_expression(capacity_prev, Operator(op), seed + cap * rate)
    else:
        expr = operator_expression(cap, Operator(op), seed + capacity_prev * rate)

    if isinstance(expr, bool):
        return Constraint.Skip
    return expr
