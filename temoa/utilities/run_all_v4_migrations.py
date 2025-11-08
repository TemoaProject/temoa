#!/usr/bin/env python3
"""
run_all_v4_migrations.py

Iterates over all .sql files in a specified directory, runs the v3.1 to v4
SQL migration script on each, and overwrites the original file if successful.
Includes basic error handling to restore original files on failure.

Usage:
  python run_all_migrations.py --input_dir /path/to/your/sql_files \
                               --migration_script ./sql_migration_v_3_1_to_v4.py \
                               --v4_schema_path ./temoa_schema_v4.sql
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(
    cmd: list[str], cwd: Path | None = None, capture_output: bool = True
) -> subprocess.CompletedProcess:
    """Helper to run shell commands."""
    print(f'Executing: {" ".join(cmd)}')
    result = subprocess.run(cmd, cwd=cwd, capture_output=capture_output, text=True, check=False)
    if result.returncode != 0 and capture_output:
        print(f'COMMAND FAILED (exit code {result.returncode}):')
        print('STDOUT:\n', result.stdout)
        print('STDERR:\n', result.stderr)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Run SQL migration on all .sql files in a directory, overwriting originals.'
    )
    parser.add_argument(
        '--input_dir',
        required=True,
        type=Path,
        help='Directory containing the .sql files to migrate.',
    )
    parser.add_argument(
        '--migration_script',
        required=True,
        type=Path,
        help='Path to the sql_migration_v_3_1_to_v4.py script.',
    )
    parser.add_argument(
        '--v4_schema_path',
        required=True,
        type=Path,
        help='Path to the canonical v4 schema SQL file (temoa_schema_v4.sql).',
    )
    parser.add_argument(
        '--dry_run',
        action='store_true',
        help='Perform a dry run: show which files would be processed, but do not modify.',
    )

    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    migration_script = args.migration_script.resolve()
    v4_schema_path = args.v4_schema_path.resolve()

    if not input_dir.is_dir():
        print(f'Error: Input directory not found at {input_dir}')
        sys.exit(1)
    if not migration_script.is_file():
        print(f'Error: Migration script not found at {migration_script}')
        sys.exit(1)
    if not v4_schema_path.is_file():
        print(f'Error: V4 schema file not found at {v4_schema_path}')
        sys.exit(1)

    print(f'Scanning for .sql files in: {input_dir}')
    sql_files = list(input_dir.glob('*.sql'))

    if not sql_files:
        print(f'No .sql files found in {input_dir}. Exiting.')
        sys.exit(0)

    if args.dry_run:
        print('\n--- Dry Run ---')
        print(f'The following {len(sql_files)} .sql files would be processed:')
        for f in sql_files:
            print(f'  - {f.name}')
        print('\nNo files will be modified in dry run mode.')
        sys.exit(0)

    print(f'\n--- Starting Migration of {len(sql_files)} files ---')
    processed_count = 0
    failed_files = []

    for sql_file in sql_files:
        print(f'\nProcessing: {sql_file.name}')

        temp_output_file = Path(tempfile.mkstemp(suffix='.sql', prefix='temp_migrated_')[1])
        original_backup_file = Path(tempfile.mkstemp(suffix='.bak', prefix='orig_backup_')[1])

        try:
            # 1. Back up original file (to restore on failure)
            shutil.copy2(sql_file, original_backup_file)

            # 2. Run migration script, outputting to a temporary file
            migration_cmd = [
                'python3',
                str(migration_script),
                '--input',
                str(sql_file),
                '--schema',
                str(v4_schema_path),
                '--output',
                str(temp_output_file),
            ]
            result = run_command(migration_cmd, cwd=Path.cwd())

            if result.returncode == 0:
                # 3. If successful, overwrite original file with converted content
                shutil.copy2(temp_output_file, sql_file)
                print(f'SUCCESS: {sql_file.name} migrated and overwritten.')
                processed_count += 1
            else:
                # 4. On failure, restore original file
                print(f'FAILED: Migration for {sql_file.name} failed. Restoring original file.')
                shutil.copy2(original_backup_file, sql_file)
                failed_files.append(sql_file.name)

        except Exception as e:
            print(f'CRITICAL ERROR processing {sql_file.name}: {e}. Restoring original file.')
            if original_backup_file.exists():
                shutil.copy2(original_backup_file, sql_file)
            failed_files.append(sql_file.name)
        finally:
            # Clean up temporary files
            if temp_output_file.exists():
                os.remove(temp_output_file)
            if original_backup_file.exists():
                os.remove(original_backup_file)

    print('\n--- Migration Summary ---')
    print(f'Total files processed: {processed_count}')
    if failed_files:
        print(f'FAILED files: {", ".join(failed_files)}')
        sys.exit(1)
    else:
        print('All files migrated successfully.')
        sys.exit(0)


if __name__ == '__main__':
    main()
