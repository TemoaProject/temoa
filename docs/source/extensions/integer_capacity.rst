.. _extension-integer-capacity:

Integer Capacity
================================

The **integer_capacity** extension adds optional constraints that force the
capacity of a technology or technology group to be deployed in discrete,
indivisible units rather than as a continuous quantity. This is useful for
modeling lumpy investments or retirements such as a power plant, reactor, or
other facility that can only exist in whole units of a fixed size.

Enabling the extension introduces integer decision variables, which turns the
model into a mixed-integer program (MIP). It is disabled by default and enabled
per run through configuration:

.. code-block:: toml

   extensions = ["integer_capacity"]

Its parameters live in the extension-owned tables of the same name and are loaded
only when the extension is enabled. See :ref:`extensions` for how the extension
framework wires these components into the model.

Parameters
----------

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LINC}_{r,t}`", ":code:`limit_integer_new_capacity`", ":code:`limit_integer_new_capacity`", "unit size for new capacity additions; new capacity is forced to an integer multiple of this size; :code:`tech_or_group` column accepts a technology name or group name"
   ":math:`\text{LIC}_{r,t}`", ":code:`limit_integer_net_capacity`", ":code:`limit_integer_net_capacity`", "unit size for total available (retirement-adjusted) capacity; net capacity is forced to an integer multiple of this size; :code:`tech_or_group` column accepts a technology name or group name"


limit_integer_new_capacity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`{LINC}_{r \in R, t \in T}`

The :code:`limit_integer_new_capacity` parameter specifies the unit size for new
capacity additions of a technology (or group). The new capacity built in each
vintage is forced to be an integer multiple of this unit size. The
:code:`tech_or_group` column accepts a technology name or group name, and the
:code:`capacity` column gives the size of a single unit.


limit_integer_net_capacity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`{LIC}_{r \in R, t \in T}`

The :code:`limit_integer_net_capacity` parameter specifies the unit size for the
total available (retirement-adjusted) capacity of a technology (or group). The
net capacity available in each period is forced to be an integer multiple of this
unit size. The :code:`tech_or_group` column accepts a technology name or group
name, and the :code:`capacity` column gives the size of a single unit.


Decision Variables
------------------

Enabling the extension adds two integer decision variables, one per constraint.
Each counts the number of discrete units, which is multiplied by the
corresponding unit size to recover the capacity quantity.

v_integer_new_capacity
~~~~~~~~~~~~~~~~~~~~~~~~

:math:`INCAP_{r, t, v}`

The number of discrete units of new capacity built for technology (or group)
:math:`t` in region :math:`r` and vintage :math:`v`.  It is restricted to
non-negative integers, and the total new capacity equals this count multiplied by
the unit size :math:`LINC_{r, t}`.


v_integer_net_capacity
~~~~~~~~~~~~~~~~~~~~~~~~

:math:`ICAP_{r, p, t}`

The number of discrete units of total available (retirement-adjusted) capacity
for technology (or group) :math:`t` in region :math:`r` and period :math:`p`.  It
is restricted to non-negative integers, and the net available capacity equals this
count multiplied by the unit size :math:`LIC_{r, t}`.


Constraints
-----------

.. autofunction:: temoa.extensions.integer_capacity.components.integer_capacity.limit_integer_new_capacity_constraint_rule

.. autofunction:: temoa.extensions.integer_capacity.components.integer_capacity.limit_integer_net_capacity_constraint_rule
