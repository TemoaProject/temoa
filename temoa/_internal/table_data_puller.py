"""
A companion module to the table writer to hold some data-pulling functions and small utilities and
separate them from the writing process for organization and to isolate the DB access in the writer
such that these functions can be called on a model instance without any DB interactions.  (Intended
to support use by Workers who shouldn't interact with DB).  Dev Note:  In future, if transition
away from sqlite, this could all be refactored to perform tasks within workers, but concurrent
access to sqlite is a no-go
"""

from __future__ import annotations

import functools
import logging
from collections import defaultdict
from typing import TYPE_CHECKING, cast

from pyomo.common.numeric_types import value
from pyomo.core import Objective

from temoa._internal.exchange_tech_cost_ledger import CostType, ExchangeTechCostLedger
from temoa.components import costs
from temoa.components.utils import get_variable_efficiency
from temoa.types.model_types import EI, FI, SLI, CapData, FlowType

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.types.core_types import Commodity, Period, Region, Technology, Vintage

logger = logging.getLogger(__name__)


def _marks(num: int) -> str:
    """convenience to make a sequence of question marks for query"""
    qs = ','.join('?' for _ in range(num))
    marks = '(' + qs + ')'
    return marks


def ritvo(fi: FI) -> tuple[Region, Commodity, Technology, Vintage, Commodity]:
    """convert FI to ritvo index"""
    return fi.r, fi.i, fi.t, fi.v, fi.o


def rpetv(fi: FI, e: Commodity) -> tuple[Region, Period, Commodity, Technology, Vintage]:
    """convert FI and emission to rpetv index"""
    return fi.r, fi.p, e, fi.t, fi.v


def poll_capacity_results(model: TemoaModel, epsilon: float = 1e-5) -> CapData:
    """
    Poll a solved model for capacity results.
    :param M: Solved Model
    :param epsilon: epsilon (default 1e-5)
    :return: a CapData object
    """
    # Built Capacity
    built = []
    for r, t, v in model.v_new_capacity.keys():
        if v in model.time_optimize:
            val = value(model.v_new_capacity[r, t, v])
            if abs(val) < epsilon:
                continue
            new_cap = (r, t, v, val)
            built.append(new_cap)

    # NetCapacity
    net = []
    for r, p, t, v in model.v_capacity.keys():
        val = value(model.v_capacity[r, p, t, v])
        if abs(val) < epsilon:
            continue
        new_net_cap = (r, p, t, v, val)
        net.append(new_net_cap)

    # Retired Capacity
    ret = []
    for r, t, v in model.retirement_periods:
        lifetime = value(model.lifetime_process[r, t, v])
        for p in model.retirement_periods[r, t, v]:
            # We want to output period retirement, not annual retirement, so multiply by
            # PeriodLength
            eol = value(model.period_length[p]) * value(model.v_annual_retirement[r, p, t, v])
            early = 0
            if t in model.tech_retirement and v < p <= v + lifetime - value(model.period_length[p]):
                early = value(model.v_retired_capacity[r, p, t, v])
                eol -= early
            early = 0 if abs(early) < epsilon else early
            eol = 0 if abs(eol) < epsilon else eol
            if early == 0 and eol == 0:
                continue
            new_retired_cap = (r, p, t, v, eol, early)
            ret.append(new_retired_cap)

    return CapData(built=built, net=net, retired=ret)


def poll_flow_results(model: TemoaModel, epsilon: float = 1e-5) -> dict[FI, dict[FlowType, float]]:
    """
    Poll a solved model for flow results.
    :param M: A solved Model
    :param epsilon: epsilon (default 1e-5)
    :return: nested dictionary of FlowIndex, FlowType : value
    """
    dd: functools.partial[dict[FlowType, float]] = functools.partial(defaultdict, float)
    res: dict[FI, dict[FlowType, float]] = defaultdict(dd)

    # ---- NON-annual ----

    # Storage, which has a unique v_flow_in (non-storage techs do not have this variable)
    for key in model.v_flow_in.keys():
        fi = FI(*key)
        flow = value(model.v_flow_in[fi])
        if abs(flow) < epsilon:
            continue
        res[fi][FlowType.IN] = flow
        res[fi][FlowType.LOST] = (1 - get_variable_efficiency(model, *key)) * flow

    # regular flows
    for key in model.v_flow_out.keys():
        fi = FI(*key)
        flow = value(model.v_flow_out[fi])
        if abs(flow) < epsilon:
            continue
        res[fi][FlowType.OUT] = flow

        if fi.t not in model.tech_storage:  # we can get the flow in by out/eff...
            flow = value(model.v_flow_out[fi]) / get_variable_efficiency(model, *key)
            res[fi][FlowType.IN] = flow
            res[fi][FlowType.LOST] = (1 - get_variable_efficiency(model, *key)) * flow

    # curtailment flows
    for key in model.v_curtailment.keys():
        fi = FI(*key)
        val = value(model.v_curtailment[fi])
        if abs(val) < epsilon:
            continue
        res[fi][FlowType.CURTAIL] = val

    # flex techs.  This will subtract the flex from their output flow IOT make OUT the "net"
    for key in model.v_flex.keys():
        fi = FI(*key)
        flow = value(model.v_flex[fi])
        if abs(flow) < epsilon:
            continue
        res[fi][FlowType.FLEX] = flow
        res[fi][FlowType.OUT] -= flow

    # ---- annual ----

    # basic annual flows
    for r, p, i, t, v, o in model.v_flow_out_annual.keys():
        # Make sure this isn't just a non-annual demand tech
        if t not in model.tech_annual:
            continue
        for s in model.time_season[p]:
            for d in model.time_of_day:
                if o in model.commodity_demand:
                    distribution = value(model.demand_specific_distribution[r, p, s, d, o])
                else:
                    distribution = value(model.segment_fraction[p, s, d])
                fi = FI(r, p, s, d, i, t, v, o)
                flow = value(model.v_flow_out_annual[r, p, i, t, v, o]) * distribution
                if abs(flow) < epsilon:
                    continue
                res[fi][FlowType.OUT] = flow
                res[fi][FlowType.IN] = flow / value(model.efficiency[ritvo(fi)])
                res[fi][FlowType.LOST] = (1 - value(model.efficiency[ritvo(fi)])) * res[fi][
                    FlowType.IN
                ]

    # flex annual
    for r, p, i, t, v, o in model.v_flex_annual.keys():
        for s in model.time_season[p]:
            for d in model.time_of_day:
                fi = FI(r, p, s, d, i, t, v, o)
                flow = value(model.v_flex_annual[r, p, i, t, v, o]) * value(
                    model.segment_fraction[p, s, d]
                )
                if abs(flow) < epsilon:
                    continue
                res[fi][FlowType.FLEX] = flow
                res[fi][FlowType.OUT] -= flow

    # construction flows
    for r, i, t, v in model.construction_input.sparse_iterkeys():
        annual = (
            value(model.construction_input[r, i, t, v])
            * value(model.v_new_capacity[r, t, v])
            / value(model.period_length[v])
        )
        for s in model.time_season[v]:
            for d in model.time_of_day:
                fi = FI(r, v, s, d, i, t, v, cast('Commodity', 'construction_input'))
                flow = annual * value(model.segment_fraction[v, s, d])
                if abs(flow) < epsilon:
                    continue
                res[fi][FlowType.IN] = flow

    # end of life flows
    for r, t, v, o in model.end_of_life_output.sparse_iterkeys():
        if (r, t, v) not in model.retirement_periods:
            continue
        for p in model.retirement_periods[r, t, v]:
            annual = value(model.end_of_life_output[r, t, v, o]) * value(
                model.v_annual_retirement[r, p, t, v]
            )
            for s in model.time_season[p]:
                for d in model.time_of_day:
                    fi = FI(r, p, s, d, cast('Commodity', 'end_of_life_output'), t, v, o)
                    flow = annual * value(model.segment_fraction[p, s, d])
                    if abs(flow) < epsilon:
                        continue
                    res[fi][FlowType.OUT] = flow

    return res


def poll_storage_level_results(model: TemoaModel, epsilon: float = 1e-5) -> dict[SLI, float]:
    """
    Poll a solved model for flow results.
    :param M: A solved Model
    :param epsilon: epsilon (default 1e-5)
    :return: dictionary of storage level index, storage level
    """
    res: dict[SLI, float] = defaultdict(float)

    # Storage level, the state variable for all but last time slice of each season
    for r, p, s, d, t, v in model.storage_level_rpsdtv:
        if t in model.tech_seasonal_storage:
            continue
        state = value(model.v_storage_level[r, p, s, d, t, v]) / (
            value(model.segment_fraction_per_season[p, s]) * value(model.days_per_period)
        )
        sli = SLI(r, p, s, d, t, v)
        if abs(state) < epsilon:
            state = 0  # still want to know but decimals are ugly
        res[sli] = state

    for r, p, s_seq, t, v in model.seasonal_storage_level_rpstv:
        s = model.sequential_to_season[p, s_seq]
        # Ratio of days in virtual storage season to days in actual season
        # Flows and StorageLevel are normalised to the number of days in the ACTUAL season, so must
        # be adjusted to the number of days in the virtual storage season
        days_adjust = value(model.time_season_sequential[p, s_seq, s]) / (
            value(model.segment_fraction_per_season[p, s]) * value(model.days_per_period)
        )
        for d in model.time_of_day:
            state = (
                value(model.v_seasonal_storage_level[r, p, s_seq, t, v])
                + value(model.v_storage_level[r, p, s, d, t, v]) * days_adjust
            )
            sli = SLI(r, p, s_seq, d, t, v)
            if abs(state) < epsilon:
                state = 0  # still want to know but decimals are ugly
            res[sli] = state

    return res


def poll_objective(model: TemoaModel) -> list[tuple[str, float]]:
    """gather objective name, value tuples for all active objectives"""
    objs: list[Objective] = list(model.component_data_objects(Objective))
    active_objs = [obj for obj in objs if obj.active]
    if len(active_objs) > 1:
        logger.warning('Multiple active objectives found.  All will be logged in db')
    res = []
    for obj in active_objs:
        obj_name, obj_value = obj.getname(fully_qualified=True), float(value(obj))
        res.append((obj_name, obj_value))
    return res


def poll_cost_results(
    model: TemoaModel, p_0: Period | None, epsilon: float = 1e-5
) -> tuple[
    dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]],
    dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]],
]:
    """
    Poll a solved model for all cost results
    :param M: Solved Model
    :param p_0: a base year for discounting of loans, typically only used in MYOPIC.  If none,
                first optimization year used
    :param epsilon: epsilon (default 1e-5)
    :return: tuple of cost_dict, exchange_cost_dict (for exchange techs)
    """
    p_0_true: Period
    if p_0 is None:
        p_0_true = min(model.time_optimize)
    else:
        p_0_true = p_0

    p_e = model.time_future.last()

    # conveniences...
    global_discount_rate = value(model.global_discount_rate)
    # MPL = M.ModelProcessLife
    loan_lifetime_process = model.loan_lifetime_process

    exchange_costs = ExchangeTechCostLedger(model)
    entries: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]] = defaultdict(
        dict
    )
    for r, t, v in model.cost_invest.sparse_iterkeys():  # Returns only non-zero values
        # gather details...
        cap = value(model.v_new_capacity[r, t, v])
        if abs(cap) < epsilon:
            continue
        loan_life = value(loan_lifetime_process[r, t, v])
        loan_rate = value(model.loan_rate[r, t, v])

        if model.is_survival_curve_process[r, t, v]:
            model_loan_cost, undiscounted_cost = loan_costs_survival_curve(
                model=model,
                r=r,
                t=t,
                v=v,
                loan_rate=loan_rate,
                loan_life=loan_life,
                capacity=cap,
                invest_cost=value(model.cost_invest[r, t, v]),
                p_0=p_0_true,
                p_e=p_e,
                global_discount_rate=global_discount_rate,
                vintage=v,
            )
        else:
            model_loan_cost, undiscounted_cost = loan_costs(
                loan_rate=loan_rate,
                loan_life=loan_life,
                capacity=cap,
                invest_cost=value(model.cost_invest[r, t, v]),
                process_life=value(model.lifetime_process[r, t, v]),
                p_0=p_0_true,
                p_e=p_e,
                global_discount_rate=global_discount_rate,
                vintage=v,
            )
        # screen for linked region...
        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=v,
                tech=t,
                vintage=v,
                cost=model_loan_cost,
                cost_type=CostType.D_INVEST,
            )
            exchange_costs.add_cost_record(
                r,
                period=v,
                tech=t,
                vintage=v,
                cost=undiscounted_cost,
                cost_type=CostType.INVEST,
            )
        else:
            # The period `p` for an investment cost is its vintage `v`.
            key = (cast('Region', r), cast('Period', v), cast('Technology', t), cast('Vintage', v))
            entries[key].update(
                {CostType.D_INVEST: model_loan_cost, CostType.INVEST: undiscounted_cost}
            )

    for r, p, t, v in model.cost_fixed.sparse_iterkeys():
        cap = value(model.v_capacity[r, p, t, v])
        if abs(cap) < epsilon:
            continue

        fixed_cost = value(model.cost_fixed[r, p, t, v])
        undiscounted_fixed_cost = cap * fixed_cost * value(model.period_length[p])

        model_fixed_cost = costs.fixed_or_variable_cost(
            cap,
            value(fixed_cost),
            value(model.period_length[p]),
            global_discount_rate=global_discount_rate,
            p_0=float(p_0_true),
            p=p,
        )
        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=v,
                cost=float(value(model_fixed_cost)),
                cost_type=CostType.D_FIXED,
            )
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=v,
                cost=float(value(undiscounted_fixed_cost)),
                cost_type=CostType.FIXED,
            )
        else:
            entries[r, p, t, v].update(
                {
                    CostType.D_FIXED: float(value(model_fixed_cost)),
                    CostType.FIXED: float(value(undiscounted_fixed_cost)),
                }
            )

    for r, p, t, v in model.cost_variable.sparse_iterkeys():
        if t not in model.tech_annual:
            activity = sum(
                value(model.v_flow_out[r, p, S_s, S_d, S_i, t, v, S_o])
                for S_i in model.process_inputs[r, p, t, v]
                for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
                for S_s in model.time_season[p]
                for S_d in model.time_of_day
            )
        else:
            activity = sum(
                value(model.v_flow_out_annual[r, p, S_i, t, v, S_o])
                for S_i in model.process_inputs[r, p, t, v]
                for S_o in model.process_outputs_by_input[r, p, t, v, S_i]
            )
        if abs(activity) < epsilon:
            continue

        var_cost = value(model.cost_variable[r, p, t, v])
        undiscounted_var_cost = activity * var_cost * value(model.period_length[p])

        model_var_cost = costs.fixed_or_variable_cost(
            activity,
            var_cost,
            value(model.period_length[p]),
            global_discount_rate=global_discount_rate,
            p_0=float(p_0_true),
            p=p,
        )
        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=v,
                cost=float(value(model_var_cost)),
                cost_type=CostType.D_VARIABLE,
            )
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=v,
                cost=float(value(undiscounted_var_cost)),
                cost_type=CostType.VARIABLE,
            )
        else:
            entries[r, p, t, v].update(
                {
                    CostType.D_VARIABLE: float(value(model_var_cost)),
                    CostType.VARIABLE: float(value(undiscounted_var_cost)),
                }
            )
    exchange_entries = exchange_costs.get_entries()
    return entries, exchange_entries


def loan_costs(
    loan_rate: float,  # this is referred to as loan_rate in parameters
    loan_life: float,
    capacity: float,
    invest_cost: float,
    process_life: int,
    p_0: int,
    p_e: int,
    global_discount_rate: float,
    vintage: int,
    **kwargs: object,
) -> tuple[float, float]:
    """
    Calculate Loan costs by calling the loan annualize and loan cost functions in temoa_rules
    :return: tuple of [model-view discounted cost, un-discounted annuity]
    """
    # dev note:  this is a passthrough function.  Sole intent is to use the EXACT formula the
    #            model uses for these costs
    loan_ar = costs.pv_to_annuity(rate=loan_rate, periods=int(loan_life))
    model_ic = costs.loan_cost(
        capacity,
        invest_cost,
        loan_annualize=float(value(loan_ar)),
        lifetime_loan_process=loan_life,
        lifetime_process=process_life,
        p_0=p_0,
        p_e=p_e,
        global_discount_rate=global_discount_rate,
        vintage=vintage,
    )
    # Override the GDR to get the undiscounted value
    global_discount_rate = 0
    undiscounted_cost = costs.loan_cost(
        capacity,
        invest_cost,
        loan_annualize=float(value(loan_ar)),
        lifetime_loan_process=loan_life,
        lifetime_process=process_life,
        p_0=p_0,
        p_e=p_e,
        global_discount_rate=global_discount_rate,
        vintage=vintage,
    )
    return float(value(model_ic)), float(value(undiscounted_cost))


def loan_costs_survival_curve(
    model: TemoaModel,
    r: Region,
    t: Technology,
    v: Vintage,
    loan_rate: float,  # this is referred to as loan_rate in parameters
    loan_life: float,
    capacity: float,
    invest_cost: float,
    p_0: Period,
    p_e: Period,
    global_discount_rate: float,
    vintage: Vintage,
    **kwargs: object,
) -> tuple[float, float]:
    """
    Calculate Loan costs by calling the loan annualize and loan cost functions in temoa_rules
    :return: tuple of [model-view discounted cost, un-discounted annuity]
    """
    # dev note:  this is a passthrough function.  Sole intent is to use the EXACT formula the
    #            model uses for these costs
    loan_ar = costs.pv_to_annuity(rate=loan_rate, periods=int(loan_life))
    model_ic = costs.loan_cost_survival_curve(
        model,
        r,
        t,
        v,
        capacity,
        invest_cost,
        loan_annualize=float(value(loan_ar)),
        lifetime_loan_process=loan_life,
        p_0=p_0,
        p_e=p_e,
        global_discount_rate=global_discount_rate,
    )
    # Override the GDR to get the undiscounted value
    global_discount_rate = 0
    undiscounted_cost = costs.loan_cost_survival_curve(
        model,
        r,
        t,
        v,
        capacity,
        invest_cost,
        loan_annualize=float(value(loan_ar)),
        lifetime_loan_process=loan_life,
        p_0=p_0,
        p_e=p_e,
        global_discount_rate=global_discount_rate,
    )
    return float(value(model_ic)), float(value(undiscounted_cost))


def poll_emissions(
    model: TemoaModel, p_0: Period | None = None, epsilon: float = 1e-5
) -> tuple[
    dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]], dict[EI, float]
]:
    """
    Gather all emission flows, cost them and provide a tuple of costs and flows
    :param M: the model
    :param p_0: the first period, if other than min(time_optimize), as in MYOPIC
    :param epsilon: a minimal epsilon for ignored values
    :return: cost_dict, flow_dict
    """

    # UPDATE:  older versions brought forward had some accounting errors here for flex/curtailed
    #          emissions
    #          see the note on emissions in the Cost function in temoa_rules
    p_0_true: Period
    if p_0 is None:
        p_0_true = min(model.time_optimize)
    else:
        p_0_true = p_0

    global_discount_rate = value(model.global_discount_rate)

    ###########################
    #   Process Emissions
    ###########################

    base = [
        (r, p, e, i, t, v, o)
        for (r, e, i, t, v, o) in model.emission_activity.sparse_iterkeys()
        for p in model.time_optimize
        if (r, p, t, v) in model.process_inputs
    ]

    # The "base set" can be expanded now to cover normal/annual indexing sets
    normal = [
        (r, p, e, s, d, i, t, v, o)
        for (r, p, e, i, t, v, o) in base
        for s in model.time_season[p]
        for d in model.time_of_day
        if t not in model.tech_annual
    ]
    annual = [(r, p, e, i, t, v, o) for (r, p, e, i, t, v, o) in base if t in model.tech_annual]

    flows: dict[EI, float] = defaultdict(float)
    # iterate through the normal and annual and accumulate flow values
    for r, p, e, s, d, i, t, v, o in normal:
        flows[EI(r, p, t, v, e)] += (
            value(model.v_flow_out[r, p, s, d, i, t, v, o])
            * model.emission_activity[r, e, i, t, v, o]
        )

    for r, p, e, i, t, v, o in annual:
        flows[EI(r, p, t, v, e)] += (
            value(model.v_flow_out_annual[r, p, i, t, v, o])
            * model.emission_activity[r, e, i, t, v, o]
        )

    # gather costs
    ud_costs: dict[tuple[Region, Period, Technology, Vintage], float] = defaultdict(float)
    d_costs: dict[tuple[Region, Period, Technology, Vintage], float] = defaultdict(float)
    for ei in flows:
        # zero out tiny flows
        if abs(flows[ei]) < epsilon:
            flows[ei] = 0.0
            continue
        # screen to see if there is an associated cost
        cost_index = (ei.r, ei.p, ei.e)
        if cost_index not in model.cost_emission:
            continue
        undiscounted_emiss_cost = (
            flows[ei] * model.cost_emission[ei.r, ei.p, ei.e] * model.period_length[ei.p]
        )
        discounted_emiss_cost = costs.fixed_or_variable_cost(
            cap_or_flow=flows[ei],
            cost_factor=value(model.cost_emission[ei.r, ei.p, ei.e]),
            cost_years=model.period_length[ei.p],
            global_discount_rate=global_discount_rate,
            p_0=p_0_true,
            p=ei.p,
        )
        ud_costs[ei.r, ei.p, ei.t, ei.v] += float(value(undiscounted_emiss_cost))
        d_costs[ei.r, ei.p, ei.t, ei.v] += float(value(discounted_emiss_cost))

    ###########################
    #   Embodied Emissions
    ###########################

    # iterate through embodied flows
    embodied_flows: dict[EI, float] = defaultdict(float)
    for r, e, t, v in model.emission_embodied.sparse_iterkeys():
        embodied_flows[EI(r, v, t, v, e)] += value(
            model.v_new_capacity[r, t, v]
            * model.emission_embodied[r, e, t, v]
            / model.period_length[v]
        )  # for embodied costs
        flows[EI(r, v, t, v, e)] += value(
            model.v_new_capacity[r, t, v]
            * model.emission_embodied[r, e, t, v]
            / model.period_length[v]
        )  # add embodied to process emissions

    # add embodied costs to process costs
    for ei in embodied_flows:
        # zero out again if still tiny after embodied flows
        if abs(flows[ei]) < epsilon:
            flows[ei] = 0.0
            continue
        # screen to see if there is an associated cost
        cost_index = (ei.r, cast('Period', ei.v), ei.e)
        if cost_index not in model.cost_emission:
            continue
        undiscounted_emiss_cost = (
            embodied_flows[ei]
            * model.cost_emission[ei.r, cast('Period', ei.v), ei.e]
            * model.period_length[
                cast('Period', ei.v)
            ]  # treat as fixed cost distributed over construction period
        )
        discounted_emiss_cost = costs.fixed_or_variable_cost(
            cap_or_flow=embodied_flows[ei],
            cost_factor=value(model.cost_emission[ei.r, cast('Period', ei.v), ei.e]),
            cost_years=model.period_length[
                cast('Period', ei.v)
            ],  # treat as fixed cost distributed over construction period
            global_discount_rate=global_discount_rate,
            p_0=p_0_true,
            p=cast('Period', ei.v),
        )
        ud_costs[ei.r, cast('Period', ei.v), ei.t, ei.v] += float(value(undiscounted_emiss_cost))
        d_costs[ei.r, cast('Period', ei.v), ei.t, ei.v] += float(value(discounted_emiss_cost))

    ###########################
    #   End of life Emissions
    ###########################

    # iterate through end of life flows
    eol_flows: dict[EI, float] = defaultdict(float)
    for r, e, t, v in model.emission_end_of_life.sparse_iterkeys():
        if (r, t, v) not in model.retirement_periods:
            continue
        for p in model.retirement_periods[r, t, v]:
            eol_flows[EI(r, p, t, v, e)] += value(
                model.v_annual_retirement[r, p, t, v] * model.emission_end_of_life[r, e, t, v]
            )  # for eol costs
            flows[EI(r, p, t, v, e)] += value(
                model.v_annual_retirement[r, p, t, v] * model.emission_end_of_life[r, e, t, v]
            )  # add eol to process emissions

    # add embodied costs to process costs
    for ei in eol_flows:
        # zero out again if still tiny
        if abs(flows[ei]) < epsilon:
            flows[ei] = 0.0
            continue
        # screen to see if there is an associated cost
        cost_index = (ei.r, ei.p, ei.e)
        if cost_index not in model.cost_emission:
            continue
        undiscounted_emiss_cost = (
            eol_flows[ei]
            * model.cost_emission[ei.r, ei.p, ei.e]
            * model.period_length[ei.p]  # treat as fixed cost distributed over retirement period
        )
        discounted_emiss_cost = costs.fixed_or_variable_cost(
            cap_or_flow=eol_flows[ei],
            cost_factor=value(model.cost_emission[ei.r, ei.p, ei.e]),
            cost_years=model.period_length[
                ei.p
            ],  # treat as fixed cost distributed over retirement period
            global_discount_rate=global_discount_rate,
            p_0=p_0_true,
            p=ei.p,
        )
        ud_costs[ei.r, ei.p, ei.t, ei.v] += float(value(undiscounted_emiss_cost))
        d_costs[ei.r, ei.p, ei.t, ei.v] += float(value(discounted_emiss_cost))

    # finally, now that all costs are added up for each rptv, put in cost dict
    costs_dict: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]] = (
        defaultdict(dict)
    )
    for rptv in ud_costs:
        costs_dict[rptv][CostType.EMISS] = ud_costs[rptv]
    for rptv in d_costs:
        costs_dict[rptv][CostType.D_EMISS] = d_costs[rptv]

    # wow, that was like pulling teeth
    return costs_dict, flows
