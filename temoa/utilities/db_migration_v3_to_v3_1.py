"""
Transition a v3.0 database to a v3.1 database.
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd

from temoa.core.model import TemoaModel

# Just to get the default lifetime...
this_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(this_dir, '../..'))
sys.path.append(root_dir)


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
with open(schema_file) as src:
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

    missing = [c for c in new_columns if c not in old_columns and c not in ('period', 'notes')]
    if len(missing) > 0:
        msg = (
            f'Columns of {new_name} in the new database missing from {old_name} in old database. '
            'Try adding or renaming the column in the old database:'
            f'\n{missing}\n'
        )
        print(msg)
        return False
    return True


# table mapping for DIRECT transfers
# fmt: off
direct_transfer_tables = [
    ("",                      "CapacityCredit"),
    ("",                      "CapacityToActivity"),
    ("",                      "Commodity"),
    ("",                      "CommodityType"),
    ("",                      "CostEmission"),
    ("",                      "CostFixed"),
    ("",                      "CostInvest"),
    ("",                      "CostVariable"),
    ("",                      "Demand"),
    ("",                      "Efficiency"),
    ("",                      "EmissionActivity"),
    ("",                      "ExistingCapacity"),
    ("",                      "LifetimeProcess"),
    ("",                      "LifetimeTech"),
    ("",                      "LinkedTech"),
    ("",                      "LoanRate"),
    ("",                      "MetaData"),
    ("",                      "MetaDataReal"),
    ("",                      "PlanningReserveMargin"),
    ("RampDown",              "RampDownHourly"),
    ("RampUp",                "RampUpHourly"),
    ("",                      "Region"),
    ("",                      "RPSRequirement"),
    ("",                      "SectorLabel"),
    ("",                      "StorageDuration"),
    ("",                      "TechGroup"),
    ("",                      "TechGroupMember"),
    ("",                      "Technology"),
    ("",                      "TechnologyType"),
    ("",                      "TimeOfDay"),
    ("",                      "TimePeriod"),
    ("",                      "TimePeriodType"),
]

period_added_tables = [
    ("",                      "CapacityFactorProcess"),
    ("",                      "CapacityFactorTech"),
    ("",                      "DemandSpecificDistribution"),
    ("",                      "TimeSeason"),
    ("",                      "TimeSegmentFraction"),
]

operator_added_tables = {
    "EmissionLimit": ("LimitEmission", "le"),
    "TechOutputSplit": ("LimitTechOutputSplit", "ge"),
    "TechInputSplitAnnual": ("LimitTechInputSplitAnnual", "ge"),
    "TechInputSplitAverage": ("LimitTechInputSplitAnnual", "ge"),
    "TechInputSplit": ("LimitTechInputSplit", "ge"),
    "MinNewCapacityShare": ("LimitNewCapacityShare", "ge"),
    "MinNewCapacityGroupShare": ("LimitNewCapacityShare", "ge"),
    "MinNewCapacityGroup": ("LimitNewCapacity", "ge"),
    "MinNewCapacity": ("LimitNewCapacity", "ge"),
    "MinCapacityShare": ("LimitCapacityShare", "ge"),
    "MinCapacityGroup": ("LimitCapacity", "ge"),
    "MinCapacity": ("LimitCapacity", "ge"),
    "MinAnnualCapacityFactor": ("LimitAnnualCapacityFactor", "ge"),
    "MinActivityShare": ("LimitActivityShare", "ge"),
    "MinActivityGroup": ("LimitActivity", "ge"),
    "MinActivity": ("LimitActivity", "ge"),
    "MaxNewCapacityShare": ("LimitNewCapacityShare", "le"),
    "MaxNewCapacityGroupShare": ("LimitNewCapacityShare", "le"),
    "MaxNewCapacityGroup": ("LimitNewCapacity", "le"),
    "MaxNewCapacity": ("LimitNewCapacity", "le"),
    "MaxCapacityShare": ("LimitCapacityShare", "le"),
    "MaxCapacityGroup": ("LimitCapacity", "le"),
    "MaxCapacity": ("LimitCapacity", "le"),
    "MaxAnnualCapacityFactor": ("LimitAnnualCapacityFactor", "le"),
    "MaxActivityShare": ("LimitActivityShare", "le"),
    "MaxActivityGroup": ("LimitActivity", "le"),
    "MaxActivity": ("LimitActivity", "le"),
    "MaxResource": ("LimitResource", "le"),
}

no_transfer = {
    "MinSeasonalActivity": "LimitSeasonalCapacityFactor",
    "MaxSeasonalActivity": "LimitSeasonalCapacityFactor",
    "StorageInit": "LimitStorageLevelFraction",
}


all_good = True
for old_name, new_name in direct_transfer_tables:
    all_good = all_good and column_check(old_name, new_name)
for old_name, new_name in period_added_tables:
    all_good = all_good and column_check(old_name, new_name)
if not all_good:
    sys.exit(1)


# Collapse Max/Min constraint tables
print("\n --- Collapsing Max/Min tables and adding operators ---")
for old_name, (new_name, operator) in operator_added_tables.items():

    try:
        data = con_old.execute(f"SELECT * FROM {old_name}").fetchall()
    except sqlite3.OperationalError:
        print("TABLE NOT FOUND: " + old_name)
        continue

    if not data:
        print("No data for: " + old_name)
        continue

    new_cols: list[str] = [
        c[1] for c in con_new.execute(f"PRAGMA table_info({new_name});").fetchall()
    ]
    op_index = new_cols.index("operator")
    data = [(*row[0:op_index], operator, *row[op_index:len(new_cols)-1]) for row in data]

    # construct the query with correct number of placeholders
    num_placeholders = len(data[0])
    placeholders = ",".join(["?" for _ in range(num_placeholders)])
    query = f"INSERT OR REPLACE INTO {new_name} VALUES ({placeholders})"
    con_new.executemany(query, data)
    print(f"Transfered {len(data)} rows from {old_name} to {new_name}")

# It wasn't active anyway... can't be bothered
# StorageInit -> LimitStorageLevelFraction

# execute the direct transfers
print("\n --- Executing direct transfers ---")
for old_name, new_name in direct_transfer_tables:
    if old_name == "":
        old_name = new_name

    try:
        con_old.execute(f"SELECT * FROM {old_name}").fetchone()
    except sqlite3.OperationalError:
        print("TABLE NOT FOUND: " + old_name)
        continue

    old_columns = [c[1] for c in con_old.execute(f"PRAGMA table_info({old_name});").fetchall()]
    new_columns = [c[1] for c in con_new.execute(f"PRAGMA table_info({new_name});").fetchall()]
    cols = [c for c in new_columns if c in old_columns]
    data = con_old.execute(f'SELECT {str(cols)[1:-1].replace("'","")} FROM {old_name}').fetchall()

    if not data:
        print("No data for: " + old_name)
        continue

    # construct the query with correct number of placeholders
    num_placeholders = len(data[0])
    placeholders = ",".join(["?" for _ in range(num_placeholders)])
    query = (
        "INSERT OR REPLACE INTO "
        f"{new_name}{tuple(c for c in cols) if len(cols)>1 else f'({cols[0]})'} "
        f"VALUES ({placeholders})"
    )
    con_new.executemany(query, data)
    print(f"Transfered {len(data)} rows from {old_name} to {new_name}")

time_all = [
    p[0] for p in cur.execute("SELECT period FROM TimePeriod").fetchall()
]
time_all = sorted(time_all)[0:-1] # Exclude horizon end

# get lifetimes. Major headache but needs to be done
lifetime_process = {}
data = cur.execute("SELECT region, tech, vintage FROM Efficiency").fetchall()
for rtv in data:
    lifetime_process[rtv] = TemoaModel.default_lifetime_tech
data = cur.execute("SELECT region, tech, lifetime FROM LifetimeTech").fetchall()
for rtl in data:
    for v in time_all:
        lifetime_process[*rtl[0:2], v] = rtl[2]
data = cur.execute("SELECT region, tech, vintage, lifetime FROM LifetimeProcess").fetchall()
for rtvl in data:
    lifetime_process[rtvl[0:3]] = rtvl[3]

# Planning periods to add to period indices
time_optimize = [
    p[0] for p in cur.execute('SELECT period FROM TimePeriod WHERE flag == "f"').fetchall()
]
time_optimize = sorted(time_optimize)[0:-1] # Exclude horizon end

# add period indexing to seasonal tables
print("\n --- Adding period index to some tables ---")
for old_name, new_name in period_added_tables:
    if old_name == "":
        old_name = new_name

    try:
        con_old.execute(f"SELECT * FROM {old_name}").fetchone()
    except sqlite3.OperationalError:
        print("TABLE NOT FOUND: " + old_name)
        continue

    old_columns = [c[1] for c in con_old.execute(f"PRAGMA table_info({old_name});").fetchall()]
    new_columns = [c[1] for c in con_new.execute(f"PRAGMA table_info({new_name});").fetchall()]
    cols = [c for c in new_columns if c in old_columns]
    data = pd.read_sql_query(f'SELECT {str(cols)[1:-1].replace("'","")} FROM {old_name}', con_old)

    if len(data) == 0:
        print("No data for: " + old_name)
        continue

    # This insanity collects the viable periods for each table
    if "vintage" in cols:
        data["periods"] = [
            (
                p for p in time_optimize
                if v <= p < v+lifetime_process[r, t, v]
            )
            for r, t, v in data[["region","tech","vintage"]]
        ]
    elif "tech" in cols:
        periods = {}
        for r, t in data[["region","tech"]].drop_duplicates().values:
            periods[r, t] = [
                p for p in time_optimize
                if any(
                    v <= p < v+lifetime_process[r, t, v]
                    for v in [
                        t[0] for t in con_old.execute(
                            f'SELECT vintage FROM Efficiency WHERE region == "{r}" AND '
                            f'tech == "{t}"'
                        ).fetchall()
                    ]
                )
            ]
        data["periods"] = [
            periods[r, t]
            for (r, t) in data[["region","tech"]].values
        ]
    else:
        data["periods"] = [time_optimize for i in data.index]

    data_new = []
    for p in time_optimize:
        for _idx, row in data.iterrows():
            if p not in row["periods"]:
                continue
            if old_name[0:5] == "TimeS": # horrible but covers TimeSeason and TimeSegmentFraction
                data_new.append((p, *row.iloc[0:-1]))
            else:
                data_new.append((row.iloc[0], p, *row.iloc[1:-1]))

    if old_name[0:5] == "TimeS": # horrible but covers TimeSeason and TimeSegmentFraction
        cols = ["period",*cols]
    else:
        cols = [cols[0],"period",*cols[1::]]

    # construct the query with correct number of placeholders
    num_placeholders = len(data_new[0])
    placeholders = ",".join(["?" for _ in range(num_placeholders)])
    query = (
        "INSERT OR REPLACE INTO "
        f"{new_name}{tuple(c for c in cols) if len(cols)>1 else f'({cols[0]})'} "
        f"VALUES ({placeholders})"
    )
    con_new.executemany(query, data_new)
    print(f"Transfered {len(data_new)} rows from {old_name} to {new_name}")


print("\n --- Making some final changes ---")
n_del = len(con_new.execute(
    "SELECT * FROM DemandSpecificDistribution "
    "WHERE (region, period, demand_name) "
    "NOT IN (SELECT region, period, commodity FROM Demand)"
).fetchall())
if n_del > 0:
    con_new.execute(
        "DELETE FROM DemandSpecificDistribution "
        "WHERE (region, period, demand_name) "
        "NOT IN (SELECT region, period, commodity FROM Demand)"
    )
    print(
        f"{n_del} extraneous rows removed from DemandSpecificDistribution after adding period index"
    )

# TimeSeason unique seasons to SeasonLabel
con_new.execute("INSERT OR REPLACE INTO SeasonLabel(season) SELECT DISTINCT season FROM TimeSeason")
print("Filled SeasonLabel")

# Removal of tech_resource
con_new.execute("UPDATE Technology SET flag='p' WHERE flag=='r';")
print("Converted all resource techs to production techs.")

# LoanLifetimeTech -> LoanLifetimeProcess
try:
    data = con_old.execute("SELECT region, tech, lifetime, notes FROM LoanLifetimeTech").fetchall()
except sqlite3.OperationalError:
    print("TABLE NOT FOUND: LoanLifetimeTech")

if not data:
    print("No data for: LoanLifetimeTech")
else:
    new_data = []
    for row in data:
        vints = [
            v[0]
            for v in con_old.execute(
                f'SELECT vintage FROM Efficiency WHERE region=="{row[0]}" AND tech="{row[1]}"'
            ).fetchall()
        ]
        for v in vints:
            new_data.append((row[0], row[1], v, row[2], row[3]))
    query = "INSERT OR REPLACE INTO LoanLifetimeProcess VALUES (?,?,?,?,?)"
    con_new.executemany(query, new_data)
    print(f"Transfered {len(new_data)} rows from LifetimeLoanTech to LifetimeLoanProcess")


# Warn about incompatible changes
print(
    "\n --- The following transfers were impossible due to incompatible changes. Transfer "
    "manually. ---"
)
for old_name, new_name in no_transfer.items():
    print(f"{old_name} to {new_name}")


print("\n --- Updating MetaData ---")
cur.execute("DELETE FROM MetaData WHERE element == 'myopic_base_year'")
print(
    "myopic_base_year removed from MetaData. This parameter is no longer used. " \
    "Costs will discount to the first future period."
)
cur.execute("UPDATE MetaData SET value = 1 WHERE element == 'DB_MINOR'")
print("Updated database version to 3.1")



print("\n --- Validating foreign keys ---")
con_new.commit()
con_new.execute("VACUUM;")
con_new.execute("PRAGMA FOREIGN_KEYS=1;")
try:
    data = con_new.execute("PRAGMA FOREIGN_KEY_CHECK;").fetchall()
    if not data:
        print("No Foreign Key Failures.  (Good news!)")
    else:
        print("\nFK check fails (MUST BE FIXED):")
        print("(Table, Row ID, Reference Table, (fkid) )")
        for row in data:
            print(row)
except sqlite3.OperationalError as e:
    print("Foreign Key Check FAILED on new DB.  Something may be wrong with schema.")
    print(e)

print("\nFinished! Check your database for any missing data."
      " If there was a mismatch of table names, something may have been lost.")

con_new.close()
con_old.close()
