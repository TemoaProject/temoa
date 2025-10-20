"""
top-level folder to provide project-wide definitions & references
"""

import os
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

OUTPUT_PATH: Path | None = None


def get_OUTPUT_PATH() -> Path:
    if OUTPUT_PATH is None:
        raise RuntimeError('Output path not yet defined')
    # Use cast to help mypy understand the type
    return OUTPUT_PATH


def set_OUTPUT_PATH(path: Path) -> None:
    global OUTPUT_PATH
    OUTPUT_PATH = path
