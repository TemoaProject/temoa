"""Data-loading manifest for the template extension.

TEMPLATE: ``build_manifest_items`` returns one ``LoadItem`` per database table
this extension reads. The loader uses each item to query, validate, and populate
the matching Pyomo component declared in core/model.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from temoa.data_io.loader_manifest import LoadItem

if TYPE_CHECKING:
    from temoa.core.model import TemoaModel
    from temoa.extensions.template.core.model import ExampleModel


def build_manifest_items(model: TemoaModel) -> list[LoadItem]:
    """Return the LoadItems for the template extension.

    TEMPLATE: As with ``register_model_components``, keep the public parameter
    typed as ``TemoaModel`` (to match ``ExtensionSpec.build_manifest_items``) and
    ``cast`` to the extension subtype so the extension-owned components type-check.
    """
    m = cast('ExampleModel', model)
    return [
        LoadItem(
            # The Pyomo component to populate.
            component=m.example_new_capacity_limit,
            # Source table name.
            table='example_new_capacity_limit',
            # Columns to select; for a Param the final column is the value.
            columns=['region', 'tech_or_group', 'value'],
            # Number of leading columns that form the index (here: region, tech).
            index_length=2,
            # Source-trace validator on the loader (filters to viable r/t pairs).
            validator_name='viable_rt',
            # Which index columns to validate (region=0, tech=1).
            validation_map=(0, 1),
            # Extension tables are optional inputs, so do not require the table.
            is_table_required=False,
        ),
    ]
