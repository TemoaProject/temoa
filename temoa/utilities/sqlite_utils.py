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

    try:
        con.execute(f'PRAGMA journal_mode = {journal_mode}')
        con.execute(f'PRAGMA synchronous = {synchronous}')
        con.execute(f'PRAGMA temp_store = {temp_store}')
        con.execute(f'PRAGMA mmap_size = {mmap_size}')
        con.execute(f'PRAGMA cache_size = {cache_size}')
        logger.debug(
            'SQLite tuned: journal_mode=%s, synchronous=%s, temp_store=%s, '
            'mmap_size=%d, cache_size=%d',
            journal_mode,
            synchronous,
            temp_store,
            mmap_size,
            cache_size,
        )
    except sqlite3.Error as e:
        logger.warning('Failed to apply some SQLite performance PRAGMAs: %s', e)
