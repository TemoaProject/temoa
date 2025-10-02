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

Written by:  I. D. Elder
iandavidelder@gmail.com
Created on:  2025/06/10

Collapses group/non-group Limit tables
"""

import argparse
import sqlite3
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument(
    '--source',
    help='Path to original database',
    required=True,
    action='store',
    dest='source_db',
)
parser.add_argument(
    '--schema',
    help='Path to schema file (default=data_files/temoa_schema_v3_3)',
    required=False,
    dest='schema',
    default='data_files/temoa_schema_v3_3.sql',
)
options = parser.parse_args()
legacy_db: Path = Path(options.source_db)
schema_file = Path(options.schema)

new_db_name = legacy_db.stem + '_v3_3.sqlite'
new_db_path = Path(legacy_db.parent, new_db_name)

con_old = sqlite3.connect(legacy_db)
con_new = sqlite3.connect(new_db_path)
cur = con_new.cursor()

# bring in the new schema and execute
with open(schema_file, 'r') as src:
    sql_script = src.read()
con_new.executescript(sql_script)

# turn off FK verification while process executes
con_new.execute('PRAGMA foreign_keys = 0;')

tables_to_collapse = {
    'LimitActivityGroup': 'LimitActivity',
    'LimitCapacityGroup': 'LimitCapacity',
    'LimitNewCapacityGroup': 'LimitNewCapacity',
    'LimitNewCapacityGroupShare': 'LimitNewCapacityShare',
}

old_tables = set([t[1] for t in con_old.execute('SELECT * FROM sqlite_master WHERE type="table";')])
new_tables = set([t[1] for t in con_new.execute('SELECT * FROM sqlite_master WHERE type="table";')])
collapsed_tables = set(tables_to_collapse.keys())

direct_transfer_tables = (new_tables & old_tables) - collapsed_tables

transfers: dict = {t: t for t in direct_transfer_tables}
transfers.update(tables_to_collapse)

print('\n --- Executing direct transfers ---')
for old_table, new_table in transfers.items():

    try:
        con_old.execute(f'SELECT * FROM {old_table}').fetchone()
    except sqlite3.OperationalError:
        print('TABLE NOT FOUND: ' + old_table)
        continue

    data = con_old.execute(f'SELECT * FROM {old_table}').fetchall()

    if not data:
        print('No data for: ' + old_table)
        continue

    # construct the query with correct number of placeholders
    num_placeholders = len(data[0])
    placeholders = ','.join(['?' for _ in range(num_placeholders)])
    query = f'INSERT OR REPLACE INTO {new_table} VALUES ({placeholders})'
    con_new.executemany(query, data)
    print(f'Transferred {len(data)} rows from {old_table} to {new_table}')


print('\n --- Validating foreign keys ---')
con_new.commit()
con_new.execute('VACUUM;')
con_new.execute('PRAGMA FOREIGN_KEYS=1;')
try:
    data = con_new.execute('PRAGMA FOREIGN_KEY_CHECK;').fetchall()
    if not data:
        print('No Foreign Key Failures.  (Good news!)')
    else:
        print('\nFK check fails (MUST BE FIXED):')
        print('(Table, Row ID, Reference Table, (fkid) )')
        for row in data:
            print(row)
except sqlite3.OperationalError as e:
    print('Foreign Key Check FAILED on new DB.  Something may be wrong with schema.')
    print(e)

print('\nFinished! Check your database for any missing data.'
      ' If there was a mismatch of table names, something may have been lost.')

con_new.close()
con_old.close()