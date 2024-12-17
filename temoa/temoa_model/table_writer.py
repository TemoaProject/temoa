"""
tool for writing outputs to database tables
"""
import sqlite3
import sys
from collections import defaultdict
from collections.abc import Iterable
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from pyomo.opt import SolverResults

from definitions import PROJECT_ROOT
from temoa.extensions.monte_carlo.mc_run import ChangeRecord
from temoa.temoa_model.data_brick import DataBrick
from temoa.temoa_model.exchange_tech_cost_ledger import CostType
from temoa.temoa_model.table_data_puller import (
    poll_capacity_results,
    poll_flow_results,
    FI,
    FlowType,
    EI,
    _marks,
    CapData,
    poll_objective,
    poll_cost_results,
    poll_emissions,
)
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
optional_output_tables = ['OutputFlowOutSummary', 'OutputMCDelta']

flow_summary_file_loc = Path(
    PROJECT_ROOT, 'temoa/extensions/modeling_to_generate_alternatives/make_flow_summary_table.sql'
)
mc_tweaks_file_loc = Path(PROJECT_ROOT, 'temoa/extensions/monte_carlo/make_deltas_table.sql')


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
            self._set_tech_sectors()
        self.write_objective(M, iteration=iteration)
        self.write_capacity_tables(M, iteration=iteration)
        # analyze the emissions to get the costs and flows
        if self.config.scenario_mode == TemoaMode.MYOPIC:
            p_0 = M.MyopicBaseyear
        else:
            p_0 = None  # min year will be used in poll
        e_costs, e_flows = poll_emissions(M=M, p_0=p_0)
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
            self._set_tech_sectors()
        self.write_objective(M, iteration=iteration)
        # analyze the emissions to get the costs and flows
        e_costs, e_flows = poll_emissions(M=M)
        self.emission_register = e_flows
        self.write_emissions(iteration=iteration)
        self.con.commit()
        self.con.execute('VACUUM')

    def write_mc_results(self, brick: DataBrick, iteration: int):
        """
        tailored write function to capture appropriate monte carlo results
        :param M: solve model
        :param iteration: iteration number
        :return:
        """
        if not self.tech_sectors:
            self._set_tech_sectors()
        # analyze the emissions to get the costs and flows
        e_costs, e_flows = brick.emission_cost_data, brick.emission_flows
        self.emission_register = e_flows
        self.write_emissions(iteration=iteration)

        # the rest can be directly inserted from the data_brick
        self._insert_capacity_results(brick.capacity_data, iteration=iteration)
        self._insert_summary_flow_results(flow_data=brick.flow_data, iteration=iteration)
        self._insert_cost_results(
            regular_entries=brick.cost_data,
            exchange_entries=brick.exchange_cost_data,
            emission_entries=e_costs,
            iteration=iteration,
        )
        self._insert_objective_results(brick.obj_data, iteration=iteration)
        self.con.commit()
        self.con.execute('VACUUM')

    def _set_tech_sectors(self):
        """pull the sector info and fill the mapping"""
        qry = 'SELECT tech, sector FROM Technology'
        data = self.con.execute(qry).fetchall()
        self.tech_sectors = dict(data)

    def clear_scenario(self):
        cur = self.con.cursor()
        for table in basic_output_tables:
            cur.execute(f'DELETE FROM {table} WHERE scenario = ?', (self.config.scenario,))
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
        for table in optional_output_tables:
            try:
                cur.execute(f'DELETE FROM {table} WHERE scenario like ?', (target,))
            except sqlite3.OperationalError:
                pass
        self.con.commit()

    def write_objective(self, M: TemoaModel, iteration=None) -> None:
        """Write the value of all ACTIVE objectives to the DB"""
        obj_vals = poll_objective(M=M)
        self._insert_objective_results(obj_vals, iteration=iteration)

    def _insert_objective_results(self, obj_vals: list, iteration: int) -> None:
        scenario_name = (
            self.config.scenario + f'-{iteration}'
            if iteration is not None
            else self.config.scenario
        )
        for obj_name, obj_value in obj_vals:
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

    def _insert_capacity_results(self, cap_data: CapData, iteration: int | None) -> None:
        if not self.tech_sectors:
            raise RuntimeError('tech sectors not available... code error')
        scenario = self.config.scenario
        if iteration is not None:
            scenario = scenario + f'-{iteration}'
        # Built Capacity
        data = []
        for r, t, v, val in cap_data.built:
            s = self.tech_sectors.get(t)
            new_cap = (scenario, r, s, t, v, val)
            data.append(new_cap)
        qry = 'INSERT INTO OutputBuiltCapacity VALUES (?, ?, ?, ?, ?, ?)'
        self.con.executemany(qry, data)

        # NetCapacity
        data = []
        for r, p, t, v, val in cap_data.net:
            s = self.tech_sectors.get(t)
            new_net_cap = (scenario, r, s, p, t, v, val)
            data.append(new_net_cap)
        qry = 'INSERT INTO OutputNetCapacity VALUES (?, ?, ?, ?, ?, ?, ?)'
        self.con.executemany(qry, data)

        # Retired Capacity
        data = []
        for r, p, t, v, val in cap_data.retired:
            s = self.tech_sectors.get(t)
            new_retired_cap = (scenario, r, s, p, t, v, val)
            data.append(new_retired_cap)
        qry = 'INSERT INTO OutputRetiredCapacity VALUES (?, ?, ?, ?, ?, ?, ?)'
        self.con.executemany(qry, data)
        self.con.commit()

    def write_capacity_tables(self, M: TemoaModel, iteration: int | None = None) -> None:
        """Write the capacity tables to the DB"""
        cap_data = poll_capacity_results(M=M)
        self._insert_capacity_results(cap_data=cap_data, iteration=iteration)

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
        flow_data = self.calculate_flows(M=M)
        self._insert_summary_flow_results(flow_data=flow_data, iteration=iteration)

    def _insert_summary_flow_results(self, flow_data: dict, iteration: int | None) -> None:
        if not self.tech_sectors:
            raise RuntimeError('tech sectors not available... code error')

        self.flow_register = flow_data
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

    # @staticmethod
    # def poll_summary_flow_results( M:TemoaModel) -> dict:
    #     flow_data = self.calculate_flows(M)

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
        return poll_flow_results(M, self.epsilon)

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

        entries, exchange_entries = poll_cost_results(M, p_0, self.epsilon)

        # write to table
        self._insert_cost_results(entries, exchange_entries, emission_entries, iteration)

    def _insert_cost_results(self, regular_entries, exchange_entries, emission_entries, iteration):
        # add the emission costs to the same row data, if provided
        if emission_entries:
            for k in emission_entries.keys():
                regular_entries[k].update(emission_entries[k])
        self._write_cost_rows(regular_entries, iteration=iteration)
        self._write_cost_rows(exchange_entries, iteration=iteration)

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

    # MONTE CARLO stuff

    def write_tweaks(self, iteration: int, change_records: Iterable[ChangeRecord]):
        scenario = f'{self.config.scenario}-{iteration}'
        records = []
        for change_record in change_records:
            element = (
                scenario,
                iteration,
                change_record.param_name,
                str(change_record.param_index).replace("'", ''),
                change_record.old_value,
                change_record.new_value,
            )
            records.append(element)
        qry = 'INSERT INTO OutputMCDelta VALUES (?, ?, ?, ?, ?, ?)'
        self.con.executemany(qry, records)
        self.con.commit()

    def __del__(self):
        if self.con:
            self.con.close()

    def make_summary_flow_table(self):
        # make the additional output table, if needed...
        self.execute_script(flow_summary_file_loc)

    def make_mc_tweaks_table(self):
        # make the table for monte carlo tweaks, if needed...
        self.execute_script(mc_tweaks_file_loc)

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
