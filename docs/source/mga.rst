.. _mga:

Modeling to Generate Alternatives (MGA)
=======================================

Temoa provides two extensions for Modeling to Generate Alternatives (MGA), an
algorithm to explore the near-optimal solution space: hull expansion and
single-vector MGA. Both are described in more detail below.

Hull Expansion
--------------

Hull expansion creates the convex hull containing all near-optimal solutions
bound by the extreme points along a particular solution axis and then samples
the continuum of solutions. The size of the convex hull is determined by the
degree of cost relaxation (``cost_epsilon``). The method is described in
`Pedersen et al. (2021) <https://www.sciencedirect.com/science/article/pii/S0360544221015425>`_

Configuration
~~~~~~~~~~~~~

To enable hull expansion, set the ``scenario_mode`` to ``"mga"`` in your
configuration TOML file and provide an ``[MGA]`` section:

.. code-block:: toml

   scenario_mode = "mga"

   [MGA]
   cost_epsilon = 0.05        # Relax cost by 5%
   iteration_limit = 20       # Number of alternative solutions to generate
   time_limit_hrs = 12        # Stop after 12 hours
   axis = "TECH_CATEGORY_ACTIVITY"
   weighting = "HULL_EXPANSION"

Options
^^^^^^^

* **cost_epsilon**: The fraction by which the optimal cost is allowed to increase
  (e.g., ``0.05`` for 5%).
* **iteration_limit**: The number of alternative solutions to generate, in addition to
  the baseline solve. The run produces exactly this many alternatives, unless it is
  stopped earlier by ``time_limit_hrs``.
* **time_limit_hrs**: The maximum wall-clock time for the entire MGA run.
* **axis**: The dimension along which to optimize. Supported values:
    * ``TECH_CAPACITY``
    * ``TECH_CATEGORY_CAPACITY``
    * ``TECH_CATEGORY_ACTIVITY`` (Default)
    * ``EMISSION_ACTIVITY``
* **weighting**: The algorithm used to select the next optimization vector.
  Currently, only ``HULL_EXPANSION`` is supported.
* **hull_max_dimension**: The largest number of axes (technology categories) for a single
  convex hull (default ``8``). With more categories, the axes are split at random into groups
  of at most this many, each with its own hull, and the groups are drawn again whenever the
  search directions run low. The progress report and ``hull_performance.png`` then show the
  geometric mean of the axis ranges, relative to the first hull, instead of the hull volume.

Single-Vector MGA (SVMGA)
-------------------------

Single-Vector MGA is a simplified, two-stage process. First, it solves the base
model to find the minimum cost. Second, it adds a cost relaxation constraint and
creates a new objective function that minimizes user-specified quantities, such
as technology-specific installed capacity or total carbon dioxide emissions.


Configuration
~~~~~~~~~~~~~

To enable SVMGA, set the ``scenario_mode`` to ``"svmga"`` and provide an
``[SVMGA]`` section:

.. code-block:: toml

   scenario_mode = "svmga"

   [SVMGA]
   cost_epsilon = 0.05
   capacity_labels = ["solar_pv", "wind_onshore"]
   # emissions_labels = ["CO2"]
   # activity_labels = ["coal_power"]

Options
^^^^^^^

* **cost_epsilon**: Same as in hull expansion.
* **capacity_labels**: A list of technology names whose total capacity should be
  maximized in the second stage. Matching is **exact and case-sensitive** against
  the identifiers in the ``tech_all`` set. Example: ``["solar_pv", "wind_onshore"]``.
* **emissions_labels**: A list of emission commodities whose total emissions
  should be minimized. Matching is **exact and case-sensitive** against
  identifiers in the ``commodity_emissions`` set. Example: ``["CO2"]``.
* **activity_labels**: A list of technology names whose total activity
  (energy flow out) should be maximized. Matching is **exact and case-sensitive**.
  Example: ``["coal_power"]``.

Note: SVMGA will construct an unweighted sum of all variables matching these
labels as the new objective function. Be careful not to mix different units. In
addition, note that the MGA objective function is set to minimize regardless of
the label choice.

Parallel Execution and Solver Options
-------------------------------------

Standard MGA supports parallel execution of iterative solves to maximize
performance. **Note: SVMGA executes sequentially and does not utilize parallel
workers.** Each worker also takes the results out of the alternative it solved
(capacities, flows, and the point of the hull it adds) and sends back only those,
so the main process only writes them and updates the hull.

The number of worker processes and their solver options are set in the
``[MGA]`` section of the configuration file:

.. code-block:: toml

   [MGA]
   num_workers = 4
   solver_options = { Method = 2, Threads = 4, BarConvTol = 0.01 }

The solver options of the workers are merged as follows, the last layer taking
precedence:

1. Temoa's default options for the solver.
2. The section of the solver in
   ``temoa/extensions/modeling_to_generate_alternatives/MGA_solver_options.toml``,
   which also holds a fallback ``num_workers``.
3. The ``options`` of the ``solver`` entry of the configuration file.
4. The ``solver_options`` of the ``[MGA]`` section.

The ``num_workers`` of the ``[MGA]`` section takes precedence over the one of
``MGA_solver_options.toml``. The initial solve, which sets the optimal cost,
only uses the ``options`` of the ``solver`` entry.

.. tip::
   When choosing ``num_workers``, a good rule of thumb is to set it to the
   number of available CPU cores minus one. This leaves room for the main
   orchestration process and ensures that the system remains responsive. Also,
   be mindful of the ``Threads`` setting within solver blocks, as the total
   thread count will be ``num_workers * Threads``.

Outputs
-------

MGA results are stored in the same output database specified in your
configuration. Each iteration is saved as a unique scenario to allow for easy
comparison and analysis.

Scenario Naming Convention
~~~~~~~~~~~~~~~~~~~~~~~~~~

Each run is saved under a unique scenario name in the output tables, following
the format: ``<base_scenario>-<iteration_index>``.

*   **Iteration 0**: The original baseline solve (optimal solution).
*   **Iterations 1-N**: The alternative solutions generated by the MGA algorithm.

For example, if your base scenario is ``utopia_mga``, the results for the base
case will be found under scenario ``utopia_mga-0``, and the first alternative
will be under ``utopia_mga-1``.

With ``save_storage_levels = true`` in the configuration file, **output_storage_level**
holds the storage levels of the baseline solve and of each iteration. Duals are not
saved in MGA runs.

Key Database Tables
~~~~~~~~~~~~~~~~~~~

The results are spread across several tables, consistent with standard Temoa runs:

*   **output_objective**: Stores the total system cost and MGA optimization objective for each iteration.
*   **output_net_capacity**: Stores the installed capacity for each technology, period, and iteration.
*   **output_flow_out** / **output_flow_out_summary**: Stores energy flows between technologies.
*   **output_emission**: Stores emission results per commodity and technology.
*   **output_cost**: Stores detailed cost breakdowns (investment, fixed, variable).

Comparing Iterations
~~~~~~~~~~~~~~~~~~~~

You can use SQL queries to compare results across different MGA iterations.

**Comparing Total System Cost:**

.. code-block:: sql

   SELECT scenario, total_system_cost
   FROM output_objective
   WHERE scenario LIKE 'utopia_mga-%'
     AND objective_name = 'total_cost'
   ORDER BY scenario;

**Comparing Capacity for a Specific Technology:**

.. code-block:: sql

   SELECT scenario, tech, period, capacity, units
   FROM output_net_capacity
   WHERE scenario LIKE 'utopia_mga-%'
     AND tech = 'solar_pv'
   ORDER BY scenario, period;

**Analyzing Diversity (SQL Join Example):**

.. code-block:: sql

   SELECT a.scenario, a.tech, a.capacity as cap_a, b.capacity as cap_b, (a.capacity - b.capacity) as diff
   FROM output_net_capacity a
   JOIN output_net_capacity b ON a.tech = b.tech AND a.period = b.period
   WHERE a.scenario = 'utopia_mga-1'
     AND b.scenario = 'utopia_mga-0'
     AND a.tech = 'solar_pv';
