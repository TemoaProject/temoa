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
    if 'eos' not in model.enabled_extensions:
        return
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
            if CostType.INVEST in entries.get(key, {}):
                entries[key][CostType.D_INVEST] += discounted_cost
                entries[key][CostType.INVEST] += undiscounted_cost
            else:
                entries[key].update(
                    {CostType.D_INVEST: discounted_cost, CostType.INVEST: undiscounted_cost}
                )

    for r, p, t in model.cost_fixed_eos_period_rpt:
        fixed_cost = value(cost_fixed_eos.period_cost(model, r, p, t))
        if fixed_cost < epsilon:
            continue

        undiscounted_fixed_cost = fixed_cost * value(model.period_length[p])
        discounted_fixed_cost = costs.fixed_or_variable_cost(
            1,
            fixed_cost,
            value(model.period_length[p]),
            global_discount_rate=global_discount_rate,
            p_0=p_0,
            p=p,
        )

        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=p,
                cost=float(value(discounted_fixed_cost)),
                cost_type=CostType.D_FIXED,
            )
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=p,
                cost=float(undiscounted_fixed_cost),
                cost_type=CostType.FIXED,
            )
        else:
            entries[r, p, t, p].update(
                {
                    CostType.D_FIXED: float(value(discounted_fixed_cost)),
                    CostType.FIXED: float(undiscounted_fixed_cost),
                }
            )

    for r, p, t in model.cost_fixed_eos_period_rpt:
        variable_cost = value(cost_variable_eos.period_cost(model, r, p, t))
        if variable_cost < epsilon:
            continue

        undiscounted_variable_cost = variable_cost * value(model.period_length[p])
        discounted_variable_cost = costs.fixed_or_variable_cost(
            1,
            variable_cost,
            value(model.period_length[p]),
            global_discount_rate=global_discount_rate,
            p_0=p_0,
            p=p,
        )

        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=p,
                cost=float(value(discounted_variable_cost)),
                cost_type=CostType.D_VARIABLE,
            )
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=p,
                cost=float(undiscounted_variable_cost),
                cost_type=CostType.VARIABLE,
            )
        else:
            entries[r, p, t, p].update(
                {
                    CostType.D_VARIABLE: float(value(discounted_variable_cost)),
                    CostType.VARIABLE: float(undiscounted_variable_cost),
                }
            )
