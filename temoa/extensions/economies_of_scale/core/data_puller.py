from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

from pyomo.environ import value

from temoa._internal.exchange_tech_cost_ledger import CostType, ExchangeTechCostLedger
from temoa.components import costs
from temoa.extensions.economies_of_scale.components import (
    cost_fixed_eos,
    cost_invest_eos,
    cost_variable_eos,
)

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.extensions.economies_of_scale.core.model import EOSModel
    from temoa.types import Period, Region, Technology, Vintage

logger = logging.getLogger(__name__)


# --- Poll cost results ---
def poll_costs(
    model: TemoaModel,
    exchange_costs: ExchangeTechCostLedger,
    entries: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]],
    p_0: Period,
    epsilon: float,
) -> None:
    """
    Poll the fixed and variable costs for all EOS clusters in the planning horizon
    and add them to the cost entries for the model.
    """
    model = cast('EOSModel', model)

    global_discount_rate = value(model.global_discount_rate)

    for r, p, t in model.cost_invest_eos_period_rpt:
        cost = value(cost_invest_eos.period_cost(model, r, p, t))
        if cost < epsilon:
            continue

        # gather details...
        r0, t0 = model.cost_invest_eos_reference_process[r, p, t]
        loan_life = value(model.loan_lifetime_process[r0, t0, p])
        loan_annualize = value(model.loan_annualize[r0, t0, p])
        life = value(model.lifetime_process[r0, t0, p])

        if model.is_survival_curve_process[r0, t0, p]:
            discounted_cost, undiscounted_cost = costs.poll_loan_costs_survival_curve(
                model=model,
                r=r0,
                t=t0,
                v=p,
                loan_life=loan_life,
                loan_annualize=loan_annualize,
                capacity=1,
                invest_cost=cost,
                p_0=p_0,
                p_e=model.time_future.last(),
                global_discount_rate=global_discount_rate,
            )
        else:
            discounted_cost, undiscounted_cost = costs.poll_loan_costs(
                loan_life=loan_life,
                loan_annualize=loan_annualize,
                capacity=1,
                invest_cost=cost,
                process_life=life,
                p_0=p_0,
                p_e=model.time_future.last(),
                global_discount_rate=global_discount_rate,
                vintage=p,
            )

        # screen for linked region...
        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=p,
                cost=discounted_cost,
                cost_type=CostType.D_INVEST,
            )
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=p,
                cost=undiscounted_cost,
                cost_type=CostType.INVEST,
            )
        else:
            # The period `p` for an investment cost is its vintage `v`.
            key = (cast('Region', r), cast('Period', p), cast('Technology', t), cast('Vintage', p))
            entry = entries[key]
            entry[CostType.D_INVEST] = entry.get(CostType.D_INVEST, 0.0) + discounted_cost
            entry[CostType.INVEST] = entry.get(CostType.INVEST, 0.0) + undiscounted_cost

    for r, p, t in model.cost_fixed_eos_period_rpt:
        fixed_cost = value(cost_fixed_eos.period_cost(model, r, p, t))
        if fixed_cost < epsilon:
            continue

        ud_fixed = float(fixed_cost * value(model.period_length[p]))
        d_fixed = costs.fixed_or_variable_cost(
            1,
            fixed_cost,
            value(model.period_length[p]),
            global_discount_rate=global_discount_rate,
            p_0=p_0,
            p=p,
        )
        d_fixed = float(value(d_fixed))

        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=p,
                cost=d_fixed,
                cost_type=CostType.D_FIXED,
            )
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=p,
                cost=ud_fixed,
                cost_type=CostType.FIXED,
            )
        else:
            key = (cast('Region', r), cast('Period', p), cast('Technology', t), cast('Vintage', p))
            entry = entries[key]
            entry[CostType.D_FIXED] = entry.get(CostType.D_FIXED, 0.0) + d_fixed
            entry[CostType.FIXED] = entry.get(CostType.FIXED, 0.0) + ud_fixed

    for r, p, t in model.cost_variable_eos_period_rpt:
        variable_cost = value(cost_variable_eos.period_cost(model, r, p, t))
        if variable_cost < epsilon:
            continue

        ud_variable = float(variable_cost * value(model.period_length[p]))
        d_variable = costs.fixed_or_variable_cost(
            1,
            variable_cost,
            value(model.period_length[p]),
            global_discount_rate=global_discount_rate,
            p_0=p_0,
            p=p,
        )
        d_variable = float(value(d_variable))

        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=p,
                cost=d_variable,
                cost_type=CostType.D_VARIABLE,
            )
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=p,
                cost=ud_variable,
                cost_type=CostType.VARIABLE,
            )
        else:
            key = (cast('Region', r), cast('Period', p), cast('Technology', t), cast('Vintage', p))
            entry = entries[key]
            entry[CostType.D_VARIABLE] = entry.get(CostType.D_VARIABLE, 0.0) + d_variable
            entry[CostType.VARIABLE] = entry.get(CostType.VARIABLE, 0.0) + ud_variable
