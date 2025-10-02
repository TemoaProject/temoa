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
Created on:  2025/03/14

Convert various constraints on the Max/Min separate tables paradigm
to the new operator-based single Limit table paradigm.
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
    help='Path to schema file (default=data_files/temoa_schema_v3_2)',
    required=False,
    dest='schema',
    default='data_files/temoa_schema_v3_2.sql',
)
options = parser.parse_args()
legacy_db: Path = Path(options.source_db)
schema_file = Path(options.schema)

new_db_name = legacy_db.stem + '_v3_2.sqlite'
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

add_operator_tables = {
    'EmissionLimit': ('LimitEmission', 'le'),
    'MinTechOutputSplitAnnual': ('LimitTechOutputSplitAnnual', 'ge'),
    'MinTechOutputSplit': ('LimitTechOutputSplit', 'ge'),
    'MinTechInputSplitAnnual': ('LimitTechInputSplitAnnual', 'le'),
    'MinTechInputSplit': ('LimitTechInputSplit', 'ge'),
    'MinSeasonalActivity': ('LimitSeasonalActivity', 'ge'),
    'MinNewCapacityShare': ('LimitNewCapacityShare', 'ge'),
    'MinNewCapacityGroupShare': ('LimitNewCapacityGroupShare', 'ge'),
    'MinNewCapacityGroup': ('LimitNewCapacityGroup', 'ge'),
    'MinNewCapacity': ('LimitNewCapacity', 'ge'),
    'MinCapacityShare': ('LimitCapacityShare', 'ge'),
    'MinCapacityGroup': ('LimitCapacityGroup', 'ge'),
    'MinCapacity': ('LimitCapacity', 'ge'),
    'MinAnnualCapacityFactor': ('LimitAnnualCapacityFactor', 'ge'),
    'MinActivityShare': ('LimitActivityShare', 'ge'),
    'MinActivityGroup': ('LimitActivityGroup', 'ge'),
    'MinActivity': ('LimitActivity', 'ge'),
    'MaxTechOutputSplitAnnual': ('LimitTechOutputSplitAnnual', 'le'),
    'MaxTechOutputSplit': ('LimitTechOutputSplit', 'le'),
    'MaxTechInputSplitAnnual': ('LimitTechInputSplitAnnual', 'le'),
    'MaxTechInputSplit': ('LimitTechInputSplit', 'le'),
    'MaxSeasonalActivity': ('LimitSeasonalActivity', 'le'),
    'MaxNewCapacityShare': ('LimitNewCapacityShare', 'le'),
    'MaxNewCapacityGroupShare': ('LimitNewCapacityGroupShare', 'le'),
    'MaxNewCapacityGroup': ('LimitNewCapacityGroup', 'le'),
    'MaxNewCapacity': ('LimitNewCapacity', 'le'),
    'MaxCapacityShare': ('LimitCapacityShare', 'le'),
    'MaxCapacityGroup': ('LimitCapacityGroup', 'le'),
    'MaxCapacity': ('LimitCapacity', 'le'),
    'MaxAnnualCapacityFactor': ('LimitAnnualCapacityFactor', 'le'),
    'MaxActivityShare': ('LimitActivityShare', 'le'),
    'MaxActivityGroup': ('LimitActivityGroup', 'le'),
    'MaxActivity': ('LimitActivity', 'le'),
    'MaxResource': ('LimitResource', 'le'),
    'StorageLevelFraction': ('LimitStorageLevelFraction', 'e'),
}


# Collapse Max/Min constraint tables
print('\n --- Collapsing Max/Min tables and adding operators ---')
for old_name, (new_name, operator) in add_operator_tables.items():

    try:
        data = con_old.execute(f'SELECT * FROM {old_name}').fetchall()
    except sqlite3.OperationalError:
        print('TABLE NOT FOUND: ' + old_name)
        continue

    if not data:
        print('No data for: ' + old_name)
        continue

    new_cols: tuple = [c[1] for c in con_new.execute(f'PRAGMA table_info({new_name});').fetchall()]
    op_index = new_cols.index('operator')
    data = [(*row[0:op_index], operator, *row[op_index::]) for row in data]

    # construct the query with correct number of placeholders
    num_placeholders = len(data[0])
    placeholders = ','.join(['?' for _ in range(num_placeholders)])
    query = f'INSERT OR REPLACE INTO {new_name} VALUES ({placeholders})'
    con_new.executemany(query, data)
    print(f'Added operator index to {new_name} and inserted {len(data)} rows')


old_tables = set([t[1] for t in con_old.execute('SELECT * FROM sqlite_master WHERE type="table";')])
new_tables = set([t[1] for t in con_new.execute('SELECT * FROM sqlite_master WHERE type="table";')])
limit_tables = set(add_operator_tables.keys())

direct_transfer_tables = (new_tables & old_tables) - limit_tables

print('\n --- Executing direct transfers ---')
for table in direct_transfer_tables:

    try:
        con_old.execute(f'SELECT * FROM {table}').fetchone()
    except sqlite3.OperationalError:
        print('TABLE NOT FOUND: ' + table)
        continue

    data = con_old.execute(f'SELECT * FROM {table}').fetchall()

    if not data:
        print('No data for: ' + table)
        continue

    # construct the query with correct number of placeholders
    num_placeholders = len(data[0])
    placeholders = ','.join(['?' for _ in range(num_placeholders)])
    query = f'INSERT OR REPLACE INTO {table} VALUES ({placeholders})'
    con_new.executemany(query, data)
    print(f'Transferred {len(data)} rows from {table}')


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