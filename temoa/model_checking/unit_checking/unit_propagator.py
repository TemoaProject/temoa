"""
Unit Propagator - derives units for output tables from input table definitions.

This module provides the UnitPropagator class which builds lookup tables from
input data and provides unit derivation methods for populating output tables.

All methods should return None gracefully when units cannot be determined, ensuring
backward compatibility with databases that lack unit information.
"""

import logging
import re
import sqlite3
from typing import TYPE_CHECKING

from temoa.model_checking.unit_checking.relations_checker import (
    IOUnits,
    check_efficiency_table,
    make_c2a_lut,
    make_commodity_lut,
)

if TYPE_CHECKING:
    from pint import Unit

logger = logging.getLogger(__name__)


class UnitPropagator:
    """
    Provides unit derivation for output table writing.

    Builds lookup tables once at initialization from input tables and provides
    simple getter methods for each output table type. All methods should return None
    if units cannot be determined, ensuring graceful fallback for databases
    without unit information.

    Usage:
        propagator = UnitPropagator(conn)
        flow_units = propagator.get_flow_out_units('electricity')  # e.g., 'PJ'
        cap_units = propagator.get_capacity_units('E_NUCLEAR')     # e.g., 'GW'
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        """
        Initialize the propagator by building lookup tables from input data.

        Args:
            conn: SQLite connection to the database with input tables.
        """
        self._conn = conn
        self._commodity_units: dict[str, Unit] | None = None
        self._tech_io_units: dict[str, IOUnits] | None = None
        self._c2a_units: dict[str, Unit] | None = None
        self._capacity_units: dict[str, str] | None = None
        self._cost_unit: str | None = None
        self._storage_tech_commodities: dict[str, str] | None = None

        # Build all lookups, handling failures gracefully
        self._build_lookups()

    def _build_lookups(self) -> None:
        """Build all lookup tables, logging warnings on failure."""
        try:
            self._commodity_units = make_commodity_lut(self._conn)
        except (sqlite3.Error, KeyError) as e:
            logger.debug('Could not build commodity units lookup: %s', e)
            self._commodity_units = {}

        try:
            if self._commodity_units:
                tech_result = check_efficiency_table(self._conn, self._commodity_units)
                self._tech_io_units = tech_result[0]
            else:
                self._tech_io_units = {}
        except (sqlite3.Error, KeyError) as e:
            logger.debug('Could not build tech I/O units lookup: %s', e)
            self._tech_io_units = {}

        try:
            self._c2a_units = make_c2a_lut(self._conn)
        except (sqlite3.Error, KeyError) as e:
            logger.debug('Could not build C2A units lookup: %s', e)
            self._c2a_units = {}

        try:
            self._capacity_units = self._build_capacity_lut()
        except (sqlite3.Error, KeyError) as e:
            logger.debug('Could not build capacity units lookup: %s', e)
            self._capacity_units = {}

        try:
            self._cost_unit = self._derive_common_cost_unit()
        except (sqlite3.Error, KeyError) as e:
            logger.debug('Could not derive common cost unit: %s', e)
            self._cost_unit = None

        try:
            self._storage_tech_commodities = self._build_storage_commodity_lut()
        except (sqlite3.Error, KeyError) as e:
            logger.debug('Could not build storage commodity lookup: %s', e)
            self._storage_tech_commodities = {}

    def _build_capacity_lut(self) -> dict[str, str]:
        """
        Build lookup of tech -> capacity units.

        Sources (in order of precedence):
        1. existing_capacity table (direct unit definition)
        2. cost_invest table (derived from denominator, e.g. Mdollar/GW -> GW)

        Returns:
            Dictionary mapping technology name to capacity unit string.
        """
        result: dict[str, str] = {}

        # 1. Check existing_capacity
        try:
            query = 'SELECT tech, units FROM existing_capacity WHERE units IS NOT NULL'
            rows = self._conn.execute(query).fetchall()
            for tech, units in rows:
                if units and tech not in result:
                    result[tech] = units
        except sqlite3.OperationalError:
            pass

        # 2. Check cost_invest for new technologies
        try:
            query = 'SELECT tech, units FROM cost_invest WHERE units IS NOT NULL'
            rows = self._conn.execute(query).fetchall()
            for tech, units in rows:
                if tech not in result and units:
                    cap_unit = self._extract_capacity_unit(units)
                    if cap_unit:
                        result[tech] = cap_unit
        except sqlite3.OperationalError:
            pass

        return result

    @staticmethod
    def _extract_capacity_unit(unit_str: str) -> str | None:
        """
        Scavenge for a capacity unit within a complex unit string.

        Handles complex composite units like 'Mdollar / (PJ^2 / GW)' by extracting
        the known power unit (GW, MW, kW, etc.).
        """
        # Prioritize finding standard power units
        # Use word boundaries to avoid partial matches (e.g. GWh matching GW)
        patterns = [
            r'\bGW\b',
            r'\bMW\b',
            r'\bkW\b',
            r'\bTW\b',
            r'\bgigawatt\b',
            r'\bmegawatt\b',
            r'\bkilowatt\b',
        ]
        for pat in patterns:
            match = re.search(pat, unit_str)
            if match:
                return match.group(0)
        return None

    def _derive_common_cost_unit(self) -> str | None:
        """
        Derive the common cost unit from cost input tables.

        Extracts the currency portion (numerator) from the first valid cost
        table entry.

        Returns:
            Common cost unit string (e.g., 'Mdollar') or None.
        """
        cost_tables = ['cost_invest', 'cost_fixed', 'cost_variable', 'cost_emission']
        for table in cost_tables:
            try:
                query = f'SELECT units FROM {table} WHERE units IS NOT NULL LIMIT 1'
                row = self._conn.execute(query).fetchone()
                if row and row[0]:
                    units_str = row[0]
                    # Extract numerator from ratio format "MUSD / (GW)"
                    # Use regex to safely split at the main division " / ("
                    # This handles cases like "kWh/day / (GW)" where numerator has slashes
                    parts = re.split(r'\s*/\s*\(', units_str, maxsplit=1)
                    if len(parts) > 1:
                        return parts[0].strip()

                    # Fallback for simple ratios without parentheses or if strict format not used
                    if '/' in units_str:
                        return units_str.split('/', 1)[0].strip()
                    return units_str
            except sqlite3.OperationalError as e:
                logger.debug('Cost table %s not found or query failed: %s', table, e)
                continue
        return None

    def _build_storage_commodity_lut(self) -> dict[str, str]:
        """
        Build lookup of storage tech -> output commodity from efficiency table.

        Returns:
            Dictionary mapping storage technology to its output commodity.
        """
        result: dict[str, str] = {}
        try:
            # Get storage technologies from storage_duration table
            query = """
                SELECT DISTINCT e.tech, e.output_comm
                FROM efficiency e
                LEFT JOIN technology t ON e.tech = t.tech
                LEFT JOIN storage_duration sd ON e.tech = sd.tech
                WHERE t.flag = 'ps'
            """
            rows = self._conn.execute(query).fetchall()
            for tech, output_comm in rows:
                if tech not in result:
                    result[tech] = output_comm
        except sqlite3.OperationalError:
            pass
        return result

    def get_flow_out_units(self, output_comm: str) -> str | None:
        """
        Get units for output flow based on output commodity.

        Args:
            output_comm: Output commodity name.

        Returns:
            Unit string or None if not available.
        """
        if not self._commodity_units:
            return None
        unit = self._commodity_units.get(output_comm)
        return f'{unit:~}' if unit else None

    def get_flow_in_units(self, input_comm: str) -> str | None:
        """
        Get units for input flow based on input commodity.

        Args:
            input_comm: Input commodity name.

        Returns:
            Unit string or None if not available.
        """
        if not self._commodity_units:
            return None
        unit = self._commodity_units.get(input_comm)
        return f'{unit:~}' if unit else None

    def get_curtailment_units(self, output_comm: str) -> str | None:
        """
        Get units for curtailment based on output commodity.

        Args:
            output_comm: Output commodity name.

        Returns:
            Unit string or None if not available.
        """
        return self.get_flow_out_units(output_comm)

    def get_capacity_units(self, tech: str) -> str | None:
        """
        Get capacity units for a technology.

        Args:
            tech: Technology name.

        Returns:
            Unit string or None if not available.
        """
        if not self._capacity_units:
            return None
        return self._capacity_units.get(tech)

    def get_emission_units(self, emis_comm: str) -> str | None:
        """
        Get units for emissions based on emission commodity.

        Args:
            emis_comm: Emission commodity name.

        Returns:
            Unit string or None if not available.
        """
        if not self._commodity_units:
            return None
        unit = self._commodity_units.get(emis_comm)
        return f'{unit:~}' if unit else None

    def get_cost_units(self) -> str | None:
        """
        Get common cost units for cost output.

        Returns:
            Common cost unit string (e.g., 'Mdollar') or None.
        """
        return self._cost_unit

    def get_storage_units(self, tech: str) -> str | None:
        """
        Get storage level units for a storage technology.

        Storage levels are in the units of the stored commodity.

        Args:
            tech: Storage technology name.

        Returns:
            Unit string or None if not available.
        """
        if not self._storage_tech_commodities or not self._commodity_units:
            return None
        commodity = self._storage_tech_commodities.get(tech)
        if commodity:
            unit = self._commodity_units.get(commodity)
            return f'{unit:~}' if unit else None
        return None

    @property
    def has_unit_data(self) -> bool:
        """
        Check if any unit information is available.

        Returns:
            True if at least one lookup has data, False otherwise.
        """
        return bool(
            self._commodity_units or self._capacity_units or self._cost_unit or self._tech_io_units
        )
