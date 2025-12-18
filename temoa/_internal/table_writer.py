"""
tool for writing outputs to database tables
"""

from __future__ import annotations

import sqlite3
import sys
from collections import defaultdict
from importlib import resources
from logging import getLogger
from typing import TYPE_CHECKING, Any

from pyomo.core import value

from temoa._internal.exchange_tech_cost_ledger import CostType
from temoa._internal.table_data_puller import (
    EI,
    FI,
    CapData,
    FlowType,
    poll_capacity_results,
    poll_cost_results,
    poll_emissions,
    poll_flow_results,
    poll_objective,
    poll_storage_level_results,
)
from temoa.core.modes import TemoaMode

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path
    from types import TracebackType

    from pyomo.opt import SolverResults

    from temoa._internal.data_brick import DataBrick
    from temoa.core.config import TemoaConfig
    from temoa.core.model import TemoaModel
    from temoa.extensions.monte_carlo.mc_run import ChangeRecord
    from temoa.model_checking.unit_checking.unit_propagator import UnitPropagator
    from temoa.types.core_types import Period, Region, Technology, Vintage

logger = getLogger(__name__)

# Basic tables that are always cleared on run
BASIC_OUTPUT_TABLES = [
    'output_built_capacity',
    'output_cost',
    'output_curtailment',
    'output_dual_variable',
    'output_emission',
    'output_flow_in',
    'output_flow_out',
    'output_net_capacity',
    'output_objective',
    'output_retired_capacity',
]

OPTIONAL_OUTPUT_TABLES = [
    'output_flow_out_summary',
    'output_mc_delta',
    'output_storage_level',
]

FLOW_SUMMARY_FILE_LOC = (
    resources.files('temoa.extensions.modeling_to_generate_alternatives')
    / 'make_flow_summary_table.sql'
)
MC_TWEAKS_FILE_LOC = resources.files('temoa.extensions.monte_carlo') / 'make_deltas_table.sql'


class TableWriter:
    con: sqlite3.Connection | None

    def __init__(self, config: TemoaConfig, epsilon: float = 1e-5) -> None:
        self.config = config
        self.epsilon = epsilon
        self.tech_sectors: dict[str, str] | None = None
        self.flow_register: dict[FI, dict[FlowType, float]] = {}
        self.emission_register: dict[EI, float] | None = None
        self.con = None

        # Cache for table columns to avoid repeated PRAGMA calls
        self._table_columns_cache: dict[str, set[str]] = {}

        try:
            self.con = sqlite3.connect(config.output_database)
            self.con.execute('PRAGMA foreign_keys = OFF')
        except sqlite3.OperationalError as _:
            logger.exception('Failed to connect to output database: %s', config.output_database)
            sys.exit(-1)

        # Unit propagator for populating units in output tables (lazy init)
        self._unit_propagator: UnitPropagator | None = None

    @property
    def connection(self) -> sqlite3.Connection:
        """
        Returns the active database connection.
        Raises RuntimeError if the connection is closed or not initialized.
        This serves as a central type guard for Mypy.
        """
        if self.con is None:
            raise RuntimeError('Database connection is closed')
        return self.con

    def __enter__(self) -> TableWriter:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Explicitly close the database connection."""
        if self.con:
            try:
                self.con.close()
            except (sqlite3.Error, OSError) as e:
                logger.warning('Error closing database connection: %s', e)
            finally:
                self.con = None

    @property
    def unit_propagator(self) -> UnitPropagator | None:
        """
        Lazily initialize and return the unit propagator.

        Returns None if initialization fails, ensuring graceful fallback
        for databases without unit information.
        """
        if self._unit_propagator is None:
            try:
                from temoa.model_checking.unit_checking.unit_propagator import (
                    UnitPropagator,
                )

                self._unit_propagator = UnitPropagator(self.connection)
                if not self._unit_propagator.has_unit_data:
                    logger.debug('No unit data available in database')
            except (ImportError, sqlite3.Error, RuntimeError) as e:
                logger.debug('Could not initialize unit propagator: %s', e, exc_info=True)
                # Leave as None - units will be None in output
        return self._unit_propagator

    def _validate_foreign_keys(self) -> None:
        """
        Re-enables foreign keys, runs a check, and logs any violations.
        This is essentially a "soft" integrity check that won't crash the write process
        but will alert the user to data consistency issues.
        """
        if self.con is None:
            return

        try:
            # Re-enable foreign keys to check for violations
            self.connection.execute('PRAGMA foreign_keys = ON')

            # Check for violations
            cursor = self.connection.execute('PRAGMA foreign_key_check')
            violations = cursor.fetchall()

            if violations:
                logger.error('Foreign key constraint violations found in output database:')
                for violation in violations:
                    # violation tuple: (table, rowid, parent, fkid)
                    table_name = violation[0]
                    row_id = violation[1]
                    parent_table = violation[2]
                    logger.error(
                        "  Table '%s' (row %s) violates FK to parent '%s'",
                        table_name,
                        row_id,
                        parent_table,
                    )
        except sqlite3.Error as _:
            logger.exception('Error during foreign key validation')

    def _get_table_columns(self, table_name: str) -> set[str]:
        """Returns a set of column names for the given table."""
        if table_name not in self._table_columns_cache:
            cursor = self.connection.execute(f'PRAGMA table_info({table_name})')
            # row[1] is the column name in sqlite PRAGMA table_info
            columns = {row[1] for row in cursor.fetchall()}
            self._table_columns_cache[table_name] = columns
        return self._table_columns_cache[table_name]

    def _bulk_insert(self, table_name: str, records: list[dict[str, Any]]) -> None:
        """
        Dynamically inserts records into a table.

        1. Checks the DB schema to see which columns exist.
        2. Filters the input dictionary to match existing columns.
        3. Handles the optional 'units' column automatically.
        """
        if not records:
            return

        valid_columns = self._get_table_columns(table_name)

        # Determine the columns we will actually write to based on the first record
        # and the valid schema columns.
        data_keys = set(records[0].keys())

        # Intersection: keys present in data AND present in database table
        target_columns = list(data_keys.intersection(valid_columns))
        target_columns.sort()  # Sort to ensure consistent order

        if not target_columns:
            logger.warning('No matching columns found for table %s. Skipping insert.', table_name)
            return

        # Prepare SQL statement
        cols_str = ', '.join(target_columns)
        placeholders = ', '.join(['?'] * len(target_columns))
        query = f'INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})'

        # Prepare values tuple generator
        rows_to_insert = []
        for rec in records:
            rows_to_insert.append(tuple(rec[col] for col in target_columns))

        self.connection.executemany(query, rows_to_insert)

    def write_results(
        self,
        model: TemoaModel,
        results_with_duals: SolverResults | None = None,
        save_storage_levels: bool = False,
        append: bool = False,
        iteration: int | None = None,
    ) -> None:
        try:
            if not append:
                self.clear_scenario()

            if not self.tech_sectors:
                self._set_tech_sectors()

            self.write_objective(model, iteration=iteration)
            self.write_capacity_tables(model, iteration=iteration)

            # Poll and Write Emissions
            if self.config.scenario_mode == TemoaMode.MYOPIC:
                p_0 = model.myopic_discounting_year
            else:
                p_0 = None

            e_costs, e_flows = poll_emissions(model=model, p_0=value(p_0))
            self.emission_register = e_flows
            self.write_emissions(iteration=iteration)

            # Costs and Flows
            self.write_costs(model, emission_entries=e_costs, iteration=iteration)

            self.flow_register = self.calculate_flows(model)
            self.check_flow_balance(model)
            self.write_flow_tables(iteration=iteration)

            if results_with_duals:
                self.write_dual_variables(results_with_duals, iteration=iteration)

            if save_storage_levels:
                self.write_storage_level(model, iteration=iteration)

        finally:
            self._validate_foreign_keys()
            self.connection.commit()

    def write_mm_results(self, model: TemoaModel, iteration: int) -> None:
        try:
            if not self.tech_sectors:
                self._set_tech_sectors()
            self.write_objective(model, iteration=iteration)
            _e_costs, e_flows = poll_emissions(model=model)
            self.emission_register = e_flows
            self.write_emissions(iteration=iteration)
        finally:
            self._validate_foreign_keys()
            self.connection.commit()

    def write_mc_results(self, brick: DataBrick, iteration: int) -> None:
        try:
            if not self.tech_sectors:
                self._set_tech_sectors()

            e_costs, e_flows = brick.emission_cost_data, brick.emission_flows
            self.emission_register = e_flows
            self.write_emissions(iteration=iteration)

            self._insert_capacity_results(brick.capacity_data, iteration=iteration)
            self._insert_summary_flow_results(flow_data=brick.flow_data, iteration=iteration)
            self._insert_cost_results(
                regular_entries=brick.cost_data,
                exchange_entries=brick.exchange_cost_data,
                emission_entries=e_costs,
                iteration=iteration,
            )
            self._insert_objective_results(brick.obj_data, iteration=iteration)
        finally:
            self._validate_foreign_keys()
            self.connection.commit()

    def _set_tech_sectors(self) -> None:
        qry = 'SELECT tech, sector FROM Technology'
        data = self.connection.execute(qry).fetchall()
        self.tech_sectors = dict(data)

    def _get_scenario_name(self, iteration: int | None) -> str:
        if iteration is not None:
            return f'{self.config.scenario}-{iteration}'
        return self.config.scenario

    def clear_scenario(self) -> None:
        cur = self.connection.cursor()
        for table in BASIC_OUTPUT_TABLES:
            cur.execute(f'DELETE FROM {table} WHERE scenario == ?', (self.config.scenario,))
        for table in OPTIONAL_OUTPUT_TABLES:
            try:
                cur.execute(f'DELETE FROM {table} WHERE scenario == ?', (self.config.scenario,))
            except sqlite3.OperationalError:
                pass
        self.connection.commit()
        self.clear_iterative_runs()

    def clear_iterative_runs(self) -> None:
        target = self.config.scenario + '-%'
        cur = self.connection.cursor()
        tables = BASIC_OUTPUT_TABLES + OPTIONAL_OUTPUT_TABLES
        for table in tables:
            try:
                cur.execute(f'DELETE FROM {table} WHERE scenario like ?', (target,))
            except sqlite3.OperationalError:
                pass
        self.connection.commit()

    # -------------------------------------------------------------------------
    # WRITE IMPLEMENTATIONS
    # -------------------------------------------------------------------------

    def write_storage_level(self, model: TemoaModel, iteration: int | None = None) -> None:
        if self.tech_sectors is None:
            raise RuntimeError('tech sectors not available... code error')

        storage_levels = poll_storage_level_results(model=model)
        scenario = self._get_scenario_name(iteration)
        unit_prop = self.unit_propagator

        records = []
        for sli, val in storage_levels.items():
            records.append(
                {
                    'scenario': scenario,
                    'region': sli.r,
                    'sector': self.tech_sectors.get(sli.t),
                    'period': sli.p,
                    'season': sli.s,
                    'tod': sli.d,
                    'tech': sli.t,
                    'vintage': sli.v,
                    'level': val,
                    'units': unit_prop.get_storage_units(sli.t) if unit_prop else None,
                }
            )

        self._bulk_insert('output_storage_level', records)
        self.connection.commit()

    def write_objective(self, model: TemoaModel, iteration: int | None = None) -> None:
        obj_vals = poll_objective(model=model)
        self._insert_objective_results(obj_vals, iteration=iteration)

    def _insert_objective_results(
        self, obj_vals: list[tuple[str, float]], iteration: int | None
    ) -> None:
        scenario = self._get_scenario_name(iteration)
        records = [
            {
                'scenario': scenario,
                'objective_name': obj_name,
                'total_system_cost': obj_value,
            }
            for obj_name, obj_value in obj_vals
        ]
        self._bulk_insert('output_objective', records)
        self.connection.commit()

    def write_emissions(self, iteration: int | None = None) -> None:
        if self.tech_sectors is None or self.emission_register is None:
            raise RuntimeError('Dependencies missing (tech_sectors or emission_register)')

        scenario = self._get_scenario_name(iteration)
        unit_prop = self.unit_propagator
        records = []

        for ei, val in self.emission_register.items():
            if abs(val) < self.epsilon:
                continue

            row = {
                'scenario': scenario,
                'region': ei.r,
                'sector': self.tech_sectors.get(ei.t),
                'emission': val,
                'emis_comm': ei.e,
                'tech': ei.t,
                'vintage': ei.v,
                'units': unit_prop.get_emission_units(ei.e) if unit_prop else None,
            }

            if hasattr(ei, 'p'):  # emissions from flows
                row['period'] = ei.p
            else:  # embodied emissions (use vintage as period)
                row['period'] = ei.v

            records.append(row)

        self._bulk_insert('output_emission', records)
        self.connection.commit()

    def write_capacity_tables(self, model: TemoaModel, iteration: int | None = None) -> None:
        cap_data = poll_capacity_results(model=model)
        self._insert_capacity_results(cap_data=cap_data, iteration=iteration)

    def _insert_capacity_results(self, cap_data: CapData, iteration: int | None) -> None:
        if self.tech_sectors is None:
            raise RuntimeError('tech sectors not available... code error')

        scenario = self._get_scenario_name(iteration)
        unit_prop = self.unit_propagator

        # 1. Built Capacity
        built_recs = []
        for r, t, v, val in cap_data.built:
            built_recs.append(
                {
                    'scenario': scenario,
                    'region': r,
                    'sector': self.tech_sectors.get(t),
                    'tech': t,
                    'vintage': v,
                    'capacity': val,
                    'units': unit_prop.get_capacity_units(t) if unit_prop else None,
                }
            )
        self._bulk_insert('output_built_capacity', built_recs)

        # 2. Net Capacity
        net_recs = []
        for r, p, t, v, val in cap_data.net:
            net_recs.append(
                {
                    'scenario': scenario,
                    'region': r,
                    'sector': self.tech_sectors.get(t),
                    'period': p,
                    'tech': t,
                    'vintage': v,
                    'capacity': val,
                    'units': unit_prop.get_capacity_units(t) if unit_prop else None,
                }
            )
        self._bulk_insert('output_net_capacity', net_recs)

        # 3. Retired Capacity
        ret_recs = []
        for r, p, t, v, eol, early in cap_data.retired:
            ret_recs.append(
                {
                    'scenario': scenario,
                    'region': r,
                    'sector': self.tech_sectors.get(t),
                    'period': p,
                    'tech': t,
                    'vintage': v,
                    'cap_eol': eol,
                    'cap_early': early,
                    'units': unit_prop.get_capacity_units(t) if unit_prop else None,
                }
            )
        self._bulk_insert('output_retired_capacity', ret_recs)

        self.connection.commit()

    def write_flow_tables(self, iteration: int | None = None) -> None:
        if not self.tech_sectors or not self.flow_register:
            raise RuntimeError('Dependencies missing (tech_sectors or flow_register)')

        scenario = self._get_scenario_name(iteration)

        # Structure to hold list of dicts for each table type
        table_data: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

        map_flow_to_table = {
            FlowType.OUT: 'output_flow_out',
            FlowType.IN: 'output_flow_in',
            FlowType.CURTAIL: 'output_curtailment',
            FlowType.FLEX: 'output_curtailment',
        }

        for fi, flows in self.flow_register.items():
            sector = self.tech_sectors.get(fi.t)

            for flow_type, val in flows.items():
                if abs(val) < self.epsilon:
                    continue

                table_name = map_flow_to_table.get(flow_type)
                if not table_name:
                    continue

                row: dict[str, Any] = {
                    'scenario': scenario,
                    'region': fi.r,
                    'sector': sector,
                    'period': fi.p,
                    'season': fi.s,
                    'tod': fi.d,
                    'input_comm': fi.i,
                    'tech': fi.t,
                    'vintage': fi.v,
                    'output_comm': fi.o,
                    'units': self._get_flow_units(flow_type, fi.i, fi.o),
                }

                # Assign value to correct column name based on table/type
                if table_name == 'output_curtailment':
                    row['curtailment'] = val
                else:
                    row['flow'] = val

                table_data[table_name].append(row)

        for table_name, records in table_data.items():
            self._bulk_insert(table_name, records)

        self.connection.commit()

    def _get_flow_units(self, flow_type: FlowType, input_comm: str, output_comm: str) -> str | None:
        """
        Get units for flow based on flow type.

        For output flows and curtailment, uses the output commodity units.
        For input flows, uses the input commodity units.

        Args:
            flow_type: Type of flow (IN, OUT, CURTAIL, FLEX).
            input_comm: Input commodity name.
            output_comm: Output commodity name.

        Returns:
            Unit string or None if not available.
        """
        unit_prop = self.unit_propagator
        if not unit_prop:
            return None

        if flow_type == FlowType.IN:
            return unit_prop.get_flow_in_units(input_comm)
        else:
            # OUT, CURTAIL, FLEX all use output commodity units
            return unit_prop.get_flow_out_units(output_comm)

    def write_summary_flow(self, model: TemoaModel, iteration: int | None = None) -> None:
        flow_data = self.calculate_flows(model=model)
        self._insert_summary_flow_results(flow_data=flow_data, iteration=iteration)

    def _insert_summary_flow_results(
        self, flow_data: dict[FI, dict[FlowType, float]], iteration: int | None
    ) -> None:
        if self.tech_sectors is None:
            raise RuntimeError('tech sectors not available... code error')

        scenario = self._get_scenario_name(iteration)
        self.flow_register = flow_data

        # Aggregate flows (sum across seasons/time of day)
        output_flows: defaultdict[tuple[str, Period, str, Technology, Vintage, str], float] = (
            defaultdict(float)
        )

        for fi, flows in self.flow_register.items():
            val = flows.get(FlowType.OUT)
            if val:
                key = (fi.r, fi.p, fi.i, fi.t, fi.v, fi.o)
                output_flows[key] += val

        records = []
        for (r, p, i, t, v, o), val in output_flows.items():
            if abs(val) < self.epsilon:
                continue
            records.append(
                {
                    'scenario': scenario,
                    'region': r,
                    'sector': self.tech_sectors.get(t),
                    'period': p,
                    'input_comm': i,
                    'tech': t,
                    'vintage': v,
                    'output_comm': o,
                    'flow': val,
                    'units': None,
                }
            )

        self._bulk_insert('output_flow_out_summary', records)
        self.connection.commit()

    def check_flow_balance(self, model: TemoaModel) -> bool:
        """Sanity check to ensure that the flow tables are balanced."""
        flows = self.flow_register
        all_good = True

        for fi, flow_vals in flows.items():
            if fi.t in model.tech_storage:
                continue
            if fi.i == 'end_of_life_output' or fi.o == 'construction_input':
                continue

            fin = flow_vals.get(FlowType.IN, 0)
            fout = flow_vals.get(FlowType.OUT, 0)
            flost = flow_vals.get(FlowType.LOST, 0)
            fflex = flow_vals.get(FlowType.FLEX, 0)

            delta = fin - fout - flost - fflex

            # Check logic
            if fin != 0:
                if abs(delta / fin) > 0.02:
                    all_good = False
                    logger.warning('Flow imbalance > 2%% for %s: delta=%.2f', fi, delta)
            elif abs(delta) > 0.02:
                all_good = False
                logger.warning('Flow imbalance (zero input) for %s: delta=%.2f', fi, delta)

        return all_good

    def calculate_flows(self, model: TemoaModel) -> dict[FI, dict[FlowType, float]]:
        return poll_flow_results(model, self.epsilon)

    def write_costs(
        self,
        model: TemoaModel,
        emission_entries: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]]
        | None = None,
        iteration: int | None = None,
    ) -> None:
        if self.config.scenario_mode == TemoaMode.MYOPIC:
            p_0 = model.myopic_discounting_year
        else:
            p_0 = min(model.time_optimize)

        entries, exchange_entries = poll_cost_results(model, value(p_0), self.epsilon)
        self._insert_cost_results(entries, exchange_entries, emission_entries, iteration)

    def _insert_cost_results(
        self,
        regular_entries: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]],
        exchange_entries: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]],
        emission_entries: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]]
        | None,
        iteration: int | None,
    ) -> None:
        if emission_entries:
            # Create a copy to avoid mutating the input
            regular_entries = dict(regular_entries)

            for k, v in emission_entries.items():
                if k in regular_entries:
                    regular_entries[k].update(v)
                else:
                    regular_entries[k] = v

        self._write_cost_rows(regular_entries, iteration)
        self._write_cost_rows(exchange_entries, iteration)

    def _write_cost_rows(
        self,
        entries: dict[tuple[Region, Period, Technology, Vintage], dict[CostType, float]],
        iteration: int | None = None,
    ) -> None:
        if self.tech_sectors is None:
            raise RuntimeError('tech sectors not available... code error')

        scenario = self._get_scenario_name(iteration)
        unit_prop = self.unit_propagator
        records = []

        sorted_keys = sorted(entries.keys())

        for r, p, t, v in sorted_keys:
            costs = entries[(r, p, t, v)]
            records.append(
                {
                    'scenario': scenario,
                    'region': r,
                    'sector': self.tech_sectors.get(t),
                    'period': p,
                    'tech': t,
                    'vintage': v,
                    'd_invest': costs.get(CostType.D_INVEST, 0),
                    'd_fixed': costs.get(CostType.D_FIXED, 0),
                    'd_var': costs.get(CostType.D_VARIABLE, 0),
                    'd_emiss': costs.get(CostType.D_EMISS, 0),
                    'invest': costs.get(CostType.INVEST, 0),
                    'fixed': costs.get(CostType.FIXED, 0),
                    'var': costs.get(CostType.VARIABLE, 0),
                    'emiss': costs.get(CostType.EMISS, 0),
                    'units': unit_prop.get_cost_units() if unit_prop else None,
                }
            )

        self._bulk_insert('output_cost', records)
        self.connection.commit()

    def write_dual_variables(self, results: SolverResults, iteration: int | None = None) -> None:
        scenario = self._get_scenario_name(iteration)
        constraint_data = results['Solution'].Constraint.items()

        records = [
            {
                'scenario': scenario,
                'constraint_name': name,
                'dual': data['Dual'],
            }
            for name, data in constraint_data
        ]
        self._bulk_insert('output_dual_variable', records)
        self.connection.commit()

    def write_tweaks(self, iteration: int, change_records: Iterable[ChangeRecord]) -> None:
        scenario = self._get_scenario_name(iteration)
        records = []

        for cr in change_records:
            records.append(
                {
                    'scenario': scenario,
                    'iteration': iteration,
                    'param_name': cr.param_name,
                    'param_index': str(cr.param_index).replace("'", ''),
                    'old_value': cr.old_value,
                    'new_value': cr.new_value,
                }
            )

        self._bulk_insert('output_mc_delta', records)
        self.connection.commit()

    def execute_script(self, script_file: str | Path | resources.abc.Traversable) -> None:
        if isinstance(script_file, resources.abc.Traversable):
            sql_commands = script_file.read_text()
        else:
            with open(script_file) as table_script:
                sql_commands = table_script.read()

        self.connection.executescript(sql_commands)
        self.connection.commit()

    def make_summary_flow_table(self) -> None:
        self.execute_script(FLOW_SUMMARY_FILE_LOC)

    def make_mc_tweaks_table(self) -> None:
        self.execute_script(MC_TWEAKS_FILE_LOC)

    def __del__(self) -> None:
        self.close()
