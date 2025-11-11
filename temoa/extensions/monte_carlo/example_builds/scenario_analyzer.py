"""
Simple analyzer--example only
"""
from math import sqrt
from pathlib import Path
from sqlite3 import Connection

from importlib import resources
from matplotlib import pyplot as plt

scenario_name = 'Purple Onion'  # must match config file
db_resource = resources.files('data_files.example_dbs') / 'utopia.sqlite'
with resources.as_file(db_resource) as db_path, Connection(str(db_path)) as conn:
    cur = conn.cursor()
    obj_values = cur.execute(
        f"SELECT total_system_cost FROM output_objective WHERE scenario LIKE '{scenario_name}-%'"
    ).fetchall()
    obj_values = tuple(t[0] for t in obj_values)

plt.hist(obj_values, bins=int(sqrt(len(obj_values))))
plt.show()
