.. _extension-discrete-capacity:

Discrete Capacity
================================

The **discrete_capacity** extension adds optional constraints that force the
capacity of a technology or technology group to be deployed in discrete,
indivisible units rather than as a continuous quantity. This is useful for
modeling lumpy investments or retirements such as a power plant, reactor, or
other facility that can only exist in whole units of a fixed size.

Enabling the extension introduces integer decision variables, which turns the
model into a mixed-integer program (MIP). It is disabled by default and enabled
per run through configuration:

.. code-block:: toml

   extensions = ["discrete_capacity"]

Its parameters live in the extension-owned tables of the same name and are loaded
only when the extension is enabled. See :ref:`extensions` for how the extension
framework wires these components into the model.

Parameters
----------

.. csv-table::
   :header: "Parameter", "Database Table", "Model Element", "Notes"
   :widths: 15, 20, 25, 40

   ":math:`\text{LDNC}_{r,t}`", ":code:`limit_discrete_new_capacity`", ":code:`limit_discrete_new_capacity`", "unit size for new capacity additions; new capacity is forced to an discrete multiple of this size; :code:`tech_or_group` column accepts a technology name or group name"
   ":math:`\text{LDC}_{r,t}`", ":code:`limit_discrete_capacity`", ":code:`limit_discrete_capacity`", "unit size for total available (retirement-adjusted) capacity; net capacity is forced to an integer multiple of this size; :code:`tech_or_group` column accepts a technology name or group name"


limit_discrete_new_capacity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`{LDNC}_{r \in R, t \in T}`

The :code:`limit_discrete_new_capacity` parameter specifies the unit size for new
capacity additions of a technology (or group). The new capacity built in each
vintage is forced to be an integer multiple of this unit size. The
:code:`tech_or_group` column accepts a technology name or group name, and the
:code:`capacity` column gives the size of a single unit.


limit_discrete_capacity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:math:`{LDC}_{r \in R, t \in T}`

The :code:`limit_discrete_capacity` parameter specifies the unit size for the
total available (retirement-adjusted) capacity of a technology (or group). The
net capacity available in each period is forced to be an integer multiple of this
unit size. The :code:`tech_or_group` column accepts a technology name or group
name, and the :code:`capacity` column gives the size of a single unit.


Decision Variables
------------------

Enabling the extension adds two integer decision variables, one per constraint.
Each counts the number of discrete units, which is multiplied by the
corresponding unit size to recover the capacity quantity.

v_discrete_new_capacity
~~~~~~~~~~~~~~~~~~~~~~~~

:math:`DNCAP_{r, t, v}`

The number of discrete units of new capacity built for technology (or group)
:math:`t` in region :math:`r` and vintage :math:`v`.  It is restricted to
non-negative integers, and the total new capacity equals this count multiplied by
the unit size :math:`LDNC_{r, t}`.


v_discrete_capacity
~~~~~~~~~~~~~~~~~~~~~~~~

:math:`DCAP_{r, p, t}`

The number of discrete units of total available (retirement-adjusted) capacity
for technology (or group) :math:`t` in region :math:`r` and period :math:`p`.  It
is restricted to non-negative integers, and the net available capacity equals this
count multiplied by the unit size :math:`LDC_{r, t}`.


Constraints
-----------

.. autofunction:: temoa.extensions.discrete_capacity.components.discrete_capacity.limit_discrete_new_capacity_constraint_rule

.. autofunction:: temoa.extensions.discrete_capacity.components.discrete_capacity.limit_discrete_capacity_constraint_rule
