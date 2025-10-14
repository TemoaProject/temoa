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

This code is modified from original work on Method of Morris framework
by Hadi Eshragi.  Original morris.py file can be located in the energysystem
branch

Modified/Refactored by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  5/30/24

An event sequencer to control the flow of a Method of Morris calculation.  This code uses multiprocessing via
the joblib library

"""

import csv
import logging
import multiprocessing
import sqlite3
import sys
import tomllib
from logging.handlers import QueueListener
from pathlib import Path

from joblib import Parallel, delayed
from numpy import array
from SALib.analyze import morris
from SALib.sample.morris import sample
from SALib.util import compute_groups_matrix, read_param_file

from definitions import PROJECT_ROOT, get_OUTPUT_PATH
from temoa._internal.table_writer import TableWriter
from temoa.core.config import TemoaConfig
from temoa.data_io.hybrid_loader import HybridLoader
from temoa.extensions.method_of_morris.morris_evaluate import evaluate

logger = logging.getLogger(__name__)

solver_options_file = Path(
    PROJECT_ROOT, 'temoa/extensions/method_of_morris/morris_solver_options.toml'
)


class MorrisSequencer:
    def __init__(self, config: TemoaConfig):
        self.config = config
        # PRELIMINARIES...
        # let's start with the assumption that input db = output db...  this may change?
        if not config.input_database == config.output_database:
            raise NotImplementedError('MM assumes input and output databases are same')
        self.con = sqlite3.connect(config.input_database)

        if config.save_lp_file:
            logger.info('Saving LP file is disabled during Morris runs.')
            config.save_lp_file = False
        if config.save_duals:
            logger.info('Saving duals is disabled during Morris runs.')
            config.save_duals = False
        if config.save_excel:
            logger.info('Saving excel is disabled during Morris runs.')
            config.save_excel = False
        if config.price_check:
            logger.warning(
                'Price check is disabled during Morris runs.  If you wish to check costs, run "CHECK" on model before MM'
            )
            config.price_check = False
        self.config = config

        # read in the options
        try:
            with open(solver_options_file, 'rb') as f:
                all_options = tomllib.load(f)
            s_options = all_options.get(self.config.solver_name, {})
            logger.info('Using solver options: %s', s_options)

        except FileNotFoundError:
            logger.warning('Unable to find solver options toml file.  Using default options.')
            s_options = {}

        # output handling
        self.verbose = False  # for troubleshooting
        self.mm_output_folder = get_OUTPUT_PATH() / 'MM_outputs'
        self.mm_output_folder.mkdir(exist_ok=True)
        self.param_file: Path = self.mm_output_folder / 'params.csv'

        # MM Options
        # the amount to perturb the marked params
        pert = config.morris_inputs.get('perturbation')
        if pert:
            self.mm_perturbation = pert
            logger.info('Morris perturbation: %0.2f', self.mm_perturbation)
        else:
            self.mm_perturbation = 0.10
            logger.warning(
                'No value received for perturbation, using default: %0.2f', self.mm_perturbation
            )

        levels = config.morris_inputs.get('levels')
        if levels:
            self.num_levels = levels
            logger.info('Morris levels: %d', self.num_levels)
        else:
            self.num_levels = (
                8  # the number of levels to divide the param range into (must be even number)
            )
            logger.warning('No value received for levels, using default: %d', self.num_levels)

        traj = config.morris_inputs.get('trajectories')
        if traj:
            self.trajectories = traj
            logger.info('Morris trajectories: %d', self.trajectories)
        else:
            self.trajectories = 4  # number of morris trajectories to generate
            logger.warning(
                'No value received for trajectories, using default: %d', self.trajectories
            )
        # Note:  Problem size (in general) is (Groups + 1) * trajectories see the SALib Dox (which aren't super)

        seed = config.morris_inputs.get('seed')
        self.seed = seed if seed else None
        logger.info('Morris Seed (None indicates system generated): %s', self.seed)

        self.conf_level = 0.95  # confidence level for mu_star analysis

        self.num_cores = config.morris_inputs.get('cores', 0)
        if self.num_cores == 0:
            self.num_cores = multiprocessing.cpu_count()
        logger.info('Morris number of cores: %d', self.num_cores)
        logger.info('Initialized Morris Sequencer')
        logger.info(
            'Currently, MM only logs ERROR level messages during model build, which is done repeatedly.'
            '  If there are issues building the model, run Temoa in CHECK separately to get more detail on the model.'
        )

    def start(self):
        """
        run the sequence of steps to do a MM analysis
        0.  clear any prior results with this scenario name.  this sequencer appends the DB, so start fresh
        1.  gather the parameters from items marked in the DB
        2.  build a data portal as a basis
        3.  use SALib to construct the sample
        4.  set up logging to cover the multiprocessing phase
        5.  run the evaluation of all instances in the mm_samples
        6.  use SALib to analyze the outputs
        :return:
        """
        # 0.  clear the scenario
        tw = TableWriter(config=self.config)
        tw.clear_scenario()

        # 1.  Gather param info from the DB and construct the param file, which will be basis of the 'problem'
        param_names = self.gather_parameters()

        # 2.  Use the loader to get raw access to the model's data (dictionary)
        loader = HybridLoader(db_connection=self.con, config=self.config)
        loader.load_data_portal()
        data = loader.data

        # 3.  Construct the MM Sample
        problem = read_param_file(str(self.param_file))
        if self.verbose:
            print(problem)
        mm_samples = sample(
            problem,
            N=self.trajectories,
            num_levels=self.num_levels,
            optimal_trajectories=False,
            local_optimization=False,
            seed=self.seed,
        )
        # 4.  Set up logging for workers
        m = multiprocessing.Manager()
        log_queue = m.Queue()  # Queue()

        log_listener = QueueListener(log_queue, *logging.root.handlers)
        log_level = logger.getEffectiveLevel()
        log_listener.start()

        # 5.  Run the processing:
        if not self.config.silent:
            msg = f'Starting {len(mm_samples)} MM runs on {self.num_cores} cores.\n'
            sys.stdout.write(msg)
            sys.stdout.write('=' * (len(msg) - 1) + '\n')
            sys.stdout.flush()
        morris_results = Parallel(n_jobs=self.num_cores)(
            delayed(evaluate)(
                param_names, mm_samples[i, :], data, i, self.config, log_queue, log_level
            )
            for i in range(0, len(mm_samples))
        )
        log_listener.stop()

        # 6.  Process results
        cost_mu_star = self.process_results(problem, mm_samples, morris_results)

        # 7.  Return the cost objective Mu_Star for testing purposes...
        return cost_mu_star

    def process_results(self, problem, mm_samples, morris_results):
        """
        Process the results of the runs on the mm_samples
        :param problem: the problem structure
        :param mm_samples: the n samples used for the runs
        :param morris_results: n * 2 array of results for the 2 objectives tracked
        :return:
        """
        morris_objectives = array(morris_results)
        analysis = {}
        analysis['cost'] = morris.analyze(
            problem,
            mm_samples,
            morris_objectives[:, 0],
            conf_level=self.conf_level,
            print_to_console=False,
            num_levels=self.num_levels,
            num_resamples=1000,
            seed=self.seed + 1 if self.seed else None,
        )

        analysis['co2'] = morris.analyze(
            problem,
            mm_samples,
            morris_objectives[:, 1],
            conf_level=self.conf_level,
            print_to_console=False,
            num_levels=self.num_levels,
            num_resamples=1000,
            seed=self.seed + 2 if self.seed else None,
        )
        groups, unique_group_names = compute_groups_matrix(problem['groups'])
        number_of_groups = len(unique_group_names)
        mu_star_conf_label = f'Mu_Star_Conf[{self.conf_level}]'
        if not self.config.silent:
            for category in analysis.keys():
                print(f'\nAnalysis of {category}:')
                print(
                    '{0:<30} {1:>10} {2:>10} {3:>20} {4:>10}'.format(
                        'Parameter', 'Mu_Star', 'Mu', mu_star_conf_label, 'Sigma'
                    )
                )
                for j in list(range(number_of_groups)):
                    print(
                        '{0:30} {1:10.3f} {2:10.3f} {3:20.3f} {4:10.3f}'.format(
                            analysis[category]['names'][j],
                            analysis[category]['mu_star'][j],
                            analysis[category]['mu'][j],
                            analysis[category]['mu_star_conf'][j],
                            analysis[category]['sigma'][j],
                        )
                    )

        header = ('param', 'mu', 'mu_star', mu_star_conf_label, 'sigma')
        for category in analysis.keys():
            f_name = f'{category}_analysis.csv'
            output_file_path = self.mm_output_folder / f_name
            with open(output_file_path, 'w') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(header)
                for j in list(range(number_of_groups)):
                    row = (
                        analysis[category]['names'][j],
                        analysis[category]['mu'][j],
                        analysis[category]['mu_star'][j],
                        analysis[category]['mu_star_conf'][j],
                        analysis[category]['sigma'][j],
                    )
                    writer.writerow(row)
        return analysis['cost']

    def gather_parameters(self):
        """
        Scan the annotated DB tables for marked parameters and capture them
        in the parameters file.  Also capture the names in the param_info data
        structure for use in pulling data
        """

        param_names = {}
        cur = self.con.cursor()
        with open(self.param_file, 'w') as f:
            v_idx = 4  # index of variable to perturb
            raw = cur.execute(
                'SELECT region, period, tech, vintage, cost, MMAnalysis FROM CostVariable WHERE MMAnalysis IS NOT NULL'
            ).fetchall()
            g1 = len(raw)
            for i in range(0, len(raw)):
                param_names[i] = [
                    'CostVariable',
                    *raw[i][:4],
                    'cost_variable',
                ]
                iter = f'x{i}'
                low = str(raw[i][v_idx] * (1 - self.mm_perturbation))
                high = str(raw[i][v_idx] * (1 + self.mm_perturbation))
                mm_name = raw[i][-1]

                row = ','.join((iter, low, high, mm_name))
                f.write(row + '\n')

            v_idx = 3
            raw = cur.execute(
                'SELECT region, tech, vintage, cost, MMAnalysis FROM CostInvest WHERE MMAnalysis IS NOT NULL'
            ).fetchall()
            g2 = len(raw)
            for i in range(0, len(raw)):
                param_names[i + g1] = ['CostInvest', *raw[i][:3], 'cost_invest']

                iter = f'x{i + g1}'
                low = str(raw[i][v_idx] * (1 - self.mm_perturbation))
                high = str(raw[i][v_idx] * (1 + self.mm_perturbation))
                mm_name = raw[i][-1]

                row = ','.join((iter, low, high, mm_name))
                f.write(row + '\n')

            v_idx = 5
            raw = cur.execute(
                'SELECT DISTINCT region, input_comm, tech, vintage, output_comm, efficiency, '
                'MMAnalysis FROM Efficiency WHERE MMAnalysis IS NOT NULL'
            ).fetchall()

            g3 = len(raw)
            for i in range(0, len(raw)):
                param_names[i + g1 + g2] = [
                    'Efficiency',
                    *raw[i][:5],
                    'efficiency',
                ]

                iter = f'x{i + g1 + g2}'
                low = str(raw[i][v_idx] * (1 - self.mm_perturbation))
                high = str(raw[i][v_idx] * (1 + self.mm_perturbation))
                mm_name = raw[i][-1]

                row = ','.join((iter, low, high, mm_name))
                f.write(row + '\n')
        # check for empty (no marked params)
        if sum((g1, g2, g3)) == 0:
            logger.error('No parameters marked for MM analysis')
            raise ValueError('No parameters marked for MM analysis')

        return param_names

    def __del__(self):
        self.con.close()
