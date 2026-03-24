import sqlite3
import logging
from temoa.extensions.myopic.myopic_index import MyopicIndex

logger = logging.getLogger(__name__)

def iterate(
        idx: MyopicIndex | None = None,
        prev_base_year: int | None = None,
        last_instance_status: str | None = None,
        db_con: sqlite3.Connection | None = None,
    ) -> None:
    """
    This function is called at the end of each myopic iteration,
    after the results have been recorded to the myopic database.
    You can use it to update your myopic database with any additional
    information you want to track across iterations, or to implement
    an evolving myopic approach where the model structure changes
    across iterations based on some user-defined logic.
        Parameters:
        - idx (MyopicIndex): The index object for the current iteration,
            containing information about the base year, view depth, etc.
        - prev_base_year (int): The base year of the previous iteration.
        - last_instance_status (str): The status of the last solved instance
            ('optimal' meaning successful or 'roll_back' meaning solver failure
            and rollback to previous iteration).
        - db_con (sqlite3.Connection): A connection object to the myopic database,
            which you can use to read/write data as needed.
    """

    logger.info(f"Running myopic iteration updater for base year {idx.base_year}")

    # Update your myopic database here.

    return
