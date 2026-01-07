Monte Carlo Uncertainty Quantification
========================================

Temoa provides a Monte Carlo simulation framework that allows users to perform
probabilistic analysis by executing multiple model runs with varying input parameters.
This feature is useful for characterizing the distribution of outcomes under
uncertainty or performing sensitivity analysis.

Overall Framework
-----------------

The Monte Carlo extension in Temoa is designed to:

* Execute an arbitrary number of structured runs.
* Provide a clean interface to specify parameter deviations for each run.
* Support multiple deviations (tweaks) per individual run.
* Record all parameter adjustments in the output database for verification.
* Utilize parallel processing to speed up the execution of multiple runs.

Configuration
-------------

To enable Monte Carlo mode, set the ``scenario_mode`` to ``"monte_carlo"`` in
your configuration TOML file and provide the path to the run settings file
under a ``[monte_carlo]`` section:

.. code-block:: toml

   scenario_mode = "monte_carlo"

   [monte_carlo]
   run_settings = "path/to/mc_settings.csv"
   solver_options = "mc_solver_options.toml"  # Optional

Settings
~~~~~~~~

* **run_settings**: Path to the CSV file containing the parameter deviations.
* **solver_options** (Optional): Path to a TOML file containing worker counts and solver-specific options. If not provided, Temoa uses the default options file in ``temoa/extensions/monte_carlo/MC_solver_options.toml``.

Input File Format
-----------------

The Monte Carlo settings are defined in a CSV file. The file must contain a header
and follow this structure:

.. code-block:: none

   run,param,index,mod,value,notes
   1,cost_invest,utopia|TXD|2010,a,-44.0,reduce invest cost to 1000
   2,demand,utopia|2010|RH,r,0.1,increase demand by 10%
   2,cost_fixed,utopia|TXD|2010|2010,s,15.0,set fixed cost to 15.0

Columns
~~~~~~~

* **run**: An integer representing the run index. Multiple lines with the same run index will be applied to the same model instance.
* **param**: The name of the Temoa parameter to adjust (e.g., ``cost_invest``, ``demand``).
* **index**: The index of the parameter, using the pipe (``|``) character as a separator.
* **mod**: The adjustment type (see below).
* **value**: The numeric value used for the adjustment.
* **notes**: A free-text field for user notes.

Adjustment Types
~~~~~~~~~~~~~~~~

The ``mod`` column supports three types of adjustments:

* **a (Absolute Change)**: Adds the ``value`` to the baseline parameter value.
  Formula: :math:`new\_value = old\_value + value`
* **r (Relative Change)**: Adjusts the baseline value by a percentage.
  Formula: :math:`new\_value = old\_value \times (1 + value)`
* **s (Substitution)**: Replaces the baseline value with the provided ``value``.
  Formula: :math:`new\_value = value`

Advanced Indexing
~~~~~~~~~~~~~~~~~

* **Wildcards**: You can use an asterisk (``*``) as a wildcard in any position of the ``index`` to apply the adjustment to all matching elements.
  Example: ``utopia|*|2010`` would match all regions for the given tech/commodity in 2010.
* **Multi-tokens**: You can specify multiple identifiers for a single index position by separating them with a forward slash (``/``). This will create a Cartesian product of all specified combinations.
  Example: ``utopia/usa|TXD|2010`` would apply the tweak to both ``utopia|TXD|2010`` and ``usa|TXD|2010``.

Parallel Execution
------------------

Monte Carlo runs are executed in parallel to maximize performance. The number of
worker processes and solver-specific options for these workers are controlled
by a configuration file.

By default, Temoa uses the ``MC_solver_options.toml`` file located in the
``temoa/extensions/monte_carlo/`` directory. However, you can provide your own
file by specifying the ``solver_options`` path in your configuration TOML.

.. tip::
   The default configuration uses 11 worker processes. If you provide a custom
   ``solver_options`` file, you can adjust the ``num_workers`` setting and add
   solver-specific parameters (e.g., threads, tolerances) for each solver.

Outputs
-------

The results of each Monte Carlo run are stored in the output database specified
in your configuration.

Model Scenarios
~~~~~~~~~~~~~~~

Each run is saved under a unique scenario name in the output tables, following
the format: ``<base_scenario>-<run_index>``. For example, if your base scenario
is ``utopia_mc``, the results for the first run will be labeled ``utopia_mc-1``.

Tweak Log Table
~~~~~~~~~~~~~~~

The specific adjustments made for each run are recorded in the ``output_mc_delta``
table. This table contains the following columns:

* **scenario**: The unique scenario name for the run.
* **run**: The run index.
* **param**: The parameter that was adjusted.
* **param_index**: The specific index that was tweaked.
* **old_val**: The original value from the baseline data.
* **new_val**: The new value after the adjustment was applied.
