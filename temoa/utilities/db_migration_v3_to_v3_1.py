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

Transition a v3.0 database to a v3.1 database.
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
    help='Path to schema file (default=data_files/temoa_schema_v3_1)',
    required=False,
    dest='schema',
    default='data_files/temoa_schema_v3_1.sql',
)
options = parser.parse_args()
legacy_db: Path = Path(options.source_db)
schema_file = Path(options.schema)

new_db_name = legacy_db.stem + '_v3_1.sqlite'
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

def column_check(old_name: str, new_name: str) -> bool:
    if old_name == '':
        old_name = new_name

    try:
        con_old.execute(f'SELECT * FROM {old_name}').fetchone()
    except sqlite3.OperationalError:
        return True

    new_columns = [c[1] for c in con_new.execute(f'PRAGMA table_info({new_name});').fetchall()]
    old_columns = [c[1] for c in con_old.execute(f'PRAGMA table_info({old_name});').fetchall()]

    missing = [c for c in new_columns if c not in old_columns and c != 'period']
    if len(missing) > 0:
        msg = (
            f'Columns of {new_name} in the new database missing from {old_name} in old database. Try adding or renaming the column in the old database:'
            f'\n{missing}\n'
            )
        print(msg)
        return False
    return True

# table mapping for DIRECT transfers
# fmt: off
direct_transfer_tables = [
    ('',                      'CapacityCredit'),
    ('',                      'CapacityToActivity'),
    ('',                      'Commodity'),
    ('',                      'CommodityType'),
    ('',                      'CostEmission'),
    ('',                      'CostFixed'),
    ('',                      'CostInvest'),
    ('',                      'CostVariable'),
    ('',                      'Demand'),
    ('',                      'Efficiency'),
    ('',                      'EmissionActivity'),
    ('',                      'ExistingCapacity'),
    ('',                      'LifetimeProcess'),
    ('',                      'LifetimeTech'),
    ('',                      'LinkedTech'),
    ('',                      'LoanRate'),
    ('',                      'MetaData'),
    ('',                      'MetaDataReal'),
    ('',                      'PlanningReserveMargin'),
    ('',                      'RampDown'),
    ('',                      'RampUp'),
    ('',                      'Region'),
    ('',                      'RPSRequirement'),
    ('',                      'SectorLabel'),
    ('',                      'StorageDuration'),
    ('',                      'TechGroup'),
    ('',                      'TechGroupMember'),
    ('',                      'Technology'),
    ('',                      'TechnologyType'),
    ('',                      'TimeOfDay'),
    ('',                      'TimePeriod'),
    ('',                      'TimePeriodType'),
]

period_added_tables = [
    ('',                      'CapacityFactorProcess'),
    ('',                      'CapacityFactorTech'),
    ('',                      'DemandSpecificDistribution'),
    ('',                      'TimeSeason'),
    ('',                      'TimeSegmentFraction'),
]

operator_added_tables = {
    'EmissionLimit': ('LimitEmission', 'le'),
    'TechOutputSplit': ('LimitTechOutputSplit', 'ge'),
    'TechInputSplitAnnual': ('LimitTechInputSplitAnnual', 'le'),
    'TechInputSplitAverage': ('LimitTechInputSplitAnnual', 'le'),
    'TechInputSplit': ('LimitTechInputSplit', 'ge'),
    'MinNewCapacityShare': ('LimitNewCapacityShare', 'ge'),
    'MinNewCapacityGroupShare': ('LimitNewCapacityShare', 'ge'),
    'MinNewCapacityGroup': ('LimitNewCapacity', 'ge'),
    'MinNewCapacity': ('LimitNewCapacity', 'ge'),
    'MinCapacityShare': ('LimitCapacityShare', 'ge'),
    'MinCapacityGroup': ('LimitCapacity', 'ge'),
    'MinCapacity': ('LimitCapacity', 'ge'),
    'MinAnnualCapacityFactor': ('LimitAnnualCapacityFactor', 'ge'),
    'MinActivityShare': ('LimitActivityShare', 'ge'),
    'MinActivityGroup': ('LimitActivity', 'ge'),
    'MinActivity': ('LimitActivity', 'ge'),
    'MaxNewCapacityShare': ('LimitNewCapacityShare', 'le'),
    'MaxNewCapacityGroupShare': ('LimitNewCapacityShare', 'le'),
    'MaxNewCapacityGroup': ('LimitNewCapacity', 'le'),
    'MaxNewCapacity': ('LimitNewCapacity', 'le'),
    'MaxCapacityShare': ('LimitCapacityShare', 'le'),
    'MaxCapacityGroup': ('LimitCapacity', 'le'),
    'MaxCapacity': ('LimitCapacity', 'le'),
    'MaxAnnualCapacityFactor': ('LimitAnnualCapacityFactor', 'le'),
    'MaxActivityShare': ('LimitActivityShare', 'le'),
    'MaxActivityGroup': ('LimitActivity', 'le'),
    'MaxActivity': ('LimitActivity', 'le'),
    'MaxResource': ('LimitResource', 'le'),
}

no_transfer = {
    'MinSeasonalActivity': 'LimitSeasonalCapacityFactor',
    'MaxSeasonalActivity': 'LimitSeasonalCapacityFactor',
    'StorageInit': 'LimitStorageLevelFraction',
}


all_good = True
for old_name, new_name in direct_transfer_tables:
    good = column_check(old_name, new_name)
    all_good = all_good and good
for old_name, new_name in period_added_tables:
    good = column_check(old_name, new_name)
    all_good = all_good and good
if not all_good: sys.exit(-1)


# Collapse Max/Min constraint tables
print('\n --- Collapsing Max/Min tables and adding operators ---')
for old_name, (new_name, operator) in operator_added_tables.items():

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
    data = [(*row[0:op_index], operator, *row[op_index:len(new_cols)-1]) for row in data]

    # construct the query with correct number of placeholders
    num_placeholders = len(data[0])
    placeholders = ','.join(['?' for _ in range(num_placeholders)])
    query = f'INSERT OR REPLACE INTO {new_name} VALUES ({placeholders})'
    con_new.executemany(query, data)
    print(f'Transfered {len(data)} rows from {old_name} to {new_name}')

# It wasn't active anyway... can't be bothered
# StorageInit -> LimitStorageLevelFraction

# execute the direct transfers
print('\n --- Executing direct transfers ---')
for old_name, new_name in direct_transfer_tables:
    if old_name == '':
        old_name = new_name

    try:
        con_old.execute(f'SELECT * FROM {old_name}').fetchone()
    except sqlite3.OperationalError:
        print('TABLE NOT FOUND: ' + old_name)
        continue

    new_columns = [c[1] for c in con_new.execute(f'PRAGMA table_info({new_name});').fetchall()]
    data = con_old.execute(f'SELECT {str(new_columns)[1:-1].replace("'","")} FROM {old_name}').fetchall()

    if not data:
        print('No data for: ' + old_name)
        continue

    # construct the query with correct number of placeholders
    num_placeholders = len(data[0])
    placeholders = ','.join(['?' for _ in range(num_placeholders)])
    query = f'INSERT OR REPLACE INTO {new_name} VALUES ({placeholders})'
    con_new.executemany(query, data)
    print(f'Transfered {len(data)} rows from {old_name} to {new_name}')

# get lifetimes. Major headache but needs to be done
data = cur.execute('SELECT region, tech, lifetime FROM LifetimeTech').fetchall()
lifetime_tech = dict()
for rtl in data: lifetime_tech[rtl[0:2]] = rtl[2]
data = cur.execute('SELECT region, tech, vintage, lifetime FROM LifetimeProcess').fetchall()
lifetime_process = dict()
for rtvl in data: lifetime_process[rtvl[0:3]] = rtvl[3]

# add period indexing to seasonal tables
print('\n --- Adding period index to some tables ---')
time_future = cur.execute('SELECT period FROM TimePeriod WHERE flag == "f"').fetchall()
time_optimize = [p[0] for p in time_future[0:-1]]
for old_name, new_name in period_added_tables:
    if old_name == '':
        old_name = new_name

    try:
        con_old.execute(f'SELECT * FROM {old_name}').fetchone()
    except sqlite3.OperationalError:
        print('TABLE NOT FOUND: ' + old_name)
        continue
    
    columns = [c[1] for c in con_new.execute(f'PRAGMA table_info({new_name});').fetchall() if c[1] != 'period']
    data = con_old.execute(f'SELECT {str(columns)[1:-1].replace("'","")} FROM {old_name}').fetchall()

    if not data:
        print('No data for: ' + old_name)
        continue
    
    if 'vintage' in columns:
        r = columns.index('region')
        t = columns.index('tech')
        v = columns.index('vintage')

    data_new = []
    for p in time_optimize:
        for row in data:
            # Remove infeasible rows
            if 'vintage' in columns:
                if row[v] > p: continue # v <= p
                if (row[r], row[t], row[v]) in lifetime_process: life = lifetime_process[row[r], row[t], row[v]]
                elif (row[r], row[t]) in lifetime_tech: life = lifetime_tech[row[r], row[t]]
                else: life = 40 # TODO replace by calling default lifetime from TemoaModel
                if row[v] + life <= p: continue # v+l > p

            if old_name[0:5] == 'TimeS': # horrible but covers TimeSeason and TimeSegmentFraction
                data_new.append((p, *row))
            else:
                data_new.append((row[0], p, *row[1::]))

    # construct the query with correct number of placeholders
    num_placeholders = len(data_new[0])
    placeholders = ','.join(['?' for _ in range(num_placeholders)])
    query = f'INSERT OR REPLACE INTO {new_name} VALUES ({placeholders})'
    con_new.executemany(query, data_new)
    print(f'Transfered {len(data)} rows from {old_name} to {new_name}')


# LoanLifetimeTech -> LoanLifetimeProcess
try:
    data = con_old.execute('SELECT region, tech, lifetime, notes FROM LoanLifetimeTech').fetchall()
except sqlite3.OperationalError:
    print('TABLE NOT FOUND: LoanLifetimeTech')

if not data:
    print('No data for: LoanLifetimeTech')
else:
    new_data = []
    for row in data:
        vints = [v[0] for v in con_old.execute(f'SELECT vintage FROM Efficiency WHERE region=="{row[0]}" AND tech="{row[1]}"').fetchall()]
        for v in vints:
            new_data.append((row[0], row[1], v, row[2], row[3]))
    query = f'INSERT OR REPLACE INTO LoanLifetimeProcess VALUES (?,?,?,?,?)'
    con_new.executemany(query, new_data)
    print(f'Transfered {len(new_data)} rows from LifetimeLoanTech to LifetimeLoanProcess')


# Warn about incompatible changes
print('\n --- The following transfers were impossible due to incompatible changes. Transfer manually. ---')
for old_name, new_name in no_transfer.items():
    print(f'{old_name} to {new_name}')
    

# state_sequencing parameter
print('\n --- Updating MetaData ---')
cur.execute(
    """REPLACE INTO
    MetaData(element, value, notes)
    VALUES('state_sequencing', 0, '0 = loop periods, 1 = loop seasons')"""
)
print("Added state_sequencing parameter")
# new database version
cur.execute("UPDATE MetaData SET value = 1 WHERE element == 'DB_MINOR'")
print("Updated database version to 3.1")


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