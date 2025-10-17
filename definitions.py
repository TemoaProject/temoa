"""
top-level folder to provide project-wide definitions & references
"""

# Written by:  J. F. Hyink
# jeff@westernspark.us
# https://westernspark.us

# Created on:  6/28/23

import os
from pathlib import Path
from typing import cast

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

OUTPUT_PATH = None


def get_OUTPUT_PATH() -> Path:
    if OUTPUT_PATH is None:
        raise RuntimeError('Output path not yet defined')
    # Use cast to help mypy understand the type
    return cast(Path, OUTPUT_PATH)  # type: ignore[unreachable]


def set_OUTPUT_PATH(path: Path) -> None:
    global OUTPUT_PATH
    OUTPUT_PATH = path
