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
from collections import defaultdict

from pyomo.common.numeric_types import value
from pyomo.core import Objective

from temoa._internal.exchange_tech_cost_ledger import CostType, ExchangeTechCostLedger
from temoa.components import costs
from temoa.components.utils import get_variable_efficiency
from temoa.core.model import TemoaModel
from temoa.types.model_types import EI, FI, SLI, CapData, FlowType

logger = logging.getLogger(__name__)


def _marks(num: int) -> str:
    """convenience to make a sequence of question marks for query"""
    qs = ','.join('?' for _ in range(num))
    marks = '(' + qs + ')'
    return marks


def ritvo(fi: FI) -> tuple[str, str, str, int, str]:
    """convert FI to ritvo index"""
    return fi.r, fi.i, fi.t, fi.v, fi.o


def rpetv(fi: FI, e: str) -> tuple[str, int, str, str, int]:
    """convert FI and emission to rpetv index"""
    return fi.r, fi.p, e, fi.t, fi.v


def poll_capacity_results(M: TemoaModel, epsilon: float = 1e-5) -> CapData:
    """
    Poll a solved model for capacity results.
    :param M: Solved Model
    :param epsilon: epsilon (default 1e-5)
    :return: a CapData object
    """
    # Built Capacity
    built = []
    for r, t, v in M.V_NewCapacity.keys():
        if v in M.time_optimize:
            val = value(M.V_NewCapacity[r, t, v])
            if abs(val) < epsilon:
                continue
            new_cap = (r, t, v, val)
            built.append(new_cap)

    # NetCapacity
    net = []
    for r, p, t, v in M.V_Capacity.keys():
        val = value(M.V_Capacity[r, p, t, v])
        if abs(val) < epsilon:
            continue
        new_net_cap = (r, p, t, v, val)
        net.append(new_net_cap)

    # Retired Capacity
    ret = []
    for r, t, v in M.retirementPeriods:
        lifetime = value(M.LifetimeProcess[r, t, v])
        for p in M.retirementPeriods[r, t, v]:
            # We want to output period retirement, not annual retirement, so multiply by PeriodLength
            eol = value(M.PeriodLength[p]) * value(M.V_AnnualRetirement[r, p, t, v])
            early = 0
            if t in M.tech_retirement and v < p <= v + lifetime - value(M.PeriodLength[p]):
                early = value(M.V_RetiredCapacity[r, p, t, v])
                eol -= early
            early = 0 if abs(early) < epsilon else early
            eol = 0 if abs(eol) < epsilon else eol
            if early == 0 and eol == 0:
                continue
            new_retired_cap = (r, p, t, v, eol, early)
            ret.append(new_retired_cap)

    return CapData(built=built, net=net, retired=ret)


def poll_flow_results(M: TemoaModel, epsilon: float = 1e-5) -> dict[FI, dict[FlowType, float]]:
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
    for key in M.V_FlowIn.keys():
        fi = FI(*key)
        flow = value(M.V_FlowIn[fi])
        if abs(flow) < epsilon:
            continue
        res[fi][FlowType.IN] = flow
        res[fi][FlowType.LOST] = (1 - get_variable_efficiency(M, *key)) * flow

    # regular flows
    for key in M.V_FlowOut.keys():
        fi = FI(*key)
        flow = value(M.V_FlowOut[fi])
        if abs(flow) < epsilon:
            continue
        res[fi][FlowType.OUT] = flow

        if fi.t not in M.tech_storage:  # we can get the flow in by out/eff...
            flow = value(M.V_FlowOut[fi]) / get_variable_efficiency(M, *key)
            res[fi][FlowType.IN] = flow
            res[fi][FlowType.LOST] = (1 - get_variable_efficiency(M, *key)) * flow

    # curtailment flows
    for key in M.V_Curtailment.keys():
        fi = FI(*key)
        val = value(M.V_Curtailment[fi])
        if abs(val) < epsilon:
            continue
        res[fi][FlowType.CURTAIL] = val

    # flex techs.  This will subtract the flex from their output flow IOT make OUT the "net"
    for key in M.V_Flex.keys():
        fi = FI(*key)
        flow = value(M.V_Flex[fi])
        if abs(flow) < epsilon:
            continue
        res[fi][FlowType.FLEX] = flow
        res[fi][FlowType.OUT] -= flow

    # ---- annual ----

    # basic annual flows
    for r, p, i, t, v, o in M.V_FlowOutAnnual.keys():
        # Make sure this isn't just a non-annual demand tech
        if t not in M.tech_annual:
            continue
        for s in M.TimeSeason[p]:
            for d in M.time_of_day:
                if o in M.commodity_demand:
                    distribution = value(M.DemandSpecificDistribution[r, p, s, d, o])
                else:
                    distribution = value(M.SegFrac[p, s, d])
                fi = FI(r, p, s, d, i, t, v, o)
                flow = value(M.V_FlowOutAnnual[r, p, i, t, v, o]) * distribution
                if abs(flow) < epsilon:
                    continue
                res[fi][FlowType.OUT] = flow
                res[fi][FlowType.IN] = flow / value(M.Efficiency[ritvo(fi)])
                res[fi][FlowType.LOST] = (1 - value(M.Efficiency[ritvo(fi)])) * res[fi][FlowType.IN]

    # flex annual
    for r, p, i, t, v, o in M.V_FlexAnnual.keys():
        for s in M.TimeSeason[p]:
            for d in M.time_of_day:
                fi = FI(r, p, s, d, i, t, v, o)
                flow = value(M.V_FlexAnnual[r, p, i, t, v, o]) * value(M.SegFrac[p, s, d])
                if abs(flow) < epsilon:
                    continue
                res[fi][FlowType.FLEX] = flow
                res[fi][FlowType.OUT] -= flow

    # construction flows
    for r, i, t, v in M.ConstructionInput.sparse_iterkeys():
        annual = (
            value(M.ConstructionInput[r, i, t, v])
            * value(M.V_NewCapacity[r, t, v])
            / value(M.PeriodLength[v])
        )
        for s in M.TimeSeason[v]:
            for d in M.time_of_day:
                fi = FI(r, v, s, d, i, t, v, 'ConstructionInput')
                flow = annual * value(M.SegFrac[v, s, d])
                if abs(flow) < epsilon:
                    continue
                res[fi][FlowType.IN] = flow

    # end of life flows
    for r, t, v, o in M.EndOfLifeOutput.sparse_iterkeys():
        if (r, t, v) not in M.retirementPeriods:
            continue
        for p in M.retirementPeriods[r, t, v]:
            annual = value(M.EndOfLifeOutput[r, t, v, o]) * value(M.V_AnnualRetirement[r, p, t, v])
            for s in M.TimeSeason[p]:
                for d in M.time_of_day:
                    fi = FI(r, p, s, d, 'EndOfLifeOutput', t, v, o)
                    flow = annual * value(M.SegFrac[p, s, d])
                    if abs(flow) < epsilon:
                        continue
                    res[fi][FlowType.OUT] = flow

    return res


def poll_storage_level_results(M: TemoaModel, epsilon: float = 1e-5) -> dict[SLI, float]:
    """
    Poll a solved model for flow results.
    :param M: A solved Model
    :param epsilon: epsilon (default 1e-5)
    :return: dictionary of storage level index, storage level
    """
    res: dict[SLI, float] = defaultdict(float)

    # Storage level, the state variable for all but last time slice of each season
    for r, p, s, d, t, v in M.StorageLevel_rpsdtv:
        if t in M.tech_seasonal_storage:
            continue
        state = value(M.V_StorageLevel[r, p, s, d, t, v]) / (
            value(M.SegFracPerSeason[p, s]) * value(M.DaysPerPeriod)
        )
        sli = SLI(r, p, s, d, t, v)
        if abs(state) < epsilon:
            state = 0  # still want to know but decimals are ugly
        res[sli] = state

    for r, p, s_seq, t, v in M.SeasonalStorageLevel_rpstv:
        s = M.sequential_to_season[p, s_seq]
        # Ratio of days in virtual storage season to days in actual season
        # Flows and StorageLevel are normalised to the number of days in the ACTUAL season, so must
        # be adjusted to the number of days in the virtual storage season
        days_adjust = value(M.TimeSeasonSequential[p, s_seq, s]) / (
            value(M.SegFracPerSeason[p, s]) * value(M.DaysPerPeriod)
        )
        for d in M.time_of_day:
            state = (
                value(M.V_SeasonalStorageLevel[r, p, s_seq, t, v])
                + value(M.V_StorageLevel[r, p, s, d, t, v]) * days_adjust
            )
            sli = SLI(r, p, s_seq, d, t, v)
            if abs(state) < epsilon:
                state = 0  # still want to know but decimals are ugly
            res[sli] = state

    return res


def poll_objective(M: TemoaModel) -> list[tuple[str, float]]:
    """gather objective name, value tuples for all active objectives"""
    objs: list[Objective] = list(M.component_data_objects(Objective))
    active_objs = [obj for obj in objs if obj.active]
    if len(active_objs) > 1:
        logger.warning('Multiple active objectives found.  All will be logged in db')
    res = []
    for obj in active_objs:
        obj_name, obj_value = obj.getname(fully_qualified=True), float(value(obj))
        res.append((obj_name, obj_value))
    return res


def poll_cost_results(
    M: TemoaModel, p_0: int | None, epsilon: float = 1e-5
) -> tuple[
    dict[tuple[str, int, str, int], dict[CostType, float]],
    dict[tuple[str, int, str, int], dict[CostType, float]],
]:
    """
    Poll a solved model for all cost results
    :param M: Solved Model
    :param p_0: a base year for discounting of loans, typically only used in MYOPIC.  If none, first optimization year used
    :param epsilon: epsilon (default 1e-5)
    :return: tuple of cost_dict, exchange_cost_dict (for exchange techs)
    """
    p_0_true: int
    if p_0 is None:
        p_0_true = min(M.time_optimize)
    else:
        p_0_true = p_0

    p_e = M.time_future.last()

    # conveniences...
    GDR = value(M.GlobalDiscountRate)
    # MPL = M.ModelProcessLife
    LLN = M.LoanLifetimeProcess

    exchange_costs = ExchangeTechCostLedger(M)
    entries: dict[tuple[str, int, str, int], dict[CostType, float]] = defaultdict(dict)
    for r, t, v in M.CostInvest.sparse_iterkeys():  # Returns only non-zero values
        # gather details...
        cap = value(M.V_NewCapacity[r, t, v])
        if abs(cap) < epsilon:
            continue
        loan_life = value(LLN[r, t, v])
        loan_rate = value(M.LoanRate[r, t, v])

        if M.isSurvivalCurveProcess[r, t, v]:
            model_loan_cost, undiscounted_cost = loan_costs_survival_curve(
                M=M,
                r=r,
                t=t,
                v=v,
                loan_rate=loan_rate,
                loan_life=loan_life,
                capacity=cap,
                invest_cost=value(M.CostInvest[r, t, v]),
                p_0=p_0_true,
                p_e=p_e,
                global_discount_rate=GDR,
                vintage=v,
            )
        else:
            model_loan_cost, undiscounted_cost = loan_costs(
                loan_rate=loan_rate,
                loan_life=loan_life,
                capacity=cap,
                invest_cost=value(M.CostInvest[r, t, v]),
                process_life=value(M.LifetimeProcess[r, t, v]),
                p_0=p_0_true,
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
        undiscounted_fixed_cost = cap * fixed_cost * value(M.PeriodLength[p])

        model_fixed_cost = costs.fixed_or_variable_cost(
            cap,
            value(fixed_cost),
            value(M.PeriodLength[p]),
            GDR=GDR,
            P_0=float(p_0) if p_0 is not None else 0.0,
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

    for r, p, t, v in M.CostVariable.sparse_iterkeys():
        if t not in M.tech_annual:
            activity = sum(
                value(M.V_FlowOut[r, p, S_s, S_d, S_i, t, v, S_o])
                for S_i in M.processInputs[r, p, t, v]
                for S_o in M.processOutputsByInput[r, p, t, v, S_i]
                for S_s in M.TimeSeason[p]
                for S_d in M.time_of_day
            )
        else:
            activity = sum(
                value(M.V_FlowOutAnnual[r, p, S_i, t, v, S_o])
                for S_i in M.processInputs[r, p, t, v]
                for S_o in M.processOutputsByInput[r, p, t, v, S_i]
            )
        if abs(activity) < epsilon:
            continue

        var_cost = value(M.CostVariable[r, p, t, v])
        undiscounted_var_cost = activity * var_cost * value(M.PeriodLength[p])

        model_var_cost = costs.fixed_or_variable_cost(
            activity,
            var_cost,
            value(M.PeriodLength[p]),
            GDR=GDR,
            P_0=float(p_0) if p_0 is not None else 0.0,
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
    loan_rate: float,  # this is referred to as LoanRate in parameters
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
        P_0=p_0,
        P_e=p_e,
        GDR=global_discount_rate,
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
        P_0=p_0,
        P_e=p_e,
        GDR=global_discount_rate,
        vintage=vintage,
    )
    return float(value(model_ic)), float(value(undiscounted_cost))


def loan_costs_survival_curve(
    M: TemoaModel,
    r: str,
    t: str,
    v: int,
    loan_rate: float,  # this is referred to as LoanRate in parameters
    loan_life: float,
    capacity: float,
    invest_cost: float,
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
    model_ic = costs.loan_cost_survival_curve(
        M,
        r,
        t,
        v,
        capacity,
        invest_cost,
        loan_annualize=float(value(loan_ar)),
        lifetime_loan_process=loan_life,
        P_0=p_0,
        P_e=p_e,
        GDR=global_discount_rate,
    )
    # Override the GDR to get the undiscounted value
    global_discount_rate = 0
    undiscounted_cost = costs.loan_cost_survival_curve(
        M,
        r,
        t,
        v,
        capacity,
        invest_cost,
        loan_annualize=float(value(loan_ar)),
        lifetime_loan_process=loan_life,
        P_0=p_0,
        P_e=p_e,
        GDR=global_discount_rate,
    )
    return float(value(model_ic)), float(value(undiscounted_cost))


def poll_emissions(
    M: TemoaModel, p_0: int | None = None, epsilon: float = 1e-5
) -> tuple[dict[tuple[str, int, str, int], dict[CostType, float]], dict[EI, float]]:
    """
    Gather all emission flows, cost them and provide a tuple of costs and flows
    :param M: the model
    :param p_0: the first period, if other than min(time_optimize), as in MYOPIC
    :param epsilon: a minimal epsilon for ignored values
    :return: cost_dict, flow_dict
    """

    # UPDATE:  older versions brought forward had some accounting errors here for flex/curtailed emissions
    #          see the note on emissions in the Cost function in temoa_rules
    p_0_true: int
    if p_0 is None:
        p_0_true = min(M.time_optimize)
    else:
        p_0_true = p_0

    GDR = value(M.GlobalDiscountRate)

    ###########################
    #   Process Emissions
    ###########################

    base = [
        (r, p, e, i, t, v, o)
        for (r, e, i, t, v, o) in M.EmissionActivity.sparse_iterkeys()
        for p in M.time_optimize
        if (r, p, t, v) in M.processInputs
    ]

    # The "base set" can be expanded now to cover normal/annual indexing sets
    normal = [
        (r, p, e, s, d, i, t, v, o)
        for (r, p, e, i, t, v, o) in base
        for s in M.TimeSeason[p]
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
    ud_costs: dict[tuple[str, int, str, int], float] = defaultdict(float)
    d_costs: dict[tuple[str, int, str, int], float] = defaultdict(float)
    for ei in flows:
        # zero out tiny flows
        if abs(flows[ei]) < epsilon:
            flows[ei] = 0.0
            continue
        # screen to see if there is an associated cost
        cost_index = (ei.r, ei.p, ei.e)
        if cost_index not in M.CostEmission:
            continue
        undiscounted_emiss_cost = (
            flows[ei] * M.CostEmission[ei.r, ei.p, ei.e] * M.PeriodLength[ei.p]
        )
        discounted_emiss_cost = costs.fixed_or_variable_cost(
            cap_or_flow=flows[ei],
            cost_factor=value(M.CostEmission[ei.r, ei.p, ei.e]),
            cost_years=M.PeriodLength[ei.p],
            GDR=GDR,
            P_0=p_0_true,
            p=ei.p,
        )
        ud_costs[ei.r, ei.p, ei.t, ei.v] += float(value(undiscounted_emiss_cost))
        d_costs[ei.r, ei.p, ei.t, ei.v] += float(value(discounted_emiss_cost))

    ###########################
    #   Embodied Emissions
    ###########################

    # iterate through embodied flows
    embodied_flows: dict[EI, float] = defaultdict(float)
    for r, e, t, v in M.EmissionEmbodied.sparse_iterkeys():
        embodied_flows[EI(r, v, t, v, e)] += value(
            M.V_NewCapacity[r, t, v] * M.EmissionEmbodied[r, e, t, v] / M.PeriodLength[v]
        )  # for embodied costs
        flows[EI(r, v, t, v, e)] += value(
            M.V_NewCapacity[r, t, v] * M.EmissionEmbodied[r, e, t, v] / M.PeriodLength[v]
        )  # add embodied to process emissions

    # add embodied costs to process costs
    for ei in embodied_flows:
        # zero out again if still tiny after embodied flows
        if abs(flows[ei]) < epsilon:
            flows[ei] = 0.0
            continue
        # screen to see if there is an associated cost
        cost_index = (ei.r, ei.v, ei.e)
        if cost_index not in M.CostEmission:
            continue
        undiscounted_emiss_cost = (
            embodied_flows[ei]
            * M.CostEmission[ei.r, ei.v, ei.e]
            * M.PeriodLength[ei.v]  # treat as fixed cost distributed over construction period
        )
        discounted_emiss_cost = costs.fixed_or_variable_cost(
            cap_or_flow=embodied_flows[ei],
            cost_factor=value(M.CostEmission[ei.r, ei.v, ei.e]),
            cost_years=M.PeriodLength[
                ei.v
            ],  # treat as fixed cost distributed over construction period
            GDR=GDR,
            P_0=p_0_true,
            p=ei.v,
        )
        ud_costs[ei.r, ei.v, ei.t, ei.v] += float(value(undiscounted_emiss_cost))
        d_costs[ei.r, ei.v, ei.t, ei.v] += float(value(discounted_emiss_cost))

    ###########################
    #   End of life Emissions
    ###########################

    # iterate through end of life flows
    eol_flows: dict[EI, float] = defaultdict(float)
    for r, e, t, v in M.EmissionEndOfLife.sparse_iterkeys():
        if (r, t, v) not in M.retirementPeriods:
            continue
        for p in M.retirementPeriods[r, t, v]:
            eol_flows[EI(r, p, t, v, e)] += value(
                M.V_AnnualRetirement[r, p, t, v] * M.EmissionEndOfLife[r, e, t, v]
            )  # for eol costs
            flows[EI(r, p, t, v, e)] += value(
                M.V_AnnualRetirement[r, p, t, v] * M.EmissionEndOfLife[r, e, t, v]
            )  # add eol to process emissions

    # add embodied costs to process costs
    for ei in eol_flows:
        # zero out again if still tiny
        if abs(flows[ei]) < epsilon:
            flows[ei] = 0.0
            continue
        # screen to see if there is an associated cost
        cost_index = (ei.r, ei.p, ei.e)
        if cost_index not in M.CostEmission:
            continue
        undiscounted_emiss_cost = (
            eol_flows[ei]
            * M.CostEmission[ei.r, ei.p, ei.e]
            * M.PeriodLength[ei.p]  # treat as fixed cost distributed over retirement period
        )
        discounted_emiss_cost = costs.fixed_or_variable_cost(
            cap_or_flow=eol_flows[ei],
            cost_factor=value(M.CostEmission[ei.r, ei.p, ei.e]),
            cost_years=M.PeriodLength[
                ei.p
            ],  # treat as fixed cost distributed over retirement period
            GDR=GDR,
            P_0=p_0_true,
            p=ei.p,
        )
        ud_costs[ei.r, ei.p, ei.t, ei.v] += float(value(undiscounted_emiss_cost))
        d_costs[ei.r, ei.p, ei.t, ei.v] += float(value(discounted_emiss_cost))

    # finally, now that all costs are added up for each rptv, put in cost dict
    costs_dict: dict[tuple[str, int, str, int], dict[CostType, float]] = defaultdict(dict)
    for rptv in ud_costs:
        costs_dict[rptv][CostType.EMISS] = ud_costs[rptv]
    for rptv in d_costs:
        costs_dict[rptv][CostType.D_EMISS] = d_costs[rptv]

    # wow, that was like pulling teeth
    return costs_dict, flows
