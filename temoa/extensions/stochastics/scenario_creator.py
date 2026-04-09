from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING, Any, cast
from collections.abc import Iterable

from mpisppy.utils.sputils import attach_root_node  # type: ignore[import-untyped]

from temoa._internal.run_actions import build_instance
from temoa.components.costs import period_cost_rule
from temoa.data_io.hybrid_loader import HybridLoader

if TYPE_CHECKING:
    from temoa.core.config import TemoaConfig
    from temoa.data_io.hybrid_loader import LoadItem
    from temoa.extensions.stochastics.stochastic_config import StochasticConfig

logger = logging.getLogger(__name__)


def scenario_creator(scenario_name: str, **kwargs: Any) -> Any:
    """
    Creator for mpi-sppy scenarios.

    Args:
        scenario_name (str): Name of the scenario to create.
        **kwargs: Must contain 'temoa_config' and 'stoch_config'.
    """
    if 'temoa_config' not in kwargs or 'stoch_config' not in kwargs:
        raise ValueError("scenario_creator requires 'temoa_config' and 'stoch_config' in kwargs")

    temoa_config: TemoaConfig = kwargs['temoa_config']
    stoch_config: StochasticConfig = kwargs['stoch_config']

    # 1. Load base data
    try:
        with sqlite3.connect(temoa_config.input_database) as con:
            hybrid_loader = HybridLoader(db_connection=con, config=temoa_config)
            data_dict = hybrid_loader.create_data_dict(myopic_index=None)

            # Build a map of table -> index columns from the manifest
            # For each LoadItem, the index columns are all but the last one (which is the value)
            table_index_map: dict[str, list[str]] = {}
            for item in cast('Iterable[LoadItem]', hybrid_loader.manifest):
                if item.table not in table_index_map and item.columns:
                    table_index_map[item.table] = list(item.columns[:-1])
    except Exception as e:
        logger.exception('Failed to connect to database %s', temoa_config.input_database)
        raise RuntimeError(f'Failed to connect to database {temoa_config.input_database}') from e

    # 2. Apply perturbations for this scenario
    for p in stoch_config.perturbations:
        if p.scenario != scenario_name:
            continue

        target_param = cast(dict[Any, Any] | None, data_dict.get(p.table))
        if target_param is None:
            logger.warning(
                'Table %s not found in data_dict for scenario %s', p.table, scenario_name
            )
            continue

        # target_param is {(idx...): value}
        # We need to find entries matching p.filter
        index_cols = table_index_map.get(p.table)
        if index_cols is None:
            logger.warning(
                'Table %s not found in manifest; cannot map indices for scenario %s',
                p.table,
                scenario_name,
            )
            continue

        for idx, current_val in list(target_param.items()):
            # Map index tuple to names based on table manifest
            # normalize idx to tuple if it is a single value
            idx_tuple = idx if isinstance(idx, tuple) else (idx,)
            index_map = dict(zip(index_cols, idx_tuple, strict=True))

            # Check if filter matches
            match = True
            for filter_key, filter_val in p.filter.items():
                if index_map.get(filter_key) != filter_val:
                    match = False
                    break

            if match:
                if p.action == 'multiply':
                    target_param[idx] = current_val * p.value
                elif p.action == 'add':
                    target_param[idx] = current_val + p.value
                elif p.action == 'set':
                    target_param[idx] = p.value

    # 3. Build instance
    data_portal = HybridLoader.data_portal_from_data(data_dict)
    instance = build_instance(data_portal, silent=True)

    # 4. Attach root node (Stage 1)
    periods = sorted(instance.time_optimize)
    first_period = periods[0]

    prob = stoch_config.scenarios.get(scenario_name)
    if prob is None:
        logger.warning(
            "Scenario '%s' not found in stochastic config probabilities; defaulting to 1.0",
            scenario_name,
        )
        prob = 1.0
    instance._mpisppy_probability = prob

    # First stage variables: v_new_capacity[*, *, first_period]
    first_stage_vars = []
    for r, t, p in instance.v_new_capacity:
        if p == first_period:
            first_stage_vars.append(instance.v_new_capacity[r, t, p])

    if not first_stage_vars:
        logger.error(
            'No first-stage variables (v_new_capacity for period %s) found for scenario %s. '
            'Stochastic optimization requires at least one first-stage decision.',
            first_period,
            scenario_name,
        )
        raise ValueError(f'No first-stage variables found for scenario {scenario_name}')

    # First stage cost: PeriodCost[first_period]
    # We can use the period_cost_rule directly
    first_stage_cost_expr = period_cost_rule(instance, first_period)

    # Attach root node
    attach_root_node(instance, first_stage_cost_expr, first_stage_vars)

    return instance
