"""
A quick utility to clear all of the data in all of the output tables in a
Temoa V3 database
"""

import sqlite3
import sys
from pathlib import Path

basic_output_tables = [
    'output_built_capacity',
    'output_cost',
    'output_curtailment',
    'output_dual_variable',
    'output_emissionn',
    'output_flow_in',
    'output_flow_out',
    'output_net_capacity',
    'output_objective',
    'output_retired_capacity',
]
optional_output_tables = ['output_flow_out_summary', 'myopic_efficiency']

if len(sys.argv) != 2:
    print('this utility file expects a CLA for the path to the database to clear')
    sys.exit(-1)

target_db_str = sys.argv[1]

proceed = input('This will clear ALL output tables in ' + target_db_str + '? (y/n): ')
if proceed == 'y':
    target_db = Path(target_db_str)
    if not target_db.exists():
        print(f'path provided to database is invalid: {target_db}')
        sys.exit(-1)
    try:
        with sqlite3.connect(target_db) as conn:
            for table in basic_output_tables:
                conn.execute('DELETE FROM ' + table + ' WHERE 1')
            for table in optional_output_tables:
                try:
                    conn.execute('DELETE FROM ' + table + ' WHERE 1')
                except sqlite3.OperationalError:
                    pass
            conn.commit()
            print('All output tables cleared.')
    except sqlite3.OperationalError:
        print('problem with database connection')
else:
    print('exiting')
