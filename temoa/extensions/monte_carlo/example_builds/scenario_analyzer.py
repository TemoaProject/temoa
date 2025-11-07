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
Created on:  11/11/24

Simple analyzer--example only

"""
from math import sqrt
from pathlib import Path
from sqlite3 import Connection

from matplotlib import pyplot as plt

from definitions import PROJECT_ROOT

scenario_name = 'Purple Onion'  # must match config file
db_path = Path(PROJECT_ROOT, 'data_files/example_dbs/utopia.sqlite')
with Connection(db_path) as conn:
    cur = conn.cursor()
    obj_values = cur.execute(
        f"SELECT total_system_cost FROM output_objective WHERE scenario LIKE '{scenario_name}-%'"
    ).fetchall()
    obj_values = tuple(t[0] for t in obj_values)

plt.hist(obj_values, bins=int(sqrt(len(obj_values))))
plt.show()
