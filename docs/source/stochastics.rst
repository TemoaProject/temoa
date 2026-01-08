
.. _stochastics:

Stochastic Programming
======================

The Stochastics extension in Temoa v4 provides support for stochastic programming using the `mpi-sppy <https://github.com/Pyomo/mpi-sppy>`_ library. This allows for decision-making under uncertainty by considering multiple scenarios simultaneously and finding an optimal "first-stage" decision that minimizes the expected cost over all scenarios.

Stochastic programming is particularly useful for modeling uncertainties in future costs, demands, or resource availability.

Dependencies
------------

The stochastics extension requires the ``mpi-sppy`` package. You can install it using ``uv``:

.. code-block:: bash

   uv add mpi-sppy

Or using ``pip``:

.. code-block:: bash

   pip install mpi-sppy

Configuration
-------------

To run Temoa in stochastic mode, you need to modify your main configuration TOML file and provide an additional stochastic configuration file.

Main Configuration TOML
~~~~~~~~~~~~~~~~~~~~~~~

Set the ``scenario_mode`` to ``"stochastic"`` and add a ``[stochastic]`` section:

.. code-block:: toml

   scenario_mode = "stochastic"

   # ... other standard options ...

   [stochastic]
   # Path to the stochastic configuration file, relative to this file
   stochastic_config = "stochastic_config.toml"

Stochastic Configuration TOML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The stochastic configuration file defines the scenarios, their probabilities, and the data perturbations associated with each scenario.

.. code-block:: toml

   # Define the scenarios
   [scenarios]
   # Each key is a scenario name, and the value is its probability
   # Probabilities must sum to 1.0
   low_cost = 0.5
   high_cost = 0.5

   # Define perturbations for a specific scenario
   [[perturbations]]
   scenario = "low_cost"
   table = "cost_variable"
   # Filter specifies which rows in the table to perturb
   filter = { tech = "IMPHCO1" }
   # Action can be "multiply", "add", or "set" (defaults to "set")
   action = "multiply"
   value = 0.5

   [[perturbations]]
   scenario = "high_cost"
   table = "cost_variable"
   filter = { tech = "IMPHCO1" }
   action = "multiply"
   value = 1.5

Perturbation Options
^^^^^^^^^^^^^^^^^^^^

Currently, the following fields are required for each perturbation:

* **scenario**: The name of the scenario to which this perturbation applies.
* **table**: The Temoa parameter (database table) to perturb (e.g., ``cost_variable``, ``demand``, ``capacity_factor_process``).
* **filter**: A dictionary of column-value pairs used to identify specific rows. Since the extension uses the dynamic manifest from ``HybridLoader``, any column belonging to the table's index can be used for filtering.
* **action**: The operation to perform. Supported values:
    * ``multiply``: Multiply the base value by ``value``.
    * ``add``: Add ``value`` to the base value.
    * ``set``: Replace the base value with ``value``.
* **value**: The numeric value used in the perturbation action.

How it Works
------------

When running in stochastic mode, Temoa:

1. Loads the base data from the input database.
2. Identifies the "first-stage" variables. In the current implementation, all decisions in the first time period are considered first-stage.
3. Orchestrates multiple scenario runs using the ``mpi-sppy`` Extensive Form (EF) solver.
4. For each scenario, the ``scenario_creator`` applies the specified perturbations to the base data and builds a Pyomo model instance.
5. The EF solver binds the first-stage variables across all scenarios (non-anticipativity constraints) and optimizes the total expected cost.
6. The terminal output reports the Stochastic Expected Value.

Limitations
-----------

* **Two-Stage Only**: While ``mpi-sppy`` supports multi-stage stochastic programming, the current Temoa integration is tailored for two-stage problems where the first time period constitutes the first stage.
* **Result Persistence**: Currently, only the expected objective value and summary logs are produced. Detailed per-scenario result persistence to the database is under development.
