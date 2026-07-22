.. _extension-unit-commitment:

Unit Commitment
===============

The **unit_commitment** extension adds commitment-level operational constraints
to selected technologies: online/started/stopped unit accounting, minimum
output floors, maximum output ceilings, and minimum up-time and down-time windows.
It also supports discounted startup costs and startup emissions and input flows.

It is disabled by default and enabled per run through configuration:

.. code-block:: toml

   extensions = ["unit_commitment"]

Conceptual Model
----------------

The core idea is that the continuous capacity variable :math:`\textbf{CAP}_{r,p,t,v}` is
*notionally divided* into discrete units, each of size :math:`UC_{r,t}`.  The number of
units available is therefore :math:`\textbf{CAP}_{r,p,t,v} / UC_{r,t}`.  Crucially,
:math:`\textbf{CAP}` itself remains a standard linear (continuous) Pyomo variable — the
extension does not change its domain.  In practice, because the UC constraints tie output
directly to the integer count of online units, the optimiser will typically land on a
solution where :math:`\textbf{CAP}` is an integer multiple of :math:`UC_{r,t}`, but this
is a consequence of the optimisation rather than an explicit constraint.

The three UC variables — :math:`\textbf{UCN}` (online), :math:`\textbf{UCST}` (started),
and :math:`\textbf{UCSP}` (stopped) — count whole units and are promoted to non-negative
integers by default (MIP).  In **linearized mode** (:code:`linearized = 1`), these
variables are kept continuous.  This is equivalent to imagining that :math:`UC_{r,t}` is
infinitesimally small: the commitment variables become fractional occupancy factors rather
than discrete unit counts, and the min-output bound acts as a simple lower capacity-factor
constraint without any integer requirements.  Linearized mode is useful for reducing solve
time.

Integration with Core Constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For some existing core constraints, the extension overrides a utility function —
:func:`~temoa.components.utils.get_available_output` — that computes
the maximum available output for a process in a given time slice.  For UC technologies,
this function returns a commitment-aware expression based on online units rather than total
installed capacity.  Because this function is used throughout the core model, the following
constraints automatically become UC-aware for registered technologies with no further changes:

- :code:`capacity_constraint` — output bounded by online capacity
- :code:`storage_charge_rate_constraint`, :code:`storage_discharge_rate_constraint`,
  :code:`storage_throughput_constraint` — storage rates scale with online units
- :code:`reserve_margin_constraint` (dynamic mode only) — reserve contribution from online units only

Ramp constraints are the only exception: they require explicit knowledge of
started/stopped units to compute the ramp envelope and are therefore fully replaced by
UC-aware versions for technologies that appear in both :code:`unit_commitment` and the
ramp tables.

.. autofunction:: temoa.components.utils.available_output_base

.. autofunction:: temoa.extensions.unit_commitment.components.commitment.uc_available_output

.. warning::

   **Annual technologies are incompatible with unit commitment.**  Technologies
   in the :code:`tech_annual` set have no time-slice flexibility and cannot be
   committed; the model will raise an error if any annual technology appears in
   the :code:`unit_commitment` table.

.. warning::

   **Integer vs. linear relaxation.**  By default all three UC variables
   (:math:`\textbf{UCN}`, :math:`\textbf{UCST}`, :math:`\textbf{UCSP}`) are
   promoted to non-negative integers, turning the problem into a MIP.  Set
   :code:`linearized = 1` in the :code:`unit_commitment` table for a
   particular technology to keep those variables continuous (LP relaxation).

Overview
--------

.. list-table::
   :header-rows: 1
   :widths: 28 38 34

   * - Table
     - Purpose
     - Key interaction
   * - :code:`unit_commitment`
     - Core UC parameters (unit size, output fractions, up/down times).
     - Enables UC constraints; overrides available output calculation for UC techs.
       Commitment results are written to :code:`output_unit_commitment`.
   * - :code:`unit_commitment_startup_cost`
     - Direct startup cost per unit of capacity started.
     - Added to variable costs.
   * - :code:`unit_commitment_startup_emissions`
     - Emissions produced at startup per unit of capacity started.
     - Added to :code:`limit_emission_constraint` totals, emission
       costs and :code:`output_emission` table.
   * - :code:`unit_commitment_startup_input`
     - Input commodity consumed at startup per unit of capacity started.
     - Added to consumption in :code:`commodity_balance_constraint` and
       results in :code:`output_flow_in`.

Parameters
----------

unit_commitment
~~~~~~~~~~~~~~~

:math:`{UC}_{r \in R,\, t \in T}`

The primary UC table.  Each row registers a technology (or technology group)
as subject to unit-commitment constraints and specifies all operational
parameters.  Exactly one row per :math:`(r, t)` pair is required.

.. csv-table::
   :header: "Column", "Symbol", "Default", "Description"
   :widths: 24, 22, 10, 44

   ":code:`region`", ":math:`r`", "—", "region label"
   ":code:`tech`", ":math:`t`", "—", "technology name"
   ":code:`unit_capacity`", ":math:`UC_{r,t}`", "—", "nameplate capacity per discrete unit (same units as :code:`v_capacity`); **required**"
   ":code:`min_output_fraction`", ":math:`\underline{f}_{r,t}`", "0", "minimum output as a fraction of available nameplate output per online unit; :math:`[0, 1]`"
   ":code:`max_output_fraction`", ":math:`\overline{f}_{r,t}`", "1", "maximum output as a fraction of available nameplate output per online unit; :math:`(0, 1]`"
   ":code:`min_up_time_hours`", ":math:`T^{up}_{r,t}`", "0", "minimum number of consecutive hours a unit must remain online after starting"
   ":code:`min_down_time_hours`", ":math:`T^{dn}_{r,t}`", "0", "minimum number of consecutive hours a unit must remain offline after stopping"
   ":code:`linearized`", "—", "0", "if 1, UC variables are kept continuous (LP relaxation); if 0, they are promoted to non-negative integers (MIP)"

unit_commitment_startup_cost
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`{UCSC}_{r \in R,\, t \in T}`

Optional.  Specifies a cost incurred each time a unit is started, expressed
per unit of capacity.  The total startup cost in a timeslice :math:`(s, d)` is:

.. math::

   \text{startup cost} = \textbf{UCST}_{r,p,s,d,t,v} \cdot UC_{r,t} \cdot UCSC_{r,t}

.. csv-table::
   :header: "Column", "Symbol", "Description"
   :widths: 22, 20, 58

   ":code:`region`", ":math:`r`", "region label"
   ":code:`tech`", ":math:`t`", "technology name"
   ":code:`cost_per_cap`", ":math:`UCSC_{r,t}`", "startup cost per unit of capacity (same currency units as :code:`cost_invest`)"

unit_commitment_startup_emissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`{UCSE}_{r \in R,\, e \in C^e,\, t \in T}`

Optional.  Specifies an emission produced at startup per unit of capacity
started.  Startup emissions are summed into the :code:`limit_emission_constraint`
alongside normal activity-based emissions.

.. csv-table::
   :header: "Column", "Symbol", "Description"
   :widths: 22, 20, 58

   ":code:`region`", ":math:`r`", "region label"
   ":code:`emis_comm`", ":math:`e`", "emission commodity"
   ":code:`tech`", ":math:`t`", "technology name"
   ":code:`emis_per_cap`", ":math:`UCSE_{r,e,t}`", "emission per unit of capacity started (same units as :code:`emission_activity`)"

unit_commitment_startup_input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`{UCSI}_{r \in R,\, i \in C^p,\, t \in T}`

Optional.  Specifies a physical commodity consumed at startup per unit of
capacity started.  Startup inputs are summed into the
:code:`commodity_balance_constraint` alongside normal flow-based consumption.

.. csv-table::
   :header: "Column", "Symbol", "Description"
   :widths: 22, 20, 58

   ":code:`region`", ":math:`r`", "region label"
   ":code:`input_comm`", ":math:`i`", "input commodity"
   ":code:`tech`", ":math:`t`", "technology name"
   ":code:`input_per_cap`", ":math:`UCSI_{r,i,t}`", "input commodity consumed per unit of capacity started"

.. note::

   These inputs are **not** considered in network checking. If no other process produces or consumes the
   input commodity in this region and period, it may be removed from the model and lead to errors.

Decision Variables
------------------

Three UC decision variables are added per :math:`(r, p, s, d, t, v)` index.
By default they are non-negative integers (MIP); set :code:`linearized = 1`
to relax them to continuous non-negative reals.

.. csv-table::
   :header: "Variable", "Domain", "Description"
   :widths: 36, 16, 48

   ":math:`\textbf{UCN}_{r,p,s,d,t,v}` (:code:`v_uc_online`)", ":math:`\mathbb{Z}_{\ge 0}`", "number of units online at the start of timeslice :math:`(s,d)`"
   ":math:`\textbf{UCST}_{r,p,s,d,t,v}` (:code:`v_uc_started`)", ":math:`\mathbb{Z}_{\ge 0}`", "number of units that start up during timeslice :math:`(s,d)`"
   ":math:`\textbf{UCSP}_{r,p,s,d,t,v}` (:code:`v_uc_stopped`)", ":math:`\mathbb{Z}_{\ge 0}`", "number of units that shut down during timeslice :math:`(s,d)`"

Constraints
-----------

Unit Count Bounds
~~~~~~~~~~~~~~~~~

.. autofunction:: temoa.extensions.unit_commitment.components.commitment.uc_online_upper_constraint

.. autofunction:: temoa.extensions.unit_commitment.components.commitment.uc_started_upper_tightening_constraint

.. autofunction:: temoa.extensions.unit_commitment.components.commitment.uc_stopped_upper_tightening_constraint

Commitment Transition
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: temoa.extensions.unit_commitment.components.commitment.uc_transition_constraint

Output Bounds
~~~~~~~~~~~~~

The minimum output constraint enforces a floor on generation per online unit.
The maximum output (capacity) constraint is handled by the standard core-model
:code:`capacity_constraint` — the extension overrides
:func:`~temoa.components.utils.get_available_output` so that available output
is based on online units rather than total installed capacity, requiring no
separate replacement constraint.

.. autofunction:: temoa.extensions.unit_commitment.components.commitment.uc_min_output_constraint

Minimum Up/Down Time
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: temoa.extensions.unit_commitment.components.commitment.uc_min_up_time_constraint

.. autofunction:: temoa.extensions.unit_commitment.components.commitment.uc_min_down_time_constraint

Ramp Constraints
~~~~~~~~~~~~~~~~

When a technology appears in both the :code:`unit_commitment` table and the
:code:`ramp_up_hourly` / :code:`ramp_down_hourly` tables, the standard core-model
ramp constraints (:code:`ramp_up_constraint`, :code:`ramp_down_constraint`) are
**replaced** by UC-aware versions for that technology.  Non-UC technologies retain
the original core-model ramp constraints unchanged.

The core ramp constraint bounds the change in hourly activity against a fraction of
total installed capacity.  The UC version replaces this with a commitment-aware
expression: only online units contribute to the ramp envelope, and the operating
point assumed for units that start or stop during the transition adds or removes
headroom according to the effective minimum output fraction.  Units are assumed to
start and stop at their minimum viable output level, taken as the larger of their
:code:`min_output_fraction` and :code:`ramp_up_fraction` / :code:`ramp_down_fraction`.

.. autofunction:: temoa.extensions.unit_commitment.components.commitment.uc_ramp_up_constraint

.. autofunction:: temoa.extensions.unit_commitment.components.commitment.uc_ramp_down_constraint

Objective Contributions
-----------------------

.. autofunction:: temoa.extensions.unit_commitment.components.startup.append_startup_costs

Output Table
------------

Results are written to the :code:`output_unit_commitment` table with one row per
:math:`(scenario, region, period, season, tod, tech, vintage)`:

.. csv-table::
   :header: "Column", "Description"
   :widths: 22, 78

   ":code:`online_cap`", "capacity online at the start of the timeslice (:math:`\textbf{UCN} \cdot UC_{r,t}`)"
   ":code:`start_cap`", "capacity started during the timeslice (:math:`\textbf{UCST} \cdot UC_{r,t}`)"
   ":code:`stop_cap`", "capacity stopped during the timeslice (:math:`\textbf{UCSP} \cdot UC_{r,t}`)"

.. note::

   **Starts and stops take effect in the following time slice.**  The transition
   constraint links :math:`\textbf{UCST}_{s,d}` and :math:`\textbf{UCSP}_{s,d}` to the
   *change* in online count between :math:`(s,d)` and its successor
   :math:`(s_{next}, d_{next})`.  A unit started during slice :math:`(s,d)` therefore
   first appears as online — and is first able to produce output — in
   :math:`(s_{next}, d_{next})`.  Equivalently, a unit stopped during :math:`(s,d)` is
   still counted as online for that slice and goes offline from
   :math:`(s_{next}, d_{next})` onward.
