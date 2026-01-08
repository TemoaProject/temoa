import logging
from typing import Any

import pyomo.environ as pyo

from temoa.core.config import TemoaConfig
from temoa.extensions.stochastics.stochastic_config import StochasticConfig

logger = logging.getLogger(__name__)


class StochasticSequencer:
    """
    Orchestrates a stochastic run using mpi-sppy.
    """

    def __init__(self, config: TemoaConfig) -> None:
        self.config = config
        self.objective_value: float | None = None
        if not self.config.stochastic_config:
            raise ValueError("Stochastic mode requires a 'stochastic_config' in the TOML.")

        sc_path = self.config.stochastic_config
        if not sc_path.exists():
            raise ValueError(f'Stochastic config file not found: {sc_path}')
        if not sc_path.is_file():
            raise ValueError(f'Stochastic config path is not a file: {sc_path}')

        try:
            self.stoch_config = StochasticConfig.from_toml(sc_path)
        except Exception as e:
            logger.exception('Failed to load stochastic config from %s', sc_path)
            raise ValueError(f'Error parsing stochastic config {sc_path}') from e

    def start(self) -> None:
        """
        Execute the stochastic run.
        """
        try:
            from mpisppy.opt.ef import ExtensiveForm
        except ImportError as e:
            logger.exception('mpi-sppy is not installed. Please install it to use stochastic mode.')
            raise RuntimeError('mpi-sppy not found') from e

        from temoa.extensions.stochastics.scenario_creator import scenario_creator

        # Merge solver options from stoch_config
        solver_options = self.stoch_config.solver_options.get(self.config.solver_name, {})

        options = {
            'solver': self.config.solver_name,
        }

        if not self.stoch_config.scenarios:
            raise ValueError(
                'No scenarios found in stoch_config.scenarios; provide at least one scenario '
                'before constructing the ExtensiveForm'
            )

        # For now, we only support Extensive Form (EF)
        # We need to provide a list of scenario names to mpi-sppy
        all_scenario_names = list(self.stoch_config.scenarios.keys())

        scenario_creator_kwargs = {
            'temoa_config': self.config,
            'stoch_config': self.stoch_config,
        }

        logger.info('Starting mpi-sppy Extensive Form (EF) solver...')

        ef = ExtensiveForm(
            options,
            all_scenario_names,
            scenario_creator,
            scenario_creator_kwargs=scenario_creator_kwargs,
        )

        results = ef.solve_extensive_form(solver_options=solver_options)

        # Check for optimal termination before accessing objective
        if not pyo.check_optimal_termination(results):
            termination = 'unknown'
            if hasattr(results, 'solver'):
                termination = getattr(results.solver, 'termination_condition', 'unknown')

            logger.error('Stochastic solve failed with termination condition: %s', termination)
            raise RuntimeError(f'Stochastic solve failed: {termination}')

        obj_val = ef.get_objective_value()
        self.objective_value = obj_val
        logger.info('Stochastic Expected Value: %s', obj_val)

        # TODO: Integrate with TableWriter to save results to database
        # This might require a modified handle_results or a new one for stochastics
