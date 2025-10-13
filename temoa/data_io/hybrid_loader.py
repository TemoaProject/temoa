import sys
import time
from collections import defaultdict
from logging import getLogger
from sqlite3 import Connection, Cursor, OperationalError
from typing import Sequence

from pyomo.core import Param, Set
from pyomo.dataportal import DataPortal

from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel
from temoa.core.modes import TemoaMode
from temoa.data_io.component_manifest import build_manifest
from temoa.data_io.loader_manifest import LoadItem
from temoa.extensions.myopic.myopic_index import MyopicIndex
from temoa.model_checking import element_checker, network_model_data
from temoa.model_checking.commodity_network_manager import CommodityNetworkManager
from temoa.model_checking.element_checker import ViableSet

logger = getLogger(__name__)

# the tables below are ones in which we might find regional groups which should be captured
# to make the members of the RegionalGlobalIndices Set in the model.  They need to aggregated
tables_with_regional_groups = {
    'LimitAnnualCapacityFactor': 'region',
    'LimitEmission': 'region',
    'LimitSeasonalCapacityFactor': 'region',
    'LimitCapacity': 'region',
    'LimitActivity': 'region',
    'LimitNewCapacity': 'region',
    'LimitActivityShare': 'region',
    'LimitCapacityShare': 'region',
    'LimitNewCapacityShare': 'region',
    'LimitResource': 'region',
    'LimitGrowthCapacity': 'region',
    'LimitDegrowthCapacity': 'region',
    'LimitGrowthNewCapacity': 'region',
    'LimitDegrowthNewCapacity': 'region',
    'LimitGrowthNewCapacityDelta': 'region',
    'LimitDegrowthNewCapacityDelta': 'region',
}


class HybridLoader:
    """
    An instance of the HybridLoader
    """

    def __init__(self, db_connection: Connection, config: TemoaConfig):
        """
        build a loader for an instance.
        :param db_connection: a Connection to the database
        :param config: the config, which controls some options during execution
        """
        self.debugging = False  # for T/S, will print to screen the data load values
        self.con = db_connection
        self.config = config

        # Build the data loading manifest
        M = TemoaModel()
        self.manifest = build_manifest(M)
        self.manifest_map = {item.component.name: item for item in self.manifest}

        self.manager: CommodityNetworkManager | None = None

        # filters for myopic ops
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
        self.viable_rtt: ViableSet | None = None  # to support scanning LinkedTech
        self.efficiency_values: list[tuple] = []

        # container for loaded data
        self.data: dict | None = None

    def source_trace_only(self, make_plots: bool = False, myopic_index: MyopicIndex | None = None):
        if myopic_index and not isinstance(myopic_index, MyopicIndex):
            raise ValueError('myopic_index must be an instance of MyopicIndex')
        self._source_trace(myopic_index)
        self.manager = None  # to prevent possible out-of-synch build from stale data

    def _source_trace(self, myopic_index: MyopicIndex = None):
        network_data = network_model_data.build(self.con, myopic_index=myopic_index)
        cur = self.con.cursor()
        # need periods to execute the source check by [r, p].  At this point, we can only pull from DB
        periods = {
            period for (period, *_) in cur.execute("SELECT period FROM TimePeriod WHERE flag = 'f'")
        }
        # we need to exclude the last period, it is a non-demand year
        periods = sorted(periods)[:-1]

        if myopic_index:
            periods = {
                p for p in periods if myopic_index.base_year <= p <= myopic_index.last_demand_year
            }
        self.manager = CommodityNetworkManager(periods=periods, network_data=network_data)
        all_regions_clean = self.manager.analyze_network()
        if not all_regions_clean and not self.config.silent:
            print('\nWarning:  Orphaned processes detected.  See log file for details.')
        self.manager.analyze_graphs(self.config)

    def _build_efficiency_dataset(
        self, use_raw_data=False, myopic_index: MyopicIndex | None = None
    ):
        """
        Build the efficiency dataset.  For myopic mode, this means pull from MyopicEfficiency table
        and we cannot use raw data.  For other modes, we can either use raw data or the filtered data
        provided by the manager (normal)
        :param use_raw_data: if True, use raw data (without source-trace filtering) for build
        :param myopic_index: the myopic index to use (or None for other modes)
        :return:
        """
        if myopic_index and use_raw_data:
            raise RuntimeError('Cannot build from raw data in myopic mode...  Likely coding error.')
        cur = self.con.cursor()
        # pull the data based on whether myopic/not
        if myopic_index:
            # pull from MyopicEfficiency, and filter by myopic index years
            contents = cur.execute(
                'SELECT region, input_comm, tech, vintage, output_comm, efficiency, lifetime  '
                'FROM MyopicEfficiency '
                'WHERE vintage + lifetime > ?',
                (myopic_index.base_year,),
            ).fetchall()
        else:
            # pull from regular Efficiency table
            contents = cur.execute(
                'SELECT region, input_comm, tech, vintage, output_comm, efficiency, NULL FROM main.Efficiency'
            ).fetchall()

        # set up filters, if requested...
        if use_raw_data:
            efficiency_entries = [row[:-1] for row in contents]

        else:  # (always must when myopic)
            if self.manager:
                filts = self.manager.build_filters()
            else:
                raise RuntimeError('trying to filter, but manager has not analyzed network yet.')
            self.viable_ritvo = filts['ritvo']
            self.viable_rtv = filts['rtv']
            self.viable_rt = filts['rt']
            self.viable_rpit = filts['rpit']
            self.viable_rpto = filts['rpto']
            self.viable_techs = filts['t']
            self.viable_input_comms = filts['ic']
            self.viable_vintages = filts['v']
            self.viable_output_comms = filts['oc']
            self.viable_comms = ViableSet(
                elements=self.viable_input_comms.members | self.viable_output_comms.members
            )
            rtt = {
                (r, t1, t2) for r, t1 in self.viable_rt.members for t2 in self.viable_techs.members
            }
            self.viable_rtt = ViableSet(
                elements=rtt, exception_loc=0, exception_vals=ViableSet.REGION_REGEXES
            )
            efficiency_entries = {
                (r, i, t, v, o, eff)
                for r, i, t, v, o, eff, lifetime in contents
                if (r, i, t, v, o) in self.viable_ritvo.members
            }
        logger.debug('polled %d elements from MyopicEfficiency table', len(efficiency_entries))

        # book the EfficiencyTable
        # we should sort here for deterministic results after pulling from set
        self.efficiency_values = sorted(efficiency_entries)

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the schema... for use with "optional" tables
        :param table_name: the table name to check
        :return: True if it exists in the schema
        """
        table_name_check = (
            self.con.cursor()
            .execute("SELECT name FROM sqlite_master WHERE type='table' AND name= ?", (table_name,))
            .fetchone()
        )
        if table_name_check:
            return True
        logger.info('Did not find existing table for (optional) table:  %s', table_name)
        return False

        pass

    def load_data_portal(self, myopic_index: MyopicIndex | None = None) -> DataPortal:
        # time the creation of the data portal
        tic = time.time()
        data_dict = self.create_data_dict(myopic_index=myopic_index)

        # pyomo namespace format has data[namespace][idx]=value
        # the default namespace is None, thus...
        namespace = {None: data_dict}
        if self.debugging:
            for item in namespace[None].items():
                print(item[0], item[1])
        dp = DataPortal(data_dict=namespace)
        toc = time.time()
        logger.debug('Data Portal Load time: %0.5f seconds', (toc - tic))
        return dp

    @staticmethod
    def data_portal_from_data(data_source: dict) -> DataPortal:
        """
        Create a DataPortal object from a data dictionary.  Useful when the data has been modified
        :param data_source: the dataset to use
        :return: a new DataPortal object
        """
        namespace = {None: data_source}
        dp = DataPortal(data_dict=namespace)
        return dp

    def create_data_dict(self, myopic_index: MyopicIndex | None = None) -> dict:
        """
        Create and Load a Data Portal.  If source tracing is enabled in the config, the source trace will
        be executed and filtered data will be used.  Without source-trace, raw (unfiltered) data will be loaded.
        :param myopic_index: the MyopicIndex for myopic run.  None for other modes
        :return:
        """
        logger.info('Loading data dictionary')

        # ---------------------------------------------------------------------
        # Preamble: Setup, source tracing, and loading critical index sets
        # ---------------------------------------------------------------------
        if myopic_index is not None:
            if not isinstance(myopic_index, MyopicIndex):
                raise ValueError(f'received an illegal entry for the myopic index: {myopic_index}')
            if self.config.scenario_mode != TemoaMode.MYOPIC:
                raise RuntimeError('Myopic Index passed, but mode is not Myopic.')
        elif myopic_index is None and self.config.scenario_mode == TemoaMode.MYOPIC:
            raise RuntimeError('Mode is myopic, but no MyopicIndex specified.')

        if self.config.source_trace or self.config.scenario_mode == TemoaMode.MYOPIC:
            use_raw_data = False
            self._source_trace(myopic_index=myopic_index)
        else:
            use_raw_data = True

        self._build_efficiency_dataset(use_raw_data=use_raw_data, myopic_index=myopic_index)
        mi = myopic_index  # convenience

        data: dict[str, list | dict] = {}
        cur = self.con.cursor()

        M = TemoaModel()

        # Load critical time sets first, as they are used to index other components
        if mi:
            raw_exist = cur.execute(
                'SELECT period FROM main.TimePeriod WHERE period < ? ORDER BY sequence',
                (mi.base_year,),
            ).fetchall()
            raw_future = cur.execute(
                'SELECT period FROM main.TimePeriod WHERE flag = "f" AND period >= ? AND period <= ? ORDER BY sequence',
                (mi.base_year, mi.last_year),
            ).fetchall()
        else:
            raw_exist = cur.execute(
                "SELECT period FROM main.TimePeriod WHERE flag = 'e' ORDER BY sequence"
            ).fetchall()
            raw_future = cur.execute(
                "SELECT period FROM main.TimePeriod WHERE flag = 'f' ORDER BY sequence"
            ).fetchall()
        self._load_component_data(data, M.time_exist, raw_exist)
        self._load_component_data(data, M.time_future, raw_future)
        time_optimize = [p[0] for p in raw_future[0:-1]]

        # ---------------------------------------------------------------------
        # Manifest-driven loading for migrated components
        # ---------------------------------------------------------------------

        # Run the manifest-based loader first for migrated components
        for item in self.manifest:
            if item.is_table_required and not self.table_exists(item.table):
                logger.info(f"Skipping {item.component.name}: table '{item.table}' not found.")
                continue

            # 1. Get raw data from the database
            raw_data = self._fetch_data(cur, item, myopic_index)
            if not raw_data:
                continue

            # 2. Validate/filter data
            filtered_data = self._filter_data(raw_data, item, use_raw_data)

            # 3. Load into the data dictionary
            self._load_component_data(data, item.component, filtered_data)

        # ---------------------------------------------------------------------
        # Legacy loader for components pending migration
        # ---------------------------------------------------------------------

        # Call the legacy loader and pass it the data dictionary to populate.
        # As we migrate components to the manifest, they will be removed from the legacy method.
        self._create_data_dict_legacy(
            myopic_index=mi, data=data, use_raw_data=use_raw_data, time_optimize=time_optimize
        )

        return data

    def _fetch_data(self, cur: Cursor, item: LoadItem, mi: MyopicIndex | None) -> list[tuple]:
        """Fetches data for a component based on its manifest item."""
        query = f'SELECT {", ".join(item.columns)} FROM main.{item.table}'
        params = []

        # Combine WHERE clauses
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
            # This can happen if a column doesn't exist (e.g., unlim_cap)
            if item.is_table_required is False:
                logger.info(
                    f'Could not load optional component {item.component.name}, likely due to older schema. Skipping. Error: {e}'
                )
                return []
            else:
                raise e

    def _filter_data(
        self, values: Sequence[tuple], item: LoadItem, use_raw_data: bool
    ) -> Sequence[tuple]:
        """Applies validation filters to a list of data tuples."""
        if use_raw_data or not item.validator_name:
            return values

        validator = getattr(self, item.validator_name, None)
        if validator is None:
            # This can happen if source tracing isn't run, which is valid.
            # In that case, no filtering should occur.
            return values

        return element_checker.filter_elements(
            values=values, validation=validator, value_locations=item.validation_map
        )

    def _load_component_data(
        self, data: dict, component: Set | Param, values: Sequence[tuple]
    ) -> None:
        """Loads a sequence of values into the data dictionary for the given component."""
        if not values:
            return
        if isinstance(component, Set):
            if len(values[0]) == 1:  # A simple set of single values
                data[component.name] = [t[0] for t in values]
            else:  # A set of tuples
                data[component.name] = list(values)
        elif isinstance(component, Param):
            data[component.name] = {t[:-1]: t[-1] for t in values}

    def _create_data_dict_legacy(
        self,
        myopic_index: MyopicIndex | None,
        data: dict,
        use_raw_data: bool,
        time_optimize: list[int],
    ) -> None:
        """
        The original, monolithic data loading method. This will be incrementally
        refactored until it is empty. It now populates a dictionary passed to it.
        """

        mi = myopic_index  # convenience

        def load_element(
            c: Set | Param,
            values: Sequence[tuple],
            validation: ViableSet | None = None,
            val_loc: tuple = (0,),
        ) -> Sequence[tuple]:
            """
            Helper to alleviate some typing!
            Expects that the values passed in are an iterable of tuples, like a standard
            query result.  Note that any filtering is disregarded if there is no myopic index in use
            :param c: the model component to load
            :param values: the keys for param or the item values for set as tuples (should be Sequence to help
            get deterministic results)
            :param validation: the set to validate the keys/set value against
            :param val_loc: tuple of the positions of r, t, v in the key for validation
            :return: a sequence of the values loaded
            """
            if len(values) == 0:
                logger.info('table, but no (usable) values for param or set: %s', c.name)
                return []
            if not isinstance(values[0], tuple):
                raise ValueError('values must be an iterable of tuples')

            if use_raw_data or validation is None:
                screened = list(values)
            else:
                try:
                    screened = element_checker.filter_elements(
                        values=values, validation=validation, value_locations=val_loc
                    )
                except ValueError as e:
                    raise ValueError(
                        'Failed to validate members of %s.  Coding error likely.\n%s' % (c.name, e)
                    ) from e
            if len(screened) < len(values):
                msg = 'Some values for {} failed to validate and were ignored: {}'
                logger.warning(msg.format(c.name, [val for val in values if val not in screened]))
            match c:
                case Set():
                    if not screened:  # no available values
                        data[c.name] = []
                    elif len(screened[0]) == 1:  # set of individual values
                        data[c.name] = [t[0] for t in screened]
                    else:  # set of tuples, pass directly...
                        data[c.name] = screened
                case Param():
                    data[c.name] = {t[:-1]: t[-1] for t in screened}
            return screened

        def load_indexed_set(indexed_set: Set, index_value, element, element_validator=None):
            """
            load an element into an indexed set in the data store
            :param indexed_set: the name of the pyomo Set
            :param index_value: the index value to load into
            :param element: the value to add to the indexed set
            :param element_validator: a set of legal elements for the element to be added, or None for all elements
            :return: None
            """
            if element_validator and element not in element_validator:
                return
            data_store = data.get(indexed_set.name, defaultdict(list))
            data_store[index_value].append(element)
            data[indexed_set.name] = data_store

        M: TemoaModel = TemoaModel()  # for typing purposes only
        cur = self.con.cursor()

        #   === TIME SETS ===

        # time_of_day
        if self.table_exists('TimeOfDay'):
            raw = cur.execute('SELECT tod FROM main.TimeOfDay ORDER BY sequence').fetchall()
            load_element(M.time_of_day, raw)
        else:
            logger.warning(
                'No TimeOfDay table found. Loading a single filler time of day "D" (assume this is an annual model)'
            )
            load_element(M.time_of_day, [('D',)])

        # TimeSequencing
        time_sequencing = self.config.time_sequencing
        match time_sequencing:
            case 'seasonal_timeslices' | 'representative_periods' | 'consecutive_days':
                pass
            case 'manual':
                # This is a hidden feature allowing the user to manually specify the sequence of states using the TimeNext table
                if self.table_exists('TimeNext'):
                    raw = self.raw_check_mi_period(
                        mi,
                        cur=cur,
                        qry='SELECT period, season, tod, season_next, tod_next FROM main.TimeNext',
                    )
                    load_element(M.TimeNext, raw)
                else:
                    # Hidden feature unlocked but not setup! Give a nice long explanation
                    msg = (
                        'Tried to manually sequence time slices using TimeNext but the table did not exist. '
                        "With time_sequencing set to 'manual' in the config file, the sequence of time slices will be pulled "
                        'directly from the TimeNext table, where each row defines the next time slice in the order. '
                        'This is an advanced feature and not recommended for most users. If you do NOT want to '
                        'manually define the sequence of time slices, change the time_sequencing parameter. Otherwise '
                        'the TimeNext table can be found commented out in the v3.1 schema.'
                    )
                    logger.error(msg)
                    raise ValueError(msg)
            case _:
                msg = (
                    f"Invalid time sequencing parameter '{time_sequencing}'. Check the config file."
                )
                logger.error(msg)
                raise ValueError(msg)
        load_element(M.TimeSequencing, [(time_sequencing,)])

        # ReserveMarginMethod
        load_element(M.ReserveMarginMethod, [(self.config.reserve_margin,)])

        # myopic_base_year
        if mi:
            # assume first future period by default
            p0 = cur.execute("SELECT min(period) FROM TimePeriod WHERE flag == 'f'").fetchone()
            # load as a singleton...
            data[M.MyopicDiscountingYear.name] = {None: int(p0[0])}

        # days_per_season
        raw = cur.execute(
            "SELECT value from MetaData WHERE element == 'days_per_period'"
        ).fetchall()
        if not raw:
            logger.info(
                'No value found for days_per_period in the MetaData table. '
                'Assuming this is an annual database (365 days per period)'
            )
            raw = [(365,)]
        data[M.DaysPerPeriod.name] = {None: int(raw[0][0])}

        #  === REGION SETS ===

        # region-groups  (these are the R1+R2, R1+R4+R6 type region labels) AND regular region names
        # currently, we just load all the indices from the tables that could employ them.
        # the validator is used to ensure they are legit.  (see temoa_model)
        regions_and_groups = set()
        for table, field_name in tables_with_regional_groups.items():
            if self.table_exists(table):
                raw = cur.execute(f'SELECT {field_name} from main.{table}').fetchall()
                regions_and_groups.update({t[0] for t in raw})
                if None in regions_and_groups:
                    raise ValueError('Table %s appears to have an empty entry for region.' % table)
        # sort (for deterministic pyomo behavior)
        list_of_groups = sorted((t,) for t in regions_and_groups)
        load_element(M.regionalGlobalIndices, list_of_groups)

        # region-exchanges
        # auto-generated

        #  === TECH SETS ===

        # tech_resource # devnote: not used anywhere
        # raw = cur.execute("SELECT tech FROM main.Technology WHERE flag = 'r'").fetchall()
        # load_element(M.tech_resource, raw, self.viable_techs)

        # groups & tech_groups (supports RPS and general tech grouping)

        if self.table_exists('TechGroupMember'):
            raw = cur.execute('SELECT group_name, tech FROM main.TechGroupMember').fetchall()
            validator = self.viable_techs.members if self.viable_techs else None
            for row in raw:
                load_indexed_set(
                    M.tech_group_members,
                    index_value=row[0],
                    element=row[1],
                    element_validator=validator,
                )

        #  === COMMODITIES ===

        #  === OPERATORS ===

        #  === PARAMS ===

        # Efficiency
        # we have already computed/filtered this... no need for another data pull
        raw = self.efficiency_values
        load_element(M.Efficiency, raw)

        # EfficiencyVariable
        if self.table_exists('EfficiencyVariable'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, season, tod, input_comm, tech, vintage, output_comm, efficiency FROM main.EfficiencyVariable',
            )
            load_element(M.EfficiencyVariable, raw, self.viable_ritvo, (0, 4, 5, 6, 7))

        # ExistingCapacity
        if self.table_exists('ExistingCapacity'):
            if mi:
                # In order to get accurate capacity at start of this interval, we want to
                # 1.  Only look at the previous period in the net capacity table (things that had some capacity)
                # 2.  Omit any techs that are "unlimited capacity" to keep them out of capacity variables
                # 3.  add in everything from the original ExistingCapacity table

                # get previous period
                raw = cur.execute(
                    'SELECT MAX(period) FROM main.TimePeriod WHERE period < ?', (mi.base_year,)
                ).fetchone()
                previous_period = raw[0]
                # noinspection SqlUnused
                raw = cur.execute(
                    'SELECT region, tech, vintage, capacity FROM main.OutputBuiltCapacity '
                    ' WHERE vintage <= ? '
                    ' AND scenario = ? '
                    'UNION '
                    '  SELECT region, tech, vintage, capacity FROM main.ExistingCapacity ',
                    (previous_period, self.config.scenario),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, tech, vintage, capacity FROM main.ExistingCapacity'
                ).fetchall()
            # devnote: We want full existing capacity history for end of life flows and growth constraints
            # load_element(M.ExistingCapacity, raw, self.viable_rtv, (0, 1, 2))
            load_element(M.ExistingCapacity, raw)
            load_element(
                M.tech_exist, list({(row[1],) for row in raw})
            )  # need to keep these for accounting purposes

        # GlobalDiscountRate
        if self.table_exists('MetaDataReal'):
            raw = cur.execute(
                "SELECT value FROM main.MetaDataReal WHERE element = 'global_discount_rate'"
            ).fetchall()
            # do this separately as it is non-indexed, so we need to make a mapping with None
            data[M.GlobalDiscountRate.name] = {None: raw[0][0]}

        # SegFrac
        if self.table_exists('TimeSegmentFraction'):
            raw = self.raw_check_mi_period(
                mi=mi,
                cur=cur,
                qry='SELECT period, season, tod, segfrac FROM main.TimeSegmentFraction',
            )
        else:
            logger.warning(
                'No TimeSegmentFraction table found. Loading filler SegFrac ("S", "D") for one time segment per period'
                ' (assume this is a periodic model)'
            )
            # if no segfrac table, assume this is a periodic model
            if mi:
                raw = [
                    (p, 'S', 'D', 1)
                    for p in time_optimize
                    if mi.base_year <= p <= mi.last_demand_year
                ]
            else:
                raw = [(p, 'S', 'D', 1) for p in time_optimize]
        load_element(M.SegFrac, raw)

        # TimeSeason
        if self.table_exists('TimeSeason'):
            if mi:
                raw = cur.execute(
                    'SELECT period, season FROM main.TimeSeason WHERE'
                    ' period >= ? AND period <= ? ORDER BY period, sequence',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT period, season FROM main.TimeSeason ORDER BY period, sequence'
                ).fetchall()
            for row in raw:
                load_indexed_set(M.TimeSeason, index_value=row[0], element=row[1])
            load_element(M.time_season, list(set((row[1],) for row in raw)))
        else:
            for period in time_optimize:
                load_indexed_set(M.TimeSeason, index_value=period, element='S')
            logger.warning(
                'No TimeSeason table found. Loading a single filler season "S" (assume this is an annual model)'
            )
            load_element(M.time_season, [('S',)])

        if self.table_exists('TimeSeasonSequential'):
            if mi:
                raw = cur.execute(
                    'SELECT period, seas_seq, season, num_days FROM main.TimeSeasonSequential WHERE'
                    ' period >= ? AND period <= ? ORDER BY period, sequence',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT period, seas_seq, season, num_days FROM main.TimeSeasonSequential ORDER BY period, sequence'
                ).fetchall()
            load_element(M.TimeSeasonSequential, raw)
            if raw:
                load_element(M.ordered_season_sequential, [(row[0:3]) for row in raw])
                load_element(M.time_season_sequential, list(set((row[1],) for row in raw)))

        # DemandSpecificDistribution
        if self.table_exists('DemandSpecificDistribution'):
            raw = self.raw_check_mi_period(
                mi=mi,
                cur=cur,
                qry='SELECT region, period, season, tod, demand_name, dsd FROM main.DemandSpecificDistribution',
            )
            load_element(M.DemandSpecificDistribution, raw)

        # LifetimeSurvivalCurve
        if self.table_exists('LifetimeSurvivalCurve'):
            raw = cur.execute(
                'SELECT region, period, tech, vintage, fraction FROM main.LifetimeSurvivalCurve'
            ).fetchall()
            load_element(M.LifetimeSurvivalCurve, raw, self.viable_rtv, val_loc=(0, 2, 3))

        # LoanLifetimeProcess
        if self.table_exists('LoanLifetimeProcess'):
            raw = cur.execute(
                'SELECT region, tech, vintage, lifetime FROM main.LoanLifetimeProcess'
            ).fetchall()
            load_element(M.LoanLifetimeProcess, raw, self.viable_rtv, (0, 1, 2))

        # LimitTechInputSplit
        if self.table_exists('LimitTechInputSplit'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, input_comm, tech, operator, proportion FROM main.LimitTechInputSplit',
            )
            loaded = load_element(M.LimitTechInputSplit, raw, self.viable_rpit, (0, 1, 2, 3))
            # we need to see if anything was filtered out here and raise warning if so as it may have invalidated
            # a blending process and any missing items should be reviewed
            if len(loaded) < len(raw):
                missing = set(raw) - set(loaded)
                for item in sorted(missing, key=lambda x: (x[0], x[1], x[3], x[2])):
                    region, period, ic, tech, _, _ = item
                    logger.warning(
                        'Technology Input Split requirement in region %s, period %d for tech %s with input'
                        'commodity %s has '
                        'been removed because the tech path with that input is '
                        'invalid/not available/orphan.  See the other warnings for this TECH in '
                        'this region-period, and check for availability of all components in data.',
                        region,
                        period,
                        tech,
                        ic,
                    )

        # LimitTechInputSplitAnnual
        if self.table_exists('LimitTechInputSplitAnnual'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, input_comm, tech, operator, proportion FROM main.LimitTechInputSplitAnnual',
            )
            loaded = load_element(M.LimitTechInputSplitAnnual, raw, self.viable_rpit, (0, 1, 2, 3))
            # we need to see if anything was filtered out here and raise warning if so as it may have invalidated
            # a blending process and any missing items should be reviewed
            if len(loaded) < len(raw):
                missing = set(raw) - set(loaded)
                for item in sorted(missing, key=lambda x: (x[0], x[1], x[3], x[2])):
                    region, period, ic, tech, _, _ = item
                    logger.warning(
                        'Technology Input Split Annual requirement in region %s, period %d for tech %s with input'
                        'commodity %s has '
                        'been removed because the tech path with that input is '
                        'invalid/not available/orphan.  See the other warnings for this TECH in '
                        'this region-period, and check for availability of all components in data.',
                        region,
                        period,
                        tech,
                        ic,
                    )

        # LimitTechOutputSplit
        if self.table_exists('LimitTechOutputSplit'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, tech, output_comm, operator, proportion FROM main.LimitTechOutputSplit',
            )
            loaded = load_element(M.LimitTechOutputSplit, raw, self.viable_rpto, (0, 1, 2, 3))
            # raise warning regarding any deletions here...  similar to input split above
            if len(loaded) < len(raw):
                missing = set(raw) - set(loaded)
                for item in sorted(missing):
                    region, period, tech, oc, _, _ = item
                    logger.warning(
                        'Technology Output Split requirement in region %s, period %d for tech %s with output'
                        'commodity %s has '
                        'been removed because the tech path with that output is '
                        'invalid/not available/orphan.  See the other warnings for this TECH in '
                        'this region-period, and check for availability of all components in data.',
                        region,
                        period,
                        tech,
                        oc,
                    )

        # LimitTechOutputSplitAnnual
        if self.table_exists('LimitTechOutputSplitAnnual'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, tech, output_comm, operator, proportion FROM main.LimitTechOutputSplitAnnual',
            )
            loaded = load_element(M.LimitTechOutputSplitAnnual, raw, self.viable_rpto, (0, 1, 2, 3))
            # we need to see if anything was filtered out here and raise warning if so as it may have invalidated
            # a blending process and any missing items should be reviewed
            if len(loaded) < len(raw):
                missing = set(raw) - set(loaded)
                for item in sorted(missing):
                    region, period, tech, oc, _, _ = item
                    logger.warning(
                        'Technology Output Split Annual requirement in region %s, period %d for tech %s with output'
                        'commodity %s has '
                        'been removed because the tech path with that output is '
                        'invalid/not available/orphan.  See the other warnings for this TECH in '
                        'this region-period, and check for availability of all components in data.',
                        region,
                        period,
                        tech,
                        oc,
                    )

        # RenewablePortfolioStandard
        if self.table_exists('RPSRequirement'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, tech_group, requirement FROM main.RPSRequirement',
            )
            load_element(M.RenewablePortfolioStandard, raw)
            if len(raw) > 0:
                logger.warning(
                    'The RenewablePortfolioStandard constraint has been deprecated. Use the '
                    'LimitActivityShare constraint instead, using the same sub group and '
                    'constructing a new super group for all relevant generators. The constraint '
                    'has been applied for now but this feature will be removed in the future.'
                )

        # CostFixed
        raw = self.raw_check_mi_period(
            mi, cur=cur, qry='SELECT region, period, tech, vintage, cost FROM main.CostFixed'
        )
        load_element(M.CostFixed, raw, self.viable_rtv, val_loc=(0, 2, 3))

        # CostInvest
        # exclude "existing" vintages by screening for base year and beyond.
        # the "viable_rtv" will filter anything beyond view
        if mi:
            raw = cur.execute(
                'SELECT region, tech, vintage, cost FROM main.CostInvest WHERE vintage >= ?',
                (mi.base_year,),
            ).fetchall()
        else:
            raw = cur.execute('SELECT region, tech, vintage, cost FROM main.CostInvest ').fetchall()
        load_element(M.CostInvest, raw, self.viable_rtv, (0, 1, 2))

        # CostVariable
        raw = self.raw_check_mi_period(
            mi, cur=cur, qry='SELECT region, period, tech, vintage, cost FROM main.CostVariable'
        )
        load_element(M.CostVariable, raw, self.viable_rtv, (0, 2, 3))

        # CostEmissions (and supporting index set)
        if self.table_exists('CostEmission'):
            raw = self.raw_check_mi_period(
                mi, cur=cur, qry='SELECT region, period, emis_comm, cost from main.CostEmission'
            )
            load_element(M.CostEmission, raw)

        # DefaultLoanRate
        if self.table_exists('MetaDataReal'):
            raw = cur.execute(
                "SELECT value FROM main.MetaDataReal WHERE element = 'default_loan_rate'"
            ).fetchall()
            # do this separately as it is non-indexed, so we need to make a mapping with None
            data[M.DefaultLoanRate.name] = {None: raw[0][0]}

        # LoanRate
        if self.table_exists('LoanRate'):
            if mi:
                raw = cur.execute(
                    'SELECT region, tech, vintage, rate FROM main.LoanRate WHERE vintage >= ?',
                    (mi.base_year,),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, tech, vintage, rate FROM main.LoanRate '
                ).fetchall()

            load_element(M.LoanRate, raw, self.viable_rtv, (0, 1, 2))

        # LimitCapacity
        if self.table_exists('LimitCapacity'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, tech_or_group, operator, capacity FROM main.LimitCapacity',
            )
            load_element(M.LimitCapacity, raw)  # , self.viable_rt, (0, 2))

        # LimitNewCapacity
        if self.table_exists('LimitNewCapacity'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, tech_or_group, operator, new_cap FROM main.LimitNewCapacity',
            )
            load_element(M.LimitNewCapacity, raw)

        # LimitCapacityShare
        if self.table_exists('LimitCapacityShare'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, sub_group, super_group, operator, share FROM main.LimitCapacityShare',
            )
            load_element(M.LimitCapacityShare, raw)

        # LimitNewCapacityShare
        if self.table_exists('LimitNewCapacityShare'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, sub_group, super_group, operator, share FROM main.LimitNewCapacityShare',
            )
            load_element(M.LimitNewCapacityShare, raw)

        # LimitActivityShare
        if self.table_exists('LimitActivityShare'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, sub_group, super_group, operator, share FROM main.LimitActivityShare',
            )
            load_element(M.LimitActivityShare, raw)

        # LimitResource
        if self.table_exists('LimitResource'):
            raw = cur.execute(
                'SELECT region, tech_or_group, operator, cum_act FROM main.LimitResource'
            ).fetchall()
            load_element(M.LimitResource, raw)

        # LimitActivity
        if self.table_exists('LimitActivity'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, tech_or_group, operator, activity FROM main.LimitActivity',
            )
            load_element(M.LimitActivity, raw)

        # LimitSeasonalCapacityFactor
        if self.table_exists('LimitSeasonalCapacityFactor'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, season, tech, operator, factor FROM main.LimitSeasonalCapacityFactor',
            )
            load_element(M.LimitSeasonalCapacityFactor, raw, self.viable_rt, (0, 3))

        # LimitAnnualCapacityFactor
        if self.table_exists('LimitAnnualCapacityFactor'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, tech, output_comm, operator, factor FROM main.LimitAnnualCapacityFactor',
            )
            load_element(M.LimitAnnualCapacityFactor, raw, self.viable_rpto, (0, 1, 2, 3))

        # LimitGrowthCapacity
        if self.table_exists('LimitGrowthCapacity'):
            raw = cur.execute(
                'SELECT region, tech_or_group, operator, rate, seed FROM main.LimitGrowthCapacity'
            ).fetchall()
            raw = self.tuple_values(raw, 3)
            load_element(M.LimitGrowthCapacity, raw)

        # LimitDegrowthCapacity
        if self.table_exists('LimitDegrowthCapacity'):
            raw = cur.execute(
                'SELECT region, tech_or_group, operator, rate, seed FROM main.LimitDegrowthCapacity'
            ).fetchall()
            raw = self.tuple_values(raw, 3)
            load_element(M.LimitDegrowthCapacity, raw)

        # LimitGrowthNewCapacity
        if self.table_exists('LimitGrowthNewCapacity'):
            raw = cur.execute(
                'SELECT region, tech_or_group, operator, rate, seed FROM main.LimitGrowthNewCapacity'
            ).fetchall()
            raw = self.tuple_values(raw, 3)
            load_element(M.LimitGrowthNewCapacity, raw)

        # LimitDegrowthNewCapacity
        if self.table_exists('LimitDegrowthNewCapacity'):
            raw = cur.execute(
                'SELECT region, tech_or_group, operator, rate, seed FROM main.LimitDegrowthNewCapacity'
            ).fetchall()
            raw = self.tuple_values(raw, 3)
            load_element(M.LimitDegrowthNewCapacity, raw)

        # LimitGrowthNewCapacityDelta
        if self.table_exists('LimitGrowthNewCapacityDelta'):
            raw = cur.execute(
                'SELECT region, tech_or_group, operator, rate, seed FROM main.LimitGrowthNewCapacityDelta'
            ).fetchall()
            raw = self.tuple_values(raw, 3)
            load_element(M.LimitGrowthNewCapacityDelta, raw)

        # LimitDegrowthNewCapacityDelta
        if self.table_exists('LimitDegrowthNewCapacityDelta'):
            raw = cur.execute(
                'SELECT region, tech_or_group, operator, rate, seed FROM main.LimitDegrowthNewCapacityDelta'
            ).fetchall()
            raw = self.tuple_values(raw, 3)
            load_element(M.LimitDegrowthNewCapacityDelta, raw)

        # LimitEmission
        if self.table_exists('LimitEmission'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, emis_comm, operator, value FROM main.LimitEmission',
            )
            load_element(M.LimitEmission, raw)

        # EmissionActivity
        # The current emission constraint screens by valid inputs, so if it is NOT
        # built in a particular region, this should still be OK
        if self.table_exists('EmissionActivity'):
            raw = cur.execute(
                'SELECT region, emis_comm, input_comm, tech, vintage, output_comm, activity '
                'FROM main.EmissionActivity '
            ).fetchall()
            load_element(M.EmissionActivity, raw, self.viable_ritvo, (0, 2, 3, 4, 5))

        # EmissionEmbodied
        if self.table_exists('EmissionEmbodied'):
            raw = cur.execute(
                'SELECT region, emis_comm, tech, vintage, value FROM main.EmissionEmbodied'
            ).fetchall()
            load_element(M.EmissionEmbodied, raw, self.viable_rtv, (0, 2, 3))

        # EmissionEndOfLife
        if self.table_exists('EmissionEndOfLife'):
            raw = cur.execute(
                'SELECT region, emis_comm, tech, vintage, value FROM main.EmissionEndOfLife'
            ).fetchall()
            load_element(M.EmissionEndOfLife, raw, self.viable_rtv, (0, 2, 3))

        # ConstructionInput
        if self.table_exists('ConstructionInput'):
            raw = cur.execute(
                'SELECT region, input_comm, tech, vintage, value FROM main.ConstructionInput'
            ).fetchall()
            load_element(M.ConstructionInput, raw, self.viable_rtv, (0, 2, 3))

        # EndOfLifeOutput
        if self.table_exists('EndOfLifeOutput'):
            raw = cur.execute(
                'SELECT region, tech, vintage, output_comm, value FROM main.EndOfLifeOutput'
            ).fetchall()
            load_element(M.EndOfLifeOutput, raw, self.viable_rtv, (0, 1, 2))

        # LinkedTechs
        # Note:  Both of the linked techs must be viable.  As this is non period/vintage
        #        specific, it should be true that if one is built, the other is also
        if self.table_exists('LinkedTech'):
            raw = cur.execute(
                'SELECT primary_region, primary_tech, emis_comm, driven_tech FROM main.LinkedTech'
            ).fetchall()
            loaded = load_element(M.LinkedTechs, raw, self.viable_rtt, (0, 1, 3))
            # The below is a second check (belt and suspenders) and shouldn't really be needed, but it is
            # preserved for now.
            # we are checking that for each of the rejected LinkedTechs that each of the individual
            # techs are also to be rejected (not members of valid_tech) ... if not ODD behavior
            # could occur if the linkage is NOT established and the techs operate independently!
            if len(loaded) < len(raw):
                missing = set(raw) - set(loaded)
                valid_techs = self.viable_techs.members
                for item in missing:
                    t1 = item[1]
                    t2 = item[3]
                    if t1 in valid_techs or t2 in valid_techs:
                        # this is a PROBLEM.  The commodity network should have removed both the
                        # driver and driven techs from the valid tech set, and they should not be in
                        # the valid tech set lest they be allowed in the model independently.
                        logger.error('Linked Tech item %s is not valid.  Check data', item)
                        print('problem loading linked tech.  See log file')
                        sys.exit(-1)

        # RampUpHourly
        if self.table_exists('RampUpHourly'):
            raw = cur.execute('SELECT region, tech, rate FROM main.RampUpHourly').fetchall()
            load_element(M.RampUpHourly, raw, self.viable_rt, (0, 1))
            raw = cur.execute('SELECT DISTINCT tech FROM main.RampUpHourly').fetchall()
            load_element(M.tech_upramping, raw, self.viable_techs)

        # RampDownHourly
        if self.table_exists('RampDownHourly'):
            raw = cur.execute('SELECT region, tech, rate FROM main.RampDownHourly').fetchall()
            load_element(M.RampDownHourly, raw, self.viable_rt, (0, 1))
            raw = cur.execute('SELECT DISTINCT tech FROM main.RampDownHourly').fetchall()
            load_element(M.tech_downramping, raw, self.viable_techs)

        # CapacityCredit
        if self.table_exists('CapacityCredit'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, tech, vintage, credit FROM main.CapacityCredit',
            )
            load_element(M.CapacityCredit, raw, self.viable_rtv, (0, 2, 3))

        # ReserveCapacityDerate
        if self.table_exists('ReserveCapacityDerate'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, season, tech, vintage, factor FROM main.ReserveCapacityDerate',
            )
            load_element(M.ReserveCapacityDerate, raw, self.viable_rtv, (0, 3, 4))

        # PlanningReserveMargin
        if self.table_exists('PlanningReserveMargin'):
            raw = cur.execute('SELECT region, margin FROM main.PlanningReserveMargin').fetchall()
            load_element(M.PlanningReserveMargin, raw)

        # StorageDuration
        if self.table_exists('StorageDuration'):
            raw = cur.execute('SELECT region, tech, duration FROM main.StorageDuration').fetchall()
            load_element(M.StorageDuration, raw, self.viable_rt, (0, 1))

        # StorageFraction
        if self.table_exists('LimitStorageLevelFraction'):
            raw = self.raw_check_mi_period(
                mi,
                cur=cur,
                qry='SELECT region, period, season, tod, tech, vintage, operator, fraction FROM main.LimitStorageLevelFraction',
            )
            load_element(M.LimitStorageFraction, raw, self.viable_rtv, (0, 4, 5))

        # For T/S:  dump the size of all data elements into the log
        if self.debugging:
            temp = '\n'.join((f'{k} : {len(v)}' for k, v in data.items()))
            logger.info(temp)

        # capture the parameter indexing sets
        set_data = self.load_param_idx_sets(data=data)
        data.update(set_data)
        self.data = data

    def tuple_values(self, raw, index_length):
        new_raw = []
        for row in raw:
            new_raw.append((*row[0:index_length], row[index_length::]))
        return new_raw

    def raw_check_mi_period(self, mi: MyopicIndex | None, cur: Cursor, qry: str) -> list:
        if mi:
            return cur.execute(
                qry + ' WHERE period >= ? AND period <= ?',
                (mi.base_year, mi.last_demand_year),
            ).fetchall()
        else:
            return cur.execute(qry).fetchall()

    def load_param_idx_sets(self, data: dict) -> dict:
        """
        Build a dictionary of sparse sets that can be used for indexing the parameters.
        :param data: The parameters to peel out index values from
        :return: a dictionary of the set name: values

        The purpose of this function is to use the data we have already captured for the parameters
        to make indexing sets in the model.  This replaces all of the "lambda" functions  which were
        previously used to reverse engineer the built parameters.

        Having these sets allows quicker constraint builds because they are the basis of many constraints

        It also enables the model to be serialized by python's pickle by removing functions from the model
        definitions
        """

        M: TemoaModel = TemoaModel()  # for typing
        param_idx_sets = {
            M.CostInvest.name: M.CostInvest_rtv.name,
            M.CostEmission.name: M.CostEmission_rpe.name,
            M.Demand.name: M.DemandConstraint_rpc.name,
            M.LimitEmission.name: M.LimitEmissionConstraint_rpe.name,
            M.LimitActivity.name: M.LimitActivityConstraint_rpt.name,
            M.LimitSeasonalCapacityFactor.name: M.LimitSeasonalCapacityFactorConstraint_rpst.name,
            M.LimitActivityShare.name: M.LimitActivityShareConstraint_rpgg.name,
            M.LimitAnnualCapacityFactor.name: M.LimitAnnualCapacityFactorConstraint_rpto.name,
            M.LimitCapacity.name: M.LimitCapacityConstraint_rpt.name,
            M.LimitCapacityShare.name: M.LimitCapacityShareConstraint_rpgg.name,
            M.LimitNewCapacity.name: M.LimitNewCapacityConstraint_rpt.name,
            M.LimitNewCapacityShare.name: M.LimitNewCapacityShareConstraint_rpgg.name,
            M.LimitResource.name: M.LimitResourceConstraint_rt.name,
            M.LimitStorageFraction.name: M.LimitStorageFractionConstraint_rpsdtv.name,
            M.RenewablePortfolioStandard.name: M.RenewablePortfolioStandardConstraint_rpg.name,
            # M.ResourceBound.name: M.ResourceConstraint_rpr.name,
        }

        res = {}
        for p, s in param_idx_sets.items():
            param_data = data.get(p)
            if param_data is None:
                # no data for this param... nothing to capture for idx set
                continue
            idxs = list(param_data.keys())
            res[s] = idxs
        return res
