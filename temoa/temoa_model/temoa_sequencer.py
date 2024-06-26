"""
The Temoa Sequencer's job is to sequence the actions needed to execute a scenario.  Each
scenario has a declared processing mode (regular, myopic, mga, etc.) and the Temoa Sequencer sets
up the necessary run(s) to accomplish that.  Several processing modes have requirements
for multiple runs, and the Temoa Sequencer may hand off to a mode-specific sequencer

Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  11/14/23

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
"""

import sqlite3
import sys
from logging import getLogger
from pathlib import Path

import pyomo.opt

from temoa.extensions.method_of_morris.morris_sequencer import MorrisSequencer
from temoa.extensions.modeling_to_generate_alternatives.mga_sequencer import MgaSequencer
from temoa.extensions.myopic.myopic_sequencer import MyopicSequencer
from temoa.extensions.single_vector_mga.sv_mga_sequencer import SvMgaSequencer
from temoa.temoa_model.hybrid_loader import HybridLoader
from temoa.temoa_model.model_checking.pricing_check import price_checker
from temoa.temoa_model.run_actions import (
    build_instance,
    solve_instance,
    handle_results,
    check_solve_status,
    check_python_version,
    check_database_version,
)
from temoa.temoa_model.temoa_config import TemoaConfig
from temoa.temoa_model.temoa_mode import TemoaMode
from temoa.temoa_model.temoa_model import TemoaModel
from temoa.version_information import (
    DB_MAJOR_VERSION,
    MIN_DB_MINOR_VERSION,
    MIN_PYTHON_MAJOR,
    MIN_PYTHON_MINOR,
)

logger = getLogger(__name__)


class TemoaSequencer:
    """A Sequencer instance to control all runs for a scenario based on the TemoaMode"""

    def __init__(
        self,
        config_file: str | Path,
        output_path: str | Path,
        mode_override: TemoaMode | None = None,
        silent: bool = False,
        **kwargs,
    ):
        """
        Create a new Sequencer
        :param config_file: Optional path to config file.  If not provided, it will be read
        from Command Line Args
        :param mode_override: Optional override to execution mode.  If not provided,
        it will be read from config file
        :param silent:  boolean to indicate whether to silence run-time feedback
        """
        self.config: TemoaConfig | None = None
        self.temoa_mode: TemoaMode

        self.config_file: Path = Path(config_file)
        # check it...
        if not self.config_file.is_file():
            logger.error(
                'Config file location passed %s does not point to a file', self.config_file
            )
            raise FileNotFoundError(f'Invalid config file: {self.config_file}')

        self.output_path: Path = Path(output_path)
        # check it...
        if not self.output_path.is_dir():
            logger.error('Output directory does not exist: %s', self.output_path)
            raise FileNotFoundError(f'Invalid output directory: {self.output_path}')

        self.temoa_mode: TemoaMode = TemoaMode.BUILD_ONLY  # placeholder, over-written in start()
        self.mode_override: TemoaMode = mode_override

        # for feedback to user
        self.silent = silent

        # for results catching for perfect_foresight, other modes / testing
        self.pf_results: pyomo.opt.SolverResults | None = None
        self.pf_solved_instance: TemoaModel | None = None

    def start(self) -> TemoaModel | None:
        """Start the processing of the scenario"""

        # ----- Run the "preliminaries"
        # Build a TemoaConfig
        self.config = TemoaConfig.build_config(
            config_file=self.config_file, output_path=self.output_path, silent=self.silent
        )

        # Run some checks...
        good = True
        good &= check_python_version(MIN_PYTHON_MAJOR, MIN_PYTHON_MINOR)
        good &= check_database_version(
            self.config, db_major_reqd=DB_MAJOR_VERSION, min_db_minor=MIN_DB_MINOR_VERSION
        )
        if not good:
            logger.error('Failed pre-run checks...  See log file for details')
            sys.exit(-1)

        # Distill the TemoaMode
        if self.mode_override and self.mode_override != self.config.scenario_mode:
            # capture and log the override...
            self.temoa_mode = self.mode_override
            if self.config:  # register the override in the config
                self.config.scenario_mode = self.mode_override
            logger.info('Temoa Mode overridden to be:  %s', self.temoa_mode)
        else:
            self.temoa_mode = self.config.scenario_mode
        # check it...
        if not isinstance(self.temoa_mode, TemoaMode):
            logger.error(
                'Temoa Mode not set properly.  Override: %s, Config File: %s',
                self.mode_override,
                self.config.scenario_mode,
            )
            raise RuntimeError('Problem with mode selection, see log file.')

        # Get user confirmation if not silent
        if not self.silent:
            try:
                print(self.config.__repr__())
                print('\nPlease press enter to continue or Ctrl+C to quit.\n')
                input()  # Give the user a chance to confirm input
            except KeyboardInterrupt:
                logger.warning('User aborted from confirmation page.  Exiting')
                print('\n\nUser requested quit.  Exiting Temoa ...\n')
                sys.exit()

        # ---- Select execution path based on mode ----
        match self.temoa_mode:
            case TemoaMode.BUILD_ONLY:
                # override the "extras"
                if self.config.source_trace:
                    self.config.source_trace = False
                    logger.info('Source trace disabled for BUILD_ONLY')
                if self.config.plot_commodity_network:
                    self.config.plot_commodity_network = False
                    logger.info('Plot commodity network disabled for BUILD_ONLY')
                if self.config.price_check:
                    logger.info('Price check disabled for BUILD_ONLY')
                con = sqlite3.connect(self.config.input_database)
                hybrid_loader = HybridLoader(db_connection=con, config=self.config)
                data_portal = hybrid_loader.load_data_portal(myopic_index=None)
                instance = build_instance(data_portal, silent=self.config.silent)
                con.close()
                return instance

            case TemoaMode.CHECK:
                con = sqlite3.connect(self.config.input_database)
                if self.config.source_trace is False:
                    logger.info('Source trace automatic for CHECK')
                    self.config.source_trace = True
                hybrid_loader = HybridLoader(db_connection=con, config=self.config)
                data_portal = hybrid_loader.load_data_portal(myopic_index=None)
                instance = build_instance(
                    data_portal,
                    silent=self.config.silent,
                    keep_lp_file=self.config.save_lp_file,
                    lp_path=self.config.output_path,
                )
                # disregard what the config says about price_check and source_trace and just do it...
                if self.config.price_check is False:
                    logger.info('Price check of model is automatic with CHECK')
                good_prices = price_checker(instance)
                if not good_prices and not self.config.silent:
                    print('\nWarning:  Cost anomalies discovered.  Check log file for details.')
                con.close()

            case TemoaMode.PERFECT_FORESIGHT:
                con = sqlite3.connect(self.config.input_database)
                hybrid_loader = HybridLoader(db_connection=con, config=self.config)
                data_portal = hybrid_loader.load_data_portal(myopic_index=None)
                instance = build_instance(
                    data_portal,
                    silent=self.config.silent,
                    keep_lp_file=self.config.save_lp_file,
                    lp_path=self.config.output_path,
                )
                if self.config.price_check:
                    good_prices = price_checker(instance)
                    if not good_prices and not self.config.silent:
                        print('\nWarning:  Cost anomalies discovered.  Check log file for details.')
                suffixes = (
                    [
                        'dual',
                    ]
                    if self.config.save_duals
                    else None
                )
                self.pf_solved_instance, self.pf_results = solve_instance(
                    instance,
                    self.config.solver_name,
                    silent=self.config.silent,
                    solver_suffixes=suffixes,
                )
                good_solve, msg = check_solve_status(self.pf_results)
                if not good_solve:
                    logger.error('The solve result is reported as %s.  Aborting', msg)
                    logger.error(
                        'This may be the result of the output messaging of the chosen solver'
                        'If this is deemed an acceptable status, adjustment may be needed to the '
                        'function check_solve_status in run_actions.py'
                    )
                    sys.exit(-1)
                handle_results(self.pf_solved_instance, self.pf_results, self.config)

                con.close()

            case TemoaMode.MYOPIC:
                # create a myopic sequencer and shift control to it
                myopic_sequencer = MyopicSequencer(config=self.config)
                myopic_sequencer.start()

            case TemoaMode.MGA:
                mga_sequencer = MgaSequencer(config=self.config)
                mga_sequencer.start()

            case TemoaMode.SVMGA:
                sv_mga_sequencer = SvMgaSequencer(config=self.config)
                sv_mga_sequencer.start()

            case TemoaMode.METHOD_OF_MORRIS:
                mm_sequencer = MorrisSequencer(config=self.config)
                mm_sequencer.start()

            case _:
                raise NotImplementedError('not yet built')
