"""
The purpose of this module is to build an Object to hold all of the network data for the entire
model in a usable format for the commodity_network_manager to use in building the individual
network.
"""

from __future__ import annotations

import copy
import logging
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from typing import TYPE_CHECKING, NamedTuple, Self, TypedDict, cast, overload

import deprecated
from pyomo.core.base import ConcreteModel

from temoa.core.model import TemoaModel
from temoa.types.core_types import ParameterValue

if TYPE_CHECKING:
    from collections.abc import Callable

    from temoa.extensions.myopic.myopic_index import MyopicIndex
    from temoa.types import Commodity, Period, Region, Sector, Technology, Vintage


# --- Type Definitions ---
class EdgeTuple(NamedTuple):
    region: Region
    input_comm: Commodity
    tech: Technology
    vintage: Vintage
    output_comm: Commodity
    lifetime: int | None = None
    sector: Sector | None = None


class LinkedTechTuple(NamedTuple):
    region: Region
    driver: Technology
    emission: Commodity
    driven: Technology


type TechAttributeValue = ParameterValue
type DbConnection = sqlite3.Connection
type ModelBlock = TemoaModel | ConcreteModel


class BasicData(TypedDict):
    """Defines the shape of the data returned by _fetch_basic_data."""

    tech_retire: set[Technology]
    tech_survival_curve: set[tuple[Region, Technology, Vintage]]
    periods: list[Period]
    period_length: dict[Period, int]
    physical_commodities: set[Commodity]
    waste_commodities_all: set[Commodity]
    source_commodities_all: set[Commodity]
    demand_commodities: defaultdict[tuple[Region, Period], set[Commodity]]


class LookupData(TypedDict):
    """Defines the shape of the data returned by _fetch_lookup_data."""

    eol: defaultdict[tuple[Region, Technology, Vintage], list[Commodity]]
    construction: list[tuple[Region, Commodity, Technology, Vintage]]
    linked: set[tuple[Region, Technology, Commodity, Technology]]
    neg_cost_techs: set[Technology]


logger = logging.getLogger(__name__)


# --- Data Structure ---
@dataclass
class NetworkModelData:
    """A simple encapsulation of data needed for the Commodity Network using a dataclass."""

    demand_commodities: defaultdict[tuple[Region, Period], set[Commodity]] = field(
        default_factory=lambda: defaultdict(set)
    )
    waste_commodities: defaultdict[tuple[Region, Period], set[Commodity]] = field(
        default_factory=lambda: defaultdict(set)
    )
    capacity_commodities: set[Commodity] = field(default_factory=set)
    exchange_commodities: set[Commodity] = field(default_factory=set)
    source_commodities: defaultdict[tuple[Region, Period], set[Commodity]] = field(
        default_factory=lambda: defaultdict(set)
    )
    physical_commodities: set[Commodity] = field(default_factory=set)
    available_techs: defaultdict[tuple[Region, Period], set[EdgeTuple]] = field(
        default_factory=lambda: defaultdict(set)
    )
    available_linked_techs: set[LinkedTechTuple] = field(default_factory=set)
    tech_data: defaultdict[Technology, dict[str, TechAttributeValue]] = field(
        default_factory=lambda: defaultdict(dict)
    )

    def __post_init__(self) -> None:
        """Validate data consistency after initialization."""
        for (r, _), techs in self.available_techs.items():
            for tech in techs:
                if tech.region != r:
                    raise ValueError(
                        f'Improperly constructed set of techs for region {r}, tech: {tech}'
                    )

    def clone(self) -> Self:
        """Create a deep copy of the current object."""
        return copy.deepcopy(self)

    def update_tech_data(self, tech: Technology, element: str, value: TechAttributeValue) -> None:
        """Update a data element for a tech."""
        self.tech_data[tech][element] = value

    def get_driven_techs(self, region: Region, period: Period) -> set[EdgeTuple]:
        """Identifies all linked techs by name from the linked tech names."""
        driven_tech_names = {lt.driven for lt in self.available_linked_techs}
        return {
            efficiencyTuple
            for efficiencyTuple in self.available_techs.get((region, period), set())
            if efficiencyTuple.tech in driven_tech_names
        }

    def __str__(self) -> str:
        return (
            f'physical commodities: {len(self.physical_commodities)}, '
            f'demand commodities: {len({c for s in self.demand_commodities.values() for c in s})}, '
            f'source commodities: {len({c for s in self.source_commodities.values() for c in s})}, '
            f'available techs: {len(tuple(chain(*self.available_techs.values())))}, '
            f'linked techs: {len(self.available_linked_techs)}'
        )


# --- Builder Factory ---
@overload
def build(data: DbConnection, myopic_index: MyopicIndex | None = ...) -> NetworkModelData: ...
@overload
def build(data: ModelBlock, *args: object, **kwargs: object) -> NetworkModelData: ...
def build(data: ModelBlock | DbConnection, *args: object, **kwargs: object) -> NetworkModelData:
    """Factory function to dispatch to the correct builder based on data type."""
    builder = _get_builder(data)
    return builder(data, *args, **kwargs)


def _get_builder(data: ModelBlock | DbConnection) -> Callable[..., NetworkModelData]:
    """Selects the appropriate builder function based on the input data type."""
    if isinstance(data, TemoaModel | ConcreteModel):
        return _build_from_model
    if isinstance(data, sqlite3.Connection):
        return _build_from_db
    raise NotImplementedError(f'Cannot build NetworkModelData from type: {type(data)}')


# --- Builder Implementations ---
@deprecated.deprecated('no longer supported... build from db connection instead')
def _build_from_model(
    model: TemoaModel, myopic_index: MyopicIndex | None = None
) -> NetworkModelData:
    """Build a NetworkModelData from a TemoaModel."""
    if myopic_index is not None:
        raise NotImplementedError('Cannot build network data from model using a myopic_index')

    dem_com = defaultdict(set)
    for r, p, d in model.demand.sparse_iterkeys():
        dem_com[r, p].add(d)

    techs: defaultdict[tuple[Region, Period], set[EdgeTuple]] = defaultdict(set)
    if model.active_flow_rpsditvo is not None:
        for r, p, _s, _d, ic, tech, v, oc in model.active_flow_rpsditvo:
            techs[r, p].add(EdgeTuple(r, ic, tech, v, oc))
    if model.active_flow_rpitvo is not None:
        for r, p, ic, tech, v, oc in model.active_flow_rpitvo:
            techs[r, p].add(EdgeTuple(r, ic, tech, v, oc))

    linked_techs = {
        LinkedTechTuple(r, driver, emission, driven)
        for r, driver, emission, driven in model.linked_techs.sparse_iterkeys()
    }

    res = NetworkModelData(
        physical_commodities=set(model.commodity_all),
        demand_commodities=dem_com,
        available_techs=techs,
        available_linked_techs=linked_techs,
    )
    logger.debug('built network data: %s', res)
    return res


def _fetch_basic_data(cur: sqlite3.Cursor) -> BasicData:
    """Fetches simple, required tables and parameters from the DB."""
    tech_retire = {
        t[0] for t in cur.execute('SELECT tech FROM technology WHERE retire==1').fetchall()
    }
    try:
        tech_survival_curve = set(
            cur.execute('SELECT DISTINCT region, tech, vintage FROM survival_curve').fetchall()
        )
    except sqlite3.OperationalError:
        tech_survival_curve = set()

    periods_full = sorted(p[0] for p in cur.execute('SELECT period FROM time_period').fetchall())
    periods = periods_full[:-1]
    period_length = {
        periods_full[i]: periods_full[i + 1] - periods_full[i] for i in range(len(periods_full) - 1)
    }

    physical_commodities = {
        c[0]
        for c in cur.execute(
            "SELECT name FROM main.commodity WHERE flag LIKE '%p%' OR flag = 's' OR flag LIKE '%a%'"
        ).fetchall()
    }
    waste_commodities_all = {
        c[0] for c in cur.execute("SELECT name FROM commodity WHERE flag LIKE '%w%'").fetchall()
    }
    source_commodities_all = {
        c[0] for c in cur.execute("SELECT name FROM commodity WHERE flag = 's'").fetchall()
    }

    demand_commodities: defaultdict[tuple[Region, Period], set[Commodity]] = defaultdict(set)
    for r, p, d in cur.execute('SELECT region, period, commodity FROM main.demand').fetchall():
        demand_commodities[r, p].add(d)

    return BasicData(
        tech_retire=tech_retire,
        tech_survival_curve=tech_survival_curve,
        periods=periods,
        period_length=period_length,
        physical_commodities=physical_commodities,
        waste_commodities_all=waste_commodities_all,
        source_commodities_all=source_commodities_all,
        demand_commodities=demand_commodities,
    )


def _fetch_all_tech_definitions(
    cur: sqlite3.Cursor, myopic_index: MyopicIndex | None
) -> list[
    tuple[Region, Commodity, Technology, Vintage, Commodity, int]
    | tuple[Region, Commodity, Technology, Vintage, Commodity, int, Sector]
]:
    """Fetches the main block of technology efficiency and lifetime data."""
    default_lifetime = TemoaModel.default_lifetime_tech
    table = 'myopic_efficiency' if myopic_index else 'efficiency'

    # Check if Technology table has sector column
    try:
        cur.execute('SELECT sector FROM technology LIMIT 1')
        has_sector = True
    except sqlite3.OperationalError:
        has_sector = False
    except (sqlite3.DatabaseError, AttributeError):
        # For atypical cursors/mocks without schema
        has_sector = False

    if has_sector:
        query = f"""
            SELECT
                eff.region, eff.input_comm, eff.tech, eff.vintage, eff.output_comm,
                COALESCE(lp.lifetime, lt.lifetime, ?) AS lifetime,
                COALESCE(tech_dim.sector, 'Other') AS sector
            FROM main.{table} AS eff
            LEFT JOIN main.lifetime_process AS lp ON eff.tech = lp.tech AND eff.vintage = lp.vintage
            AND eff.region = lp.region
            LEFT JOIN main.lifetime_tech AS lt ON eff.tech = lt.tech AND eff.region = lt.region
            LEFT JOIN main.technology AS tech_dim ON eff.tech = tech_dim.tech
            JOIN main.time_period AS tp ON eff.vintage = tp.period
        """
    else:
        query = f"""
            SELECT
                eff.region, eff.input_comm, eff.tech, eff.vintage, eff.output_comm,
                COALESCE(lp.lifetime, lt.lifetime, ?) AS lifetime
            FROM main.{table} AS eff
            LEFT JOIN main.lifetime_process AS lp ON eff.tech = lp.tech AND eff.vintage = lp.vintage
            AND eff.region = lp.region
            LEFT JOIN main.lifetime_tech AS lt ON eff.tech = lt.tech AND eff.region = lt.region
            JOIN main.time_period AS tp ON eff.vintage = tp.period
        """
    cursor = cur.execute(query, (default_lifetime,))
    return cursor.fetchall()


def _fetch_lookup_data(cur: sqlite3.Cursor) -> LookupData:
    """Fetches data from all optional tables to avoid N+1 queries."""
    lookups = LookupData(eol=defaultdict(list), construction=[], linked=set(), neg_cost_techs=set())

    try:
        for r, tech, v, oc in cur.execute(
            'SELECT region, tech, vintage, output_comm FROM end_of_life_output'
        ).fetchall():
            lookups['eol'][(r, tech, v)].append(oc)
    except sqlite3.OperationalError:
        logger.warning('Table end_of_life_output not found, skipping.')

    try:
        lookups['construction'] = cur.execute(
            'SELECT region, input_comm, tech, vintage FROM construction_input'
        ).fetchall()
    except sqlite3.OperationalError:
        logger.warning('Table construction_input not found, skipping.')

    try:
        lookups['linked'] = set(
            cur.execute(
                'SELECT primary_region, primary_tech, emis_comm, driven_tech FROM main.linked_tech'
            ).fetchall()
        )
    except sqlite3.OperationalError:
        logger.warning('Table linked_tech not found, skipping.')

    try:
        lookups['neg_cost_techs'] = {
            tech
            for (tech,) in cur.execute(
                'SELECT DISTINCT tech FROM cost_variable WHERE cost < 0'
            ).fetchall()
        }
    except sqlite3.OperationalError:
        logger.warning('Table cost_variable not found, skipping.')

    return lookups


def _build_from_db(con: DbConnection, myopic_index: MyopicIndex | None = None) -> NetworkModelData:
    """Build NetworkModelData object from a sqlite database."""
    cur = con.cursor()
    res = NetworkModelData()

    # --- 1. Fetch all data from DB ---
    basic_data = _fetch_basic_data(cur)
    raw_techs = _fetch_all_tech_definitions(cur, myopic_index)
    lookup_data = _fetch_lookup_data(cur)

    res.physical_commodities = basic_data['physical_commodities']
    res.demand_commodities = basic_data['demand_commodities']

    periods: list[Period] | set[Period] = basic_data['periods']
    if myopic_index:
        periods = {
            p for p in periods if myopic_index.base_year <= p <= myopic_index.last_demand_year
        }

    living_techs: set[Technology] = set()

    # --- 2. Process technologies ---
    for tech_data in raw_techs:
        logger.debug(tech_data)
        if len(tech_data) == 7:  # Has sector
            r, ic, tech, v, oc, lifetime, sector = tech_data
        else:  # No sector
            r, ic, tech, v, oc, lifetime = tech_data
            sector = None

        for p in periods:
            if not (v <= p < v + lifetime):
                continue

            living_techs.add(tech)
            if '-' in r and r.count('-') == 1:  # Inter-regional transfer
                r1, r2 = (cast('Region', reg) for reg in r.split('-', 1))
                source_comm, dest_comm = (
                    cast('Commodity', f'{ic} ({r1})'),
                    cast('Commodity', f'{oc} ({r2})'),
                )
                res.available_techs[r2, p].add(
                    EdgeTuple(
                        region=r2,
                        input_comm=source_comm,
                        tech=tech,
                        vintage=v,
                        output_comm=oc,
                        lifetime=lifetime,
                        sector=sector,
                    )
                )
                res.available_techs[r1, p].add(
                    EdgeTuple(
                        region=r1,
                        input_comm=ic,
                        tech=tech,
                        vintage=v,
                        output_comm=dest_comm,
                        lifetime=lifetime,
                        sector=sector,
                    )
                )
                res.available_techs[r, p].add(
                    EdgeTuple(
                        region=r,
                        input_comm=ic,
                        tech=tech,
                        vintage=v,
                        output_comm=oc,
                        lifetime=lifetime,
                        sector=sector,
                    )
                )
                res.source_commodities[r2, p].add(source_comm)
                res.demand_commodities[r1, p].add(dest_comm)
                res.physical_commodities.update([source_comm, dest_comm])
                res.exchange_commodities.update([source_comm, dest_comm])
            else:  # Standard technology
                res.available_techs[r, p].add(
                    EdgeTuple(
                        region=r,
                        input_comm=ic,
                        tech=tech,
                        vintage=v,
                        output_comm=oc,
                        lifetime=lifetime,
                        sector=sector,
                    )
                )
                if ic in basic_data['source_commodities_all']:
                    res.source_commodities[r, p].add(ic)
                if oc in basic_data['waste_commodities_all']:
                    res.waste_commodities[r, p].add(oc)

            is_natural_eol = p <= v + lifetime < p + basic_data['period_length'][p]
            is_retireable = (
                tech in basic_data['tech_retire']
                and v < p <= v + lifetime - basic_data['period_length'][p]
            )
            has_survival = (r, tech, v) in basic_data['tech_survival_curve']

            if is_natural_eol or is_retireable or has_survival:
                for eol_oc in lookup_data['eol'].get((r, tech, v), []):
                    res.available_techs[r, p].add(
                        EdgeTuple(
                            region=r,
                            input_comm=cast('Commodity', tech),
                            tech=cast('Technology', 'end_of_life'),
                            vintage=v,
                            output_comm=eol_oc,
                            lifetime=lifetime,
                            sector=cast('Sector', 'other'),
                        )
                    )
                    res.source_commodities[r, p].add(cast('Commodity', tech))
                    res.capacity_commodities.add(cast('Commodity', tech))
                    if eol_oc in basic_data['waste_commodities_all']:
                        res.waste_commodities[r, p].add(eol_oc)

    # --- 3. Process Construction ---
    for r, ic, tech, v in lookup_data['construction']:
        construction_lifetime = basic_data['period_length'].get(
            cast('Period', v), cast('Period', 1)
        )
        res.available_techs[r, cast('Period', v)].add(
            EdgeTuple(
                region=r,
                input_comm=ic,
                tech=cast('Technology', 'construction'),
                vintage=v,
                output_comm=cast(
                    'Commodity', tech
                ),  # commodity is kind of input to the capacity of the technology/vice versa
                lifetime=construction_lifetime,
                sector=cast('Sector', 'other'),
            )
        )
        res.demand_commodities[r, cast('Period', v)].add(cast('Commodity', tech))
        res.capacity_commodities.add(cast('Commodity', tech))
        living_techs.add(tech)

    # --- 4. Process Linked Techs and Other Metadata ---
    res.available_linked_techs = {
        LinkedTechTuple(r, driver, emiss, driven)
        for r, driver, emiss, driven in lookup_data['linked']
        if driver in living_techs and driven in living_techs
    }
    for tech in lookup_data['neg_cost_techs']:
        res.update_tech_data(tech=tech, element='neg_cost', value=True)

    logger.debug('built network data: %s', res)
    return res
