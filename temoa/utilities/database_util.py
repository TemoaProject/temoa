"""
Utility class for interacting with a Temoa scenario database (SQLite).

This module provides the DatabaseUtil class to abstract the database connection
and querying process. It offers methods to retrieve specific data slices
such as technologies, commodities, capacity, and flows for given scenarios,
periods, and regions.
"""

import os
import re
import sqlite3
from os import PathLike

import deprecated
import pandas as pd


class DatabaseUtil:
    """
    A utility to connect to and query a Temoa SQLite database.

    This class provides methods to extract data from the database, handling
    connection management and query construction. It can be used as a context
    manager to ensure database connections are closed properly.

    Args:
        database_path: The file path to the SQLite database.
        scenario: The specific scenario to query within the database.

    Raises:
        ValueError: If the database path does not exist or if connecting fails.
    """

    database: str
    scenario: str | None
    con: sqlite3.Connection
    cur: sqlite3.Cursor

    def __init__(self, database_path: str | PathLike[str], scenario: str | None = None) -> None:
        self.database = os.path.abspath(database_path)
        self.scenario = scenario
        if not os.path.exists(self.database):
            raise ValueError("The database file path doesn't exist")

        if self.is_database_file(self.database):
            try:
                self.con = sqlite3.connect(self.database)
                self.cur = self.con.cursor()
                self.con.text_factory = str
            except sqlite3.Error as e:
                raise ValueError(f'Unable to connect to database: {e}') from e
        elif self.database.endswith('.dat'):
            raise ValueError('Reading .dat files is no longer supported')

    def close(self) -> None:
        """Closes the database cursor and connection."""
        if self.cur:
            self.cur.close()
        if self.con:
            self.con.close()

    @staticmethod
    def is_database_file(file: str | PathLike[str]) -> bool:
        """Checks if a file has a common SQLite database extension."""
        return str(file).endswith(('.db', '.sqlite', '.sqlite3'))

    @deprecated.deprecated(version='0.9.0', reason='Reading from .dat files is no longer supported')
    def read_from_dat_file(self, inp_comm: str | None, inp_tech: str | None) -> pd.DataFrame:
        """
        This method is deprecated and will raise a ValueError if called on a
        database connection.
        """
        # This check ensures the method is unreachable with a valid DB connection.
        if hasattr(self, 'cur') and self.cur is not None:
            raise ValueError('Invalid Operation For Database file')

        # The following code is unreachable in the current design but is kept
        # to document the deprecated functionality.
        inp_comm_re = inp_comm if inp_comm is not None else r'\w+'
        inp_tech_re = inp_tech if inp_tech is not None else r'\w+'

        rows: list[tuple[str, ...]] = []
        eff_flag = False
        with open(self.database, encoding='utf-8') as f:
            for line in f:
                if not eff_flag and re.search(r'^\s*param\s+efficiency\s*[:][=]', line, re.I):
                    eff_flag = True
                elif eff_flag:
                    line = re.sub(r'[#].*$', ' ', line)
                    if re.search(r'^\s*;\s*$', line):
                        break
                    if re.search(r'^\s+$', line):
                        continue
                    line = line.strip()
                    row_parts = tuple(re.split(r'\s+', line))
                    if (
                        len(row_parts) >= 4
                        and not re.search(inp_comm_re, row_parts[0])
                        and not re.search(inp_comm_re, row_parts[3])
                        and not re.search(inp_tech_re, row_parts[1])
                    ):
                        continue
                    rows.append(row_parts)

        result = pd.DataFrame(rows, columns=['input_comm', 'tech', 'period', 'output_comm', 'flow'])
        return result[['input_comm', 'tech', 'output_comm']]

    def get_time_peridos_for_flags(self, flags: list[str] | None = None) -> set[int]:
        """Retrieves a set of time periods, optionally filtered by flags."""
        if (flags is None) or (not flags):
            query = 'SELECT period FROM time_period'
        else:
            in_clause = ', '.join(f"'{flag}'" for flag in flags)
            query = f'SELECT period FROM time_period WHERE flag IN ({in_clause})'

        self.cur.execute(query)
        return {int(row[0]) for row in self.cur}

    def get_technologies_for_flags(self, flags: list[str] | None = None) -> set[str]:
        """Retrieves a set of technologies, optionally filtered by flags."""
        if (flags is None) or (not flags):
            query = 'SELECT tech FROM Technology'
        else:
            in_clause = ', '.join(f"'{flag}'" for flag in flags)
            query = f'SELECT tech FROM Technology WHERE flag IN ({in_clause})'

        return {row[0] for row in self.cur.execute(query)}

    def get_commodities_and_tech(
        self, inp_comm: str | None, inp_tech: str | None, region: str | None
    ) -> pd.DataFrame:
        """Retrieves technologies and commodities based on filters."""
        inp_comm_sql = f"'{inp_comm}'" if inp_comm else 'NULL'
        inp_tech_sql = f"'{inp_tech}'" if inp_tech else 'NULL'

        if not inp_comm and not inp_tech:
            inp_comm_sql = 'NOT NULL'
            inp_tech_sql = 'NOT NULL'

        where_clause = (
            f'(input_comm IS {inp_comm_sql} OR output_comm IS {inp_comm_sql} OR tech IS '
            f'{inp_tech_sql})'
        )
        if region:
            where_clause = f"region LIKE '%{region}%' AND {where_clause}"

        query = f'SELECT input_comm, tech, output_comm FROM efficiency WHERE {where_clause}'
        self.cur.execute(query)
        return pd.DataFrame(self.cur.fetchall(), columns=['input_comm', 'tech', 'output_comm'])

    def get_existing_technologies_for_commodity(
        self, comm: str, region: str | None, comm_type: str = 'input'
    ) -> pd.DataFrame:
        """Retrieves technologies associated with a specific commodity."""
        if comm_type == 'input':
            query = f"SELECT DISTINCT tech FROM efficiency WHERE input_comm IS '{comm}'"
        else:
            query = f"SELECT DISTINCT tech FROM efficiency WHERE output_comm IS '{comm}'"
        if region:
            query += f" AND region LIKE '%{region}%'"

        self.cur.execute(query)
        return pd.DataFrame(self.cur.fetchall(), columns=['tech'])

    def get_commodities_for_flags(self, flags: list[str] | None = None) -> set[str]:
        """Retrieves a set of commodities, optionally filtered by flags."""
        if (flags is None) or (not flags):
            query = 'SELECT name FROM Commodity'
        else:
            in_clause = ', '.join(f"'{flag}'" for flag in flags)
            query = f'SELECT name FROM Commodity WHERE flag IN ({in_clause})'

        return {row[0] for row in self.cur.execute(query)}

    def get_commodities_by_technology(
        self, region: str | None, comm_type: str = 'input'
    ) -> set[tuple[str, str]]:
        """Retrieves commodity-technology pairs."""
        if comm_type == 'input':
            query = 'SELECT DISTINCT input_comm, tech FROM efficiency'
        elif comm_type == 'output':
            query = 'SELECT DISTINCT tech, output_comm FROM efficiency'
        else:
            raise ValueError("Invalid comm_type: can only be 'input' or 'output'")

        if region:
            query += f" WHERE region LIKE '%{region}%'"

        return {tuple(row) for row in self.cur.execute(query)}

    def get_capacity_for_tech_and_period(
        self, tech: str | None = None, period: int | None = None, region: str | None = None
    ) -> pd.DataFrame | pd.Series:
        """Retrieves capacity data, aggregated by technology."""
        if not self.scenario:
            raise ValueError('A scenario must be set for output-related queries')

        columns = ['tech', 'period', 'SUM(capacity)', 'region']
        query = (
            f'SELECT {", ".join(columns)} FROM output_net_capacity WHERE scenario IS '
            f"'{self.scenario}'"
        )

        if region:
            query += f" AND region LIKE '{region}%'"
        if tech:
            query += f" AND tech IS '{tech}'"
        if period:
            query += f" AND period IS '{period}'"

        query += ' GROUP BY tech, region, period, sector;'
        self.cur.execute(query)

        df_columns = [col.replace('SUM(capacity)', 'capacity') for col in columns]
        result = pd.DataFrame(self.cur.fetchall(), columns=df_columns)

        if region is None and not result.empty:
            mask = result['region'].str.contains('-')
            result.loc[mask, 'capacity'] /= 2

        result.drop(columns=['region'], inplace=True)
        if len(df_columns) == 2:
            return result.sum()
        else:
            return result.groupby(by='tech').sum().reset_index()

    def get_output_flow_for_period(
        self,
        period: int,
        region: str | None,
        comm_type: str = 'input',
        commodity: str | None = None,
    ) -> pd.DataFrame:
        """Retrieves aggregated output flow data."""
        if not self.scenario:
            raise ValueError('A scenario must be set for output-related queries')

        columns: list[str] = []
        table = ''
        if comm_type == 'input':
            table = 'output_flow_in'
            if commodity is None:
                columns.append('input_comm')
        elif comm_type == 'output':
            table = 'output_flow_out'
            if commodity is None:
                columns.append('output_comm')
        columns.append('tech')

        query = (
            f'SELECT DISTINCT {", ".join(columns)}, SUM(flow) AS flow FROM {table} WHERE '
            f"scenario IS '{self.scenario}'"
        )

        if region:
            query += f" AND region LIKE '{region}%'"
        query += f" AND period IS '{period}'"

        group_by = ['tech']
        if commodity:
            query += f" AND {comm_type}_comm IS '{commodity}'"
            if comm_type == 'output':
                query += " AND input_comm != 'ethos'"
        else:
            group_by.append(f'{comm_type}_comm')

        query += f' GROUP BY {", ".join(group_by)}'
        self.cur.execute(query)

        df_columns = columns + ['flow']
        return pd.DataFrame(self.cur.fetchall(), columns=df_columns)

    def get_emissions_activity_for_period(self, period: int, region: str | None) -> pd.DataFrame:
        """Retrieves emissions activity data."""
        if not self.scenario:
            raise ValueError('A scenario must be set for output-related queries')

        query = f"""
            SELECT E.emis_comm, E.tech, SUM(E.activity * O.flow)
            FROM emission_activity E, output_flow_out O
            WHERE E.input_comm = O.input_comm
              AND E.tech = O.tech
              AND E.vintage = O.vintage
              AND E.output_comm = O.output_comm
              AND O.scenario = '{self.scenario}'
              AND O.period = '{period}'
        """
        if region:
            query += f" AND E.region LIKE '%{region}%'"
        query += ' GROUP BY E.tech, E.emis_comm'
        self.cur.execute(query)
        return pd.DataFrame(self.cur.fetchall(), columns=['emis_comm', 'tech', 'emis_activity'])

    def get_commodity_wise_input_and_output_flow(
        self, tech: str, period: int, region: str | None
    ) -> pd.DataFrame:
        """Retrieves detailed input and output flows for a technology."""
        if not self.scenario:
            raise ValueError('A scenario must be set for output-related queries')

        query = f"""
            SELECT
                OF.input_comm, OF.output_comm, OF.vintage, OF.region,
                SUM(OF.vflow_in) AS vflow_in,
                SUM(OFO.vflow_out) AS vflow_out,
                OC.capacity
            FROM (
                SELECT region, scenario, period, input_comm, tech, vintage, output_comm,
                SUM(flow) AS vflow_in
                FROM output_flow_in
                GROUP BY region, scenario, period, input_comm, tech, vintage, output_comm
            ) AS OF
            INNER JOIN (
                SELECT region, scenario, period, input_comm, tech, vintage, output_comm,
                SUM(flow) AS vflow_out
                FROM output_flow_out
                GROUP BY region, scenario, period, input_comm, tech, vintage, output_comm
            ) AS OFO ON
                OF.region = OFO.region AND
                OF.scenario = OFO.scenario AND
                OF.period = OFO.period AND
                OF.tech = OFO.tech AND
                OF.input_comm = OFO.input_comm AND
                OF.vintage = OFO.vintage AND
                OF.output_comm = OFO.output_comm
            INNER JOIN output_net_capacity OC ON
                OF.region = OC.region AND
                OF.scenario = OC.scenario AND
                OF.tech = OC.tech AND
                OF.vintage = OC.vintage
            WHERE
                OF.period = '{period}' AND
                OF.tech IS '{tech}' AND
                OF.scenario IS '{self.scenario}'
        """
        if region:
            query += f" AND OF.region LIKE '%{region}%'"
        query += ' GROUP BY OF.region, OF.vintage, OF.input_comm, OF.output_comm'

        self.cur.execute(query)
        result = pd.DataFrame(
            self.cur.fetchall(),
            columns=[
                'input_comm',
                'output_comm',
                'vintage',
                'region',
                'flow_in',
                'flow_out',
                'capacity',
            ],
        )
        return pd.DataFrame(
            result.groupby(['input_comm', 'output_comm', 'vintage'], as_index=False).sum()
        )
