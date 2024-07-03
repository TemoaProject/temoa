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
Created on:  6/25/24

Single-Vector MGA is a 2-stage solve process to look at an alternative solution with a relaxed cost
The "single vector" distinguishes it from "regular" MGA in that this only uses 1 extra solve to look
in one particular vector direction, characterized by keywords from an associated config file
"""
import logging
import sqlite3
import sys
from collections.abc import Iterable

from pyomo.core import value, Constraint, Expression, Objective
from pyomo.dataportal import DataPortal
from pyomo.opt import check_optimal_termination

from temoa.extensions.single_vector_mga.output_summary import summarize
from temoa.temoa_model.hybrid_loader import HybridLoader
from temoa.temoa_model.model_checking.pricing_check import price_checker
from temoa.temoa_model.run_actions import build_instance, solve_instance, handle_results, save_lp
from temoa.temoa_model.table_writer import TableWriter
from temoa.temoa_model.temoa_config import TemoaConfig
from temoa.temoa_model.temoa_model import TemoaModel
from temoa.temoa_model.temoa_rules import TotalCost_rule

logger = logging.getLogger(__name__)


class SvMgaSequencer:
    def __init__(self, config: TemoaConfig):
        # PRELIMINARIES...
        # let's start with the assumption that input db = output db...  this may change?
        if not config.input_database == config.output_database:
            raise NotImplementedError('MGA assumes input and output databases are same')
        self.con = sqlite3.connect(config.input_database)
        if not config.source_trace:
            logger.warning(
                'Performing SV_MGA runs without Source Tracing.  '
                'Recommend selecting source trace in config file.'
            )
        # TODO:  Check Excel, LP files, Duals are achievable in outputs for SV_MGA
        self.config = config

        # output handling
        self.writer = TableWriter(self.config)
        self.writer.clear_scenario()
        self.verbose = False  # for troubleshooting

        self.cost_epsilon = config.svmga_inputs.get('cost_epsilon', 0.05)
        logger.info('Set SVMGA cost (relaxation) epsilon to: %0.3f', self.cost_epsilon)

        logger.info('Initialized SVMGA sequencer.')

    def start(self):
        """Run the sequencer...

        This should look pretty similar to 2 PF runs, back-to-back

        ==== basic sequence ====
        1. Load the model data, which may involve filtering it down if source tracing
        2. Solve the base model
        3. Make the cost constraint from the OBJ value
        4. Construct an alternate OBJ statement from the config data
        5. Re-solve and report

        """

        # 1. Load data
        hybrid_loader = HybridLoader(db_connection=self.con, config=self.config)
        data_portal: DataPortal = hybrid_loader.load_data_portal(myopic_index=None)
        lp_path = self.config.output_path / 'base_model'
        instance: TemoaModel = build_instance(
            loaded_portal=data_portal,
            model_name=self.config.scenario,
            silent=self.config.silent,
            keep_lp_file=self.config.save_lp_file,
            lp_path=lp_path,
        )
        if self.config.price_check:
            good_prices = price_checker(instance)
            if not good_prices and not self.config.silent:
                print('Warning:  Cost anomalies discovered.  Check log file for details.')

        # 2. Base solve
        #   ============ First Solve ============
        suffixes = (
            [
                'dual',
            ]
            if self.config.save_duals
            else None
        )
        instance, res = solve_instance(
            instance=instance,
            solver_name=self.config.solver_name,
            silent=self.config.silent,
            solver_suffixes=suffixes,
        )
        status = res.solver.termination_condition
        logger.debug('Termination condition: %s', status.name)
        if not check_optimal_termination(res):
            logger.error('The baseline SVMGA solve failed.  Terminating run.')
            raise RuntimeError('Baseline SVMGA solve failed.  Terminating run.')

        # record the 0-solve in all tables
        handle_results(instance, results=res, config=self.config, append=False, iteration=0)

        # 3a. Capture cost and make it a constraint
        tot_cost = value(instance.TotalCost)
        logger.info('Completed initial solve with total cost:  %0.2f', tot_cost)
        logger.info('Relaxing cost by fraction:  %0.3f', self.cost_epsilon)
        # get hook on the expression generator for total cost...
        cost_expression = TotalCost_rule(instance)
        instance.cost_cap = Constraint(expr=cost_expression <= (1 + self.cost_epsilon) * tot_cost)

        # 3b. remove the old objective
        # instance.TotalCost.deactivate()
        instance.del_component(instance.TotalCost)

        # 4.  Reconstruct the OBJ function...
        emission_labels = self.config.svmga_inputs.get('emission_labels', [])
        capacity_labels = self.config.svmga_inputs.get('capacity_labels', [])
        activity_labels = self.config.svmga_inputs.get('activity_labels', [])
        new_obj = SvMgaSequencer.construct_obj(
            instance, emission_labels, capacity_labels, activity_labels
        )

        # check for an empty objective
        if isinstance(new_obj, int):  # no variables found
            msg = 'Construction of the alternative OBJ in SVMGA failed to locate any variables.  Exiting'
            logger.error(msg)
            print(msg)
            sys.exit(1)

        instance.svmga_obj = Objective(expr=new_obj)
        # save it, if requested...
        if self.config.save_lp_file:
            lp_path = self.config.output_path / 'option_model'
            save_lp(instance, lp_path)

        # 5. Re-solve and report
        suffixes = (
            [
                'dual',
            ]
            if self.config.save_duals
            else None
        )
        instance, res = solve_instance(
            instance=instance,
            solver_name=self.config.solver_name,
            silent=self.config.silent,
            solver_suffixes=suffixes,
        )
        status = res.solver.termination_condition
        logger.debug('Termination condition: %s', status.name)
        if not check_optimal_termination(res):
            logger.error('The baseline SVMGA solve failed.  Terminating run.')
            raise RuntimeError('Baseline SVMGA solve failed.  Terminating run.')
        logger.info(
            'Completed secondary solve with total cost:  %0.2f', value(TotalCost_rule(instance))
        )

        # record the 1-solve in all tables
        handle_results(instance, results=res, config=self.config, append=True, iteration=1)

        if not self.config.silent:
            summarize(self.config, tot_cost, value(TotalCost_rule(instance)))

    @staticmethod
    def flow_idxs_from_eac_idx(M: TemoaModel, reitvo: tuple) -> tuple[list[tuple], ...]:
        """
        From the emission index, expand to create the full list of possible flow indices
        for regular and annual flows.  These may/may not be valid and must be screened
        for membership later
        """
        r, _, i, t, v, o = reitvo
        psd_set = [(p, s, d) for p in M.time_optimize for s in M.time_season for d in M.time_of_day]
        flow_idxs = [(r, *psd, i, t, v, o) for psd in psd_set]
        annual_flow_idxs = [(r, p, i, t, v, o) for p in M.time_optimize]

        return flow_idxs, annual_flow_idxs

    @staticmethod
    def construct_obj(
        M: TemoaModel,
        emission_labels: Iterable[str],
        capacity_labels: Iterable[str],
        activity_labels: Iterable[str],
        verbose=True,
    ) -> Expression | int:
        """
        Construct an alternative OBJ statement from the config data

        Specifically, locate the labels passed in within the related variables and kluge
        together an objective to be minimized from them.
        :param verbose: If True, report to console during construction...
        :param M: The basis model to search
        :param emission_labels: labels of emission commodities
        :param capacity_labels: labels of (capacitated) techs
        :param activity_labels: labels of techs
        :return: a suitable pyomo expression
        """
        # iterate through the collections
        expr = 0
        # run a simple check to produce warning if multiple categories are enabled...
        categories_used = 0
        if emission_labels:
            categories_used += 1
        if capacity_labels:
            categories_used += 1
        if activity_labels:
            categories_used += 1
        if categories_used > 1:
            msg = (
                'Warning:  Using labels in multiple categories during SVMGA may lead to odd results.\n'
                'The catagories are not specifically designed to work together, but rather add flexibility.\n'
                'The new OBJ function will be an *unweighted* sum of everything found, so outputs in \n'
                'differing categories with vastly different scale may have odd interactions.'
            )

            logger.warning(msg)
            print(msg)

        # handle emissions...
        for label in emission_labels:
            idxs = [idx for idx in M.EmissionActivity if idx[1] == label]
            logger.debug('Located %d items for emission label: %s', len(idxs), label)
            for idx in idxs:
                # for each indexed item in EmissionActivity, we need to search both the regular
                # flows and the annual flows.  And, we need to sum across the "expanded" index
                # for both which includes period, season, tod or just period respectively
                expanded_idxs, expanded_annual_idxs = SvMgaSequencer.flow_idxs_from_eac_idx(M, idx)
                element = sum(
                    M.V_FlowOut[flow_idx] * M.EmissionActivity[idx]
                    for flow_idx in expanded_idxs
                    if flow_idx in M.V_FlowOut
                )
                expr += element
                annual_element = sum(
                    M.V_FlowOutAnnual[annual_flow_idx] * M.EmissionActivity[idx]
                    for annual_flow_idx in expanded_annual_idxs
                    if annual_flow_idx in M.V_FlowOutAnnual
                )
                expr += annual_element

        # handle activity...
        for label in activity_labels:
            idxs = [idx for idx in M.V_FlowOut if idx[5] == label]
            logger.debug('Located %d items for activity label: %s', len(idxs), label)
            expr += sum(M.V_FlowOut[idx] for idx in idxs)

        # handle capacity...
        for label in capacity_labels:
            idxs = [idx for idx in M.V_Capacity if idx[2] == label]
            logger.debug('Located %d items for capacity label: %s', len(idxs), label)
            expr += sum(M.V_Capacity[idx] for idx in idxs)

        return expr
