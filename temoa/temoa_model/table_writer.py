"""
tool for writing outputs to database tables
"""
import sqlite3
import sys
from collections import defaultdict, namedtuple
from enum import Enum, unique
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from pyomo.core import value, Objective
from pyomo.opt import SolverResults

from definitions import PROJECT_ROOT
from temoa.temoa_model import temoa_rules
from temoa.temoa_model.exchange_tech_cost_ledger import CostType, ExchangeTechCostLedger
from temoa.temoa_model.temoa_config import TemoaConfig
from temoa.temoa_model.temoa_mode import TemoaMode
from temoa.temoa_model.temoa_model import TemoaModel

if TYPE_CHECKING:
    pass

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
Created on:  2/9/24

Note:  This file borrows heavily from the legacy pformat_results.py, and is somewhat of a restructure of that code
       to accommodate the run modes more cleanly

"""

logger = getLogger(__name__)

basic_output_tables = [
    'OutputBuiltCapacity',
    'OutputCost',
    'OutputCurtailment',
    'OutputDualVariable',
    'OutputEmission',
    'OutputFlowIn',
    'OutputFlowOut',
    'OutputNetCapacity',
    'OutputObjective',
    'OutputRetiredCapacity',
]
optional_output_tables = [
    'OutputFlowOutSummary',
]

flow_summary_file_loc = Path(
    PROJECT_ROOT, 'temoa/extensions/modeling_to_generate_alternatives/make_flow_summary_table.sql'
)


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


def ritvo(fi: FI) -> tuple:
    """convert FI to ritvo index"""
    return fi.r, fi.i, fi.t, fi.v, fi.o


def rpetv(fi: FI, e: str) -> tuple:
    """convert FI and emission to rpetv index"""
    return fi.r, fi.p, e, fi.t, fi.v


class TableWriter:
    def __init__(self, config: TemoaConfig, epsilon=1e-5):
        self.config = config
        self.epsilon = epsilon
        self.tech_sectors: dict[str, str] | None = None
        self.flow_register: dict[FI, dict[FlowType, float]] = {}
        self.emission_register: dict[EI, float] | None = None
        try:
            self.con = sqlite3.connect(config.output_database)
        except sqlite3.OperationalError as e:
            logger.error('Failed to connect to output database: %s', config.output_database)
            logger.error(e)
            sys.exit(-1)

    def write_results(
        self,
        M: TemoaModel,
        results_with_duals: SolverResults | None = None,
        append=False,
        iteration: int | None = None,
    ) -> None:
        """
        Write results to output database
        :param iteration: An interation count for repeated runs, to be passed to tables that support it
        :param results_with_duals: if provided, this will trigger the writing of dual variables, pulled from the SolverResults
        :param M: the model
        :param append: append whatever is already in the tables.  If False (default), clear existing tables by scenario name
        :return:
        """
        if not append:
            self.clear_scenario()
        if not self.tech_sectors:
            self._get_tech_sectors()
        self.write_objective(M, iteration=iteration)
        self.write_capacity_tables(M, iteration=iteration)
        # analyze the emissions to get the costs and flows
        e_costs, e_flows = self._gather_emission_costs_and_flows(M)
        self.emission_register = e_flows
        self.write_emissions(iteration=iteration)
        self.write_costs(M, emission_entries=e_costs, iteration=iteration)
        self.flow_register = self.calculate_flows(M)
        self.check_flow_balance(M)
        self.write_flow_tables(iteration=iteration)
        if results_with_duals:  # write the duals
            self.write_dual_variables(results_with_duals, iteration=iteration)
        # catch-all
        self.con.commit()
        self.con.execute('VACUUM')

    def write_mm_results(self, M: TemoaModel, iteration: int):
        """
        tailored writer function for Method of Morris which:
        (a) appends data (so scenario needs to be cleared elsewhere
        (b) requires an iteration number to separate results
        (c) only writes to MM required tables (obj, emissions right now)
        :param M: solved model
        :param iteration: an iteration index for scenario labeling
        :return:
        """
        if not self.tech_sectors:
            self._get_tech_sectors()
        self.write_objective(M, iteration=iteration)
        # analyze the emissions to get the costs and flows
        e_costs, e_flows = self._gather_emission_costs_and_flows(M)
        self.emission_register = e_flows
        self.write_emissions(iteration=iteration)
        self.con.commit()
        self.con.execute('VACUUM')

    def _get_tech_sectors(self):
        """pull the sector info and fill the mapping"""
        qry = 'SELECT tech, sector FROM Technology'
        data = self.con.execute(qry).fetchall()
        self.tech_sectors = dict(data)

    def clear_scenario(self):
        cur = self.con.cursor()
        for table in basic_output_tables:
            cur.execute(f'DELETE FROM {table} WHERE scenario = ?', (self.config.scenario,))
        for table in optional_output_tables:
            cur.execute(f'DROP TABLE IF EXISTS {table}')
        self.con.commit()
        self.clear_iterative_runs()

    def clear_iterative_runs(self):
        """
        clear runs that are iterative extensions to the scenario name
        Ex:  scenario = 'Red Monkey" ... will clear "Red Monkey-1, Red Monkey-2, Red Monkey-3, Red Monkey-4'
        :return: None
        """
        target = self.config.scenario + '-%'  # the dash followed by wildcard for anything after
        cur = self.con.cursor()
        for table in basic_output_tables:
            cur.execute(f'DELETE FROM {table} WHERE scenario like ?', (target,))
        self.con.commit()

    def write_objective(self, M: TemoaModel, iteration=None) -> None:
        """Write the value of all ACTIVE objectives to the DB"""
        objs: list[Objective] = list(M.component_data_objects(Objective))
        active_objs = [obj for obj in objs if obj.active]
        if len(active_objs) > 1:
            logger.warning(
                'Multiple active objectives found for scenario: %s.  All will be logged in db',
                self.config.scenario,
            )
        scenario_name = (
            self.config.scenario + f'-{iteration}'
            if iteration is not None
            else self.config.scenario
        )
        for obj in active_objs:
            obj_name, obj_value = obj.getname(fully_qualified=True), value(obj)
            qry = 'INSERT INTO OutputObjective VALUES (?, ?, ?)'
            data = (scenario_name, obj_name, obj_value)
            self.con.execute(qry, data)
            self.con.commit()

    def write_emissions(self, iteration=None) -> None:
        """Write the emission table to the DB"""
        if not self.tech_sectors:
            raise RuntimeError('tech sectors not available... code error')

        data = []
        scenario = (
            self.config.scenario + f'-{iteration}'
            if iteration is not None
            else self.config.scenario
        )
        for ei in self.emission_register:
            sector = self.tech_sectors[ei.t]
            val = self.emission_register[ei]
            if abs(val) < self.epsilon:
                continue
            entry = (scenario, ei.r, sector, ei.p, ei.e, ei.t, ei.v, val)
            data.append(entry)
        qry = f'INSERT INTO OutputEmission VALUES {_marks(8)}'
        self.con.executemany(qry, data)
        self.con.commit()

    def write_capacity_tables(self, M: TemoaModel, iteration: int | None = None) -> None:
        """Write the capacity tables to the DB"""
        if not self.tech_sectors:
            raise RuntimeError('tech sectors not available... code error')
        scenario = self.config.scenario
        if iteration is not None:
            scenario = scenario + f'-{iteration}'
        # Built Capacity
        data = []
        for r, t, v in M.V_NewCapacity:
            if v in M.time_optimize:
                val = value(M.V_NewCapacity[r, t, v])
                s = self.tech_sectors.get(t)
                if abs(val) < self.epsilon:
                    continue
                new_cap = (scenario, r, s, t, v, val)
                data.append(new_cap)
        qry = 'INSERT INTO OutputBuiltCapacity VALUES (?, ?, ?, ?, ?, ?)'
        self.con.executemany(qry, data)

        # NetCapacity
        data = []
        for r, p, t, v in M.V_Capacity:
            val = value(M.V_Capacity[r, p, t, v])
            if abs(val) < self.epsilon:
                continue
            s = self.tech_sectors.get(t)
            new_net_cap = (scenario, r, s, p, t, v, val)
            data.append(new_net_cap)
        qry = 'INSERT INTO OutputNetCapacity VALUES (?, ?, ?, ?, ?, ?, ?)'
        self.con.executemany(qry, data)

        # Retired Capacity
        data = []
        for r, p, t, v in M.V_RetiredCapacity:
            val = value(M.V_RetiredCapacity[r, p, t, v])
            if abs(val) < self.epsilon:
                continue
            s = self.tech_sectors.get(t)
            new_retired_cap = (scenario, r, s, p, t, v, val)
            data.append(new_retired_cap)
        qry = 'INSERT INTO OutputRetiredCapacity VALUES (?, ?, ?, ?, ?, ?, ?)'
        self.con.executemany(qry, data)

        self.con.commit()

    def write_flow_tables(self, iteration=None) -> None:
        """Write the flow tables"""
        if not self.tech_sectors:
            raise RuntimeError('tech sectors not available... code error')
        if not self.flow_register:
            raise RuntimeError('flow_register not available... code error')
        # sort the flows
        flows_by_type: dict[FlowType, list[tuple]] = defaultdict(list)
        scenario = (
            self.config.scenario + f'-{iteration}'
            if iteration is not None
            else self.config.scenario
        )
        for fi in self.flow_register:
            sector = self.tech_sectors.get(fi.t)
            for flow_type in self.flow_register[fi]:
                val = self.flow_register[fi][flow_type]
                if abs(val) < self.epsilon:
                    continue
                entry = (scenario, fi.r, sector, fi.p, fi.s, fi.d, fi.i, fi.t, fi.v, fi.o, val)
                flows_by_type[flow_type].append(entry)

        table_associations = {
            FlowType.OUT: 'OutputFlowOut',
            FlowType.IN: 'OutputFlowIn',
            FlowType.CURTAIL: 'OutputCurtailment',
            FlowType.FLEX: 'OutputCurtailment',
        }

        for flow_type, table_name in table_associations.items():
            qry = f'INSERT INTO {table_name} VALUES {_marks(11)}'
            self.con.executemany(qry, flows_by_type[flow_type])

        self.con.commit()

    def write_summary_flow(self, M: TemoaModel, iteration: int | None = None):
        """
        This is normally called from MGA (other?)
        iterative solves where capturing the annual summary of flow out is desired vs. flows by season, tod for
        single instances
        :param iteration: the number of the sequential iteration
        :param M: The solved model
        :return: None
        """
        if not self.tech_sectors:
            raise RuntimeError('tech sectors not available... code error')

        # must recalculate flows from the model
        self.flow_register = self.calculate_flows(M)
        if isinstance(iteration, int):
            scenario = self.config.scenario + f'-{iteration}'
        elif iteration is None:
            scenario = self.config.scenario
        else:
            raise ValueError(f'Illegal (non integer) value received for iteration: {iteration}')

        # iterate through all elements of the flow register, look for output flows only,
        # and gather the total by index (region, period, input_comm, tech, vintage, output_comm)
        # this is summing across season, tod
        output_flows = defaultdict(float)
        for fi in self.flow_register:
            sector = self.tech_sectors.get(fi.t)
            # get the output flow for this index, if it exists...
            flow_out_value = self.flow_register[fi].get(FlowType.OUT, None)
            if flow_out_value:
                idx = (scenario, fi.r, sector, fi.p, fi.i, fi.t, fi.v, fi.o)
                output_flows[idx] += flow_out_value

        # convert to entries, if the sum is non-negligible
        entries = []
        for idx, flow in output_flows.items():
            if abs(flow) < self.epsilon:
                continue
            entry = (*idx, flow)
            entries.append(entry)

        qry = f'INSERT INTO OutputFlowOutSummary VALUES {_marks(9)}'
        self.con.executemany(qry, entries)

        self.con.commit()

    def check_flow_balance(self, M: TemoaModel) -> bool:
        """An easy sanity check to ensure that the flow tables are balanced, except for storage"""
        flows = self.flow_register
        all_good = True
        deltas = defaultdict(float)
        for fi in flows:
            if fi.t in M.tech_storage:
                continue

            # some conveniences for the players...
            fin = flows[fi][FlowType.IN]
            fout = flows[fi][FlowType.OUT]
            fcurt = flows[fi][FlowType.CURTAIL]
            fflex = flows[fi][FlowType.FLEX]
            flost = flows[fi][FlowType.LOST]
            # some identifiers
            tech = fi.t
            var_tech = fi.t in M.tech_variable
            flex_tech = fi.t in M.tech_flex
            annual_tech = fi.t in M.tech_annual

            #  ----- flow balance equation -----
            deltas[fi] = fin - fout - flost - fflex
            # dev note:  in constraint, flex is taken out of flow_out, but in output processing,
            #            we are treating flow out as "net of flex" so this is not double-counting

            if (
                flows[fi][FlowType.IN] != 0 and abs(deltas[fi] / flows[fi][FlowType.IN]) > 0.02
            ):  # 2% of input is missing / surplus
                all_good = False
                logger.warning(
                    'Flow balance check failed for index: %s, delta: %0.2f', fi, deltas[fi]
                )
                logger.info(
                    'Tech: %s, Var: %s, Flex: %s, Annual: %s',
                    tech,
                    var_tech,
                    flex_tech,
                    annual_tech,
                )
                logger.info(
                    'IN: %0.6f, OUT: %0.6f, LOST: %0.6f, CURT: %0.6f, FLEX: %0.6f',
                    fin,
                    fout,
                    flost,
                    fcurt,
                    fflex,
                )
            elif flows[fi][FlowType.IN] == 0 and abs(deltas[fi]) > 0.02:
                all_good = False
                logger.warning(
                    'Flow balance check failed for index: %s, delta: %0.2f.  Flows happening with 0 input',
                    fi,
                    deltas[fi],
                )
        return all_good

    def calculate_flows(self, M: TemoaModel) -> dict[FI, dict[FlowType, float]]:
        """Gather all flows by Flow Index and Type"""

        res: dict[FI, dict[FlowType, float]] = defaultdict(lambda: defaultdict(float))

        # ---- NON-annual ----

        # Storage, which has a unique v_flow_in (non-storage techs do not have this variable)
        for key in M.V_FlowIn:
            fi = FI(*key)
            flow = value(M.V_FlowIn[fi])
            if abs(flow) < self.epsilon:
                continue
            res[fi][FlowType.IN] = flow
            res[fi][FlowType.LOST] = (1 - value(M.Efficiency[ritvo(fi)])) * flow

        # regular flows
        for key in M.V_FlowOut:
            fi = FI(*key)
            flow = value(M.V_FlowOut[fi])
            if abs(flow) < self.epsilon:
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
            if abs(val) < self.epsilon:
                continue
            res[fi][FlowType.CURTAIL] = val

        # flex techs.  This will subtract the flex from their output flow IOT make OUT the "net"
        for key in M.V_Flex:
            fi = FI(*key)
            flow = value(M.V_Flex[fi])
            if abs(flow) < self.epsilon:
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
                    if abs(flow) < self.epsilon:
                        continue
                    res[fi][FlowType.OUT] = flow
                    res[fi][FlowType.IN] = flow / value(M.Efficiency[ritvo(fi)])
                    res[fi][FlowType.LOST] = (1 - value(M.Efficiency[ritvo(fi)])) * res[fi][
                        FlowType.IN
                    ]

        # flex annual
        for r, p, i, t, v, o in M.V_FlexAnnual:
            for s in M.time_season:
                for d in M.time_of_day:
                    fi = FI(r, p, s, d, i, t, v, o)
                    flow = value(M.V_FlexAnnual[r, p, i, t, v, o]) * value(M.SegFrac[s, d])
                    if abs(flow) < self.epsilon:
                        continue
                    res[fi][FlowType.FLEX] = flow
                    res[fi][FlowType.OUT] -= flow

        return res

    @staticmethod
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

    def write_costs(self, M: TemoaModel, emission_entries=None, iteration=None):
        """
        Gather the cost data vars
        :param iteration: tag for iteration in scenario name
        :param emission_entries: cost dictionary for emissions
        :param M: the Temoa Model
        :return: dictionary of results of format variable name -> {idx: value}
        """

        # P_0 is usually the first optimization year, but if running myopic, we could assign it via
        # table entry.  Perhaps in future it is just always the first optimization year of the 1st iter.
        if self.config.scenario_mode == TemoaMode.MYOPIC:
            p_0 = M.MyopicBaseyear
        else:
            p_0 = min(M.time_optimize)
        # NOTE:  The end period in myopic mode is specific to the window / MyopicIndex
        #        the time_future set is specific to the window
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
            if abs(cap) < self.epsilon:
                continue
            loan_life = value(LLN[r, t, v])
            loan_rate = value(M.LoanRate[r, t, v])

            model_loan_cost, undiscounted_cost = self.loan_costs(
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
            if abs(cap) < self.epsilon:
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
            if abs(activity) < self.epsilon:
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
        if emission_entries:
            for k in emission_entries.keys():
                entries[k].update(emission_entries[k])
        # write to table
        # translate the entries into fodder for the query
        self._write_cost_rows(entries, iteration=iteration)
        self._write_cost_rows(exchange_costs.get_entries(), iteration=iteration)

    def _gather_emission_costs_and_flows(self, M: 'TemoaModel'):
        """Gather all emission flows and price them"""

        # UPDATE:  older versions brought forward had some accounting errors here for flex/curtailed emissions
        #          see the note on emissions in the Cost function in temoa_rules

        GDR = value(M.GlobalDiscountRate)
        MPL = M.ModelProcessLife
        if self.config.scenario_mode == TemoaMode.MYOPIC:
            p_0 = M.MyopicBaseyear
        else:
            p_0 = min(M.time_optimize)

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
            if abs(flows[ei]) < self.epsilon:
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

    def _write_cost_rows(self, entries, iteration=None):
        """Write the entries to the OutputCost table"""
        scenario_name = (
            self.config.scenario + f'-{iteration}'
            if iteration is not None
            else self.config.scenario
        )
        rows = [
            (
                scenario_name,
                r,
                p,
                t,
                v,
                entries[r, p, t, v].get(CostType.D_INVEST, 0),
                entries[r, p, t, v].get(CostType.D_FIXED, 0),
                entries[r, p, t, v].get(CostType.D_VARIABLE, 0),
                entries[r, p, t, v].get(CostType.D_EMISS, 0),
                entries[r, p, t, v].get(CostType.INVEST, 0),
                entries[r, p, t, v].get(CostType.FIXED, 0),
                entries[r, p, t, v].get(CostType.VARIABLE, 0),
                entries[r, p, t, v].get(CostType.EMISS, 0),
            )
            for (r, p, t, v) in entries
        ]
        # let's be kind and sort by something reasonable (r, v, t, p)
        rows.sort(key=lambda r: (r[1], r[4], r[3], r[2]))
        cur = self.con.cursor()
        qry = 'INSERT INTO OutputCost VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        cur.executemany(qry, rows)
        self.con.commit()

    def write_dual_variables(self, results: SolverResults, iteration=None):
        """Write the dual variables to the OutputCost table"""
        scenario_name = (
            self.config.scenario + f'-{iteration}'
            if iteration is not None
            else self.config.scenario
        )  # collect the values
        constraint_data = results['Solution'].Constraint.items()
        dual_data = [(scenario_name, t[0], t[1]['Dual']) for t in constraint_data]
        qry = 'INSERT INTO OutputDualVariable VALUES (?, ?, ?)'
        self.con.executemany(qry, dual_data)
        self.con.commit()

    def __del__(self):
        if self.con:
            self.con.close()

    def make_summary_flow_table(self):
        # make the additional output table, if needed...
        self.execute_script(flow_summary_file_loc)

    def execute_script(self, script_file: str | Path):
        """
        A utility to execute a sql script on the current db connection
        :return:
        """
        with open(script_file, 'r') as table_script:
            sql_commands = table_script.read()
        logger.debug('Executing sql from file: %s ', script_file)

        self.con.executescript(sql_commands)
        self.con.commit()
