"""
User-defined MOO objective functions, built as weighted sums of activity, built capacity and
net capacity.  The weights are read from optional tables of the input database.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from logging import getLogger
from typing import TYPE_CHECKING, Any

from pyomo.environ import quicksum, value

if TYPE_CHECKING:
    from sqlite3 import Connection

    from temoa.core.model import TemoaModel

logger = getLogger(__name__)

ACTIVITY_TABLE = 'moo_activity_weight'
BUILT_CAPACITY_TABLE = 'moo_built_capacity_weight'
NET_CAPACITY_TABLE = 'moo_net_capacity_weight'

WEIGHT_TABLES: dict[str, tuple[str, ...]] = {
    ACTIVITY_TABLE: ('region', 'period', 'tech', 'vintage'),
    BUILT_CAPACITY_TABLE: ('region', 'tech', 'vintage'),
    NET_CAPACITY_TABLE: ('region', 'period', 'tech', 'vintage'),
}


@dataclass
class CustomObjectiveWeights:
    name: str
    activity: dict[tuple[Any, ...], float] = field(default_factory=dict)
    built_capacity: dict[tuple[Any, ...], float] = field(default_factory=dict)
    net_capacity: dict[tuple[Any, ...], float] = field(default_factory=dict)


def _table_exists(con: Connection, table: str) -> bool:
    return bool(
        con.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (table,)
        ).fetchone()
    )


def load_custom_objective_weights(con: Connection, name: str) -> CustomObjectiveWeights:
    """Read the weights of a user-defined objective function from the database"""
    existing_tables = [table for table in WEIGHT_TABLES if _table_exists(con, table)]
    if not existing_tables:
        msg = (
            f"MOO objective '{name}' is not a built-in objective and none of the tables defining "
            f'custom objectives exists in the database: {", ".join(WEIGHT_TABLES)}.'
        )
        logger.error(msg)
        raise ValueError(msg)

    rows: dict[str, dict[tuple[Any, ...], float]] = {}
    for table in existing_tables:
        columns = ', '.join(WEIGHT_TABLES[table])
        query = f'SELECT {columns}, weight FROM main.{table} WHERE objective = ?'
        rows[table] = {tuple(row[:-1]): float(row[-1]) for row in con.execute(query, (name,))}
        missing = [idx for idx in rows[table] if any(item is None for item in idx)]
        if missing:
            msg = f'Table {table} has incomplete indices for MOO objective {name!r}: {missing}'
            logger.error(msg)
            raise ValueError(msg)

    if not any(rows.values()):
        msg = (
            f"MOO objective '{name}' is not a built-in objective and no weights are defined for "
            f'it in the table(s): {", ".join(existing_tables)}.'
        )
        logger.error(msg)
        raise ValueError(msg)

    return CustomObjectiveWeights(
        name=name,
        activity=rows.get(ACTIVITY_TABLE, {}),
        built_capacity=rows.get(BUILT_CAPACITY_TABLE, {}),
        net_capacity=rows.get(NET_CAPACITY_TABLE, {}),
    )


def _check_indices(
    name: str, table: str, indices: dict[tuple[Any, ...], float], valid: Any
) -> None:
    invalid = sorted(idx for idx in indices if idx not in valid)
    if invalid:
        msg = (
            f"Table {table} has indices for MOO objective '{name}' that do not exist in the "
            f'model: {invalid}'
        )
        logger.error(msg)
        raise ValueError(msg)


def custom_objective_expression(model: TemoaModel, weights: CustomObjectiveWeights) -> Any:
    """
    Weighted sum of the total activity over the time horizon, the built capacity and the net
    capacity in each period
    """
    activity: Any = 0
    if weights.activity:
        flows: dict[tuple[Any, ...], list[Any]] = defaultdict(list)
        for r, p, s, d, i, t, v, o in model.v_flow_out:
            flows[r, p, t, v].append(model.v_flow_out[r, p, s, d, i, t, v, o])
        for r, p, i, t, v, o in model.v_flow_out_annual:
            if t in model.tech_annual:
                flows[r, p, t, v].append(model.v_flow_out_annual[r, p, i, t, v, o])
        _check_indices(weights.name, ACTIVITY_TABLE, weights.activity, flows)
        activity = quicksum(
            weight * value(model.period_length[p]) * flow
            for (r, p, t, v), weight in weights.activity.items()
            for flow in flows[r, p, t, v]
        )

    _check_indices(weights.name, BUILT_CAPACITY_TABLE, weights.built_capacity, model.v_new_capacity)
    built_capacity = quicksum(
        weight * model.v_new_capacity[idx] for idx, weight in weights.built_capacity.items()
    )

    _check_indices(weights.name, NET_CAPACITY_TABLE, weights.net_capacity, model.v_capacity)
    net_capacity = quicksum(
        weight * model.v_capacity[idx] for idx, weight in weights.net_capacity.items()
    )

    return activity + built_capacity + net_capacity
