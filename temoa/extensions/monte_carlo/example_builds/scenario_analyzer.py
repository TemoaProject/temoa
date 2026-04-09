"""
Simple analyzer--example only
"""
from importlib import resources
from math import sqrt
from pathlib import Path
from sqlite3 import Connection

from matplotlib import pyplot as plt

scenario_name = 'Purple Onion'  # must match config file
# To run this example, ensure tutorial_database.sqlite is in your current directory.
# You can generate it using: temoa tutorial
# IMPORTANT: You must also run the model to populate results before analyzing:
#   temoa run tutorial_config.toml
db_resource = 'tutorial_database.sqlite'

if not Path(db_resource).exists():
    raise FileNotFoundError(
        f"Database file '{db_resource}' not found. "
        "Please run 'temoa tutorial' to create the base files."
    )

with Connection(db_resource) as conn:
    cur = conn.cursor()
    # Check if results exist before attempting to plot
    obj_values = cur.execute(
        "SELECT total_system_cost FROM output_objective WHERE scenario LIKE ?",
        (f"{scenario_name}-%",)
    ).fetchall()

    if len(obj_values) == 0:
        raise RuntimeError(
            f"No results found for scenario '{scenario_name}-*' in '{db_resource}'. "
            "Please run 'temoa run tutorial_config.toml' or run the tutorial model "
            "to populate output_objective with results first."
        )

    obj_values_tuple = tuple(t[0] for t in obj_values)

plt.hist(obj_values_tuple, bins=int(sqrt(len(obj_values_tuple))))
plt.show()
