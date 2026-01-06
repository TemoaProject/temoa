.. _unit_checking:

Units Checking
==============

The Temoa v4.0 database schema includes comprehensive units checking capabilities to ensure consistency
and accuracy throughout the model. Unit checking validates that all units are properly formatted,
dimensionally consistent, and align correctly across related tables.

.. important::
   The units expressed and checked via ``pint`` do not "follow the values" through the mathematics
   of the model. Unit checking is a **pre-processing validation layer** used to support documentation
   and catch input errors. **The units are not used in the model calculations themselves.**

Unit Propagation to Outputs
---------------------------

Starting with v4.0, units defined in input tables are **automatically propagated** to output tables
when model results are written. This provides traceability of units from inputs through results.

**How It Works**:

- ``output_flow_out`` / ``output_flow_in``: Units from ``commodity.units`` for the output/input commodity
- ``output_built_capacity`` / ``output_net_capacity`` / ``output_retired_capacity``: Units from ``existing_capacity.units``
- ``output_emission``: Units from ``commodity.units`` for the emission commodity
- ``output_cost``: Common currency unit extracted from cost input tables
- ``output_storage_level``: Units from the stored commodity

**Backward Compatibility**:

- Databases without unit data in input tables will write ``NULL`` units to outputs
- Databases with older schemas (no ``units`` column on output tables) continue to work normally
- Unit propagation is automatic and requires no configuration

Overview
--------

The unit checking system uses the Python package ``pint`` to perform unit validation and dimensional
analysis. This leverages pint's built-in unit registry to validate units with varying prefixes
(e.g., PJ, TJ, GJ) and enables future extensions.

The basis for most unit comparisons comes from:

- **commodity table**: Defines native units for each commodity (energy network nodes)
- **efficiency table**: Infers technology units via input/output ratios
- **capacity_to_activity table**: Provides conversion factors for capacity-based measures

Enabling Unit Checking
-----------------------

Via Configuration File
~~~~~~~~~~~~~~~~~~~~~~

Add to your ``config.toml``:

.. code-block:: toml

   [model_checks]
   check_units = true

Via CLI
~~~~~~~

Standalone unit checking for any database:

.. code-block:: bash

   # Basic usage
   temoa check-units path/to/database.sqlite

   # Custom output directory
   temoa check-units database.sqlite --output ./reports

   # Silent mode (for scripting)
   temoa check-units database.sqlite --silent

How It Works
------------

The unit checker performs five sequential tests:

1. **Database Version Check**: Ensures database is v4.0+ (checks ``metadata`` table)
2. **Units Entry Validation**: Checks for illegal characters, proper formatting, registry membership
3. **Technology I/O Alignment**: Validates ``efficiency`` table units match commodities
4. **Related Tables**: Checks tables referencing technologies for unit consistency
5. **Cost Tables**: Validates cost units and dimensional alignment

Expressing Units
----------------

Format Requirements
~~~~~~~~~~~~~~~~~~~

.. warning::
   **CRITICAL**: The unit checker uses regex parsing with strict format requirements!

Units in **efficiency** and **cost** tables MUST use ratio format:

.. code-block:: text

   Numerator / (Denominator)

   [V] CORRECT:   PJ / (PJ)
   [V] CORRECT:   Mdollar / (PJ^2 / GW)
   [X] WRONG:     PJ/PJ              (no parentheses)
   [X] WRONG:     Mdollar * GW / (PJ^2)   (denominator incomplete)

The denominator **MUST be fully enclosed in parentheses**. The regex only captures content
within ``( )`` after the ``/``.

Other tables should use plain entries:

.. code-block:: text

   [V]  PJ
   [V]  petajoules
   [V]  GW
   [V]  Mt / (GW)    (if ratio needed)

Custom Units Registry
~~~~~~~~~~~~~~~~~~~~~

Temoa extends pint's default registry with domain-specific units:

- ``dollar`` (or ``USD``)
- ``euro`` (or ``EUR``)
- ``passenger``
- ``seat`` (for passenger-miles, seat-miles)
- ``ethos`` (dimensionless source commodity)

Common Footguns and Pitfalls
-----------------------------

1. Missing Parentheses in Ratios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Forgetting to parenthesize the denominator

.. code-block:: text

   [X] cost_invest units: "Mdollar / PJ^2 / GW"

   Error: RATIO_ELEMENT regex doesn't match, only "PJ^2" captured

**Solution**: Always use parentheses

.. code-block:: text

   [V] cost_invest units: "Mdollar / (PJ^2 / GW)"

2. Capacity vs Energy Units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Using energy units (GW*year, kWh) in capacity tables

.. code-block:: text

   [X] existing_capacity units: "GW * year"

   Error: Energy units (not capacity) in capacity table

**Solution**: Use power units (negative time dimension)

.. code-block:: text

   [V] existing_capacity units: "GW"    ([time]^-3 = power)
   [X] existing_capacity units: "GWh"   ([time]^-2 = energy)

**Physics**:
- Capacity = Power (W, kW, MW, GW) -> ``[time]^-3``
- Energy = Power × Time (Wh, kWh) -> ``[time]^-2``

3. Cost Table Units and C2A
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Not accounting for capacity_to_activity conversion

For capacity-based costs, the expected denominator is:

.. math::

   \text{expected\_measure} = \text{output\_units} \times \text{C2A} \times \text{year}

**Example**:
- Output commodity: ``ELC`` = ``PJ``
- C2A: ``PJ / (GW * year)``
- Expected: ``PJ * [PJ/(GW*year)] * year`` = ``PJ^2/GW``

.. code-block:: text

   [V] cost_invest: "Mdollar / (PJ^2 / GW)"
   [V] cost_fixed:  "Mdollar / (PJ^2 / GW / year)"   (adds /year for period-based)

4. period_based Flag
~~~~~~~~~~~~~~~~~~~~

**Problem**: Misunderstanding period_based vs capacity_based

These flags are **orthogonal**:

- ``capacity_based``: Multiply expected units by C2A
- ``period_based``: Divide expected units by year

``cost_fixed`` is **BOTH** capacity_based AND period_based!

.. csv-table::
   :header: "Table", "capacity_based", "period_based", "Units Example"

   "cost_invest", "True", "False", "Mdollar / (PJ^2 / GW)"
   "cost_fixed", "True", "True", "Mdollar / (PJ^2 / GW / year)"
   "cost_variable", "False", "False", "Mdollar / (PJ)"
   "cost_emission", "False", "False", "Mdollar / (Mt)"

5. Schema Variations: tech vs tech_or_group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: v4.0 limit tables use ``tech_or_group`` not ``tech``

The unit checker automatically detects which column exists, but be aware:

.. code-block:: sql

   -- v3.1 schema
   SELECT tech, units FROM limit_capacity...

   -- v4.0 schema
   SELECT tech_or_group, units FROM limit_capacity...

Tables affected: ``limit_activity``, ``limit_capacity``, ``limit_new_capacity``

6. Technology Output Uniformity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Same technology with multiple output commodities using different units

.. warning::
   All instances of a technology MUST produce output in the **same units**, even if
   output commodities differ!

**Why**: Constraints span regions and output commodities, requiring a single unit of measure.

.. code-block:: text

   [X] WRONG:
   tech E01, output ELC: PJ
   tech E01, output HEAT: GJ    (different units!)

   [V] CORRECT:
   tech E01, output ELC: PJ
   tech E01, output HEAT: PJ    (same units)

Testing and Troubleshooting
----------------------------

Testing Units Manually
~~~~~~~~~~~~~~~~~~~~~~~

Test unit validity outside the model:

.. code-block:: python

   from temoa.model_checking.unit_checking import ureg

   # Check if units exist in registry
   print('PJ' in ureg)          # True
   print('catfood' in ureg)     # False

   # Parse and check units
   u = ureg('Mdollar / (PJ^2 / GW)')
   print(u.dimensionality)      # {[currency]: 1, [time]: 1, ...}

   # Check currency dimension (for cost tables)
   print('[currency]' in u.dimensionality)  # True

Common Error Messages
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   "Units lack currency dimension"
   -> Cost table units don't contain currency (dollar/euro)

   "Energy units (not capacity) in capacity table"
   -> Using energy units (kWh, GWh, etc.) instead of capacity units (GW, MW)

   "Non-matching measure unit"
   -> Units don't match expected format after accounting for C2A/period

   "failed to process query: no such column: tech"
   -> Using old SQL queries on v4.0 schema (should auto-fix now)

Reading Unit Check Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reports are saved to ``output_path/unit_check_reports/units_check_TIMESTAMP.txt``:

.. code-block:: text

   ======== Units Check 1 (DB Version): Started ========
   Units Check 1 (DB Version): Passed

   ======== Units Check 2 (Units Entries in Tables): Started ========
   existing_capacity: Energy units (not capacity) in capacity table: GW*year at rows: 1, 2, 3

   ======== Units Check 3 (Tech I/O via Efficiency Table): Started ========
   Efficiency units conflict with associated commodity for Technology E01 near row 1

   ======== Units Check 4 (Related Tables): Started ========
   limit_capacity: Non-standard units for tech E01 (expected GW) got: MW at rows: 5, 6

   ======== Units Check 5 (Cost Tables): Started ========
   cost_invest: Non-matching measure unit for tech/comm: E01
     Table entry: Mdollar / (PJ)
     Expected: petajoule ** 2 / gigawatt
     Found: petajoule at rows: 1, 2, 3

Each check section shows:
- Which table/tech has issues
- What was expected vs what was found
- Row numbers for easy correction

Tables Checked
--------------

v4.0 Schema Coverage
~~~~~~~~~~~~~~~~~~~~

.. csv-table::
   :header: "Table", "Has Units", "Check 2", "Check 3", "Check 4", "Check 5"
   :widths: 25, 12, 10, 12, 15, 10

   "capacity_to_activity", "[V]", "[V]", "", "(used)", "(used)"
   "commodity", "[V]", "[V]", "[V]", "", ""
   "construction_input", "[V]", "[V]", "", "", ""
   "cost_emission", "[V]", "[V]", "", "", "[V]"
   "cost_fixed", "[V]", "[V]", "", "", "[V]"
   "cost_invest", "[V]", "[V]", "", "", "[V]"
   "cost_variable", "[V]", "[V]", "", "", "[V]"
   "demand", "[V]", "[V]", "", "[V]", ""
   "efficiency", "[V]", "[V]", "[V]", "", ""
   "emission_activity", "[V]", "[V]", "", "", ""
   "emission_embodied", "[V]", "[V]", "", "", ""
   "emission_end_of_life", "[V]", "[V]", "", "", ""
   "end_of_life_output", "[V]", "[V]", "", "", ""
   "existing_capacity", "[V]", "[V]", "", "[V]", ""
   "lifetime_process", "[V]", "[V]", "", "", ""
   "lifetime_tech", "[V]", "[V]", "", "", ""
   "loan_lifetime_process", "[V]", "[V]", "", "", ""
   "limit_activity", "[V]", "[V]", "", "[V]", ""
   "limit_capacity", "[V]", "[V]", "", "[V]", ""
   "limit_emission", "[V]", "[V]", "", "", ""
   "limit_new_capacity", "[V]", "[V]", "", "[V]", ""
   "limit_resource", "[V]", "[V]", "", "", ""

**Check Legend**:
- Check 2: Standard validation (format, characters, registry)
- Check 3: Technology I/O alignment via Efficiency table
- Check 4: Related tables consistency
- Check 5: Cost tables validation

Best Practices
--------------

1. **Start with commodities**: Define commodity units first, then build tech efficiency ratios
2. **Use standard prefixes**: Stick to k, M, G, T prefixes (kilo, mega, giga, tera)
3. **Be consistent**: Use the same unit style across your database (e.g., always "PJ" not mix of "PJ"/"petajoule")
4. **Test early**: Run unit checker on partial databases during development
5. **Document assumptions**: Use notes fields to explain unusual unit choices
6. **Reference implementation**: See ``temoa/tutorial_assets/utopia.sqlite`` for a fully compliant example

Quick Reference
---------------

Common Unit Patterns
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   # Energy commodities
   commodity units: PJ, TJ, GJ, MWh

   # Capacity
   existing_capacity units: GW, MW, kW

   # Efficiency (energy tech)
   efficiency units: PJ / (PJ)      (dimensionless)
   efficiency units: PJ / (Mt)      (energy from mass)

   # C2A conversion
   capacity_to_activity units: PJ / (GW * year)

   # Costs (capacity-based tech with PJ output, PJ/(GW*year) C2A)
   cost_invest units: Mdollar / (PJ^2 / GW)
   cost_fixed units: Mdollar / (PJ^2 / GW / year)
   cost_variable units: Mdollar / (PJ)

   # Emissions
   emission_activity units: Mt / (PJ)
   emission_embodied units: Mt / (GW)

Dimension Reference
~~~~~~~~~~~~~~~~~~~

Pint tracks seven base dimensions:

- ``[length]``: meter, km, mile
- ``[mass]``: kg, tonne, Mt
- ``[time]``: second, year
- ``[current]``: ampere
- ``[temperature]``: kelvin
- ``[substance]``: mole
- ``[luminosity]``: candela
- ``[currency]``: dollar, euro (Temoa extension)

Derived dimensions:

- Energy: ``[length]^2 * [mass] / [time]^2`` (joule, kWh)
- Power: ``[length]^2 * [mass] / [time]^3`` (watt, GW)
- Force: ``[length] * [mass] / [time]^2`` (newton)

See Also
--------

- :ref:`database_schema` - v4.0 schema reference
- :ref:`configuration` - Configuration file format
- ``temoa/model_checking/unit_checking/`` - Source code
- ``tests/test_unit_checking.py`` - Unit tests with examples
