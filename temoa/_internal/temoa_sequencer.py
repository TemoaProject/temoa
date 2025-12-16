"""
The Temoa Sequencer's job is to sequence the actions needed to execute a scenario.  Each
scenario has a declared processing mode (regular, myopic, mga, etc.) and the Temoa Sequencer sets
up the necessary run(s) to accomplish that.  Several processing modes have requirements
for multiple runs, and the Temoa Sequencer may hand off to a mode-specific sequencer

"""

import sqlite3
from logging import getLogger
from typing import TYPE_CHECKING

from temoa.__about__ import (
    DB_MAJOR_VERSION,
    MIN_DB_MINOR_VERSION,
    MIN_PYTHON_MAJOR,
    MIN_PYTHON_MINOR,
)
from temoa._internal.run_actions import (
    build_instance,
    check_database_version,
    check_python_version,
    check_solve_status,
    handle_results,
    solve_instance,
)
from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel
from temoa.core.modes import TemoaMode
from temoa.data_io.hybrid_loader import HybridLoader
from temoa.extensions.method_of_morris.morris_sequencer import MorrisSequencer
from temoa.extensions.modeling_to_generate_alternatives.mga_sequencer import MgaSequencer
from temoa.extensions.monte_carlo.mc_sequencer import MCSequencer
from temoa.extensions.myopic.myopic_sequencer import MyopicSequencer
from temoa.extensions.single_vector_mga.sv_mga_sequencer import SvMgaSequencer
from temoa.model_checking.pricing_check import price_checker

if TYPE_CHECKING:
    import pyomo.opt

logger = getLogger(__name__)


class TemoaSequencer:
    """A Sequencer instance to control all runs for a scenario based on the TemoaMode."""

    def __init__(
        self,
        config: TemoaConfig,
        mode_override: TemoaMode | None = None,
    ) -> None:
        """
        Create a new Sequencer.

        :param config: A fully constructed TemoaConfig object.
        :param mode_override: Optional override to the execution mode from the config.
        """
        self.config = config
        self.temoa_mode = config.scenario_mode

        # Handle and log the mode override if provided
        if mode_override and mode_override != self.config.scenario_mode:
            self.temoa_mode = mode_override
            self.config.scenario_mode = mode_override
            logger.info('Temoa Mode overridden by caller to: %s', self.temoa_mode)

        # for results catching for perfect_foresight or testing
        self.pf_results: pyomo.opt.SolverResults | None = None
        self.pf_solved_instance: TemoaModel | None = None

    def _run_preliminary_checks(self) -> None:
        """Runs pre-flight system checks and (optionally) a non-fatal units check.

        Raises an error if Python or database version checks fail; unit-check
        failures are logged but do not abort the run.
        """
        # Unit checking - runs on database before model build
        if self.config.check_units:
            from temoa.model_checking.unit_checking.screener import screen

            logger.info('Running units consistency check on input database...')
            report_dir = self.config.output_path / 'unit_check_reports'
            success = screen(self.config.input_database, report_dir=report_dir)

            if not success:
                logger.warning(
                    'Units check found errors. See detailed report at: %s',
                    report_dir,
                )
                logger.warning('Continuing with model build despite unit check warnings...')
            else:
                logger.info('Units check completed successfully - no errors found.')

        # System checks (Python version, database version)
        checks_ok = check_python_version(MIN_PYTHON_MAJOR, MIN_PYTHON_MINOR)
        checks_ok &= check_database_version(
            self.config, db_major_reqd=DB_MAJOR_VERSION, min_db_minor=MIN_DB_MINOR_VERSION
        )
        if not checks_ok:
            # The specific reasons for failure are already in the log.
            raise RuntimeError('Failed pre-run checks. See log file for details.')

    def build_model(self) -> TemoaModel:
        """
        Builds and returns an unsolved TemoaModel instance.
        This is the dedicated method for the 'BUILD_ONLY' mode.
        """
        self._run_preliminary_checks()
        logger.info('Starting model build process (build-only mode).')

        # Capture original values to restore later
        original_source_trace = self.config.source_trace
        original_plot_commodity_network = self.config.plot_commodity_network
        original_price_check = self.config.price_check

        try:
            # Ensure certain features that don't apply to a simple build are disabled
            if self.config.source_trace:
                self.config.source_trace = False
                logger.warning('Source trace disabled for build-only mode.')
            if self.config.plot_commodity_network:
                self.config.plot_commodity_network = False
                logger.warning('Commodity network plotting disabled for build-only mode.')
            if self.config.price_check:
                self.config.price_check = False
                logger.warning('Price check disabled for build-only mode.')

            # Validate database before attempting to build model
            if not check_database_version(
                self.config, db_major_reqd=DB_MAJOR_VERSION, min_db_minor=MIN_DB_MINOR_VERSION
            ):
                raise RuntimeError('Database version check failed. See log file for details.')

            with sqlite3.connect(self.config.input_database) as con:
                hybrid_loader = HybridLoader(db_connection=con, config=self.config)
                data_portal = hybrid_loader.load_data_portal(myopic_index=None)
                instance = build_instance(data_portal, silent=self.config.silent)

            logger.info('Model build process complete.')
            return instance
        finally:
            # Restore original config values
            self.config.source_trace = original_source_trace
            self.config.plot_commodity_network = original_plot_commodity_network
            self.config.price_check = original_price_check

    def start(self) -> None:
        """
        Executes the full scenario run to completion.
        This method returns None on success and raises an exception on failure.
        """
        self._run_preliminary_checks()

        # The mode is now definitively set, so we can proceed.
        logger.info('Executing scenario in mode: %s', self.temoa_mode)

        # Select execution path based on mode
        match self.temoa_mode:
            case TemoaMode.BUILD_ONLY:
                # The `start` method's contract is to run to completion, not return a model.
                # Raise an error to guide the developer to the correct API.
                raise RuntimeError(
                    "For BUILD_ONLY mode, please use the 'build_model()' method instead of "
                    "'start()'."
                )

            case TemoaMode.CHECK:
                self._run_check_mode()

            case TemoaMode.PERFECT_FORESIGHT:
                self._run_perfect_foresight()

            case TemoaMode.MYOPIC:
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

            case TemoaMode.MONTE_CARLO:
                self._run_monte_carlo()

            case _:
                raise NotImplementedError(
                    f"The scenario mode '{self.temoa_mode}' is not yet implemented."
                )

    def _run_check_mode(self) -> None:
        """Encapsulated logic for the CHECK mode."""
        with sqlite3.connect(self.config.input_database) as con:
            if not self.config.source_trace:
                logger.warning('Source trace is automatically enabled for CHECK mode.')
                self.config.source_trace = True
            hybrid_loader = HybridLoader(db_connection=con, config=self.config)
            data_portal = hybrid_loader.load_data_portal(myopic_index=None)
            instance = build_instance(
                data_portal,
                silent=self.config.silent,
                keep_lp_file=self.config.save_lp_file,
                lp_path=self.config.output_path,
            )
            if not self.config.price_check:
                logger.warning('Price check is automatically enabled for CHECK mode.')
            price_checker(instance)

    def _run_perfect_foresight(self) -> None:
        """Encapsulated logic for the PERFECT_FORESIGHT mode."""
        with sqlite3.connect(self.config.input_database) as con:
            hybrid_loader = HybridLoader(db_connection=con, config=self.config)
            data_portal = hybrid_loader.load_data_portal(myopic_index=None)
            instance = build_instance(
                data_portal,
                silent=self.config.silent,
                keep_lp_file=self.config.save_lp_file,
                lp_path=self.config.output_path,
            )
            if self.config.price_check:
                price_checker(instance)

            suffixes = ['dual'] if self.config.save_duals else None
            self.pf_solved_instance, self.pf_results = solve_instance(
                instance,
                self.config.solver_name,
                silent=self.config.silent,
                solver_suffixes=suffixes,
            )
            good_solve, msg = check_solve_status(self.pf_results)
            if not good_solve:
                raise RuntimeError(
                    f"The solver reported a non-optimal status: '{msg}'. Aborting run. "
                    "This may be due to the solver's output messaging. If this status is "
                    'acceptable, the `check_solve_status` function may need adjustment.'
                )
            handle_results(self.pf_solved_instance, self.pf_results, self.config)

    def _run_monte_carlo(self) -> None:
        """Encapsulated logic for the MONTE_CARLO mode."""

        # Disable features not typically used in Monte Carlo runs to reduce noise/overhead
        if self.config.plot_commodity_network:
            self.config.plot_commodity_network = False
            logger.warning('Commodity network plotting disabled for MONTE_CARLO mode.')
        if self.config.price_check:
            self.config.price_check = False
            logger.warning('Price check disabled for MONTE_CARLO mode.')
        if self.config.save_excel:
            self.config.save_excel = False
            logger.warning('Excel output disabled for MONTE_CARLO mode.')
        if self.config.save_lp_file:
            self.config.save_lp_file = False
            logger.warning('LP file saving disabled for MONTE_CARLO mode.')
        if self.config.save_duals:
            self.config.save_duals = False
            logger.warning('Saving of duals disabled for MONTE_CARLO mode.')

        mc_sequencer = MCSequencer(config=self.config)
        mc_sequencer.start()
