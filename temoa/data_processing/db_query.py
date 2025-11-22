# Dev Note:  This module is unused and appears to be just a query executor.  Retained for now.
# 12JUN2024
"""
A command-line utility for sending a direct SQL query to a Temoa database.

This script allows a user to specify a Temoa SQLite database and an SQL query
string to execute against it, printing the results to the console.
"""

import getopt
import re
import sqlite3
import sys
from os import PathLike
from typing import Any


def send_query(inp_f: str | PathLike[str], query_string: str) -> str:
    """
    Connects to a database, executes a query, and returns the result as a string.

    Args:
        inp_f: The file path to the SQLite database.
        query_string: The SQL query to execute.

    Returns:
        A string containing the query results or an error message.
    """
    db_result: list[tuple[Any, ...]] = []
    try:
        con = sqlite3.connect(inp_f)
        cur = con.cursor()
        con.text_factory = str

        print(f'Executing query on: {inp_f}')
        cur.execute(query_string)

        db_result.extend(cur)

        cur.close()
        con.close()
        # Convert list of tuples to a more readable string representation
        result_str = '\n'.join(map(str, db_result))
        return f'Query Result:\n{result_str}'

    except sqlite3.Error as e:
        error_msg = f'Error in Query: {e.args[0]}'
        print(error_msg)
        return f'Query Result: {error_msg}'


def help_user() -> None:
    """Prints the help message for the script to the console."""
    print(
        """Use as:
    python db_query.py -i (or --input) <input database name>
    | -q (or --query) <sqlite query>
    | -h (or --help)"""
    )


def get_flags(inputs: dict[str, str]) -> str | None:
    """
    Parses command-line options and executes the database query.

    Args:
        inputs: A dictionary of command-line options to their arguments.

    Returns:
        The result of the database query as a string, or None if no query was run.

    Raises:
        TypeError: If no arguments are provided.
        ValueError: If the input file is not specified or is not a valid database file.
    """
    inp_file: str | None = None
    query_string: str | None = None

    if not inputs:
        raise TypeError('no arguments found')

    for opt, arg in inputs.items():
        print(f'{opt} == {arg}')

        if opt in ('-i', '--input'):
            inp_file = arg
        elif opt in ('-q', '--query'):
            query_string = arg
        elif opt in ('-h', '--help'):
            help_user()
            sys.exit(2)

    if inp_file is None:
        raise ValueError('Input file not specified')

    file_ty = re.search(r'\.(\w+)$', inp_file)

    if not file_ty or file_ty.group(1) not in ('db', 'sqlite', 'sqlite3', 'sqlitedb'):
        raise ValueError(f'The file type of "{inp_file}" is not a recognized database file.')

    if query_string is None:
        print('No query specified.')
        return None

    return send_query(inp_file, query_string)


if __name__ == '__main__':
    try:
        argv: list[str] = sys.argv[1:]
        opts: list[tuple[str, str]]
        args: list[str]
        opts, args = getopt.getopt(argv, 'hi:q:', ['help', 'input=', 'query='])

        print(f'Options found: {opts}')

    except getopt.GetoptError:
        help_user()
        sys.exit(2)

    print(get_flags(dict(opts)))
