"""
Utilities for SQLite performance tuning in Temoa.
"""

import logging
import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from temoa.core.config import TemoaConfig

logger = logging.getLogger(__name__)


def tune_sqlite_connection(con: sqlite3.Connection, config: 'TemoaConfig | None' = None) -> None:
    """
    Apply performance-tuning PRAGMAs to a SQLite connection.

    Args:
        con: The sqlite3.Connection object to tune.
        config: Optional TemoaConfig object to override defaults.
    """
    journal_mode = 'WAL'
    synchronous = 'NORMAL'
    temp_store = 'MEMORY'
    mmap_size = 8589934592  # 8GB
    cache_size = -512000  # 500MB (negative means KiB)

    if config:
        journal_mode = getattr(config, 'sqlite_journal_mode', journal_mode)
        synchronous = getattr(config, 'sqlite_synchronous', synchronous)
        temp_store = getattr(config, 'sqlite_temp_store', temp_store)
        mmap_size = getattr(config, 'sqlite_mmap_size', mmap_size)
        cache_size = getattr(config, 'sqlite_cache_size', cache_size)

    pragmas = [
        ('journal_mode', journal_mode),
        ('synchronous', synchronous),
        ('temp_store', temp_store),
        ('mmap_size', mmap_size),
        ('cache_size', cache_size),
    ]

    for name, value in pragmas:
        try:
            con.execute(f'PRAGMA {name} = {value}')
            logger.debug('Applied SQLite PRAGMA: %s = %s', name, value)
        except sqlite3.Error as e:
            logger.warning('Failed to apply SQLite PRAGMA %s: %s', name, e)
