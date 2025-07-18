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
Created on:  6/22/24

A quick utility to clear all of the data in all of the output tables in a
Temoa V3 database
"""

import sqlite3
import sys
from pathlib import Path

basic_output_tables = [
    'OutputBuiltCapacity',
    'OutputCost',
    'OutputCurtailment',
    'OutputDualVariable',
    'OutputEmission',
    'OutputFlowIn',
    'OutputFlowOut',
    'OutputNetCapacity',
    'OutputObjective',
    'OutputRetiredCapacity',
]
optional_output_tables = ['OutputFlowOutSummary', 'MyopicEfficiency']

if len(sys.argv) != 2:
    print('this utility file expects a CLA for the path to the database to clear')
    sys.exit(-1)

target_db = sys.argv[1]

proceed = input('This will clear ALL output tables in ' + target_db + '? (y/n): ')
if proceed == 'y':
    target_db = Path(target_db)
    if not Path.exists(target_db):
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
