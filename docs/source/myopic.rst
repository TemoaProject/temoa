
.. _myopic:

Myopic Optimization
===================

Myopic (or sequential) optimization in Temoa provides a way to solve the model in a series of smaller, sequential time windows. This is often used to simulate decision-making with limited foresight, where the model only "sees" a limited number of future time periods at any given step.

Overall Framework
-----------------

The Myopic extension in Temoa is designed to:

* Solve the model for a sequence of overlapping or non-overlapping time windows.
* Limit the foresight of the model to a user-specified number of future periods.
* Fix the capacity investment decisions from previous windows as "initial capacity" for subsequent windows.
* Automatically manage the ``myopic_efficiency`` table to filter active technologies based on their remaining lifetime and previous investment decisions.

Configuration
-------------

To enable Myopic mode, set the ``scenario_mode`` to ``"myopic"`` in your configuration TOML file and provide the required settings under a ``[myopic]`` section:

.. code-block:: toml

   scenario_mode = "myopic"

   [myopic]
   view_depth = 2
   step_size = 1
   evolving = false
   evolution_script = "temoa/extensions/myopic/evolution_updater.py"

Settings
~~~~~~~~

* **view_depth**: The number of future time periods visible to the model in each iteration. For example, a ``view_depth`` of 2 means the model will optimize over two periods at a time.
* **step_size**: The number of periods to advance the "base year" in each subsequent iteration. A ``step_size`` of 1 means the base year will move forward by one time period at a time.
* **evolving**: A boolean flag (``true`` or ``false``) that selects between evolving and non-evolving myopic mode. Defaults to ``false``. See :ref:`myopic-modes` below.
* **evolution_script**: Path to a Python script containing an ``iterate()`` function that is called between iterations in evolving mode. Ignored when ``evolving = false``.

.. important::
   Myopic mode requires that the ``input_database`` and ``output_database`` in your configuration point to the same file. This is because the sequencer needs to write intermediate results (like the ``myopic_efficiency`` table and capacity decisions) back to the database to inform subsequent windows.

.. _myopic-modes:

Evolving vs. Non-Evolving Mode
------------------------------

Temoa supports two myopic sub-modes that control how iterations are generated and whether the
database can be modified between solves.

Non-Evolving Mode (default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When ``evolving = false``, the sequencer eliminates **redundant iterations** near the end of the
planning horizon. If multiple consecutive iterations would all see the same final period, only
the first such iteration is kept. This avoids re-solving windows that cannot produce new information.

For example, consider a model with future periods ``[2025, 2030, 2035, 2040, 2045]``,
``view_depth = 3``, and ``step_size = 1``:

* Without pruning, the base years would be ``[2025, 2030, 2035, 2040]``.
* The iterations starting at 2035 and 2040 both see period 2045 as the last demand year, so only the first is kept.
* **Result**: 3 iterations instead of 4.

Non-evolving mode is appropriate when the model structure (technologies, constraints, costs, etc.) does
not change between iterations and you want to minimize computation.

Evolving Mode
~~~~~~~~~~~~~

When ``evolving = true``, the sequencer keeps **all** calculated iterations, stepping forward by exactly
``step_size`` until the planning horizon is exhausted. Between each iteration, the ``evolution_script``
is called, giving the modeler an opportunity to modify the database before the next window is solved.

Using the same example (periods ``[2025, 2030, 2035, 2040, 2045]``, ``view_depth = 3``, ``step_size = 1``):

* Base years are ``[2025, 2030, 2035, 2040]``.
* **All 4 iterations** are kept, because the evolution script may change data between them.

This mode is designed for scenarios where model parameters—such as technology costs, demand levels, or
policy constraints—need to evolve over time based on previous results or external logic.

.. note::
   In evolving mode, the view depth may shorten near the end of the planning horizon so that the window
   does not extend beyond the available periods. All iterations are still performed.

Writing an Evolution Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The evolution script must define an ``iterate()`` function with the following signature:

.. code-block:: python

   import sqlite3
   from temoa.extensions.myopic.myopic_index import MyopicIndex

   def iterate(
       idx: MyopicIndex | None = None,
       prev_base_year: int | None = None,
       last_instance_status: str | None = None,
       db_con: sqlite3.Connection | None = None,
   ) -> None:
       """Called between myopic iterations (evolving mode only)."""
       # Use db_con to read/write the database as needed.
       pass

Parameters:

* **idx**: The ``MyopicIndex`` for the current iteration, containing the base year, step year, last demand year, and last year.
* **prev_base_year**: The base year of the previous iteration.
* **last_instance_status**: ``'optimal'`` if the previous solve succeeded, or ``'roll_back'`` if it failed and triggered a rollback.
* **db_con**: An open SQLite connection to the myopic database, which can be used to read results from the prior iteration and modify data for the next one.

The function is called *after* results from the current iteration have been written to the database and *before*
the myopic efficiency table is updated for the next iteration. A template is provided at
``temoa/extensions/myopic/evolution_updater.py``.

How it Works
------------

When running in Myopic mode, Temoa performs the following steps:

1. **Initialization**: It identifies all future time periods and sets up a queue of "optimization windows" based on the ``view_depth`` and ``step_size``.
2. **Initial Setup**: It creates the ``myopic_efficiency`` table and pre-loads it with any existing capacity from the input database.
3. **Sequential Solve**: For each window in the queue:
   a. **Update Efficiency Table**: The ``myopic_efficiency`` table is updated to include only technologies that are still within their lifetime or were built in previous windows. Any "planned" technologies not built in the previous window's look-ahead are removed to prevent "ghost" capacity.
   b. **Data Loading**: Data is loaded specifically for the current window's time range, using the ``myopic_efficiency`` table as a filter.
   c. **Model Solve**: A standard Temoa model instance is built and solved for the current window.
   d. **Result Persistence**: Investment decisions (built and retired capacity) are saved back to the database. These decisions are treated as fixed constraints in all future windows.
4. **Final Reporting**: Once all windows are solved, a total system cost is calculated as the sum of discounted costs across all periods.

Myopic Efficiency Table
-----------------------

The ``myopic_efficiency`` table is a key internal component of the myopic sequencer. It acts as a dynamic version of the standard ``efficiency`` table, filtered for each optimization window.

* It is "actively maintained" during the run.
* Items not built in a previous time window are removed.
* Items that reach the end of their technical lifetime are retired and removed from the table.
* The table includes a computed ``lifetime`` field used internally to screen active technologies.

Backtracking and Roll-back
--------------------------

If the solver fails to find an optimal solution for a given window (e.g., due to infeasibility caused by previous decisions), the Myopic sequencer has a built-in roll-back mechanism. It will attempt to back up to the previous window and re-solve with an expanded ``view_depth`` to find a feasible path forward. If it cannot back up further, the run will abort with an error.

Notes and Caveats
-----------------

Performance and Discounting
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Reduced Compute**: Myopic mode dramatically reduces compute requirements compared to perfect foresight by using a "divide and conquer" approach, solving several smaller problems instead of one large global optimization.
* **Discounting**: All costs are discounted to the first optimization period in the database (period ``p0`` of the first myopic window).

Modeling Considerations
~~~~~~~~~~~~~~~~~~~~~~~

* **Investment Amortization**: Investment costs in Temoa are amortized over the useful life of a built technology. This harmonizes how the model perceives costs and benefits within the ``view_depth``: since the model only sees the benefits of a technology for the portion of its life that falls within the current window, the costs are similarly distributed. Consequently, discounted investment costs reported in summary logs may be significantly higher than those reported in the ``output_cost`` table.
* **Limited Foresight**: Myopic mode cannot see beyond the specified ``view_depth``, including constraints. If a constraint only becomes active later in the planning horizon, the model may make sub-optimal decisions in early time windows. This can lead to unexpected rollbacks when those constraints finally enter the visibility window, which can complicate the interpretation of the results. Modeler caution is advised when setting the ``view_depth`` relative to known future constraints.
