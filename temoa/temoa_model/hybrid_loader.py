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
in LICENSE.txt.  Users uncompressing this from an archive may not have
received this license file.  If not, see <http://www.gnu.org/licenses/>.


Written by:  J. F. Hyink
jeff@westernspark.us
https://westernspark.us
Created on:  1/21/24

A module to build/load a Data Portal for myopic run using both SQL to pull data
and python to filter results

"""


import sys
import time
from collections import defaultdict
from logging import getLogger
from sqlite3 import Connection, OperationalError
from typing import Sequence

from pyomo.core import Param, Set
from pyomo.dataportal import DataPortal

from temoa.extensions.myopic.myopic_index import MyopicIndex
from temoa.temoa_model.model_checking import network_model_data, element_checker
from temoa.temoa_model.model_checking.commodity_network_manager import CommodityNetworkManager
from temoa.temoa_model.model_checking.element_checker import ViableSet
from temoa.temoa_model.temoa_config import TemoaConfig
from temoa.temoa_model.temoa_mode import TemoaMode
from temoa.temoa_model.temoa_model import TemoaModel

logger = getLogger(__name__)

# the tables below are ones in which we might find regional groups which should be captured
# to make the members of the RegionalGlobalIndices Set in the model.  They need to aggregated
tables_with_regional_groups = {
    'MaxActivity': 'region',
    'MinActivity': 'region',
    'MinAnnualCapacityFactor': 'region',
    'MaxAnnualCapacityFactor': 'region',
    'EmissionLimit': 'region',
    'MinActivityGroup': 'region',
    'MaxActivityGroup': 'region',
    'MinCapacityGroup': 'region',
    'MaxCapacityGroup': 'region',
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
        # the general plan:
        # 0. determine if source trace needs to be done, and do it
        # 1. build the efficiency table
        # 2. iterate through the model elements that are directly read from data
        # 3. use SQL query to get the full table
        # 4. (OPTIONALLY) filter it, as needed for myopic
        # 5. load it into the data dictionary
        logger.info('Loading data dictionary')

        # some logic checking...
        if myopic_index is not None:
            if not isinstance(myopic_index, MyopicIndex):
                raise ValueError(f'received an illegal entry for the myopic index: {myopic_index}')
            if self.config.scenario_mode != TemoaMode.MYOPIC:
                raise RuntimeError(
                    'Myopic Index passed to data dictionary build, but mode is not Myopic.... '
                    'Likely code error.'
                )
        elif myopic_index is None and self.config.scenario_mode == TemoaMode.MYOPIC:
            raise RuntimeError(
                'Mode is myopic, but no MyopicIndex specified in data portal build.... Likely code '
                'error.'
            )

        if self.config.source_trace or self.config.scenario_mode == TemoaMode.MYOPIC:
            use_raw_data = False
            self._source_trace(myopic_index=myopic_index)
        else:
            use_raw_data = True

        # build the Efficiency Dataset
        self._build_efficiency_dataset(use_raw_data=use_raw_data, myopic_index=myopic_index)

        mi = myopic_index  # convenience

        # housekeeping
        data: dict[str, list | dict] = dict()

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
                        'Failed to validate members of %s.  Coding error likely.'
                        '\n%s' % (c.name, e)
                    )
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

        def load_indexed_set(indexed_set: Set, index_value, element, element_validator):
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

        # time_exist
        if mi:
            raw = cur.execute(
                'SELECT period FROM main.TimePeriod  WHERE period < ? ORDER BY sequence',
                (mi.base_year,),
            ).fetchall()
        else:
            raw = cur.execute(
                "SELECT period FROM main.TimePeriod WHERE flag = 'e' ORDER BY sequence"
            ).fetchall()
        load_element(M.time_exist, raw)

        # time_future
        if mi:
            raw = cur.execute(
                'SELECT period FROM main.TimePeriod WHERE '
                'period >= ? AND period <= ? ORDER BY sequence',
                (mi.base_year, mi.last_year),
            ).fetchall()
        else:
            raw = cur.execute(
                "SELECT period FROM main.TimePeriod WHERE flag = 'f' ORDER BY sequence"
            ).fetchall()
        load_element(M.time_future, raw)

        # time_of_day
        raw = cur.execute('SELECT tod FROM main.TimeOfDay ORDER BY sequence').fetchall()
        load_element(M.time_of_day, raw)

        # time_season
        raw = cur.execute('SELECT season FROM main.TimeSeason ORDER BY sequence').fetchall()
        load_element(M.time_season, raw)

        # link_seasons
        raw = cur.execute("SELECT value from MetaData WHERE element == 'link_seasons'").fetchall()
        if not raw:
            raise ValueError('link_seasons boolean parameter missing from MetaData table. Seasons will loop by default.')
        data[M.link_seasons.name] = {None: bool(raw[0][0])}

        # myopic_base_year
        if mi:
            raw = cur.execute(
                "SELECT value from MetaData WHERE element == 'myopic_base_year'"
            ).fetchall()
            # load as a singleton...
            if not raw:
                raise ValueError('No myopic_base_year found in MetaData table.')
            data[M.MyopicBaseyear.name] = {None: int(raw[0][0])}

        #  === REGION SETS ===

        # regions
        raw = cur.execute('SELECT region FROM main.Region').fetchall()
        load_element(M.regions, raw)

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
        load_element(M.RegionalGlobalIndices, list_of_groups)

        # region-exchanges
        # auto-generated

        #  === TECH SETS ===

        # tech_resource
        raw = cur.execute("SELECT tech FROM main.Technology WHERE flag = 'r'").fetchall()
        load_element(M.tech_resource, raw, self.viable_techs)

        # tech_production
        raw = cur.execute("SELECT tech FROM main.Technology WHERE flag LIKE 'p%'").fetchall()
        load_element(M.tech_production, raw, self.viable_techs)

        # tech_uncap
        try:
            raw = cur.execute('SELECT tech FROM main.Technology WHERE unlim_cap > 0').fetchall()
            load_element(M.tech_uncap, raw, self.viable_techs)
        except OperationalError:
            logger.info(
                'The current database does not support non-capacity techs and should be upgraded.'
            )

        # tech_baseload
        raw = cur.execute("SELECT tech FROM main.Technology WHERE flag = 'pb'").fetchall()
        load_element(M.tech_baseload, raw, self.viable_techs)

        # tech_storage
        raw = cur.execute("SELECT tech FROM main.Technology WHERE flag = 'ps'").fetchall()
        load_element(M.tech_storage, raw, self.viable_techs)

        # tech_reserve
        raw = cur.execute('SELECT tech FROM Technology WHERE reserve > 0').fetchall()
        load_element(M.tech_reserve, raw, self.viable_techs)

        # tech_ramping
        techs = set()
        if self.table_exists('RampUp'):
            ramp_up_techs = cur.execute('SELECT tech FROM main.RampUp').fetchall()
            techs.update({t[0] for t in ramp_up_techs})
        if self.table_exists('RampDown'):
            ramp_dn_techs = cur.execute('SELECT tech FROM main.RampDown').fetchall()
            techs.update({t[0] for t in ramp_dn_techs})
        load_element(M.tech_ramping, sorted((t,) for t in techs), self.viable_techs)  # sort for
        # deterministic behavior

        # tech_curtailment
        raw = cur.execute('SELECT tech FROM Technology WHERE curtail > 0').fetchall()
        load_element(M.tech_curtailment, raw, self.viable_techs)

        # tech_flex
        raw = cur.execute('SELECT tech FROM Technology WHERE flex > 0').fetchall()
        load_element(M.tech_flex, raw, self.viable_techs)

        # tech_exchange
        raw = cur.execute('SELECT tech FROM Technology WHERE exchange > 0').fetchall()
        load_element(M.tech_exchange, raw, self.viable_techs)

        # groups & tech_groups (supports RPS and general tech grouping)
        if self.table_exists('TechGroup'):
            raw = cur.execute('SELECT group_name FROM main.TechGroup').fetchall()
            load_element(M.tech_group_names, raw)

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

        # tech_annual
        raw = cur.execute('SELECT tech FROM Technology WHERE annual > 0').fetchall()
        load_element(M.tech_annual, raw, self.viable_techs)

        # tech_retirement
        raw = cur.execute('SELECT tech FROM Technology WHERE retire > 0').fetchall()
        load_element(M.tech_retirement, raw, self.viable_techs)

        #  === COMMODITIES ===

        # commodity_demand
        raw = cur.execute("SELECT name FROM main.Commodity WHERE flag = 'd'").fetchall()
        load_element(M.commodity_demand, raw, self.viable_comms)

        # commodity_emissions
        # currently NOT validated against anything... shouldn't be a problem ?
        raw = cur.execute("SELECT name FROM main.Commodity WHERE flag = 'e'").fetchall()
        load_element(M.commodity_emissions, raw)

        # commodity_physical
        raw = cur.execute(
            "SELECT name FROM main.Commodity WHERE flag = 'p' OR flag = 's' OR flag = 'a'"
        ).fetchall()
        # The model enforces 0 symmetric difference between the physical commodities
        # and the input commodities, so we need to include only the viable INPUTS
        load_element(M.commodity_physical, raw, self.viable_input_comms)

        # commodity_source
        raw = cur.execute("SELECT name FROM main.Commodity WHERE flag = 's'").fetchall()
        load_element(M.commodity_source, raw, self.viable_input_comms)

        # commodity_annual
        raw = cur.execute("SELECT name FROM main.Commodity WHERE flag = 'a'").fetchall()
        load_element(M.commodity_annual, raw, self.viable_input_comms)

        #  === PARAMS ===

        # Efficiency

        # we have already computed/filtered this... no need for another data pull
        raw = self.efficiency_values
        load_element(M.Efficiency, raw)

        # ExistingCapacity
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
                'SELECT region, tech, vintage, capacity FROM main.OutputNetCapacity '
                ' WHERE period = ? '
                ' AND scenario = ? '
                'UNION '
                '  SELECT region, tech, vintage, capacity FROM main.ExistingCapacity ',
                (previous_period, self.config.scenario),
            ).fetchall()
        else:
            raw = cur.execute(
                'SELECT region, tech, vintage, capacity FROM main.ExistingCapacity'
            ).fetchall()
        load_element(M.ExistingCapacity, raw, self.viable_rtv, (0, 1, 2))

        # GlobalDiscountRate
        raw = cur.execute(
            "SELECT value FROM main.MetaDataReal WHERE element = 'global_discount_rate'"
        ).fetchall()
        # do this separately as it is non-indexed, so we need to make a mapping with None
        data[M.GlobalDiscountRate.name] = {None: raw[0][0]}

        # SegFrac
        raw = cur.execute('SELECT season, tod, segfrac FROM main.TimeSegmentFraction').fetchall()
        load_element(M.SegFrac, raw)

        # DemandSpecificDistribution
        raw = cur.execute(
            'SELECT region, season, tod, demand_name, dsd FROM main.DemandSpecificDistribution'
        ).fetchall()
        load_element(M.DemandSpecificDistribution, raw)

        # Demand
        if mi:
            raw = cur.execute(
                'SELECT region, period, commodity, demand FROM main.Demand '
                'WHERE period >= ? AND period <= ?',
                (mi.base_year, mi.last_demand_year),
            ).fetchall()
        else:
            raw = cur.execute(
                'SELECT region, period, commodity, demand FROM main.Demand '
            ).fetchall()
        load_element(M.Demand, raw)

        # RescourceBound
        # Not currently implemented

        # CapacityToActivity
        raw = cur.execute('SELECT region, tech, c2a FROM main.CapacityToActivity ').fetchall()
        load_element(M.CapacityToActivity, raw, self.viable_rt, (0, 1))

        # CapacityFactorTech
        raw = cur.execute(
            'SELECT region, season, tod, tech, factor ' 'FROM main.CapacityFactorTech'
        ).fetchall()
        load_element(M.CapacityFactorTech, raw, self.viable_rt, (0, 3))

        # CapacityFactorProcess
        raw = cur.execute(
            'SELECT region, season, tod, tech, vintage, factor ' ' FROM main.CapacityFactorProcess'
        ).fetchall()
        load_element(M.CapacityFactorProcess, raw, self.viable_rtv, (0, 3, 4))

        # LifetimeTech
        raw = cur.execute('SELECT region, tech, lifetime FROM main.LifetimeTech').fetchall()
        load_element(M.LifetimeTech, raw, self.viable_rt, val_loc=(0, 1))

        # LifetimeProcess
        raw = cur.execute(
            'SELECT region, tech, vintage, lifetime FROM main.LifetimeProcess'
        ).fetchall()
        load_element(M.LifetimeProcess, raw, self.viable_rtv, val_loc=(0, 1, 2))

        # LoanLifetimeTech
        raw = cur.execute('SELECT region, tech, lifetime FROM main.LoanLifetimeTech').fetchall()
        load_element(M.LoanLifetimeTech, raw, self.viable_rt, (0, 1))

        # TechInputSplit
        if mi:
            raw = cur.execute(
                'SELECT region, period, input_comm, tech, min_proportion FROM main.TechInputSplit '
                'WHERE period >= ? AND period <= ?',
                (mi.base_year, mi.last_demand_year),
            ).fetchall()
        else:
            raw = cur.execute(
                'SELECT region, period, input_comm, tech, min_proportion FROM main.TechInputSplit '
            ).fetchall()
        loaded = load_element(M.TechInputSplit, raw, self.viable_rpit, (0, 1, 2, 3))
        # we need to see if anything was filtered out here and raise warning if so as it may have invalidated
        # a blending process and any missing items should be reviewed
        if len(loaded) < len(raw):
            missing = set(raw) - set(loaded)
            for item in sorted(missing, key=lambda x: (x[0], x[1], x[3], x[2])):
                region, period, ic, tech, _ = item
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

        # TechInputSplitAnnual
        if self.table_exists('TechInputSplitAnnual'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, input_comm, tech, min_proportion '
                    'FROM main.TechInputSplitAnnual '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, input_comm, tech, min_proportion '
                    'FROM main.TechInputSplitAnnual '
                ).fetchall()
            loaded = load_element(M.TechInputSplitAnnual, raw, self.viable_rpit, (0, 1, 2, 3))
            # we need to see if anything was filtered out here and raise warning if so as it may have invalidated
            # a blending process and any missing items should be reviewed
            if len(loaded) < len(raw):
                missing = set(raw) - set(loaded)
                for item in sorted(missing, key=lambda x: (x[0], x[1], x[3], x[2])):
                    region, period, ic, tech, _ = item
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
        # TechOutputSplit
        if self.table_exists('TechOutputSplit'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, tech, output_comm, min_proportion FROM main.TechOutputSplit '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, tech, output_comm, min_proportion FROM main.TechOutputSplit '
                ).fetchall()
            loaded = load_element(M.TechOutputSplit, raw, self.viable_rpto, (0, 1, 2, 3))
            # raise warning regarding any deletions here...  similar to input split above
            if len(loaded) < len(raw):
                missing = set(raw) - set(loaded)
                for item in sorted(missing):
                    region, period, tech, oc, _ = item
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

        # TechOutputSplitAnnual
        if self.table_exists('TechOutputSplitAnnual'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, tech, output_comm, min_proportion '
                    'FROM main.TechOutputSplitAnnual '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, tech, output_comm, min_proportion '
                    'FROM main.TechOutputSplitAnnual '
                ).fetchall()
            loaded = load_element(M.TechOutputSplitAnnual, raw, self.viable_rpto, (0, 1, 2, 3))
            # we need to see if anything was filtered out here and raise warning if so as it may have invalidated
            # a blending process and any missing items should be reviewed
            if len(loaded) < len(raw):
                missing = set(raw) - set(loaded)
                for item in sorted(missing):
                    region, period, tech, oc, _ = item
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
            if mi:
                raw = cur.execute(
                    'SELECT region, period, tech_group, requirement FROM main.RPSRequirement '
                    ' WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, tech_group, requirement FROM main.RPSRequirement '
                ).fetchall()
            load_element(M.RenewablePortfolioStandard, raw)

        # CostFixed
        if mi:
            raw = cur.execute(
                'SELECT region, period, tech, vintage, cost FROM main.CostFixed '
                'WHERE period >= ? AND period <= ?',
                (mi.base_year, mi.last_demand_year),
            ).fetchall()
        else:
            raw = cur.execute(
                'SELECT region, period, tech, vintage, cost FROM main.CostFixed '
            ).fetchall()
        load_element(M.CostFixed, raw, self.viable_rtv, val_loc=(0, 2, 3))

        # CostInvest
        # exclude "existing" vintages by screening for base year and beyond.
        # the "viable_rtv" will filter anything beyond view
        if mi:
            raw = cur.execute(
                'SELECT region, tech, vintage, cost FROM main.CostInvest ' 'WHERE vintage >= ?',
                (mi.base_year,),
            ).fetchall()
        else:
            raw = cur.execute('SELECT region, tech, vintage, cost FROM main.CostInvest ').fetchall()
        load_element(M.CostInvest, raw, self.viable_rtv, (0, 1, 2))

        # CostVariable
        if mi:
            raw = cur.execute(
                'SELECT region, period, tech, vintage, cost FROM main.CostVariable '
                'WHERE period >= ? AND period <= ?',
                (mi.base_year, mi.last_demand_year),
            ).fetchall()
        else:
            raw = cur.execute(
                'SELECT region, period, tech, vintage, cost FROM main.CostVariable '
            ).fetchall()
        load_element(M.CostVariable, raw, self.viable_rtv, (0, 2, 3))

        # CostEmissions (and supporting index set)
        if self.table_exists('CostEmission'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, emis_comm from main.CostEmission '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
                load_element(M.CostEmission_rpe, raw)

                raw = cur.execute(
                    'SELECT region, period, emis_comm, cost from main.CostEmission '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
                load_element(M.CostEmission, raw)
            else:
                raw = cur.execute(
                    'SELECT region, period, emis_comm from main.CostEmission '
                ).fetchall()
                load_element(M.CostEmission_rpe, raw)

                raw = cur.execute(
                    'SELECT region, period, emis_comm, cost from main.CostEmission '
                ).fetchall()
                load_element(M.CostEmission, raw)

        # DefaultLoanRate
        raw = cur.execute(
            "SELECT value FROM main.MetaDataReal WHERE element = 'default_loan_rate'"
        ).fetchall()
        # do this separately as it is non-indexed, so we need to make a mapping with None
        data[M.DefaultLoanRate.name] = {None: raw[0][0]}

        # LoanRate
        if mi:
            raw = cur.execute(
                'SELECT region, tech, vintage, rate FROM main.LoanRate ' 'WHERE vintage >= ?',
                (mi.base_year,),
            ).fetchall()
        else:
            raw = cur.execute('SELECT region, tech, vintage, rate FROM main.LoanRate ').fetchall()

        load_element(M.LoanRate, raw, self.viable_rtv, (0, 1, 2))

        # MinCapacity
        if self.table_exists('MinCapacity'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, tech, min_cap FROM main.MinCapacity '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, tech, min_cap FROM main.MinCapacity '
                ).fetchall()
            load_element(M.MinCapacity, raw, self.viable_rt, (0, 2))

        # MaxCapacity
        if self.table_exists('MaxCapacity'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, tech, max_cap FROM main.MaxCapacity '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, tech, max_cap FROM main.MaxCapacity '
                ).fetchall()
            load_element(M.MaxCapacity, raw, self.viable_rt, (0, 2))

        # MinNewCap
        if self.table_exists('MinNewCapacity'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, tech, min_cap FROM main.MinNewCapacity '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, tech, min_cap FROM main.MinNewCapacity '
                ).fetchall()
            load_element(M.MinNewCapacity, raw, self.viable_rt, (0, 2))

        # MaxNewCap
        if self.table_exists('MaxNewCapacity'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, tech, max_cap FROM main.MaxNewCapacity '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, tech, max_cap FROM main.MaxNewCapacity '
                ).fetchall()
            load_element(M.MaxNewCapacity, raw, self.viable_rt, (0, 2))

        # MaxCapacityGroup
        if self.table_exists('MaxCapacityGroup'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, group_name, max_cap FROM main.MaxCapacityGroup '
                    ' WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, group_name, max_cap FROM main.MaxCapacityGroup '
                ).fetchall()
            load_element(M.MaxCapacityGroup, raw)

        # MinCapacityGroup
        if self.table_exists('MinCapacityGroup'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, group_name, min_cap FROM main.MinCapacityGroup '
                    ' WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, group_name, min_cap FROM main.MinCapacityGroup '
                ).fetchall()
            load_element(M.MinCapacityGroup, raw)

        # MinNewCapacityGroup
        if self.table_exists('MinNewCapacityGroup'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, group_name, min_new_cap FROM main.MinNewCapacityGroup '
                    ' WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, group_name, min_new_cap FROM main.MinNewCapacityGroup '
                ).fetchall()
            load_element(M.MinNewCapacityGroup, raw)

        # MaxNewCapacityGroup
        if self.table_exists('MaxNewCapacityGroup'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, group_name, max_new_cap FROM main.MaxNewCapacityGroup '
                    ' WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, group_name, max_new_cap FROM main.MaxNewCapacityGroup '
                ).fetchall()
            load_element(M.MaxNewCapacityGroup, raw)

        # MinCapacityShare
        if self.table_exists('MinCapacityShare'):
            raw = cur.execute(
                'SELECT region, period, tech, group_name, min_proportion FROM main.MinCapacityShare'
            ).fetchall()
            load_element(M.MinCapacityShare, raw, self.viable_rt, (0, 2))

        # MaxCapacityShare
        if self.table_exists('MaxCapacityShare'):
            raw = cur.execute(
                'SELECT region, period, tech, group_name, max_proportion FROM main.MaxCapacityShare'
            ).fetchall()
            load_element(M.MaxCapacityShare, raw, self.viable_rt, (0, 2))

        # MinNewCapacityShare
        if self.table_exists('MinNewCapacityShare'):
            raw = cur.execute(
                'SELECT region, period, tech, group_name, max_proportion FROM main.MinNewCapacityShare'
            ).fetchall()
            load_element(M.MinCapacityShare, raw, self.viable_rt, (0, 2))

        # MaxNewCapacityShare
        if self.table_exists('MaxNewCapacityShare'):
            raw = cur.execute(
                'SELECT region, period, tech, group_name, max_proportion FROM main.MaxNewCapacityShare'
            ).fetchall()
            load_element(M.MaxCapacityShare, raw, self.viable_rt, (0, 2))

        # MinActivityGroup
        if self.table_exists('MinActivityGroup'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, group_name, min_act FROM main.MinActivityGroup '
                    ' WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, group_name, min_act FROM main.MinActivityGroup '
                ).fetchall()
            load_element(M.MinActivityGroup, raw)

        # MaxActivityGroup
        if self.table_exists('MaxActivityGroup'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, group_name, max_act FROM main.MaxActivityGroup '
                    ' WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, group_name, max_act FROM main.MaxActivityGroup '
                ).fetchall()
            load_element(M.MaxActivityGroup, raw)

        # MinActivityShare
        if self.table_exists('MinActivityShare'):
            raw = cur.execute(
                'SELECT region, period, tech, group_name, min_proportion FROM main.MinActivityShare'
            ).fetchall()
            load_element(M.MinActivityShare, raw, self.viable_rt, (0, 2))

        # MaxActivityShare
        if self.table_exists('MaxActivityShare'):
            raw = cur.execute(
                'SELECT region, period, tech, group_name, max_proportion FROM main.MaxActivityShare'
            ).fetchall()
            load_element(M.MaxActivityShare, raw, self.viable_rt, (0, 2))

        # MaxResource
        if self.table_exists('MaxResource'):
            raw = cur.execute('SELECT region, tech, max_res FROM main.MaxResource').fetchall()
            load_element(M.MaxResource, raw, self.viable_rt, (0, 1))

        # MaxActivity
        if self.table_exists('MaxActivity'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, tech, max_act FROM main.MaxActivity '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, tech, max_act FROM main.MaxActivity '
                ).fetchall()
            load_element(M.MaxActivity, raw, self.viable_rt, (0, 2))

        # MinActivity
        if self.table_exists('MinActivity'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, tech, min_act FROM main.MinActivity '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, tech, min_act FROM main.MinActivity '
                ).fetchall()
            load_element(M.MinActivity, raw, self.viable_rt, (0, 2))

        # MaxSeasonalActivity
        if self.table_exists('MaxSeasonalActivity'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, season, tech, max_act FROM main.MaxSeasonalActivity '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, season, tech, max_act FROM main.MaxSeasonalActivity '
                ).fetchall()
            load_element(M.MaxSeasonalActivity, raw, self.viable_rt, (0, 3))

        # MinSeasonalActivity
        if self.table_exists('MinSeasonalActivity'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, season, tech, min_act FROM main.MinSeasonalActivity '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, season, tech, min_act FROM main.MinSeasonalActivity '
                ).fetchall()
            load_element(M.MinSeasonalActivity, raw, self.viable_rt, (0, 3))

        # MinAnnualCapacityFactor
        if self.table_exists('MinAnnualCapacityFactor'):
            raw = cur.execute(
                'SELECT region, period, tech, output_comm, factor FROM main.MinAnnualCapacityFactor'
            ).fetchall()
            load_element(M.MinAnnualCapacityFactor, raw, self.viable_rt, (0, 2))

        # MaxAnnualCapacityFactor
        if self.table_exists('MaxAnnualCapacityFactor'):
            raw = cur.execute(
                'SELECT region, period, tech, output_comm, factor FROM main.MaxAnnualCapacityFactor'
            ).fetchall()
            load_element(M.MaxAnnualCapacityFactor, raw, self.viable_rt, (0, 2))

        # GrowthRateMax
        if self.table_exists('GrowthRateMax'):
            raw = cur.execute('SELECT region, tech, rate FROM main.GrowthRateMax').fetchall()
            load_element(M.GrowthRateMax, raw, self.viable_rt, (0, 1))

        # GrowthRateSeed
        if self.table_exists('GrowthRateSeed'):
            raw = cur.execute('SELECT region, tech, seed FROM main.GrowthRateSeed').fetchall()
            load_element(M.GrowthRateSeed, raw, self.viable_rt, (0, 1))

        # EmissionLimit
        if self.table_exists('EmissionLimit'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, emis_comm, value FROM main.EmissionLimit '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, emis_comm, value FROM main.EmissionLimit '
                ).fetchall()

            load_element(M.EmissionLimit, raw)

        # EmissionActivity
        # The current emission constraint screens by valid inputs, so if it is NOT
        # built in a particular region, this should still be OK
        if self.table_exists('EmissionActivity'):
            if mi:
                raw = cur.execute(
                    'SELECT region, emis_comm, input_comm, tech, vintage, output_comm, activity '
                    'FROM main.EmissionActivity '
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, emis_comm, input_comm, tech, vintage, output_comm, activity '
                    'FROM main.EmissionActivity '
                ).fetchall()
            load_element(M.EmissionActivity, raw, self.viable_ritvo, (0, 2, 3, 4, 5))

        # EmissionEmbodied
        if self.table_exists('EmissionEmbodied'):
            if mi:
                raw = cur.execute(
                    'SELECT region, emis_comm, tech, vintage, value '
                    'FROM main.EmissionEmbodied'
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, emis_comm, tech, vintage, value '
                    'FROM main.EmissionEmbodied'
                ).fetchall()
            load_element(M.EmissionEmbodied, raw, self.viable_rtv, (0, 2, 3))


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

        # RampUp
        if self.table_exists('RampUp'):
            raw = cur.execute('SELECT region, tech, rate FROM main.RampUp').fetchall()
            load_element(M.RampUp, raw, self.viable_rt, (0, 1))

        # RampDown
        if self.table_exists('RampDown'):
            raw = cur.execute('SELECT region, tech, rate FROM main.RampDown').fetchall()
            load_element(M.RampDown, raw, self.viable_rt, (0, 1))

        # CapacityCredit
        if self.table_exists('CapacityCredit'):
            if mi:
                raw = cur.execute(
                    'SELECT region, period, tech, vintage, credit FROM main.CapacityCredit '
                    'WHERE period >= ? AND period <= ?',
                    (mi.base_year, mi.last_demand_year),
                ).fetchall()
            else:
                raw = cur.execute(
                    'SELECT region, period, tech, vintage, credit FROM main.CapacityCredit '
                ).fetchall()
            load_element(M.CapacityCredit, raw, self.viable_rtv, (0, 2, 3))

        # PlanningReserveMargin
        if self.table_exists('PlanningReserveMargin'):
            raw = cur.execute('SELECT region, margin FROM main.PlanningReserveMargin').fetchall()
            load_element(M.PlanningReserveMargin, raw)

        # StorageDuration
        if self.table_exists('StorageDuration'):
            raw = cur.execute('SELECT region, tech, duration FROM main.StorageDuration').fetchall()
            load_element(M.StorageDuration, raw, self.viable_rt, (0, 1))

        # StorageInitFrac
        # Not currently supported -- odd behavior and not region-indexed
        if self.table_exists('StorageInitFrac'):
            raw = cur.execute('SELECT region, period, season, tech, vintage, frac FROM main.StorageInitFrac').fetchall()
            load_element(M.StorageInitFrac, raw, self.viable_rtv, (0,3,4))
            # if len(raw) > 0:
            #     logger.warning(
            #         'Initialization of storage values currently NOT supported.'
            #         '  Values in StorageInit table will be ignored, and storage init value'
            #         ' will be optimized.'
            #     )

        # For T/S:  dump the size of all data elements into the log
        if self.debugging:
            temp = '\n'.join((f'{k} : {len(v)}' for k, v in data.items()))
            logger.info(temp)

        # capture the parameter indexing sets
        set_data = self.load_param_idx_sets(data=data)
        data.update(set_data)
        self.data = data

        return data

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
            M.EmissionLimit.name: M.EmissionLimitConstraint_rpe.name,
            M.MaxActivity.name: M.MaxActivityConstraint_rpt.name,
            M.MaxSeasonalActivity.name: M.MaxSeasonalActivityConstraint_rpst.name,
            M.MaxActivityGroup.name: M.MaxActivityGroup_rpg.name,
            M.MaxActivityShare.name: M.MaxActivityShareConstraint_rptg.name,
            M.MaxAnnualCapacityFactor.name: M.MaxAnnualCapacityFactorConstraint_rpto.name,
            M.MaxCapacity.name: M.MaxCapacityConstraint_rpt.name,
            M.MaxCapacityGroup.name: M.MaxCapacityGroupConstraint_rpg.name,
            M.MaxCapacityShare.name: M.MaxCapacityShareConstraint_rptg.name,
            M.MaxNewCapacity.name: M.MaxNewCapacityConstraint_rpt.name,
            M.MaxNewCapacityGroup.name: M.MaxNewCapacityGroupConstraint_rpg.name,
            M.MaxNewCapacityShare.name: M.MaxNewCapacityShareConstraint_rptg.name,
            M.MaxResource.name: M.MaxResourceConstraint_rt.name,
            M.MinActivity.name: M.MinActivityConstraint_rpt.name,
            M.MinSeasonalActivity.name: M.MinSeasonalActivityConstraint_rpst.name,
            M.MinActivityGroup.name: M.MinActivityGroup_rpg.name,
            M.MinActivityShare.name: M.MinActivityShareConstraint_rptg.name,
            M.MinAnnualCapacityFactor.name: M.MinAnnualCapacityFactorConstraint_rpto.name,
            M.MinCapacity.name: M.MinCapacityConstraint_rpt.name,
            M.MinCapacityGroup.name: M.MinCapacityGroupConstraint_rpg.name,
            M.MinCapacityShare.name: M.MinCapacityShareConstraint_rptg.name,
            M.MinNewCapacity.name: M.MinNewCapacityConstraint_rpt.name,
            M.MinNewCapacityGroup.name: M.MinNewCapacityGroupConstraint_rpg.name,
            M.MinNewCapacityShare.name: M.MinNewCapacityShareConstraint_rptg.name,
            M.RenewablePortfolioStandard.name: M.RenewablePortfolioStandardConstraint_rpg.name,
            M.ResourceBound.name: M.ResourceConstraint_rpr.name,
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
