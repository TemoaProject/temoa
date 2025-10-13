# temoa/data_io/component_manifest.py
from temoa.core.model import TemoaModel
from temoa.data_io.loader_manifest import LoadItem


def build_manifest(M: TemoaModel) -> list[LoadItem]:
    """
    Builds the manifest of all data components to be loaded into the Pyomo model.

    This declarative approach separates the configuration of what to load from the
    procedural logic of how to load it.

    Args:
        M: An instance of TemoaModel to link components.

    Returns:
        A list of LoadItem objects describing the data to be loaded.
    """
    manifest = [
        # === REGION SETS ===
        LoadItem(
            component=M.regions,
            table='Region',
            columns=['region'],
            is_period_filtered=False,
        ),
        # More items will be migrated here in subsequent steps...
    ]
    return manifest
