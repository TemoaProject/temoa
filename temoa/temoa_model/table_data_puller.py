"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

Copyright (C) 2015,  NC State University

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A complete copy of the GNU General Public License v2 (GPLv2) is available
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.


Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  12/5/24

A companion module to the table writer to hold some data-pulling functions and small utilities and separate them
from the writing process for organization and to isolate the DB access in the writer such that
these functions can be called on a model instance without any DB interactions.  (Intended to support use
by Workers who shouldn't interact with DB).  Dev Note:  In future, if transition away from sqlite, this
could all be refactored to perform tasks within workers, but concurrent access to sqlite is a no-go
"""
import functools
import logging
from collections import namedtuple, defaultdict
from enum import unique, Enum

from pyomo.common.numeric_types import value
from pyomo.core import Objective

from temoa.temoa_model import temoa_rules
from temoa.temoa_model.exchange_tech_cost_ledger import ExchangeTechCostLedger, CostType
from temoa.temoa_model.temoa_model import TemoaModel

logger = logging.getLogger(__name__)


def _marks(num: int) -> str:
    """convenience to make a sequence of question marks for query"""
    qs = ','.join('?' for _ in range(num))
    marks = '(' + qs + ')'
    return marks


EI = namedtuple('EI', ['r', 'p', 't', 'v', 'e'])
"""Emission Index"""


@unique
class FlowType(Enum):
    """Types of flow tracked"""

    IN = 1
    OUT = 2
    CURTAIL = 3
    FLEX = 4
    LOST = 5


FI = namedtuple('FI', ['r', 'p', 's', 'd', 'i', 't', 'v', 'o'])
"""Flow Index"""

CapData = namedtuple('CapData', ['built', 'net', 'retired'])
"""Small container to hold named dictionaries of capacity data for processing"""


def ritvo(fi: FI) -> tuple:
    """convert FI to ritvo index"""
    return fi.r, fi.i, fi.t, fi.v, fi.o


def rpetv(fi: FI, e: str) -> tuple:
    """convert FI and emission to rpetv index"""
    return fi.r, fi.p, e, fi.t, fi.v


def poll_capacity_results(M: TemoaModel, epsilon=1e-5) -> CapData:
    """
    Poll a solved model for capacity results.
    :param M: Solved Model
    :param epsilon: epsilon (default 1e-5)
    :return: a CapData object
    """
    # Built Capacity
    built = []
    for r, t, v in M.V_NewCapacity:
        if v in M.time_optimize:
            val = value(M.V_NewCapacity[r, t, v])
            if abs(val) < epsilon:
                continue
            new_cap = (r, t, v, val)
            built.append(new_cap)

    # NetCapacity
    net = []
    for r, p, t, v in M.V_Capacity:
        val = value(M.V_Capacity[r, p, t, v])
        if abs(val) < epsilon:
            continue
        new_net_cap = (r, p, t, v, val)
        net.append(new_net_cap)

    # Retired Capacity
    ret = []
    for r, p, t, v in M.V_RetiredCapacity:
        val = value(M.V_RetiredCapacity[r, p, t, v])
        if abs(val) < epsilon:
            continue
        new_retired_cap = (r, p, t, v, val)
        ret.append(new_retired_cap)

    return CapData(built=built, net=net, retired=ret)


def poll_flow_results(M: TemoaModel, epsilon=1e-5) -> dict[FI, dict[FlowType, float]]:
    """
    Poll a solved model for flow results.
    :param M: A solved Model
    :param epsilon: epsilon (default 1e-5)
    :return: nested dictionary of FlowIndex, FlowType : value
    """
    dd = functools.partial(defaultdict, float)
    res: dict[FI, dict[FlowType, float]] = defaultdict(dd)

    # ---- NON-annual ----

    # Storage, which has a unique v_flow_in (non-storage techs do not have this variable)
    for key in M.V_FlowIn:
        fi = FI(*key)
        flow = value(M.V_FlowIn[fi])
        if abs(flow) < epsilon:
            continue
        res[fi][FlowType.IN] = flow
        res[fi][FlowType.LOST] = (1 - value(M.Efficiency[ritvo(fi)])) * flow

    # regular flows
    for key in M.V_FlowOut:
        fi = FI(*key)
        flow = value(M.V_FlowOut[fi])
        if abs(flow) < epsilon:
            continue
        res[fi][FlowType.OUT] = flow

        if fi.t not in M.tech_storage:  # we can get the flow in by out/eff...
            flow = value(M.V_FlowOut[fi]) / value(M.Efficiency[ritvo(fi)])
            res[fi][FlowType.IN] = flow
            res[fi][FlowType.LOST] = (1 - value(M.Efficiency[ritvo(fi)])) * flow

    # curtailment flows
    for key in M.V_Curtailment:
        fi = FI(*key)
        val = value(M.V_Curtailment[fi])
        if abs(val) < epsilon:
            continue
        res[fi][FlowType.CURTAIL] = val

    # flex techs.  This will subtract the flex from their output flow IOT make OUT the "net"
    for key in M.V_Flex:
        fi = FI(*key)
        flow = value(M.V_Flex[fi])
        if abs(flow) < epsilon:
            continue
        res[fi][FlowType.FLEX] = flow
        res[fi][FlowType.OUT] -= flow

    # ---- annual ----

    # basic annual flows
    for r, p, i, t, v, o in M.V_FlowOutAnnual:
        for s in M.time_season:
            for d in M.time_of_day:
                fi = FI(r, p, s, d, i, t, v, o)
                flow = value(M.V_FlowOutAnnual[r, p, i, t, v, o]) * value(M.SegFrac[s, d])
                if abs(flow) < epsilon:
                    continue
                res[fi][FlowType.OUT] = flow
                res[fi][FlowType.IN] = flow / value(M.Efficiency[ritvo(fi)])
                res[fi][FlowType.LOST] = (1 - value(M.Efficiency[ritvo(fi)])) * res[fi][FlowType.IN]

    # flex annual
    for r, p, i, t, v, o in M.V_FlexAnnual:
        for s in M.time_season:
            for d in M.time_of_day:
                fi = FI(r, p, s, d, i, t, v, o)
                flow = value(M.V_FlexAnnual[r, p, i, t, v, o]) * value(M.SegFrac[s, d])
                if abs(flow) < epsilon:
                    continue
                res[fi][FlowType.FLEX] = flow
                res[fi][FlowType.OUT] -= flow

    return res


def poll_objective(M: TemoaModel) -> list[tuple[str, float]]:
    """gather objective name, value tuples for all active objectives"""
    objs: list[Objective] = list(M.component_data_objects(Objective))
    active_objs = [obj for obj in objs if obj.active]
    if len(active_objs) > 1:
        logger.warning('Multiple active objectives found.  All will be logged in db')
    res = []
    for obj in active_objs:
        obj_name, obj_value = obj.getname(fully_qualified=True), value(obj)
        res.append((obj_name, obj_value))
    return res


def poll_cost_results(
    M: TemoaModel, p_0: int | None, epsilon=1e-5
) -> tuple[dict[tuple, dict], ...]:
    """
    Poll a solved model for all cost results
    :param M: Solved Model
    :param p_0: a base year for discounting of loans, typically only used in MYOPIC.  If none, first optimization year used
    :param epsilon: epsilon (default 1e-5)
    :return: tuple of cost_dict, exchange_cost_dict (for exchange techs)
    """
    if not p_0:
        p_0 = min(M.time_optimize)

    p_e = M.time_future.last()

    # conveniences...
    GDR = value(M.GlobalDiscountRate)
    MPL = M.ModelProcessLife
    LLN = M.LoanLifetimeProcess

    exchange_costs = ExchangeTechCostLedger(M)
    entries = defaultdict(dict)
    for r, t, v in M.CostInvest.sparse_iterkeys():  # Returns only non-zero values
        # gather details...
        cap = value(M.V_NewCapacity[r, t, v])
        if abs(cap) < epsilon:
            continue
        loan_life = value(LLN[r, t, v])
        loan_rate = value(M.LoanRate[r, t, v])

        model_loan_cost, undiscounted_cost = loan_costs(
            loan_rate=loan_rate,
            loan_life=loan_life,
            capacity=cap,
            invest_cost=value(M.CostInvest[r, t, v]),
            process_life=value(M.LifetimeProcess[r, t, v]),
            p_0=p_0,
            p_e=p_e,
            global_discount_rate=GDR,
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
            # enter it into the entries table with period of cost = vintage (p=v)
            entries[r, v, t, v].update(
                {CostType.D_INVEST: model_loan_cost, CostType.INVEST: undiscounted_cost}
            )

    for r, p, t, v in M.CostFixed.sparse_iterkeys():
        cap = value(M.V_Capacity[r, p, t, v])
        if abs(cap) < epsilon:
            continue

        fixed_cost = value(M.CostFixed[r, p, t, v])
        undiscounted_fixed_cost = cap * fixed_cost * value(MPL[r, p, t, v])

        model_fixed_cost = temoa_rules.fixed_or_variable_cost(
            cap, fixed_cost, value(MPL[r, p, t, v]), GDR=GDR, P_0=p_0, p=p
        )
        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=v,
                cost=model_fixed_cost,
                cost_type=CostType.D_FIXED,
            )
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=v,
                cost=undiscounted_fixed_cost,
                cost_type=CostType.FIXED,
            )
        else:
            entries[r, p, t, v].update(
                {CostType.D_FIXED: model_fixed_cost, CostType.FIXED: undiscounted_fixed_cost}
            )

    for r, p, t, v in M.CostVariable.sparse_iterkeys():
        if t not in M.tech_annual:
            activity = sum(
                value(M.V_FlowOut[r, p, S_s, S_d, S_i, t, v, S_o])
                for S_i in M.processInputs[r, p, t, v]
                for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i]
                for S_s in M.time_season
                for S_d in M.time_of_day
            )
        else:
            activity = sum(
                value(M.V_FlowOutAnnual[r, p, S_i, t, v, S_o])
                for S_i in M.processInputs[r, p, t, v]
                for S_o in M.ProcessOutputsByInput[r, p, t, v, S_i]
            )
        if abs(activity) < epsilon:
            continue

        var_cost = value(M.CostVariable[r, p, t, v])
        undiscounted_var_cost = activity * var_cost * value(MPL[r, p, t, v])

        model_var_cost = temoa_rules.fixed_or_variable_cost(
            activity, var_cost, value(MPL[r, p, t, v]), GDR=GDR, P_0=p_0, p=p
        )
        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=v,
                cost=model_var_cost,
                cost_type=CostType.D_VARIABLE,
            )
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=v,
                cost=undiscounted_var_cost,
                cost_type=CostType.VARIABLE,
            )
        else:
            entries[r, p, t, v].update(
                {CostType.D_VARIABLE: model_var_cost, CostType.VARIABLE: undiscounted_var_cost}
            )
    exchange_entries = exchange_costs.get_entries()
    return entries, exchange_entries


def loan_costs(
    loan_rate,  # this is referred to as LoanRate in parameters
    loan_life,
    capacity,
    invest_cost,
    process_life,
    p_0,
    p_e,
    global_discount_rate,
    vintage,
    **kwargs,
) -> tuple[float, float]:
    """
    Calculate Loan costs by calling the loan annualize and loan cost functions in temoa_rules
    :return: tuple of [model-view discounted cost, un-discounted annuity]
    """
    # dev note:  this is a passthrough function.  Sole intent is to use the EXACT formula the
    #            model uses for these costs
    loan_ar = temoa_rules.loan_annualization_rate(loan_rate=loan_rate, loan_life=loan_life)
    model_ic = temoa_rules.loan_cost(
        capacity,
        invest_cost,
        loan_annualize=loan_ar,
        lifetime_loan_process=loan_life,
        P_0=p_0,
        P_e=p_e,
        GDR=global_discount_rate,
        vintage=vintage,
    )
    # Override the GDR to get the undiscounted value
    global_discount_rate = 0
    undiscounted_cost = temoa_rules.loan_cost(
        capacity,
        invest_cost,
        loan_annualize=loan_ar,
        lifetime_loan_process=loan_life,
        P_0=p_0,
        P_e=p_e,
        GDR=global_discount_rate,
        vintage=vintage,
    )
    return model_ic, undiscounted_cost


def poll_emissions(
    M: 'TemoaModel', p_0=None, epsilon=1e-5
) -> tuple[dict[tuple, dict], dict[EI, float]]:
    """
    Gather all emission flows, cost them and provide a tuple of costs and flows
    :param M: the model
    :param p_0: the first period, if other than min(time_optimize), as in MYOPIC
    :param epsilon: a minimal epsilon for ignored values
    :return: cost_dict, flow_dict
    """

    # UPDATE:  older versions brought forward had some accounting errors here for flex/curtailed emissions
    #          see the note on emissions in the Cost function in temoa_rules
    if not p_0:
        p_0 = min(M.time_optimize)

    GDR = value(M.GlobalDiscountRate)
    MPL = M.ModelProcessLife

    base = [
        (r, p, e, i, t, v, o)
        for (r, e, i, t, v, o) in M.EmissionActivity
        for p in M.time_optimize
        if (r, p, t, v) in M.processInputs
    ]

    # The "base set" can be expanded now to cover normal/annual indexing sets
    normal = [
        (r, p, e, s, d, i, t, v, o)
        for (r, p, e, i, t, v, o) in base
        for s in M.time_season
        for d in M.time_of_day
        if t not in M.tech_annual
    ]
    annual = [(r, p, e, i, t, v, o) for (r, p, e, i, t, v, o) in base if t in M.tech_annual]

    flows: dict[EI, float] = defaultdict(float)
    # iterate through the normal and annual and accumulate flow values
    for r, p, e, s, d, i, t, v, o in normal:
        flows[EI(r, p, t, v, e)] += (
            value(M.V_FlowOut[r, p, s, d, i, t, v, o]) * M.EmissionActivity[r, e, i, t, v, o]
        )

    for r, p, e, i, t, v, o in annual:
        flows[EI(r, p, t, v, e)] += (
            value(M.V_FlowOutAnnual[r, p, i, t, v, o]) * M.EmissionActivity[r, e, i, t, v, o]
        )

    # gather costs
    ud_costs = defaultdict(float)
    d_costs = defaultdict(float)
    for ei in flows:
        # screen to see if there is an associated cost
        cost_index = (ei.r, ei.p, ei.e)
        if cost_index not in M.CostEmission:
            continue
        # check for epsilon
        if abs(flows[ei]) < epsilon:
            flows[ei] = 0.0
            continue
        undiscounted_emiss_cost = (
            flows[ei] * M.CostEmission[ei.r, ei.p, ei.e] * MPL[ei.r, ei.p, ei.t, ei.v]
        )
        discounted_emiss_cost = temoa_rules.fixed_or_variable_cost(
            cap_or_flow=flows[ei],
            cost_factor=M.CostEmission[ei.r, ei.p, ei.e],
            process_lifetime=MPL[ei.r, ei.p, ei.t, ei.v],
            GDR=GDR,
            P_0=p_0,
            p=ei.p,
        )
        ud_costs[ei.r, ei.p, ei.t, ei.v] += undiscounted_emiss_cost
        d_costs[ei.r, ei.p, ei.t, ei.v] += discounted_emiss_cost
    costs = defaultdict(dict)
    for k in ud_costs:
        costs[k][CostType.EMISS] = ud_costs[k]
    for k in d_costs:
        costs[k][CostType.D_EMISS] = d_costs[k]

    # wow, that was like pulling teeth
    return costs, flows
