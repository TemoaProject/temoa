from importlib import resources as importlib_resources

from pint import UnitRegistry
from pint.errors import DefinitionSyntaxError

# UnitRegistry is generic but doesn't require type args at instantiation
ureg: UnitRegistry = UnitRegistry()  # type: ignore[type-arg]

# Load custom unit definitions from the package resources
_resource_path = 'temoa.model_checking.unit_checking/temoa_units.txt'
try:
    data = importlib_resources.files('temoa.model_checking.unit_checking').joinpath(
        'temoa_units.txt'
    )
    # Ensure we have a real filesystem path (handles zipped resources too)
    with importlib_resources.as_file(data) as path:
        ureg.load_definitions(path)
except (FileNotFoundError, OSError, DefinitionSyntaxError) as exc:
    raise RuntimeError(
        f'Failed to load custom Temoa unit definitions from {_resource_path!r}. '
        'This may indicate a broken installation or missing resource file.'
    ) from exc
