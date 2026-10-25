"""
TEMOA Core API

This module provides the main public API for the TEMOA energy systems modeling library.
"""

from .config import TemoaConfig
from .model import TemoaModel
from .modes import TemoaMode

__version__ = '4.0.0a1'

__all__ = ['TemoaModel', 'TemoaConfig', 'TemoaMode', '__version__']
