import argparse
import os
import re
import sqlite3
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

# Define allowed database extensions for clarity
DB_EXTENSIONS = ('.db', '.sqlite', '.sqlite3', '.sqlitedb')
DAT_EXTENSIONS = ('.dat', '.txt')


class ScriptError(Exception):
    """Custom exception for script-specific errors."""

    pass


def _get_db_connection(db_path: Path) -> sqlite3.Connection:
    """Establishes and returns a SQLite database connection."""
    try:
        con = sqlite3.connect(db_path)
        con.text_factory = str  # Ensure UTF-8 encoding for text
        return con
    except sqlite3.Error as e:
        raise ScriptError(f'Error connecting to database {db_path}: {e}') from e


def get_file_type_info(
    input_file_path: Path,
) -> Tuple[str, Union[str, None]]:
    """
    Validates the input file path and determines its type ('db' or 'dat').

    Returns:
        A tuple containing the file type ('db' or 'dat') and the input file path as a string.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the file type is not recognized.
    """
    if not input_file_path.exists():
        raise FileNotFoundError(f'Input file not found: {input_file_path}')

    file_suffix = input_file_path.suffix.lower()

    if file_suffix in DB_EXTENSIONS:
        return 'db', str(input_file_path)
    elif file_suffix in DAT_EXTENSIONS:
        return 'dat', str(input_file_path)
    else:
        raise ValueError(
            f"Unrecognized file extension: '{file_suffix}'. "
            f'Please use one of {DB_EXTENSIONS} or {DAT_EXTENSIONS}.'
        )


def get_tperiods(input_file_path_str: str) -> Dict[str, List[Any]]:
    """
    Extracts time periods for each scenario from a database file.

    Args:
        input_file_path_str: Path to the database file.

    Returns:
        An OrderedDict mapping scenarios to a list of their periods,
        sorted by the period lists.
    """
    input_file_path = Path(input_file_path_str)
    file_type, _ = get_file_type_info(input_file_path)

    if file_type != 'db':
        raise ValueError(
            'Invalid file type: Time periods can only be extracted from a database file.'
        )

    periods_map: Dict[str, List[Any]] = {}
    print(f'Processing database for time periods: {input_file_path}')

    try:
        with _get_db_connection(input_file_path) as con:
            cur = con.cursor()
            cur.execute('SELECT DISTINCT scenario FROM OutputFlowOut')
            scenarios = [row[0] for row in cur.fetchall()]

            for scenario_name in scenarios:
                cur.execute(
                    'SELECT DISTINCT period FROM OutputFlowOut WHERE scenario = ?',
                    (scenario_name,),
                )
                periods_map[scenario_name] = [period_row[0] for period_row in cur.fetchall()]
    except sqlite3.Error as e:
        raise ScriptError(
            f'Database error while fetching time periods from {input_file_path}: {e}'
        ) from e

    # Sort by the list of periods (values of the dictionary)
    return OrderedDict(sorted(periods_map.items(), key=lambda item: item[1]))


def get_scenario(input_file_path_str: str) -> Dict[str, str]:
    """
    Extracts scenarios from a database file.

    Args:
        input_file_path_str: Path to the database file.

    Returns:
        An OrderedDict mapping scenario names to themselves, sorted by scenario name.
    """
    input_file_path = Path(input_file_path_str)
    file_type, _ = get_file_type_info(input_file_path)

    if file_type != 'db':
        raise ValueError('Invalid file type: Scenarios can only be extracted from a database file.')

    scenario_dict: Dict[str, str] = {}
    print(f'Processing database for scenarios: {input_file_path}')

    try:
        with _get_db_connection(input_file_path) as con:
            cur = con.cursor()
            cur.execute('SELECT DISTINCT scenario FROM OutputFlowOut')
            for row in cur.fetchall():
                scenario_name = row[0]
                scenario_dict[scenario_name] = scenario_name
    except sqlite3.Error as e:
        raise ScriptError(
            f'Database error while fetching scenarios from {input_file_path}: {e}'
        ) from e

    return OrderedDict(sorted(scenario_dict.items()))


def _get_items_from_db(
    input_file_path: Path,
    primary_table: str,
    primary_col: str,
    fallback_flow_cols: List[str],
    exclude_item: Union[str, None] = None,
) -> Dict[str, str]:
    """Helper to get items (commodities/technologies) from DB."""
    items: Dict[str, str] = {}
    try:
        with _get_db_connection(input_file_path) as con:
            cur = con.cursor()
            cur.execute(f'SELECT DISTINCT {primary_col} FROM {primary_table}')
            rows = cur.fetchall()

            if rows:
                for row in rows:
                    item_name = row[0]
                    if exclude_item is None or item_name != exclude_item:
                        items[item_name] = item_name
            else:
                # Fallback to OutputFlowOut
                union_queries = [
                    f'SELECT DISTINCT {col} FROM OutputFlowOut' for col in fallback_flow_cols
                ]
                fallback_query = ' UNION '.join(union_queries)
                cur.execute(fallback_query)
                for row in cur.fetchall():
                    item_name = row[0]
                    if item_name is not None and (
                        exclude_item is None or item_name != exclude_item
                    ):
                        items[item_name] = item_name
    except sqlite3.Error as e:
        raise ScriptError(f'Database error while fetching items from {input_file_path}: {e}') from e
    return OrderedDict(sorted(items.items()))


def _get_items_from_dat(
    input_file_path: Path, item_indices: List[int], param_name: str = 'efficiency'
) -> Dict[str, str]:
    """Helper to get items (commodities/technologies) from DAT file."""
    item_set: set[str] = set()
    eff_section_found = False

    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not eff_section_found and re.search(
                    rf'^\s*param\s+{param_name}\s*[:=]', line, flags=re.IGNORECASE
                ):
                    eff_section_found = True
                elif eff_section_found:
                    line_content = line.split('#', 1)[0].strip()  # Remove comments and strip
                    if not line_content:  # Skip empty or comment-only lines
                        continue
                    if line_content == ';':  # End of section
                        break

                    parts = re.split(r'\s+', line_content)
                    for index in item_indices:
                        if index < len(parts):
                            item_name = parts[index]
                            # Specific exclusion for commodities
                            if param_name == 'efficiency' and item_name == 'ethos' and index == 0:
                                continue
                            item_set.add(item_name)

    except FileNotFoundError:
        raise
    except IOError as e:
        raise ScriptError(f'Error reading DAT file {input_file_path}: {e}') from e

    if not eff_section_found:
        raise ScriptError(
            f"Error: The '{param_name}' parameter section was not found in {input_file_path}."
        )

    return OrderedDict(sorted({item: item for item in item_set}.items()))


def get_comm(input_file_path_str: str, is_dat_file: bool) -> Dict[str, str]:
    """
    Extracts commodities from the input file (database or DAT).

    Args:
        input_file_path_str: Path to the input file.
        is_dat_file: True if the input is a DAT file, False for database.

    Returns:
        An OrderedDict of commodities, sorted by name.
    """
    input_file_path = Path(input_file_path_str)
    print(f'Processing for commodities: {input_file_path}')

    if is_dat_file:
        return _get_items_from_dat(input_file_path, item_indices=[0, 3])
    else:
        return _get_items_from_db(
            input_file_path,
            primary_table='Commodity',
            primary_col='name',
            fallback_flow_cols=['input_comm', 'output_comm'],
            exclude_item='ethos',
        )


def get_tech(input_file_path_str: str, is_dat_file: bool) -> Dict[str, str]:
    """
    Extracts technologies from the input file (database or DAT).

    Args:
        input_file_path_str: Path to the input file.
        is_dat_file: True if the input is a DAT file, False for database.

    Returns:
        An OrderedDict of technologies, sorted by name.
    """
    input_file_path = Path(input_file_path_str)
    print(f'Processing for technologies: {input_file_path}')

    if is_dat_file:
        return _get_items_from_dat(input_file_path, item_indices=[1])
    else:
        return _get_items_from_db(
            input_file_path,
            primary_table='Technology',
            primary_col='tech',
            fallback_flow_cols=['tech'],
        )


def is_db_overwritten(db_file_str: str, inp_dat_file_str: str) -> bool:
    """
    Checks if the database file seems to have been populated by a different DAT file.

    Args:
        db_file_str: Path to the database file.
        inp_dat_file_str: Path to the input DAT file for comparison.

    Returns:
        True if the database might be overwritten by a different DAT file, False otherwise.
    """
    if os.path.basename(db_file_str) == '0':  # Special sentinel value
        return False

    db_file_path = Path(db_file_str)
    if not db_file_path.exists():
        return False  # DB file doesn't exist, so not "overwritten" in this sense

    try:
        with _get_db_connection(db_file_path) as con:
            cur = con.cursor()

            # Check if Technology table has data (implies DB is not empty/new)
            cur.execute('SELECT 1 FROM Technology LIMIT 1')
            if not cur.fetchone():
                return False  # DB is empty or Technology table is empty

            # Check for 'input_file' table
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='input_file'")
            if not cur.fetchone():
                # 'input_file' table doesn't exist, assume not overwritten by this script's logic
                return False

            # 'input_file' table exists, check the stored filename
            cur.execute("SELECT file FROM input_file WHERE id = '1'")  # Assuming id is text '1'
            row = cur.fetchone()
            if not row:
                # No record with id='1' in input_file table
                return False  # Or True, depending on desired behavior for this edge case

            tagged_file_in_db = row[0].replace('"', '')  # Remove quotes if any

            # Construct the expected DAT filename from inp_dat_file_str
            # Original logic: inp_dat_file.split('.')[0] + '.dat'
            base_name_of_input_dat = Path(inp_dat_file_str).name.split('.')[0]
            expected_dat_filename = f'{base_name_of_input_dat}.dat'

            return tagged_file_in_db != expected_dat_filename

    except sqlite3.Error:
        # If DB connection or query fails, assume not overwritten or handle error
        return False
    except Exception:  # Catch other potential errors during path manipulation
        return False


def main():
    """Main function to parse arguments and call appropriate getters."""
    parser = argparse.ArgumentParser(
        description='Extracts information (commodities, technologies, scenarios, or periods) '
        'from specified input files (database or DAT text files).',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '-i',
        '--input',
        required=True,
        help='Input filename. \nSupported DB extensions: .db, .sqlite, .sqlite3, .sqlitedb'
        '\nSupported DAT/text extensions: .dat, .txt',
    )

    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '-c',
        '--comm',
        action='store_true',
        help='Get a dictionary of commodities.',
    )
    action_group.add_argument(
        '-t',
        '--tech',
        action='store_true',
        help='Get a dictionary of technologies.',
    )
    action_group.add_argument(
        '-s',
        '--scenario',
        action='store_true',
        help='Get a dictionary of scenarios (requires DB input).',
    )
    action_group.add_argument(
        '-p',
        '--period',
        action='store_true',
        help='Get a dictionary of time periods (requires DB input).',
    )

    args = parser.parse_args()
    input_file = Path(args.input)

    try:
        file_type, input_file_str = get_file_type_info(input_file)
        is_dat = file_type == 'dat'

        result: Union[Dict[Any, Any], None] = None

        if args.comm:
            result = get_comm(input_file_str, is_dat)
        elif args.tech:
            result = get_tech(input_file_str, is_dat)
        elif args.scenario:
            if is_dat:
                raise ScriptError(
                    'Scenarios can only be extracted from a database file. '
                    f'Received DAT file: {input_file}'
                )
            result = get_scenario(input_file_str)
        elif args.period:
            if is_dat:
                raise ScriptError(
                    'Time periods can only be extracted from a database file. '
                    f'Received DAT file: {input_file}'
                )
            result = get_tperiods(input_file_str)

        if result is not None:
            print(result)

    except FileNotFoundError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
    except ValueError as e:  # Catches unrecognized file types or invalid operations
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(2)  # Usage error
    except ScriptError as e:
        print(f'Script Error: {e}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'An unexpected error occurred: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
