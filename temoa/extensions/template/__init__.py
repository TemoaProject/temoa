"""Template extension package.

TEMPLATE: This is a copy-from scaffold for building a new optional Temoa
modeling extension. It is intentionally NOT registered in
``temoa.extensions.framework.get_known_extension_specs``, so it is inert:
importing it works and it type-checks, but it cannot be enabled until you
register it.

To create a real extension:
    1. Copy this whole folder to ``temoa/extensions/<your_extension>/``.
    2. Rename the ``extension_id``, tables, params, and constraints.
    3. Register the spec in ``get_known_extension_specs`` (see framework.py).
    4. Add your tables to the database schema / ``tables.sql``.
    5. Enable it via config: ``extensions = ["<your_extension>"]``.

See ``docs/source/extensions.rst`` for the full guide.
"""

from temoa.extensions.template.extension import EXAMPLE_EXTENSION

__all__ = ['EXAMPLE_EXTENSION']
