"""

Transition a legacy database to V3 compliant.

Dev Note:  It turns out easiest to make a new db from schema and do a lot of direct copying
because contents are same with same sequence of columns, just renamed in most cases.  Other
new consolidated tables are built from old data and filled forward.
"""

import argparse
import sqlite3
import sys
from collections import defaultdict
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
    help='Path to schema file (default=data_files/temoa_schema_v3.sql)',
    required=False,
    dest='schema',
    default='data_files/temoa_schema_v3.sql',
)
options = parser.parse_args()
legacy_db: Path = Path(options.source_db)
schema_file = Path(options.schema)


new_db_name = legacy_db.stem + '_v3.sqlite'
new_db_path = Path(legacy_db.parent, new_db_name)

con_old = sqlite3.connect(legacy_db)
con_new = sqlite3.connect(new_db_path)
cur = con_new.cursor()

# bring in the new schema and execute
with open(schema_file) as src:
    sql_script = src.read()
con_new.executescript(sql_script)

# turn off FK verification while process executes
con_new.execute('PRAGMA foreign_keys = 0;')

# table mapping for DIRECT transfers
# fmt: off
direct_transfer_tables = [
    ("",                    "CapacityCredit"),
    ("",                    "CapacityFactorProcess"),
    ("",                    "CapacityFactorTech"),
    ("",                    "CapacityToActivity"),
    ("commodities",         "Commodity"),
    ("commodity_labels",    "CommodityType"),
    ("CostEmissions",       "CostEmission"),
    ("",                    "CostFixed"),
    ("",                    "CostInvest"),
    ("",                    "CostVariable"),
    ("",                    "Demand"),
    ("",                    "DemandSpecificDistribution"),
    ("",                    "Efficiency"),
    ("",                    "EmissionActivity"),
    ("",                    "EmissionLimit"),
    ("",                    "ExistingCapacity"),
    ("",                    "GrowthRateMax"),
    ("",                    "GrowthRateSeed"),
    ("",                    "LifetimeProcess"),
    ("",                    "LifetimeTech"),
    ("LinkedTechs",         "LinkedTech"),
    ("LifetimeLoanTech",    "LoanLifetimeTech"),
    ("DiscountRate",        "LoanRate"),
    ("",                    "MaxActivity"),
    ("",                    "MaxActivityShare"),
    ("",                    "MaxAnnualCapacityFactor"),
    ("",                    "MaxCapacity"),
    ("",                    "MaxCapacityShare"),
    ("",                    "MaxNewCapacity"),
    ("",                    "MaxNewCapacityGroup"),
    ("",                    "MaxNewCapacityShare"),
    ("",                    "MaxResource"),
    ("",                    "MinActivity"),
    ("",                    "MinActivityShare"),
    ("",                    "MinAnnualCapacityFactor"),
    ("",                    "MinCapacity"),
    ("",                    "MinCapacityShare"),
    ("",                    "MinNewCapacity"),
    ("",                    "MinNewCapacityGroup"),
    ("",                    "MinNewCapacityShare"),
    ("",                    "PlanningReserveMargin"),
    ("",                    "RampDown"),
    ("",                    "RampUp"),
    ("regions",             "Region"),
    ("sector_labels",       "SectorLabel"),
    ("",                    "StorageDuration"),
    ("",                    "TechInputSplit"),
    ("",                    "TechInputSplitAverage"),
    ("",                    "TechOutputSplit"),
    ("technology_labels",   "TechnologyType"),
    ("time_period_labels",  "TimePeriodType"),
    ("SegFrac",             "TimeSegmentFraction"),
]

units_added_tables = [
    ("",                    "MaxActivityGroup"),
    ("",                    "MaxCapacityGroup"),
    ("",                    "MinCapacityGroup"),
    ("",                    "MinActivityGroup"),
]

sequence_added_tables = [
    ("time_season",         "TimeSeason"),
    ("time_periods",        "time_period"),
    ("time_of_day",         "TimeOfDay"),
]
# fmt: on

# execute the direct transfers
print('\n --- Executing direct transfers ---')
for name_pair in direct_transfer_tables:
    old_name, new_name = name_pair
    if old_name == '':
        old_name = new_name

    new_columns = [c[1] for c in con_new.execute(f'PRAGMA table_info({new_name});').fetchall()]
    old_columns = [c[1] for c in con_old.execute(f'PRAGMA table_info({old_name});').fetchall()]
    cols = str(old_columns[0 : len(new_columns)])[1:-1].replace("'", '')

    try:
        data = con_old.execute(f'SELECT {cols} FROM {old_name}').fetchall()
    except sqlite3.OperationalError:
        print('TABLE NOT FOUND: ' + old_name)
        data = []
        continue

    if not data:
        print('No data for: ' + old_name)
        continue

    # construct the query with correct number of placeholders
    num_placeholders = len(data[0])
    placeholders = ','.join(['?' for _ in range(num_placeholders)])
    query = f'INSERT OR REPLACE INTO {new_name} VALUES ({placeholders})'
    con_new.executemany(query, data)
    print(f'inserted {len(data)} rows into {new_name}')

# do the tables with units added
print('\n --- Adjusting tables that need "units" added ---')
for name_pair in units_added_tables:
    old_name, new_name = name_pair
    if old_name == '':
        old_name = new_name

    new_columns = [c[1] for c in con_new.execute(f'PRAGMA table_info({new_name});').fetchall()]
    old_columns = [c[1] for c in con_old.execute(f'PRAGMA table_info({old_name});').fetchall()]
    cols = str(old_columns[0 : len(new_columns)])[1:-1].replace("'", '')

    try:
        data = con_old.execute(f'SELECT {cols} FROM {old_name}').fetchall()
    except sqlite3.OperationalError:
        print('table not found: ' + old_name)
        data = []
        continue
    if not data:
        print('no data for: ' + old_name)
        continue
    # quick check for expected number of fields...
    if len(data[0]) != 5:
        print(
            f'\nWARNING:  unexpected number of fields in table: {old_name}.  Was expecting 5:  '
            'region, period, group, value, notes'
        )
        print(
            '\nIt is possible that the older table you have was not indexed by REGION, which might '
            'be common for old datasets.  If so, that cannot be moved automatically.  You will '
            'need to do it manually.'
        )
        print(f'\n  *** IGNORING TABLE:  {old_name} in transfer!! ***\n')
        continue
    query = f'INSERT OR REPLACE INTO {new_name} VALUES (?, ?, ?, ?, "", ?)'
    con_new.executemany(query, data)
    print(f'inserted {len(data)} rows into {new_name}')

# fix the tables with a sequence number added
print('\n --- Adjusting time tables to include sequence (order) ---')
for name_pair in sequence_added_tables:
    old_name, new_name = name_pair
    if old_name == '':
        old_name = new_name

    new_columns = [c[1] for c in con_new.execute(f'PRAGMA table_info({new_name});').fetchall()]
    old_columns = [c[1] for c in con_old.execute(f'PRAGMA table_info({old_name});').fetchall()]
    cols = str(old_columns[0 : len(new_columns) - 1])[1:-1].replace("'", '')

    try:
        data = con_old.execute(f'SELECT {cols} FROM {old_name}').fetchall()
    except sqlite3.OperationalError:
        print(f'mandatory table: {old_name} not found.  Operation Failed')
        sys.exit(-1)
    count = 1
    num_placeholders = len(new_columns) - 1
    for row in data:
        placeholders = ','.join(['?' for _ in range(num_placeholders)])
        query = f'INSERT INTO {new_name} VALUES ({count}, {placeholders})'
        con_new.execute(query, row)
        count += 1
    print(f'inserted {len(data)} rows into {new_name}')
con_new.commit()

# More complicated stuff.... fixing the groups
print(
    '\n --- comparing RPS groups to a common set to see if they can be combined into 1 '
    '(except global) ---'
)

groups: dict[str, set[str]] = defaultdict(set)

# let's ensure all the non-global entries are consistent (same techs in each region)
skip_rps = False
try:
    rps_entries = con_old.execute('SELECT * FROM tech_rps').fetchall()
except sqlite3.OperationalError:
    print('source does not appear to include RPS techs...skipping')
    skip_rps = True
if not skip_rps:
    for region, tech, _notes in rps_entries:
        groups[region].add(tech)

    common: set[str] = set()
    for group, group_entries in groups.items():
        if group != 'global':
            common |= group_entries

    techs_common = True
    for group, techs in groups.items():
        print(f'group: {group} mismatches: {common ^ techs}')
        if group != 'global':
            techs_common &= not common ^ techs
            if not techs_common:
                print(
                    'combining RPS techs failed.  Some regions are not same.  Must be done '
                    'manually.'
                )

    if techs_common:
        print('\n --- Adjusting tech_group names ---')

        # put the tables into TechGroup table listing...
        cur.execute(
            'INSERT OR REPLACE INTO TechGroup VALUES (:name, :notes)',
            {'name': 'RPS_global', 'notes': ''},
        )
        cur.execute(
            'INSERT OR REPLACE INTO TechGroup VALUES (:name, :notes)',
            {'name': 'RPS_common', 'notes': ''},
        )

        # put the members into members tables
        for member in common:
            cur.execute('INSERT INTO TechGroupMember VALUES (?, ?)', ('RPS_common', member))

        for member in groups.get('global', set()):
            cur.execute('INSERT INTO TechGroupMember VALUES (?, ?)', ('RPS_global', member))

        # move things into the RPSRequirement table
        count = 0
        for entry in con_old.execute('SELECT * FROM main.RenewablePortfolioStandard').fetchall():
            r, p, rps, notes = entry
            if r not in groups.keys():
                raise ValueError(f'unusual region : {r}')
            elif r == 'global':
                tech_group = 'RPS_global'
            else:
                tech_group = 'RPS_common'
            cur.execute(
                'INSERT INTO RPSRequirement VALUES (?, ?, ?, ?, ?)', (r, p, tech_group, rps, notes)
            )
            count += 1
        print(f'moved {count} items into RPSRequirement table')

# ------- TRANSITION THE OLD tech_groups ------------
print('\n --- Adjusting tables that used tech_groups ---')
skip_tech_groups = False
try:
    # pull the entries from tech_groups, smash names and move 'em
    for entry in con_old.execute('SELECT * FROM main.tech_groups').fetchall():
        region, group_name, tech, notes = entry
        new_name = f'({region})_{group_name}'
        cur.execute(
            'INSERT OR REPLACE INTO TechGroup VALUES (?, ?)', (new_name, 'converted from old db')
        )
        cur.execute('INSERT OR REPLACE INTO TechGroupMember VALUES (?, ?)', (new_name, tech))
except sqlite3.OperationalError:
    print('source does not appear to employ tech_groups...skipping.')
    skip_tech_groups = True
except ValueError as e:
    print('\nWARNING:  unusual schema variation discovered in tech_groups.  Error:  ' + str(e))
    print('\n *** SKIPPING TRANSITION OF tech_groups and associated weightings, etc. ***\n')
    skip_tech_groups = True
if not skip_tech_groups:
    # ------- FIX TABLES THAT USED TO USE tech_groups -----------
    # We'll do this by modifying the group names similar to above (smashing the region-name
    # together to match the newly renamed groups
    tables_using_groups = [
        'MaxActivityGroup',
        'MaxActivityShare',
        'MaxCapacityGroup',
        'MaxCapacityShare',
        'MaxNewCapacityGroup',
        'MaxNewCapacityShare',
        'MinActivityGroup',
        'MinActivityShare',
        'MinCapacityGroup',
        'MinCapacityShare',
        'MinNewCapacityGroup',
        'MinNewCapacityShare',
    ]
    for table in tables_using_groups:
        # get the region-group pairs
        try:
            pairs = cur.execute(f'SELECT DISTINCT region, group_name FROM {table}').fetchall()
        except sqlite3.OperationalError:
            print(f'table not found: {table}')
            pairs = []
            continue
        if len(pairs) == 0:
            print(f'No groups found for: {table}')
        else:
            print(f'modified {len(pairs)} groups for {table}')
        renames = {(pair[0], pair[1]): f'({pair[0]})_{pair[1]}' for pair in pairs}
        for (region, group_name), new_name in renames.items():
            cur.execute(
                f'UPDATE {table} SET group_name = ? WHERE region = ? and group_name = ?',
                (new_name, region, group_name),
            )

print('\n --- Moving technologies and filling table ---')

# check for unlim_cap column...
unlim_cap_present = True
try:
    con_old.execute('SELECT unlim_cap FROM technologies').fetchall()
except sqlite3.OperationalError:
    unlim_cap_present = False

if unlim_cap_present:
    read_qry = 'SELECT tech, flag, sector, tech_category, unlim_cap, tech_desc FROM technologies'
    write_qry = "INSERT INTO Technology VALUES (?, ?, ?, ?, '', ?, 0, 0, 0, 0, 0, 0, 0, ?)"
else:
    read_qry = 'SELECT tech, flag, sector, tech_category, tech_desc FROM technologies'
    write_qry = "INSERT INTO Technology VALUES (?, ?, ?, ?, '', 0, 0, 0, 0, 0, 0, 0, 0, ?)"

data = con_old.execute(read_qry).fetchall()
if unlim_cap_present:
    # need to convert null -> 0 for unlim_cap to match new schema that does not allow null
    new_data = []
    for row in data:
        new_row = list(row)
        if new_row[4] is None:
            new_row[4] = 0
        new_data.append(tuple(new_row))
    data = new_data

cur.executemany(write_qry, data)

# gather supporting sets
data = con_old.execute('SELECT tech from tech_annual').fetchall()
print(f'updating {len(data)} annual technologies')
for row in data:
    tech = row[0]
    cur.execute('UPDATE Technology SET annual = 1 WHERE tech = ?', (tech,))
data = con_old.execute('SELECT tech from tech_reserve').fetchall()
print(f'updating {len(data)} reserve technologies')
for row in data:
    tech = row[0]
    cur.execute('UPDATE Technology SET reserve = 1 WHERE tech = ?', (tech,))
data = con_old.execute('SELECT tech from tech_curtailment').fetchall()
print(f'updating {len(data)} curtailable technologies')
for row in data:
    tech = row[0]
    cur.execute('UPDATE Technology SET curtail = 1 WHERE tech = ?', (tech,))
try:
    data = con_old.execute('SELECT tech from tech_retirement').fetchall()
except sqlite3.OperationalError:
    data = []
print(f'updating {len(data)} retirement technologies')
for row in data:
    tech = row[0]
    cur.execute('UPDATE Technology SET retire = 1 WHERE tech = ?', (tech,))
data = con_old.execute('SELECT tech from tech_flex').fetchall()
print(f'updating {len(data)} flex technologies')
for row in data:
    tech = row[0]
    cur.execute('UPDATE Technology SET flex = 1 WHERE tech = ?', (tech,))
try:
    data = con_old.execute('SELECT tech from tech_variable').fetchall()
except sqlite3.OperationalError:
    data = []
print(f'updating {len(data)} variable technologies')
for row in data:
    tech = row[0]
    cur.execute('UPDATE Technology SET variable = 1 WHERE tech = ?', (tech,))
try:
    data = con_old.execute('SELECT tech from tech_exchange').fetchall()
except sqlite3.OperationalError:
    data = []
print(f'updating {len(data)} exchange technologies')
for row in data:
    tech = row[0]
    cur.execute('UPDATE Technology SET exchange = 1 WHERE tech = ?', (tech,))

print('\n --- Moving scalar data elements ---')
try:
    myopic_result = con_old.execute('SELECT * FROM MyopicBaseyear').fetchone()
except sqlite3.OperationalError:
    myopic_result = None
if myopic_result:
    mby = myopic_result[0]
    cur.execute("INSERT OR REPLACE INTO MetaData VALUES ('myopic_base_year', ? , '')", (mby,))
    print(f'transferred myopic base year: {mby}')
else:
    print('no myopic base year discovered')

try:
    discount_result = con_old.execute('SELECT * FROM GlobalDiscountRate').fetchone()
except sqlite3.OperationalError:
    discount_result = None
if discount_result:
    rate = discount_result[0]
    cur.execute(
        "INSERT OR REPLACE INTO MetaDataReal VALUES ('global_discount_rate', ?, '')", (rate,)
    )
    print(f'transferred global discount rate: {rate}')
else:
    print('no global discount rate discovered')


con_new.commit()
con_new.execute('VACUUM;')
con_new.execute('PRAGMA FOREIGN_KEYS=1;')
try:
    data = con_new.execute('PRAGMA FOREIGN_KEY_CHECK;').fetchall()
    print('FK check fails (MUST BE FIXED):')
    if not data:
        print('\tNo Foreign Key Failures.  (Good news!)')
    else:
        print('\t(Table, Row ID, Reference Table, (fkid) )')
        for row in data:
            print(f'\t{row}')
except sqlite3.OperationalError as e:
    print('Foreign Key Check FAILED on new DB.  Something may be wrong with schema.')
    print(e)

# move the GlobalDiscountRate
# move the myopic base year
con_new.close()
con_old.close()
