"""
Tools for Energy Model Optimization and Analysis (Temoa):
An open source framework for energy systems optimization modeling

This module provides backward compatibility imports for the refactored TEMOA structure.
New code should import directly from temoa.core and temoa._internal as appropriate.
"""

# Core API - public interface
# Internal modules - for backward compatibility
# Version information
from temoa.__about__ import TEMOA_MAJOR, TEMOA_MINOR, __version__
from temoa._internal.data_brick import DataBrick, data_brick_factory
from temoa._internal.exchange_tech_cost_ledger import CostType, ExchangeTechCostLedger
from temoa._internal.run_actions import (
    build_instance,
    handle_results,
    save_lp,
    solve_instance,
)
from temoa._internal.table_data_puller import (
    loan_costs,
    poll_capacity_results,
    poll_cost_results,
    poll_emissions,
    poll_flow_results,
)
from temoa._internal.table_writer import TableWriter
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel
from temoa.core.modes import TemoaMode
from temoa.data_io.hybrid_loader import HybridLoader

# Maintain backward compatibility for common imports
__all__ = [
    # Core API
    'TemoaModel',
    'TemoaConfig',
    'TemoaMode',
    # Internal modules (for backward compatibility)
    'DataBrick',
    'data_brick_factory',
    'CostType',
    'ExchangeTechCostLedger',
    'HybridLoader',
    'build_instance',
    'solve_instance',
    'handle_results',
    'save_lp',
    'loan_costs',
    'poll_capacity_results',
    'poll_emissions',
    'poll_flow_results',
    'poll_cost_results',
    'TableWriter',
    'TemoaSequencer',
    # Version info
    'TEMOA_MAJOR',
    'TEMOA_MINOR',
    '__version__',
]
