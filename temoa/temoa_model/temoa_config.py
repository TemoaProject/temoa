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
in LICENSE.txt.  Users expanding this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.
"""

import tomllib
from logging import getLogger
from pathlib import Path
from sys import stderr as SE

from temoa.temoa_model.temoa_mode import TemoaMode

logger = getLogger(__name__)


class TemoaConfig:
    """
    The overall configuration for a Temoa Scenario
    """

    def __init__(
        self,
        scenario: str,
        scenario_mode: TemoaMode | str,
        input_database: Path,
        output_database: Path,
        output_path: Path,
        solver_name: str,
        neos: bool = False,
        save_excel: bool = False,
        save_duals: bool = False,
        save_lp_file: bool = False,
        MGA: dict | None = None,
        SVMGA: dict | None = None,
        myopic: dict | None = None,
        morris: dict | None = None,
        config_file: Path | None = None,
        silent: bool = False,
        stream_output: bool = False,
        price_check: bool = True,
        source_trace: bool = False,
        plot_commodity_network: bool = False,
    ):
        if '-' in scenario:
            raise ValueError(
                'Scenario name must not contain "-".  Dashes are used internally to indicate iterative '
                'runs.  Please rename scenario'
            )
        self.scenario = scenario
        # capture the operating mode
        self.scenario_mode: TemoaMode
        match scenario_mode:
            case TemoaMode():
                self.scenario_mode = scenario_mode
            case str():
                try:
                    self.scenario_mode = TemoaMode[scenario_mode.upper()]
                except KeyError:
                    raise AttributeError(
                        f'The mode selection received by TemoaConfig: '
                        f'{scenario_mode} is invalid.\nPossible choices are '
                        f'{list(TemoaMode.__members__.keys())} (case '
                        f'insensitive).'
                    )
            case _:
                raise AttributeError(
                    f'The mode selection received by TemoaConfig: '
                    f'{scenario_mode} is invalid.\nPossible choices are '
                    f'{list(TemoaMode.__members__.keys())} (case '
                    f'insensitive).'
                )

        self.config_file = config_file

        # accept and screen the input file
        self.input_database = Path(input_database)
        if not self.input_database.is_file():
            raise FileNotFoundError(f'could not locate the input database: {self.input_database}')
        if self.input_database.suffix not in {'.db', '.sqlite'}:
            logger.error('Input file is not of type .ddb or .sqlite')
            raise AttributeError('Input file is not of type .db or .sqlite')

        # accept and validate the output db
        self.output_database = Path(output_database)
        if not self.output_database.is_file():
            raise FileNotFoundError(f'Could not locate the output db: {self.output_database}')
        if self.output_database.suffix != '.sqlite':
            logger.error('Output DB does not appear to be a sqlite db')
            raise AttributeError('Output DB should be .sqlite type')

        # create a placeholder for .dat file.  If conversion is needed, this
        # is the destination...
        self.dat_file: Path | None = None

        self.output_path = output_path
        self.neos = neos
        if self.neos:
            raise NotImplementedError('Neos is currently not supported.')

        self.solver_name = solver_name
        self.save_excel = save_excel
        self.save_duals = save_duals
        self.save_lp_file = save_lp_file

        self.mga_inputs = MGA
        self.svmga_inputs = SVMGA
        self.myopic_inputs = myopic
        self.morris_inputs = morris
        self.silent = silent
        self.stream_output = stream_output
        self.price_check = price_check
        self.source_trace = source_trace
        if plot_commodity_network and not self.source_trace:
            logger.warning(
                'Commodity Network plotting was selected, but Source Trace was not selected.  '
                'Both are required to produce plots.'
            )
        self.plot_commodity_network = plot_commodity_network and self.source_trace

        # warn if output db != input db
        if self.input_database.suffix == self.output_database.suffix:  # they are both .db/.sqlite
            if self.input_database != self.output_database:  # they are not the same db
                msg = (
                    'Input file, which is a database, does not match the output file\n User '
                    'is responsible to ensure the data ~ results congruency in the output db'
                )
                logger.warning(msg)
                if not self.silent:
                    SE.write('Warning: ' + msg)

    @staticmethod
    def build_config(config_file: Path, output_path: Path, silent=False) -> 'TemoaConfig':
        """
        build a Temoa Config from a config file
        :param silent: suppress warnings and confirmations
        :param output_path:
        :param config_file: the path to the config file to use
        :return: a TemoaConfig instance
        """
        with open(config_file, 'rb') as f:
            data = tomllib.load(f)

        tc = TemoaConfig(output_path=output_path, config_file=config_file, silent=silent, **data)
        logger.info('Scenario Name:  %s', tc.scenario)
        logger.info('Data source:  %s', tc.input_database)
        logger.info('Data target:  %s', tc.output_database)
        logger.info('Mode:  %s', tc.scenario_mode.name)
        return tc

    def __repr__(self):
        width = 25
        spacer = '\n' + '-' * width + '\n'
        msg = spacer

        msg += '{:>{}s}: {}\n'.format('Scenario', width, self.scenario)
        msg += '{:>{}s}: {}\n'.format('Scenario mode', width, self.scenario_mode.name)
        msg += '{:>{}s}: {}\n'.format('Config file', width, self.config_file)
        msg += '{:>{}s}: {}\n'.format('Data source', width, self.input_database)
        msg += '{:>{}s}: {}\n'.format('Output database target', width, self.output_database)
        msg += '{:>{}s}: {}\n'.format('Path for outputs and log', width, self.output_path)

        msg += spacer
        msg += '{:>{}s}: {}\n'.format('Price check', width, self.price_check)
        msg += '{:>{}s}: {}\n'.format('Source trace', width, self.source_trace)
        msg += '{:>{}s}: {}\n'.format('Commodity network plots', width, self.plot_commodity_network)

        msg += spacer
        msg += '{:>{}s}: {}\n'.format('Selected solver', width, self.solver_name)
        msg += '{:>{}s}: {}\n'.format('NEOS status', width, self.neos)

        msg += spacer
        msg += '{:>{}s}: {}\n'.format('Spreadsheet output', width, self.save_excel)
        msg += '{:>{}s}: {}\n'.format('Pyomo LP write status', width, self.save_lp_file)
        msg += '{:>{}s}: {}\n'.format('Save duals to output db', width, self.save_duals)

        if self.scenario_mode == TemoaMode.MYOPIC:
            msg += spacer
            msg += '{:>{}s}: {}\n'.format(
                'Myopic view depth', width, self.myopic_inputs.get('view_depth')
            )
            msg += '{:>{}s}: {}\n'.format(
                'Myopic step size', width, self.myopic_inputs.get('step_size')
            )

        if self.scenario_mode == TemoaMode.MGA:
            msg += spacer
            msg += '{:>{}s}: {}\n'.format(
                'MGA Cost Epsilon', width, self.mga_inputs.get('cost_epsilon')
            )
            msg += '{:>{}s}: {}\n'.format(
                'MGA Iteration Limit', width, self.mga_inputs.get('iteration_limit')
            )
            msg += '{:>{}s}: {}\n'.format(
                'MGA Time Limit (hrs)', width, self.mga_inputs.get('time_limit_hrs')
            )
            msg += '{:>{}s}: {}\n'.format('MGA Axis:', width, self.mga_inputs.get('axis'))
            msg += '{:>{}s}: {}\n'.format('MGA Weighting', width, self.mga_inputs.get('weighting'))

        if self.scenario_mode == TemoaMode.METHOD_OF_MORRIS:
            msg += spacer
            msg += '{:>{}s}: {}\n'.format(
                'Morris Perturbation', width, self.morris_inputs.get('perturbation')
            )
            msg += '{:>{}s}: {}\n'.format(
                'Morris Param Levels', width, self.morris_inputs.get('levels')
            )
            msg += '{:>{}s}: {}\n'.format(
                'Morris Trajectories', width, self.morris_inputs.get('trajectories')
            )
            msg += '{:>{}s}: {}\n'.format(
                'Morris Random Seed', width, self.morris_inputs.get('seed', 'Auto')
            )
            msg += '{:>{}s}: {}\n'.format(
                'Morris CPU Cores Requested', width, self.morris_inputs.get('cores')
            )

        if self.scenario_mode == TemoaMode.SVMGA:
            msg += spacer
            msg += '{:>{}s}: {}\n'.format(
                'SVMGA Cost Epsilon', width, self.svmga_inputs.get('cost_epsilon')
            )
            msg += '{:>{}s}: {}\n'.format(
                'Emission Labels', width, self.svmga_inputs.get('emission_labels')
            )
            msg += '{:>{}s}: {}\n'.format(
                'Capacity Labels', width, self.svmga_inputs.get('capacity_labels')
            )
            msg += '{:>{}s}: {}\n'.format(
                'Activity Labels', width, self.svmga_inputs.get('activity_labels')
            )

        return msg
