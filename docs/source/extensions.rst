.. _extensions:

Extension Framework
===================

Temoa includes a lightweight framework for adding **optional model components**
without modifying the core model. An extension can contribute its own database
tables, Pyomo components (sets, parameters, and constraints), and data-loading
rules. Extensions are declared once and then enabled per run through
configuration.

This page describes how the framework works and how to author a new extension.
A ready-to-copy scaffold lives at ``temoa/extensions/template``.

Overview
--------

Use an extension when you want to add modeling capability that is:

* **Optional** -- only active when explicitly enabled.
* **Self-contained** -- owns its own tables and model components.
* **Non-invasive** -- adds to the core model rather than editing it.

If a feature is fundamental to every Temoa run, it belongs in
``temoa/components`` (a core component) instead of an extension.

Each extension is described by a single :class:`ExtensionSpec` (declarative
metadata plus hook functions). The spec is registered with the framework, after
which users can enable the extension by id.

Lifecycle
---------

When a run is configured with ``extensions = ["..."]``, the framework threads the
enabled specs through configuration, model construction, and data loading:

.. code-block:: text

   config: extensions = ["my_ext"]
        |
        v
   resolve_extension_specs()          validate ids -> ExtensionSpec list
        |
        v
   TemoaModel(extensions=[...])
        |
        +--> apply_model_extension_hooks()
        |        calls spec.register_model_components(model)
        |        -> attaches Params / Sets / Constraints to the model
        |
        v
   HybridLoader
        +--> ensure_enabled_extension_tables_exist()   (offer to append schema)
        +--> assert_disabled_extension_tables_are_empty()
        +--> merge_regional_group_tables()
        +--> build_manifest() -> appends spec.build_manifest_items(model)
                 -> loads each owned table into its component

The relevant code lives in :mod:`temoa.extensions.framework`,
:mod:`temoa.core.model`, and :mod:`temoa.data_io.hybrid_loader`.

``ExtensionSpec`` reference
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Field
     - Purpose
   * - ``extension_id``
     - Unique, lowercase id. This is what users put in ``extensions = [...]``.
   * - ``owned_tables``
     - Tuple of database tables owned exclusively by this extension. Used by the
       disabled/enabled table guards.
   * - ``regional_group_tables``
     - Map of ``table -> column`` for tables whose region column may hold a
       regional *group* name. Merged into the loader's regional-group handling.
   * - ``register_model_components``
     - Hook ``Callable[[TemoaModel], None]`` that attaches model components.
   * - ``build_manifest_items``
     - Hook ``Callable[[TemoaModel], list[LoadItem]]`` describing how to load the
       extension's data.
   * - ``schema_sql_path``
     - Path to a ``.sql`` file applied (with consent) when the extension is
       enabled but its tables are missing.
   * - ``fail_if_tables_populated_when_disabled``
     - When ``True``, loading fails if the extension is disabled but its owned
       tables contain data, preventing silently-ignored inputs.

Recommended package layout
--------------------------

Mirror the structure of the core model (``temoa/core`` + ``temoa/components``) so
extension code is organized the same way as the rest of the codebase:

.. code-block:: text

   temoa/extensions/<your_extension>/
       __init__.py             # re-export the ExtensionSpec
       extension.py            # the ExtensionSpec definition
       data_manifest.py        # build_manifest_items()
       tables.sql              # CREATE TABLE IF NOT EXISTS for owned tables
       core/
           __init__.py
           model.py            # typing subtype + register_model_components()
       components/
           __init__.py
           <family>.py         # one module per constraint family

Centralize the component *declarations* in ``core/model.py`` (just as
``temoa/core/model.py`` does) and keep the index-set and constraint-rule logic in
``components/`` modules (just as ``temoa/components`` does).

.. _extensions-typing:

The typing pattern
------------------

Core model components are declared as attribute assignments inside
``TemoaModel.__init__`` (for example ``self.time_optimize = Set(...)``), which is
why the type checker knows about them. An extension instead adds attributes from
*outside* the class, so without help the type checker reports
``"TemoaModel" has no attribute ...`` and provides no autocomplete.

Three rules make typing carry over cleanly:

1. **Declare a ``TYPE_CHECKING``-only subtype.** In ``core/model.py``, define a
   subclass of ``TemoaModel`` that annotates every component the extension adds.
   It inherits all core attributes, so component code sees both core and
   extension members.

   .. code-block:: python

      if TYPE_CHECKING:
          from temoa.core.model import TemoaModel

          class ExampleModel(TemoaModel):
              example_new_capacity_limit: Param
              example_new_capacity_limit_constraint_rpt: Set
              example_new_capacity_limit_constraint: Constraint

2. **Annotate component functions with the subtype.** Index-set and
   constraint-rule functions take ``model: ExampleModel``. This restores both
   mypy coverage and editor autocomplete.

3. **Keep spec hooks on the base type and ``cast`` internally.** Functions stored
   on the ``ExtensionSpec`` (``register_model_components`` and
   ``build_manifest_items``) must keep ``model: TemoaModel`` to match the hook
   callable types. Narrowing the parameter is a contravariance error. ``cast``
   once at the top:

   .. code-block:: python

      def register_model_components(model: TemoaModel) -> None:
          m = cast('ExampleModel', model)
          m.example_new_capacity_limit = Param(...)

.. note::
   Extension attribute names share the single ``TemoaModel`` namespace at
   runtime. Keep them unique across extensions to avoid collisions.

Adding a new extension
----------------------

#. **Copy the template.** Duplicate ``temoa/extensions/template`` to
   ``temoa/extensions/<your_extension>/``.
#. **Rename ids and tables.** Update ``extension_id``, ``owned_tables``,
   ``regional_group_tables``, params, sets, and constraints to your domain.
#. **Declare components.** Add annotations to the typing subtype in
   ``core/model.py`` and create the components in ``register_model_components``.
#. **Write the constraint logic.** Add index-set and rule functions under
   ``components/`` and annotate them with your subtype.
#. **Describe data loading.** Add one ``LoadItem`` per owned table in
   ``data_manifest.py``.
#. **Define the schema.** Add a ``CREATE TABLE IF NOT EXISTS`` per owned table to
   ``tables.sql``.
#. **Register the spec.** Import your spec in
   :func:`temoa.extensions.framework.get_known_extension_specs` and add it to the
   ``specs`` list. (Until you do this, the extension is inert -- enabling it
   raises an "Unknown extension id" error.)
#. **Enable it.** Add the id to your configuration TOML:

   .. code-block:: toml

      extensions = ["<your_extension>"]

Data loading and ``LoadItem``
-----------------------------

``build_manifest_items`` returns one :class:`temoa.data_io.loader_manifest.LoadItem`
per database table the extension reads. Common fields:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Field
     - Purpose
   * - ``component``
     - The Pyomo ``Set`` or ``Param`` to populate.
   * - ``table``
     - Source table name in the database.
   * - ``columns``
     - Columns to select; for a ``Param`` the final column is the value.
   * - ``index_length``
     - Number of leading columns that form the index.
   * - ``validator_name`` / ``validation_map``
     - Source-trace validation: a viable-set name on the loader and which index
       columns it applies to.
   * - ``is_table_required``
     - Set ``False`` for optional extension inputs so a missing table is not an
       error.

Verification
------------

After authoring an extension, confirm:

#. **Types** -- ``mypy temoa/extensions/<your_extension>`` reports no issues.
#. **Imports** -- ``python -c "import temoa.extensions.<your_extension>.extension"``.
#. **Wiring** -- a model built with the extension enabled attaches the expected
   components, and the test suite passes.

The template extension
-----------------------

``temoa/extensions/template`` is a complete, type-checked, but deliberately
**unregistered** scaffold. Because it is not listed in
``get_known_extension_specs``, it cannot be enabled until you register it, so it
never affects normal runs. Copy the folder as the starting point for a new
extension; every file carries ``# TEMPLATE:`` comments explaining what to change.

.. _extension-catalog:

Available extensions
--------------------

The extensions that ship with Temoa are documented on their own pages below.
Each page describes the extension's parameters and constraints. This list grows
as new extensions are added.

.. toctree::
   :maxdepth: 1

   extensions/growth_rates
   extensions/discrete_capacity
