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
    cmd: list[str], cwd: Path | None = None, capture_output: bool = True, silent: bool = False
) -> subprocess.CompletedProcess[str]:
    """Helper to run shell commands."""
    if not silent:
        print(f'Executing: {" ".join(cmd)}')
    result = subprocess.run(cmd, cwd=cwd, capture_output=capture_output, text=True, check=False)
    if not silent and result.returncode != 0 and capture_output:
        print(f'COMMAND FAILED (exit code {result.returncode}):')
        print('STDOUT:\n', result.stdout)
        print('STDERR:\n', result.stderr)
    return result


def run_migrations(
    input_dir: Path, migration_script: Path, schema_path: Path, dry_run: bool = False, silent: bool = False
) -> None:
    if not input_dir.is_dir():
        raise FileNotFoundError(f'Error: Input directory not found at {input_dir}')
    if not migration_script.is_file():
        raise FileNotFoundError(f'Error: Migration script not found at {migration_script}')
    if not schema_path.is_file():
        raise FileNotFoundError(f'Error: schema file not found at {schema_path}')

    if not silent:
        print(f'Scanning for .sql and .sqlite files in: {input_dir}')
    sql_files = list(input_dir.glob('*.sql'))
    db_files = list(input_dir.glob('*.sqlite')) + list(input_dir.glob('*.db'))
    all_files = sql_files + db_files

    if not all_files:
        if not silent:
            print(f'No .sql, .sqlite, or .db files found in {input_dir}. Exiting.')
        return

    if dry_run:
        if not silent:
            print('\n--- Dry Run ---')
            print(f'The following {len(all_files)} files would be processed:')
            for f in all_files:
                print(f'  - {f.name}')
            print('\nNo files will be modified in dry run mode.')
        return

    if not silent:
        print(f'\n--- Starting Migration of {len(all_files)} files ---')
    processed_count = 0
    failed_files = []

    for target_file in all_files:
        if not silent:
            print(f'\nProcessing: {target_file.name}')

        ext = target_file.suffix.lower()
        fd1, path1 = tempfile.mkstemp(suffix=ext, prefix='temp_migrated_')
        os.close(fd1)
        temp_output_file = Path(path1)

        fd2, path2 = tempfile.mkstemp(suffix='.bak', prefix='orig_backup_')
        os.close(fd2)
        original_backup_file = Path(path2)

        mig_type = 'sql' if ext == '.sql' else 'db'

        try:
            # 1. Back up original file
            shutil.copy2(target_file, original_backup_file)

            # 2. Run migration script, outputting to a temporary file
            migration_cmd = [
                sys.executable,
                str(migration_script),
                '--input',
                str(target_file),
                '--schema',
                str(schema_path),
                '--output',
                str(temp_output_file),
                '--type',
                mig_type,
            ]
            result = run_command(migration_cmd, cwd=Path.cwd(), silent=silent)

            if result.returncode == 0:
                # 3. If successful, overwrite original file
                shutil.copy2(temp_output_file, target_file)
                if not silent:
                    print(f'SUCCESS: {target_file.name} migrated and overwritten.')
                processed_count += 1
            else:
                # 4. On failure, restore original file
                if not silent:
                    print(f'FAILED: Migration for {target_file.name} failed. Restoring original file.')
                shutil.copy2(original_backup_file, target_file)
                failed_files.append(target_file.name)

        except Exception as e:
            if not silent:
                print(f'CRITICAL ERROR processing {target_file.name}: {e}. Restoring original file.')
            if original_backup_file.exists():
                shutil.copy2(original_backup_file, target_file)
            failed_files.append(target_file.name)
        finally:
            if temp_output_file.exists():
                os.remove(temp_output_file)
            if original_backup_file.exists():
                os.remove(original_backup_file)

    if not silent:
        print('\n--- Migration Summary ---')
        print(f'Total files processed: {processed_count}')
    if failed_files:
        raise RuntimeError(f'FAILED files: {", ".join(failed_files)}')

    if not silent:
        print('All files migrated successfully.')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Run script migration on all .sql/.sqlite/.db files in a directory, overwriting originals.'
    )
    parser.add_argument(
        '--input_dir',
        required=True,
        type=Path,
        help='Directory containing the files to migrate.',
    )
    parser.add_argument(
        '--migration_script',
        required=True,
        type=Path,
        help='Path to the master_migration.py script.',
    )
    parser.add_argument(
        '--v4_schema_path',
        required=True,
        type=Path,
        help='Path to the canonical v4 schema SQL file.',
    )
    parser.add_argument(
        '--dry_run',
        action='store_true',
        help='Perform a dry run: show which files would be processed, but do not modify.',
    )

    args = parser.parse_args()

    run_migrations(
        input_dir=args.input_dir.resolve(),
        migration_script=args.migration_script.resolve(),
        schema_path=args.v4_schema_path.resolve(),
        dry_run=args.dry_run,
    )


if __name__ == '__main__':
    main()
