from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING, NamedTuple, cast

from pyomo.environ import quicksum, value

from temoa._internal.exchange_tech_cost_ledger import CostType, ExchangeTechCostLedger
from temoa.components import costs
from temoa.extensions.unit_commitment.components import startup
from temoa.types.model_types import EI, FI, FlowType

if TYPE_CHECKING:
    from temoa._internal.table_writer import TableWriter
    from temoa.core.model import TemoaModel
    from temoa.extensions.unit_commitment.core.model import UnitCommitmentModel
    from temoa.types import Commodity, Period, Region, Season, Technology, TimeOfDay, Vintage

logger = logging.getLogger(__name__)


class UCI(NamedTuple):
    """Unit Commitment Index"""

    r: Region
    p: Period
    s: Season
    d: TimeOfDay
    t: Technology
    v: Vintage


def poll_commitment_results(model: TemoaModel) -> dict[UCI, tuple[float, float, float]]:
    """
    Poll the start, stop, and online capacity for all unit commitment process,
    periods, and time slices, and add them to the output_unit_commitment table.
    """
    model = cast('UnitCommitmentModel', model)

    results: dict[UCI, tuple[float, float, float]] = {}
    for r, p, s, d, t, v in model.uc_indices_rpsdtv:
        unit_cap = value(model.uc_unit_capacity[r, t])

        online = unit_cap * value(model.v_uc_online[r, p, s, d, t, v])
        started = unit_cap * value(model.v_uc_started[r, p, s, d, t, v])
        stopped = unit_cap * value(model.v_uc_stopped[r, p, s, d, t, v])

        if online > 0 or started > 0 or stopped > 0:
            results[UCI(r, p, s, d, t, v)] = (online, started, stopped)
    return results


def write_uc_results(
    model: TemoaModel, writer: TableWriter, iteration: int | None, epsilon: float = 1e-5
) -> None:
    if writer.tech_sectors is None:
        raise RuntimeError('Missing tech_sectors')

    results = poll_commitment_results(model)
    scenario = writer._get_scenario_name(iteration)
    unit_prop = writer.unit_propagator
    records = []

    for uci, (online, started, stopped) in results.items():
        if all(abs(v) < epsilon for v in (online, started, stopped)):
            continue
        row = {
            'scenario': scenario,
            'region': uci.r,
            'sector': writer.tech_sectors.get(uci.t),
            'period': uci.p,
            'season': uci.s,
            'tod': uci.d,
            'tech': uci.t,
            'vintage': uci.v,
            'online_cap': online,
            'start_cap': started,
            'stop_cap': stopped,
            'units': unit_prop.get_capacity_units(uci.t) if unit_prop else None,
        }
        records.append(row)
    try:
        writer.connection.execute(
            'DELETE FROM output_unit_commitment WHERE scenario == ?', (scenario,)
        )
    except sqlite3.OperationalError:
        pass

    writer._bulk_insert('output_unit_commitment', records)
    writer.connection.commit()


def poll_startup_input_results(
    model: TemoaModel, res: dict[FI, dict[FlowType, float]], epsilon: float = 1e-5
) -> None:
    """
    Poll the emissions for all unit commitment processes in the planning horizon
    and add them to the cost entries for the model.
    """
    model = cast('UnitCommitmentModel', model)

    keys = {
        FI(r, p, s, d, i, t, v, cast('Commodity', None))
        for r, i, t in model.uc_startup_input.sparse_keys()
        for p in model.time_optimize
        for v in model.process_vintages.get((r, p, t), [])
        for s in model.time_season
        for d in model.time_of_day
    }
    for fi in keys:
        flow = (
            value(model.uc_startup_input[fi.r, fi.i, fi.t])
            * value(model.uc_unit_capacity[fi.r, fi.t])
            * value(model.v_uc_started[fi.r, fi.p, fi.s, fi.d, fi.t, fi.v])
        )
        if abs(flow) < epsilon:
            continue
        res[fi][FlowType.IN] = flow


def poll_emission_results(model: TemoaModel, flows: dict[EI, float]) -> None:
    """
    Poll the emissions for all unit commitment processes in the planning horizon
    and add them to the cost entries for the model.
    """
    model = cast('UnitCommitmentModel', model)

    keys = {
        EI(r, p, t, v, e)
        for r, e, t in model.uc_startup_emissions.sparse_keys()
        for p in model.time_optimize
        for v in model.process_vintages.get((r, p, t), [])
    }
    for ei in keys:
        unit_cap = value(model.uc_unit_capacity[ei.r, ei.t])
        emis_per_cap = value(model.uc_startup_emissions[ei.r, ei.e, ei.t])
        emis = quicksum(
            value(model.v_uc_started[ei.r, ei.p, s, d, ei.t, ei.v]) * unit_cap * emis_per_cap
            for s in model.time_season
            for d in model.time_of_day
        )
        flows[ei] += float(emis)


# --- Poll unit commitment results ---
def poll_startup_cost_results(
    model: TemoaModel,
    exchange_costs: ExchangeTechCostLedger,
    entries: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]],
    p_0: Period,
    epsilon: float,
) -> None:
    """
    Poll the startup costs for all unit commitment processes in the planning horizon
    and add them to the cost entries for the model.
    """
    model = cast('UnitCommitmentModel', model)

    global_discount_rate = value(model.global_discount_rate)

    keys = {
        (r, p, t, v)
        for r, t in model.uc_startup_cost.sparse_keys()
        for p in model.time_optimize
        for v in model.process_vintages.get((r, p, t), [])
    }
    for r, p, t, v in keys:
        cost = float(value(startup.uc_startup_cost_rptv(model, r, p, t, v)))
        if abs(cost) < epsilon:
            continue

        ud_variable = float(cost * value(model.period_length[p]))
        d_variable = costs.fixed_or_variable_cost(
            cap_or_flow=1.0,
            cost_factor=cost,
            cost_years=value(model.period_length[p]),
            global_discount_rate=global_discount_rate,
            p_0=float(p_0),
            p=p,
        )
        d_variable = float(value(d_variable))

        if '-' in r:
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=v,
                cost=d_variable,
                cost_type=CostType.D_VARIABLE,
            )
            exchange_costs.add_cost_record(
                r,
                period=p,
                tech=t,
                vintage=v,
                cost=ud_variable,
                cost_type=CostType.VARIABLE,
            )
        else:
            entry = entries[r, p, t, v]
            entry[CostType.D_VARIABLE] = entry.get(CostType.D_VARIABLE, 0.0) + d_variable
            entry[CostType.VARIABLE] = entry.get(CostType.VARIABLE, 0.0) + ud_variable
