# temoa/data_io/hybrid_loader.py
"""
Defines the main data loading engine for the Temoa model.

The primary component of this module is the `HybridLoader` class, which is
responsible for reading, validating, and formatting data from a Temoa SQLite
database for use in a Pyomo model.

Architecture:
    The loader operates on a declarative, manifest-driven architecture. The
    configuration for what data to load is defined externally in
    `temoa.data_io.component_manifest.py`. This separation of concerns means
    that adding new, standard model components often only requires a change to
    the manifest, not this procedural code.

    For components that require complex logic (e.g., conditional queries for
    myopic mode, data aggregation, or dynamic fallbacks), the manifest directs
    the engine to use specialized 'custom loader' methods within the
    `HybridLoader` class.
"""

from __future__ import annotations

import time
from collections import defaultdict
from logging import getLogger
from sqlite3 import Connection, Cursor, OperationalError
from typing import TYPE_CHECKING, cast

from pyomo.core import Param, Set
from pyomo.dataportal import DataPortal

from temoa.core.model import TemoaModel
from temoa.core.modes import TemoaMode
from temoa.data_io.component_manifest import build_manifest
from temoa.extensions.myopic.myopic_index import MyopicIndex
from temoa.model_checking import element_checker, network_model_data
from temoa.model_checking.commodity_network_manager import CommodityNetworkManager
from temoa.model_checking.element_checker import ValidationPrimitive, ViableSet

if TYPE_CHECKING:
    from collections.abc import Sequence

    from temoa.core.config import TemoaConfig
    from temoa.data_io.loader_manifest import LoadItem

logger = getLogger(__name__)

# A manifest of tables that may contain region groups, used by a custom loader.
tables_with_regional_groups = {
    'limit_annual_capacity_factor': 'region',
    'limit_emission': 'region',
    'limit_seasonal_capacity_factor': 'region',
    'limit_capacity': 'region',
    'limit_activity': 'region',
    'limit_new_capacity': 'region',
    'limit_activity_share': 'region',
    'limit_capacity_share': 'region',
    'limit_new_capacity_share': 'region',
    'limit_resource': 'region',
    'limit_growth_capacity': 'region',
    'limit_degrowth_capacity': 'region',
    'limit_growth_new_capacity': 'region',
    'limit_degrowth_new_capacity': 'region',
    'limit_growth_new_capacity_delta': 'region',
    'limit_degrowth_new_capacity_delta': 'region',
}


class HybridLoader:
    """
    Drives the loading of model data from a SQLite database into a format
    suitable for Pyomo's DataPortal.

    This loader is manifest-driven. The `component_manifest.py` file provides a
    declarative list of all components to be loaded, separating the configuration
    of what to load from the procedural logic of how to load it.
    """

    def __init__(self, db_connection: Connection, config: TemoaConfig) -> None:
        """
        Initializes the loader.

        :param db_connection: An active SQLite database connection.
        :param config: The Temoa configuration object.
        """
        self.debugging = False
        self.con = db_connection
        self.config = config
        self.myopic_index: MyopicIndex | None = None

        # Build the data loading manifest and a name-based map for quick lookup
        model = TemoaModel()
        self.manifest = build_manifest(model)
        self.manifest_map = {item.component.name: item for item in self.manifest}

        # --- Data containers and filters populated during loading ---
        self.manager: CommodityNetworkManager | None = None
        self.efficiency_values: list[tuple[object, ...]] = []
        self.data: dict[str, object] | None = None

        # --- Viable sets for source-trace filtering ---
        self.viable_techs: ViableSet | None = None
        self.viable_comms: ViableSet | None = None
        self.viable_input_comms: ViableSet | None = None
        self.viable_output_comms: ViableSet | None = None
        self.viable_vintages: ViableSet | None = None
        self.viable_ritvo: ViableSet | None = None
        self.viable_rpto: ViableSet | None = None
        self.viable_rtv: ViableSet | None = None
        self.viable_rt: ViableSet | None = None
        self.viable_rpit: ViableSet | None = None
        self.viable_rtt: ViableSet | None = None

    def source_trace_only(self, myopic_index: MyopicIndex | None = None) -> None:
        """
        Runs only the source-trace analysis without a full data load.
        This is primarily for the 'check' mode.

        :param myopic_index: The MyopicIndex for the run, if applicable.
        """
        if myopic_index and not isinstance(myopic_index, MyopicIndex):
            raise ValueError('myopic_index must be an instance of MyopicIndex')
        self._source_trace(myopic_index)
        self.manager = None  # Prevent use of stale data

    def load_data_portal(self, myopic_index: MyopicIndex | None = None) -> DataPortal:
        """
        Main entry point to create and load a DataPortal object.

        :param myopic_index: The MyopicIndex for the run, if applicable.
        :return: A populated Pyomo DataPortal object.
        """
        tic = time.time()
        data_dict = self.create_data_dict(myopic_index=myopic_index)

        namespace = {None: data_dict}
        dp = DataPortal(data_dict=namespace)

        toc = time.time()
        logger.debug('Data Portal Load time: %0.5f seconds', (toc - tic))
        return dp

    @staticmethod
    def data_portal_from_data(data_source: dict[str, object]) -> DataPortal:
        """
        Creates a DataPortal object from an existing data dictionary.
        Useful for model runs where the data has been modified in memory.

        :param data_source: The data dictionary to use.
        :return: A new DataPortal object.
        """
        namespace = {None: data_source}
        dp = DataPortal(data_dict=namespace)
        return dp

    # =================================================================================
    # Main Data Loading Engine
    # =================================================================================

    def create_data_dict(self, myopic_index: MyopicIndex | None = None) -> dict[str, object]:
        """
        The main manifest-driven engine for loading model data.

        This method orchestrates the loading process:
        1.  Performs setup (source tracing, critical time sets).
        2.  Iterates through the manifest from `component_manifest.py`.
        3.  For each component, it fetches, filters, and loads the data.
        4.  Delegates to custom loader methods for special cases.
        5.  Finalizes the data dictionary with derived index sets.

        :param myopic_index: The MyopicIndex for myopic runs. None for other modes.
        :return: A dictionary of model data suitable for a DataPortal.
        """
        logger.info('Loading data dictionary')

        # ---------------------------------------------------------------------
        # Preamble: Setup, source tracing, and loading critical index sets
        # ---------------------------------------------------------------------
        if myopic_index:
            if not isinstance(myopic_index, MyopicIndex):
                raise ValueError(f'Received illegal entry for myopic index: {myopic_index}')
            if self.config.scenario_mode != TemoaMode.MYOPIC:
                raise RuntimeError('Myopic Index passed, but mode is not Myopic.')
        elif not myopic_index and self.config.scenario_mode == TemoaMode.MYOPIC:
            raise RuntimeError('Mode is myopic, but no MyopicIndex specified.')

        self.myopic_index = myopic_index

        use_raw_data = not (
            self.config.source_trace or self.config.scenario_mode == TemoaMode.MYOPIC
        )
        if not use_raw_data:
            self._source_trace(myopic_index=myopic_index)

        self._build_efficiency_dataset(use_raw_data=use_raw_data, myopic_index=myopic_index)

        data: dict[str, object] = {}
        cur = self.con.cursor()
        model = TemoaModel()

        # Load critical time sets first, as they index other components
        if myopic_index:
            raw_exist = cur.execute(
                'SELECT period FROM time_period WHERE period < ? ORDER BY sequence',
                (myopic_index.base_year,),
            ).fetchall()
            raw_future = cur.execute(
                'SELECT period FROM time_period WHERE flag = "f" AND period >= ? AND period <= ? '
                'ORDER BY sequence',
                (myopic_index.base_year, myopic_index.last_year),
            ).fetchall()
        else:
            raw_exist = cur.execute(
                "SELECT period FROM time_period WHERE flag = 'e' ORDER BY sequence"
            ).fetchall()
            raw_future = cur.execute(
                "SELECT period FROM time_period WHERE flag = 'f' ORDER BY sequence"
            ).fetchall()
        self._load_component_data(data, model.time_exist, raw_exist)
        self._load_component_data(data, model.time_future, raw_future)
        data['time_optimize'] = [p[0] for p in raw_future[:-1]]

        # ---------------------------------------------------------------------
        # Manifest-driven loading loop
        # ---------------------------------------------------------------------
        for item in self.manifest:
            # 1. Fetch data from the database
            raw_data = self._fetch_data(cur, item, myopic_index)

            # 2. Validate/filter data
            filtered_data = self._filter_data(raw_data, item, use_raw_data)

            # 3. Load data using either a custom loader or the standard path
            if item.custom_loader_name:
                loader_func = getattr(self, item.custom_loader_name)
                loader_func(data, raw_data, filtered_data)
            else:
                # Standard loading path for non-custom components
                if not raw_data and not item.is_table_required and item.fallback_data:
                    logger.warning(
                        "Table '%s' not found or is empty. Using default values for %s.",
                        item.table,
                        item.component.name,
                    )
                    raw_data = item.fallback_data
                    filtered_data = self._filter_data(raw_data, item, use_raw_data)

                if not filtered_data:
                    continue

                if len(filtered_data) < len(raw_data):
                    ignored_count = len(raw_data) - len(filtered_data)
                    logger.warning(
                        '%d values for %s failed to validate and were ignored.',
                        ignored_count,
                        item.component.name,
                    )
                self._load_component_data(data, item.component, filtered_data)

        # ---------------------------------------------------------------------
        # Finalization
        # ---------------------------------------------------------------------
        # Load simple config-based or myopic-specific values
        self._load_component_data(data, model.time_sequencing, [(self.config.time_sequencing,)])
        self._load_component_data(
            data, model.reserve_margin_method, [(self.config.reserve_margin,)]
        )
        if myopic_index:
            p0_result = cur.execute(
                "SELECT min(period) FROM time_period WHERE flag == 'f'"
            ).fetchone()
            if p0_result:
                data[model.myopic_discounting_year.name] = {None: int(p0_result[0])}

        # Create derived index sets for parameters now that all base data is loaded
        set_data = self.load_param_idx_sets(data=data)
        data.update(set_data)
        self.data = data

        return data

    # =================================================================================
    # Core Engine Helpers
    def _fetch_data(
        self, cur: Cursor, item: LoadItem, mi: MyopicIndex | None
    ) -> list[tuple[object, ...]]:
        """
        Fetches data for a component based on its manifest item.

        :param cur: The database cursor.
        :param item: The LoadItem describing what to fetch.
        :param mi: The MyopicIndex for period filtering, if applicable.
        :return: A list of tuples containing the raw data.
        """
        # If this is a custom loader and no columns are specified, no fetch is needed.
        if item.custom_loader_name and not item.columns:
            return []

        if not self.table_exists(item.table):
            if item.is_table_required:
                raise FileNotFoundError(f"Required table '{item.table}' not found in the database.")
            return []

        query = f'SELECT {", ".join(item.columns)} FROM main.{item.table}'
        params = []

        where_clauses = []
        if item.where_clause:
            where_clauses.append(f'({item.where_clause})')
        if item.is_period_filtered and mi:
            where_clauses.append('period >= ? AND period <= ?')
            params.extend([mi.base_year, mi.last_demand_year])

        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)

        try:
            return cur.execute(query, params).fetchall()
        except OperationalError as e:
            if not item.is_table_required:
                logger.info(
                    'Could not load optional component %s, likely due to older schema. Skipping. '
                    'Error: %s',
                    item.component.name,
                    e,
                )
                return []
            else:
                raise

    def _filter_data(
        self, values: Sequence[tuple[object, ...]], item: LoadItem, use_raw_data: bool
    ) -> Sequence[tuple[object, ...]]:
        """
        Applies validation filters to a list of data tuples.

        :param values: The raw data tuples from the database.
        :param item: The LoadItem describing the component.
        :param use_raw_data: If True, skips filtering.
        :return: A filtered sequence of data tuples.
        """
        if use_raw_data or not item.validator_name:
            return values

        validator = getattr(self, item.validator_name, None)
        if validator is None:
            return values

        typed_values = cast('Sequence[tuple[ValidationPrimitive, ...]]', values)
        return element_checker.filter_elements(
            values=typed_values, validation=validator, value_locations=item.validation_map
        )

    def _load_component_data(
        self,
        data: dict[str, object],
        component: Set | Param,
        values: Sequence[tuple[object, ...]],
    ) -> None:
        """
        Loads a sequence of values into the data dictionary for a given Pyomo component.

        :param data: The main data dictionary being built.
        :param component: The Pyomo Set or Param to load.
        :param values: The sequence of data tuples to load.
        """
        if not values:
            return
        if isinstance(component, Set):
            if len(values[0]) == 1:
                data[component.name] = [t[0] for t in values]
            else:
                data[component.name] = list(values)
        elif isinstance(component, Param):
            # A singleton/scalar Param is represented by a single tuple with one
            # element, e.g., [(value,)]. The data dictionary needs to map this
            # to {None: value}. An indexed Param has tuples with len > 1,
            # e.g., [(key1, key2, value)], which map to {(key1, key2): value}.
            if len(values[0]) == 1:
                if len(values) > 1:
                    logger.warning(
                        "Component '%s' appears to be a scalar Param but has multiple values. "
                        'Using only the first value.',
                        component.name,
                    )
                data[component.name] = {None: values[0][0]}
            else:  # Indexed Param
                data[component.name] = {t[:-1]: t[-1] for t in values}

    def table_exists(self, table_name: str) -> bool:
        """
        Checks if a table exists in the database schema.

        :param table_name: The name of the table to check.
        :return: True if the table exists, False otherwise.
        """
        table_name_check = (
            self.con.cursor()
            .execute("SELECT name FROM sqlite_master WHERE type='table' AND name= ?", (table_name,))
            .fetchone()
        )
        return bool(table_name_check)

    # =================================================================================
    # Internal Setup Methods
    # =================================================================================

    def _source_trace(self, myopic_index: MyopicIndex | None = None) -> None:
        """
        Performs the source-trace analysis to identify viable components.
        """
        network_data = network_model_data.build(self.con, myopic_index)
        cur = self.con.cursor()
        periods = set(
            [
                p
                for (p,) in cur.execute(
                    "SELECT period FROM time_period WHERE flag = 'f' ORDER BY period"
                )
            ][:-1]  # drop last period
        )

        if myopic_index:
            periods = {
                p for p in periods if myopic_index.base_year <= p <= myopic_index.last_demand_year
            }

        self.manager = CommodityNetworkManager(periods=periods, network_data=network_data)
        if not self.manager.analyze_network() and not self.config.silent:
            print('\nWarning:  Orphaned processes detected.  See log file for details.')
        self.manager.analyze_graphs(self.config)

    def _build_efficiency_dataset(
        self, use_raw_data: bool, myopic_index: MyopicIndex | None = None
    ) -> None:
        """
        Builds the efficiency dataset, applying source-trace filters if necessary.
        """
        cur = self.con.cursor()
        if myopic_index:
            contents = cur.execute(
                'SELECT region, input_comm, tech, vintage, output_comm, efficiency, lifetime '
                'FROM myopic_efficiency WHERE vintage + lifetime > ?',
                (myopic_index.base_year,),
            ).fetchall()
        else:
            contents = cur.execute(
                'SELECT region, input_comm, tech, vintage, output_comm, efficiency, NULL FROM '
                'main.efficiency'
            ).fetchall()

        if use_raw_data:
            self.efficiency_values = sorted([row[:-1] for row in contents])
            return

        if not self.manager:
            raise RuntimeError('Source trace manager not initialized for filtering.')

        filts = self.manager.build_filters()
        self.viable_ritvo = filts['ritvo']
        self.viable_rtv = filts['rtv']
        self.viable_rt = filts['rt']
        self.viable_rpit = filts['rpit']
        self.viable_rpto = filts['rpto']
        self.viable_techs = filts['t']
        self.viable_input_comms = filts['ic']
        self.viable_output_comms = filts['oc']

        # NOTE: Using member_tuples here is safer as it's unambiguously typed
        ic_tuples = self.viable_input_comms.member_tuples
        oc_tuples = self.viable_output_comms.member_tuples
        self.viable_comms = ViableSet(elements=ic_tuples | oc_tuples)

        rt_tuples = filts['rt'].member_tuples
        t_tuples = filts['t'].member_tuples
        rtt = {(r, t1, t2) for r, t1 in rt_tuples for (t2,) in t_tuples}
        self.viable_rtt = ViableSet(
            elements=rtt, exception_loc=0, exception_vals=ViableSet.REGION_REGEXES
        )

        efficiency_entries = {
            row[:-1]
            for row in contents
            if (row[0], row[1], row[2], row[3], row[4]) in self.viable_ritvo.members
        }
        logger.debug('Polled %d elements from efficiency tables', len(efficiency_entries))
        self.efficiency_values = sorted(efficiency_entries)

    # =================================================================================
    # Custom Loaders (Grouped by Cohesion)
    # =================================================================================

    # --- Core Model Structure ---
    def _load_regional_global_indices(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """
        Aggregates region and group names from the Region table and all Limit tables.
        """
        model = TemoaModel()
        cur = self.con.cursor()
        regions_and_groups: set[str] = set()

        if self.table_exists('region'):
            regions_and_groups.update(
                t[0] for t in cur.execute('SELECT region FROM main.region').fetchall()
            )

        for table, field_name in tables_with_regional_groups.items():
            if self.table_exists(table):
                regions_and_groups.update(
                    t[0] for t in cur.execute(f'SELECT {field_name} FROM main.{table}').fetchall()
                )

        if None in regions_and_groups:
            raise ValueError('A table has an empty entry for its region column.')

        list_of_groups = sorted((t,) for t in regions_and_groups)
        self._load_component_data(data, model.regional_global_indices, list_of_groups)

    def _load_tech_group_members(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Loads members into the indexed set `tech_group_members`."""
        model = TemoaModel()
        validator = self.viable_techs.members if self.viable_techs else None
        for group_name, tech in filtered_data:
            if validator is None or tech in validator:
                store = data.get(model.tech_group_members.name, defaultdict(list))
                store[group_name].append(tech)  # type: ignore[index]
                data[model.tech_group_members.name] = store

    # --- Time-Related Components ---
    def _load_time_season(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """
        Loads time_season_all (simple set of all seasons) and time_season
        (indexed set mapping periods to seasons), with a dynamic fallback
        if the table is missing.
        """
        model = TemoaModel()
        mi = self.myopic_index
        time_optimize = cast('list[int]', data.get('time_optimize', []))

        rows_to_load: list[tuple[object, ...]] = []
        if not raw_data:
            logger.warning('No time_season table found. Loading a single filler season "S".')
            rows_to_load = [(p, 'S') for p in time_optimize]
        elif mi:
            valid_periods = set(time_optimize)
            rows_to_load = [row for row in raw_data if row[0] in valid_periods]
        else:
            rows_to_load = list(raw_data)

        if not rows_to_load:
            data.setdefault(model.time_season_all.name, [])
            return

        unique_seasons = sorted({(row[1],) for row in rows_to_load})
        self._load_component_data(data, model.time_season_all, unique_seasons)

        for period, season in rows_to_load:
            store = data.get(model.time_season.name, defaultdict(list))
            store[period].append(season)  # type: ignore[index]
            data[model.time_season.name] = store

    def _load_time_season_sequential(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """
        Composite loader for time_season_sequential and its associated index sets.
        """
        model = TemoaModel()
        self._load_component_data(data, model.time_season_sequential, filtered_data)
        if filtered_data:
            ordered_data = [row[0:3] for row in filtered_data]
            self._load_component_data(data, model.ordered_season_sequential, ordered_data)
            seq_data = sorted({(row[1],) for row in filtered_data})
            self._load_component_data(data, model.time_season_to_sequential, seq_data)

    def _load_segment_fraction(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Handles dynamic fallbacks for segment_fraction if its table is missing."""
        model = TemoaModel()
        if filtered_data:
            self._load_component_data(data, model.segment_fraction, filtered_data)
        else:
            logger.warning(
                'No segment_fraction table found. Generating default segment_fraction values.'
            )
            time_optimize = data.get('time_optimize', [])
            fallback = [(p, 'S', 'D', 1.0) for p in time_optimize]  # type: ignore[attr-defined]
            self._load_component_data(data, model.segment_fraction, fallback)

    # --- Capacity and Cost Components ---
    def _load_existing_capacity(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """
        Handles different queries for myopic vs. standard runs and also
        populates the `tech_exist` set.
        """
        model = TemoaModel()
        cur = self.con.cursor()
        mi = self.myopic_index

        rows_to_load = []
        if mi:
            prev_period_res = cur.execute(
                'SELECT MAX(period) FROM time_period WHERE period < ?', (mi.base_year,)
            ).fetchone()
            prev_period = prev_period_res[0] if prev_period_res else -1
            rows_to_load = cur.execute(
                'SELECT region, tech, vintage, capacity FROM output_built_capacity WHERE '
                'vintage <= ? AND scenario = ? '
                'UNION SELECT region, tech, vintage, capacity FROM existing_capacity',
                (prev_period, self.config.scenario),
            ).fetchall()
        elif self.table_exists('existing_capacity'):
            rows_to_load = cur.execute(
                'SELECT region, tech, vintage, capacity FROM existing_capacity'
            ).fetchall()

        self._load_component_data(data, model.existing_capacity, rows_to_load)
        if rows_to_load:
            tech_exist_data = sorted({(row[1],) for row in rows_to_load})
            self._load_component_data(data, model.tech_exist, tech_exist_data)

    def _load_cost_invest(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Handles myopic period filtering for cost_invest."""
        model = TemoaModel()
        base_year = self.myopic_index.base_year if self.myopic_index else None
        data_to_load = [
            row for row in filtered_data if base_year is None or cast('int', row[2]) >= base_year
        ]
        self._load_component_data(data, model.cost_invest, data_to_load)

    def _load_loan_rate(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Handles myopic period filtering for loan_rate."""
        model = TemoaModel()
        mi = self.myopic_index
        data_to_load = [row for row in filtered_data if not mi or row[2] >= mi.base_year]  # type: ignore[operator]
        self._load_component_data(data, model.loan_rate, data_to_load)

    # --- Singleton and Configuration-based Components ---
    def _load_days_per_period(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Loads the singleton days_per_period, with a fallback."""
        model = TemoaModel()
        days = 365
        if filtered_data:
            days = cast('int', filtered_data[0][0])
        else:
            logger.info('No value for days_per_period found. Assuming 365 days per period.')
        data[model.days_per_period.name] = {None: days}

    def _load_global_discount_rate(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Loads the required singleton global_discount_rate."""
        model = TemoaModel()
        if filtered_data:
            data[model.global_discount_rate.name] = {None: cast('float', filtered_data[0][0])}
        else:
            raise ValueError(
                "Missing required parameter: 'global_discount_rate' not found in MetaDataReal "
                'table.'
            )

    def _load_default_loan_rate(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Loads the optional singleton default_loan_rate."""
        model = TemoaModel()
        if filtered_data:
            data[model.default_loan_rate.name] = {None: cast('float', filtered_data[0][0])}

    # --- Operational Constraints and Parameters ---
    def _load_efficiency(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Loads the main efficiency parameter, which is pre-calculated."""
        model = TemoaModel()
        self._load_component_data(data, model.efficiency, self.efficiency_values)

    def _load_linked_techs(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Provides critical error checking for linked_techs."""
        item = self.manifest_map['linked_techs']
        self._load_component_data(data, item.component, filtered_data)
        if len(filtered_data) < len(raw_data):
            missing = set(raw_data) - set(filtered_data)
            valid_techs = self.viable_techs.members if self.viable_techs else set()
            for entry in missing:
                p_tech, d_tech = entry[1], entry[3]
                if p_tech in valid_techs or d_tech in valid_techs:
                    msg = (
                        'A LinkedTech entry %s was invalidated, but one of its component '
                        'technologies '
                        'remains viable. This could lead to incorrect model behavior.'
                    )
                    logger.error(msg, entry)
                    raise RuntimeError(msg % (entry,))

    def _load_ramping_down(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Composite loader for ramp_down_hourly and its index set `tech_downramping`."""
        model = TemoaModel()
        self._load_component_data(data, model.ramp_down_hourly, filtered_data)
        if filtered_data:
            tech_data = sorted({(row[1],) for row in filtered_data})
            tech_filtered = self._filter_data(
                tech_data, self.manifest_map[model.tech_downramping.name], use_raw_data=False
            )
            self._load_component_data(data, model.tech_downramping, tech_filtered)

    def _load_ramping_up(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Composite loader for ramp_up_hourly and its index set `tech_upramping`."""
        model = TemoaModel()
        self._load_component_data(data, model.ramp_up_hourly, filtered_data)
        if filtered_data:
            tech_data = sorted({(row[1],) for row in filtered_data})
            tech_filtered = self._filter_data(
                tech_data, self.manifest_map[model.tech_upramping.name], use_raw_data=False
            )
            self._load_component_data(data, model.tech_upramping, tech_filtered)

    def _load_rps_requirement(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Handles deprecation warning for renewable_portfolio_standard."""
        model = TemoaModel()
        self._load_component_data(data, model.renewable_portfolio_standard, filtered_data)
        if filtered_data:
            logger.warning(
                'The renewable_portfolio_standard constraint is deprecated. Use '
                'limit_activity_share instead. '
                'The constraint has been applied but this feature may be removed in the future.'
            )

    def _load_limit_tech_input_split(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Provides detailed warnings for filtered limit_tech_input_split data."""
        item = self.manifest_map['limit_tech_input_split']
        self._load_component_data(data, item.component, filtered_data)
        if len(filtered_data) < len(raw_data):
            missing = set(raw_data) - set(filtered_data)
            for r, p, i, t, _, _ in sorted(missing, key=lambda x: (x[0], x[1], x[3], x[2])):
                logger.warning(
                    'Tech Input Split in region %s, period %d for tech %s with input %s '
                    'was removed because the path is invalid/orphaned. Review other warnings.',
                    r,
                    p,
                    t,
                    i,
                )

    def _load_limit_tech_input_split_annual(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Provides detailed warnings for filtered limit_tech_input_split_annual data."""
        item = self.manifest_map['limit_tech_input_split_annual']
        self._load_component_data(data, item.component, filtered_data)
        if len(filtered_data) < len(raw_data):
            missing = set(raw_data) - set(filtered_data)
            for r, p, i, t, _, _ in sorted(missing, key=lambda x: (x[0], x[1], x[3], x[2])):
                logger.warning(
                    'Tech Input Split Annual in region %s, period %d for tech %s with input %s '
                    'was removed because the path is invalid/orphaned. Review other warnings.',
                    r,
                    p,
                    t,
                    i,
                )

    def _load_limit_tech_output_split(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Provides detailed warnings for filtered limit_tech_output_split data."""
        item = self.manifest_map['limit_tech_output_split']
        self._load_component_data(data, item.component, filtered_data)
        if len(filtered_data) < len(raw_data):
            missing = set(raw_data) - set(filtered_data)
            for r, p, t, o, _, _ in sorted(missing, key=lambda x: (x[0], x[1], x[2], x[3])):
                logger.warning(
                    'Tech Output Split in region %s, period %d for tech %s with output %s '
                    'was removed because the path is invalid/orphaned. Review other warnings.',
                    r,
                    p,
                    t,
                    o,
                )

    def _load_limit_tech_output_split_annual(
        self,
        data: dict[str, object],
        raw_data: Sequence[tuple[object, ...]],
        filtered_data: Sequence[tuple[object, ...]],
    ) -> None:
        """Provides detailed warnings for filtered limit_tech_output_split_annual data."""
        item = self.manifest_map['limit_tech_output_split_annual']
        self._load_component_data(data, item.component, filtered_data)
        if len(filtered_data) < len(raw_data):
            missing = set(raw_data) - set(filtered_data)
            for r, p, t, o, _, _ in sorted(missing, key=lambda x: (x[0], x[1], x[2], x[3])):
                logger.warning(
                    'Tech Output Split Annual in region %s, period %d for tech %s with output %s '
                    'was removed because the path is invalid/orphaned. Review other warnings.',
                    r,
                    p,
                    t,
                    o,
                )

    # =================================================================================
    # Finalizer Method
    # =================================================================================

    def load_param_idx_sets(self, data: dict[str, object]) -> dict[str, object]:
        """
        Builds a dictionary of sparse sets used for indexing parameters.
        This is a final data enhancement step that runs after all primary data
        has been loaded.

        :param data: The main data dictionary.
        :return: A dictionary of the new index sets to be added.
        """
        model = TemoaModel()
        param_idx_sets = {
            model.cost_invest.name: model.cost_invest_rtv.name,
            model.cost_emission.name: model.cost_emission_rpe.name,
            model.demand.name: model.demand_constraint_rpc.name,
            model.limit_emission.name: model.limit_emission_constraint_rpe.name,
            model.limit_activity.name: model.limit_activity_constraint_rpt.name,
            model.limit_seasonal_capacity_factor.name: (
                model.limit_seasonal_capacity_factor_constraint_rpst.name
            ),
            model.limit_activity_share.name: model.limit_activity_share_constraint_rpgg.name,
            model.limit_annual_capacity_factor.name: (
                model.limit_annual_capacity_factor_constraint_rpto.name
            ),
            model.limit_capacity.name: model.limit_capacity_constraint_rpt.name,
            model.limit_capacity_share.name: model.limit_capacity_share_constraint_rpgg.name,
            model.limit_new_capacity.name: model.limit_new_capacity_constraint_rpt.name,
            model.limit_new_capacity_share.name: (
                model.limit_new_capacity_share_constraint_rpgg.name
            ),
            model.limit_resource.name: model.limit_resource_constraint_rt.name,
            model.limit_storage_fraction.name: model.limit_storage_fraction_constraint_rpsdtv.name,
            model.renewable_portfolio_standard.name: (
                model.renewable_portfolio_standard_constraint_rpg.name
            ),
        }

        res: dict[str, object] = {}
        for p_name, s_name in param_idx_sets.items():
            param_data = data.get(p_name)
            if isinstance(param_data, dict):
                res[s_name] = list(param_data.keys())
        return res
