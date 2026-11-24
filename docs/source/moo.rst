.. _moo:

Multi-Objective Optimization (MOO)
==================================

The Multi-Objective Optimization (MOO) extension explores the trade-off between
two objective functions by computing a set of Pareto optimal solutions. Three
objective functions are available:

* ``cost``: the total discounted system cost, i.e. the standard Temoa objective
  function.
* ``emission``: the total emissions over the whole time horizon, including
  activity, embodied and end of life emissions.
* ``construction_input``: the total commodity consumption due to the
  construction of new capacity (``construction_input`` table) over the whole
  time horizon.

The ``emission`` and ``construction_input`` objective functions are
undiscounted cumulative totals: annual values are multiplied by the length of
the period they belong to.

Method
------

The Pareto front between the first objective function :math:`f_1` and the second
objective function :math:`f_2` is computed with the augmented epsilon-constraint
method. The method is described in
`Finke and Bertsch (2023) <https://doi.org/10.1016/j.apenergy.2022.120521>`_
and consists of the following steps:

#. :math:`f_1` is minimized, returning :math:`f_1^{min}`.
#. :math:`f_2` is minimized, returning :math:`f_2^{min}`.
#. :math:`f_2` is minimized while :math:`f_1` is held at :math:`f_1^{min}`,
   returning :math:`f_2^{max}`.
#. ``ncaps`` evenly spaced caps :math:`\varepsilon_n` are defined between
   :math:`f_2^{min}` and :math:`f_2^{max}`, and for each of them the following
   problem is solved, where :math:`s` is a non-negative slack variable:

   .. math::

      \min \; f_1 - c \cdot \frac{s}{f_2^{max} - f_2^{min}}
      \qquad \text{s.t.} \qquad f_2 + s = \varepsilon_n

The slack term in the objective function guarantees that each solution is Pareto
optimal, and not just weakly Pareto optimal.

Configuration
-------------

To perform a MOO run, set the ``scenario_mode`` to ``"MOO"`` in your
configuration TOML file and provide a ``[MOO]`` section:

.. code-block:: toml

   scenario_mode = "MOO"

   [MOO]
   f1 = "cost"
   f2 = "emission"
   ncaps = 11
   c = 0.0001
   emission_commodities = ["co2"]
   construction_input_commodities = []
   # num_workers = 4
   # solver_options = { Threads = 4 }

MOO requires the input and output databases to be the same.

Options
^^^^^^^

* **f1**: The objective function that is minimized: ``cost``, ``emission``,
  ``construction_input`` or the name of a custom objective function (see
  below). Default: ``cost``.
* **f2**: The objective function that is capped. It must differ from ``f1``.
  Default: ``emission``.
* **ncaps**: The number of caps on ``f2``, i.e. the number of Pareto optimal
  solutions computed. Default: ``11``.
* **c**: The weight of the slack variable in the augmented objective function.
  It should be small (e.g. ``1E-4``) so that the slack term does not alter the
  minimization of ``f1``. Default: ``0.0001``.
* **emission_commodities**: The list of emission commodities contributing to the
  ``emission`` objective function. If empty or not specified, the flows of all
  the emission commodities are summed.
* **construction_input_commodities**: The list of commodities contributing to
  the ``construction_input`` objective function. If empty or not specified, the
  consumption of all the commodities used as construction inputs is summed.
* **num_workers**: The number of worker processes solving the Pareto optimal
  solutions in parallel (see below).
* **solver_options**: Solver options for the worker processes (see below).

.. note::
   Commodities are summed without any weighting or unit conversion. When the
   selected commodities are measured in different units, restrict the lists to
   commodities that can be meaningfully added together.

Custom objective functions
--------------------------

In addition to the built-in objective functions, the user can define any number
of custom objective functions as weighted sums of the activity, the built
capacity and the net capacity of the technologies. The weights are specified in
three optional database tables:

.. list-table::
   :header-rows: 1
   :widths: 34 40 26

   * - Table
     - Index columns
     - Weight applied to
   * - ``moo_activity_weight``
     - objective, region, period, tech, vintage
     - activity (output flow)
   * - ``moo_built_capacity_weight``
     - objective, region, tech, vintage
     - built capacity
   * - ``moo_net_capacity_weight``
     - objective, region, period, tech, vintage
     - net capacity

The ``objective`` column holds the name of the custom objective function, which
is the label to be used for ``f1`` or ``f2`` in the configuration file. The
value of a custom objective function is the sum of all the rows carrying its
name across the three tables, so that activity and capacity terms can be
combined in the same objective function. Only the technologies (and regions,
periods and vintages) listed in the tables contribute to it.

* Activity is the total over the whole time horizon: the annual activity is
  multiplied by the length of the period.
* Built capacity is counted once, in its vintage.
* Net capacity is summed over the periods without further weighting.

All the index columns must be specified, and they must correspond to processes
existing in the model, otherwise the run is stopped with an error.

The tables can be added to a database with the SQL file
``temoa/extensions/multi_objective_optimization/tables.sql``. They are only
read when ``f1`` or ``f2`` is not a built-in objective function: a database
without these tables can be used for MOO runs on the built-in objective
functions.

.. note::
   Weights can be negative, e.g. to maximize a quantity. However, the method
   requires each objective function to have a finite minimum when it is
   minimized alone, and the run is stopped with an error if this is not the
   case. For instance, maximizing the activity or the capacity of a technology
   is generally unbounded unless the model includes constraints limiting it.

Parallel Execution and Solver Options
-------------------------------------

The three solves bounding the Pareto front (lowest ``f1``, lowest ``f2`` and
``f2`` at the lowest ``f1``) are run one after the other, with the solver
options of the ``solver`` entry of the configuration file. If one of them ends
with a feasible but sub-optimal solution (e.g. a barrier solve without crossover
that cannot meet the optimality tolerances), that solution is used and a warning
is logged; any other failure stops the run. The ``ncaps
Pareto optimal solutions are then solved in parallel by ``num_workers`` worker
processes, whose solver options are merged as follows, the last layer taking
precedence:

1. Temoa's default options for the solver.
2. The section of the solver in
   ``temoa/extensions/multi_objective_optimization/MOO_solver_options.toml``,
   which also holds a fallback ``num_workers``.
3. The ``options`` of the ``solver`` entry of the configuration file.
4. The ``solver_options`` of the ``[MOO]`` section.

The ``num_workers`` of the ``[MOO]`` section takes precedence over the one of
``MOO_solver_options.toml``. Each worker runs its own solver instance, so the
total number of threads is ``num_workers`` times the threads of each solver
instance.

Each worker also takes the results out of the model it solved (capacities,
flows, costs, emissions and the objective values) and sends back only those,
so the main process only writes them to the database.

Outputs
-------

Each Pareto optimal solution is saved in the output tables under the scenario
name ``<scenario>-<n>``, with ``n`` ranging from ``0`` (highest cap on ``f2``,
i.e. lowest ``f1``) to ``ncaps - 1`` (lowest cap on ``f2``). For each solution, the
``output_objective`` table reports the value of the three built-in objective
functions (``cost``, ``emission`` and ``construction_input``), regardless of
which were selected as ``f1`` and ``f2``, and of the custom objective functions
selected as ``f1`` or ``f2``.

With ``save_storage_levels = true`` in the configuration file,
``output_storage_level`` holds the storage levels of each solution. With
``save_duals = true``, ``output_dual_variable`` holds the duals of each solution.
They are the duals of the problem solved for that solution: the dual of
``moo_f2_cap``, the cap on ``f2``, is the change of ``f1`` per unit of ``f2``
(for cost × CO2, the marginal cost of abatement at that solution), and, when
``f1`` is ``cost``, the duals of the commodity balance constraints are the
commodity prices under that cap. Duals need a solver that returns them (not
``appsi_highs``), and solvers return none for mixed-integer models (for example
with ``discrete_capacity`` or ``unit_commitment``).
