.. _extension-growth-rates:

Growth Rate Limits
==================================

The **growth_rates** extension adds optional constraints that bound how quickly
the capacity (or new capacity) of a technology or technology group may change
between consecutive model periods. It is disabled by default and enabled per
run through configuration:

.. code-block:: toml

   extensions = ["growth_rates"]

Its parameters live in the extension-owned tables of the same name and are loaded
only when the extension is enabled. See :ref:`extensions` for how the extension
framework wires these components into the model.

Parameters
----------

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LGC}_{r,t}`", ":code:`limit_growth_capacity`", ":code:`limit_growth_capacity`", "capacity growth rate limits; :code:`tech_or_group` column accepts a technology name or group name"
   ":math:`\text{LDGC}_{r,t}`", ":code:`limit_degrowth_capacity`", ":code:`limit_degrowth_capacity`", "capacity degrowth rate limits; :code:`tech_or_group` column accepts a technology name or group name"
   ":math:`\text{LGNC}_{r,t}`", ":code:`limit_growth_new_capacity`", ":code:`limit_growth_new_capacity`", "new capacity growth rate limits; :code:`tech_or_group` column accepts a technology name or group name"
   ":math:`\text{LDGNC}_{r,t}`", ":code:`limit_degrowth_new_capacity`", ":code:`limit_degrowth_new_capacity`", "new capacity degrowth rate limits; :code:`tech_or_group` column accepts a technology name or group name"
   ":math:`\mathrm{LGNC}_{\Delta,r,t}`", ":code:`limit_growth_new_capacity_delta`", ":code:`limit_growth_new_capacity_delta`", "new capacity growth acceleration limits; :code:`tech_or_group` column accepts a technology name or group name"
   ":math:`\mathrm{LDGNC}_{\Delta,r,t}`", ":code:`limit_degrowth_new_capacity_delta`", ":code:`limit_degrowth_new_capacity_delta`", "new capacity degrowth deceleration limits; :code:`tech_or_group` column accepts a technology name or group name"


limit_growth_capacity
~~~~~~~~~~~~~~~~~~~~~~~

:math:`{LGC}_{r \in R, t \in T}`

The :code:`limit_growth_capacity` parameter defines the maximum annual rate at
which the total capacity of a technology (or group) can grow between periods.
The :code:`tech_or_group` column accepts a technology name or group name.


limit_degrowth_capacity
~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`{LDGC}_{r \in R, t \in T}`

The :code:`limit_degrowth_capacity` parameter defines the maximum annual rate
at which the total capacity of a technology (or group) can shrink between
periods.  The :code:`tech_or_group` column accepts a technology name or group name.


limit_growth_new_capacity
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`{LGNC}_{r \in R, t \in T}`

The :code:`limit_growth_new_capacity` parameter constrains the rate of increase
in new capacity deployment between consecutive periods.


limit_degrowth_new_capacity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`{LDGNC}_{r \in R, t \in T}`

The :code:`limit_degrowth_new_capacity` parameter constrains the rate of decrease
in new capacity deployment between consecutive periods.


limit_growth_new_capacity_delta
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`\mathrm{LGNC}_{\Delta,r \in R, t \in T}`

The :code:`limit_growth_new_capacity_delta` parameter constrains the acceleration
of new capacity growth between periods. This essentially adds "inertia" to the
growth of new capacity deployment.


limit_degrowth_new_capacity_delta
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`\mathrm{LDGNC}_{\Delta,r \in R, t \in T}`

The :code:`limit_degrowth_new_capacity_delta` parameter constrains the
deceleration of new capacity degrowth between periods, essentially adding
"inertia" to the degrowth of new capacity deployment.


Constraints
-----------

.. autofunction:: temoa.extensions.growth_rates.components.growth_capacity.limit_growth_capacity

.. autofunction:: temoa.extensions.growth_rates.components.growth_new_capacity.limit_growth_new_capacity

.. autofunction:: temoa.extensions.growth_rates.components.growth_new_capacity_delta.limit_growth_new_capacity_delta
