import re

__version__ = '4.0.0a1'

# Parse the version string to get major and minor versions
# We use a regex to be robust against versions like "4.1a1" or "4.0.0.dev1"
_match = re.match(r'^(\d+)\.(\d+)', __version__)
if not _match:
    raise ValueError(
        f"Could not parse major/minor version from '{__version__}'. "
        "Expected format 'X.Y...' where X and Y are integers."
    )

TEMOA_MAJOR = int(_match.group(1))
TEMOA_MINOR = int(_match.group(2))

# === REQUIREMENTS ===
# python versions are tested internally for greater than these values
MIN_PYTHON_MAJOR = 3
MIN_PYTHON_MINOR = 12

# db is tested for match on major and >= on minor
DB_MAJOR_VERSION = 4
MIN_DB_MINOR_VERSION = 0
