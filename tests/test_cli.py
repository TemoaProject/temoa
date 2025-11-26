import re
import shutil
import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from temoa.cli import _is_writable, app

runner = CliRunner()

# Path to the configuration file template we will use for tests.
TESTING_CONFIGS_DIR = Path(__file__).parent / 'testing_configs'
UTOPIA_CONFIG_TEMPLATE = TESTING_CONFIGS_DIR / 'config_utopia.toml'


def create_test_config(tmp_path: Path, db_path: Path) -> Path:
    """
    Reads the config template, replaces a placeholder path with the correct
    test database path, and writes a new, runnable config file.
    """
    template_content = UTOPIA_CONFIG_TEMPLATE.read_text()
    # NOTE: This placeholder is specific to the `config_utopia.toml` file.
    placeholder = 'input_database = "tests/testing_outputs/utopia.sqlite"'
    replacement = f'input_database = "{db_path.as_posix()}"'
    config_content = template_content.replace(placeholder, replacement)
    test_config_path = tmp_path / 'test_config.toml'
    test_config_path.write_text(config_content)
    return test_config_path


def create_config_with_solver(tmp_path: Path, db_path: Path, solver_name: str) -> Path:
    """
    Creates a test config file that points to a specific solver.
    """
    test_config_path = create_test_config(tmp_path, db_path)
    config_content = test_config_path.read_text()
    if re.search(r'^\s*solver_name\s*=', config_content, re.MULTILINE):
        config_content = re.sub(
            r'^\s*solver_name\s*=\s*".*?"',
            f'solver_name = "{solver_name}"',
            config_content,
            flags=re.MULTILINE,
        )
    else:
        # Add to the end if not found
        config_content += f'\nsolver_name = "{solver_name}"\n'

    test_config_path.write_text(config_content)
    return test_config_path


def test_cli_version() -> None:
    """Test the `temoa --version` command."""
    result = runner.invoke(app, ['--version'])
    assert result.exit_code == 0
    assert 'Temoa Version' in result.stdout


def test_cli_run_command_success_silent(tmp_path: Path) -> None:
    """Test a successful silent run of the `temoa run` command."""
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_test_config(tmp_path, db_path)
    # --output is explicitly given, so it should use tmp_path
    args = ['run', str(test_config_path), '--output', str(tmp_path), '--silent']
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'CLI crashed with error: {result.exception}'
    assert 'Temoa run completed successfully' not in result.stdout  # Silent run
    assert (tmp_path / 'temoa-run.log').exists()


def test_cli_run_build_only_silent(tmp_path: Path) -> None:
    """Test the `temoa run --build-only --silent` flags."""
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_test_config(tmp_path, db_path)
    # --output is explicitly given, so it should use tmp_path
    args = ['run', str(test_config_path), '--output', str(tmp_path), '--build-only', '--silent']
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'CLI crashed with error: {result.exception}'
    assert 'Model built successfully' not in result.stdout  # Silent run
    assert (tmp_path / 'temoa-run.log').exists()


# =============================================================================
# Tests for the `validate` command
# =============================================================================


def test_cli_validate_success_verbose(tmp_path: Path) -> None:
    """Test a successful verbose run of the `temoa validate` command."""
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_test_config(tmp_path, db_path)
    args = ['validate', str(test_config_path), '--output', str(tmp_path)]
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'CLI crashed with error: {result.exception}'
    assert 'Validation successful' in result.stdout
    assert (tmp_path / 'temoa-run.log').exists()


def test_cli_validate_success_silent(tmp_path: Path) -> None:
    """Test a successful silent run of the `temoa validate` command."""
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_test_config(tmp_path, db_path)
    args = ['validate', str(test_config_path), '--output', str(tmp_path), '--silent']
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'CLI crashed with error: {result.exception}'
    assert 'Validation successful' not in result.stdout
    assert (tmp_path / 'temoa-run.log').exists()


def test_cli_validate_failure_on_invalid_db(tmp_path: Path) -> None:
    """Test a failing run of `temoa validate` with an invalid database."""
    # Create a file that is not a valid Temoa database (an empty file).
    # This will cause the version check inside the sequencer to fail.
    invalid_db_path = tmp_path / 'invalid.sqlite'
    invalid_db_path.touch()

    # Create a valid config file that points to this invalid database.
    test_config_path = create_test_config(tmp_path, invalid_db_path)

    args = ['validate', str(test_config_path), '--output', str(tmp_path)]
    result = runner.invoke(app, args)

    assert result.exit_code != 0, 'CLI should exit with a non-zero code on failure'
    assert 'Validation failed' in result.stdout
    # Check that the log was still created, containing the detailed error
    assert (tmp_path / 'temoa-run.log').exists()


def test_cli_run_missing_config() -> None:
    """Test graceful failure for a missing config file."""
    args = ['run', 'non_existent_file.toml']
    result = runner.invoke(app, args)

    assert result.exit_code != 0
    # Check that the error mentions the missing file (more robust than exact string match)
    assert 'non_existent_file.toml' in result.stderr


# =============================================================================
# Tests for the `migrate` command
# =============================================================================


def test_cli_migrate_help() -> None:
    """Test the `temoa migrate --help` command."""
    result = runner.invoke(app, ['migrate', '--help'])
    assert result.exit_code == 0
    assert 'migrate' in result.stdout
    assert 'Migrate a single Temoa database file' in result.stdout


def test_cli_migrate_sql_file(tmp_path: Path) -> None:
    """Test migrating a SQL file with explicit --output."""
    # Ensure input file is available in the test environment (e.g., copied from data_files)
    input_file_src = Path(__file__).parent.parent / 'data_files' / 'temoa_basics_0.sql'
    input_file = tmp_path / 'test_input.sql'
    shutil.copy2(input_file_src, input_file)

    output_file = tmp_path / 'migrated_explicit.sql'
    args = ['migrate', str(input_file), '--output', str(output_file)]
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'Migration failed: {result.exception}\n{result.stderr}'
    assert 'SQL dump migration completed' in result.stdout
    assert output_file.exists()


def test_cli_migrate_rejects_directory_input(tmp_path: Path) -> None:
    """Test that the migrate command rejects a directory as input."""
    dummy_dir = tmp_path / 'my_dummy_dir'
    dummy_dir.mkdir()
    args = ['migrate', str(dummy_dir)]
    result = runner.invoke(app, args)

    assert result.exit_code != 0
    # Normalize whitespace to handle platform-specific line breaks from rich.print()
    normalized_output = ' '.join(result.stdout.split())
    assert 'Error: Input path must be a file, not a directory:' in normalized_output
    # Check for the directory name in the original output (paths may be split across lines)
    assert 'my_dummy_dir' in result.stdout


def test_cli_migrate_sql_file_auto_output_writable_input_dir(tmp_path: Path) -> None:
    """
    Test migrating a SQL file without --output,
    where the input directory is writable.
    Output should be next to input with _v4.sql suffix.
    """
    src_file = Path(__file__).parent.parent / 'data_files' / 'temoa_basics_0.sql'
    input_file = tmp_path / src_file.name  # Input file in writable tmp_path
    shutil.copy2(src_file, input_file)

    args = ['migrate', str(input_file)]
    result = runner.invoke(app, args)

    assert result.exit_code == 0, (
        f'Migration failed: {result.exception}\n{result.stderr}\n{result.stdout}'
    )
    assert 'SQL dump migration completed' in result.stdout
    expected_output = input_file.with_stem(input_file.stem + '_v4').with_suffix(
        '.sql'
    )  # Explicit .sql suffix
    assert expected_output.exists()


def test_cli_migrate_sql_file_auto_output_non_writable_input_dir_fallback_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test migrating a SQL file without --output,
    where the input directory is NOT writable.
    Output should fall back to current working directory (mocked as tmp_path)
    and have a _v4.sql suffix.
    """
    non_writable_mock_parent = tmp_path / 'mock_non_writable_input_parent'
    non_writable_mock_parent.mkdir()

    src_file = Path(__file__).parent.parent / 'data_files' / 'temoa_basics_0.sql'
    input_file = non_writable_mock_parent / src_file.name
    shutil.copy2(src_file, input_file)

    def mock_is_writable(path: Path) -> bool:
        if path == non_writable_mock_parent:
            return False
        if path == tmp_path:  # CWD for the test runner is tmp_path
            return True
        return _is_writable(path)

    monkeypatch.setattr('temoa.cli._is_writable', mock_is_writable)
    monkeypatch.setattr(
        Path,
        'cwd',
        classmethod(lambda cls: tmp_path),
    )  # Ensure CWD is tmp_path for logging

    args = ['migrate', str(input_file)]
    result = runner.invoke(app, args, catch_exceptions=False)

    assert result.exit_code == 0, (
        f'Migration failed: {result.exception}\n{result.stderr}\n{result.stdout}'
    )
    # Normalize whitespace to handle platform-specific line breaks from rich.print()
    normalized_output = ' '.join(result.stdout.split())
    assert 'SQL dump migration completed' in normalized_output
    assert 'Warning: Input directory' in normalized_output
    assert str(non_writable_mock_parent) in normalized_output
    assert 'is not writable.' in normalized_output
    assert 'Saving output to current directory:' in normalized_output
    assert str(tmp_path) in normalized_output

    expected_output_in_cwd = tmp_path / (input_file.stem + '_v4.sql')
    assert expected_output_in_cwd.exists()
    assert not (non_writable_mock_parent / (input_file.stem + '_v4.sql')).exists()


def test_cli_migrate_sql_file_auto_output_no_writable_location(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test migrating a SQL file without --output,
    where neither the input directory nor the CWD are writable.
    Should exit with an error.
    """
    non_writable_mock_parent = tmp_path / 'mock_non_writable_input_parent_no_cwd'
    non_writable_mock_parent.mkdir()

    src_file = Path(__file__).parent.parent / 'data_files' / 'temoa_basics_0.sql'
    input_file = non_writable_mock_parent / src_file.name
    shutil.copy2(src_file, input_file)

    # Mock _is_writable to return False for both the input directory and the CWD (tmp_path)
    def mock_is_writable_always_false(_path: Path) -> bool:
        return False

    monkeypatch.setattr('temoa.cli._is_writable', mock_is_writable_always_false)

    args = ['migrate', str(input_file)]
    result = runner.invoke(app, args, catch_exceptions=False)

    assert result.exit_code != 0, 'Migration should fail with a non-zero exit code'
    # Normalize whitespace to handle platform-specific line breaks from rich.print()
    normalized_output = ' '.join(result.stdout.split())
    assert 'Error: Neither input directory' in normalized_output
    assert 'nor current working directory' in normalized_output
    assert 'are writable.' in normalized_output
    assert not (
        tmp_path / (input_file.stem + '_v4' + input_file.suffix)
    ).exists()  # No output created


def test_cli_migrate_invalid_file() -> None:
    """Test migrating a non-existent file."""
    args = ['migrate', 'non_existent.sql']
    result = runner.invoke(app, args)

    assert result.exit_code != 0
    # Typer handles file existence check, so error is in stderr
    assert 'does not exist' in result.stderr or 'does not exist' in str(result.exception)


def test_cli_migrate_unknown_type(tmp_path: Path) -> None:
    """Test migrating a file with unknown extension."""
    unknown_file = tmp_path / 'unknown.txt'
    unknown_file.write_text('dummy')
    args = ['migrate', str(unknown_file)]
    result = runner.invoke(app, args)

    assert result.exit_code != 0
    assert 'Cannot determine migration type' in result.stdout


def test_cli_migrate_override_type(tmp_path: Path) -> None:
    """Test migrating with explicit type override."""
    input_file_src = Path(__file__).parent.parent / 'data_files' / 'temoa_basics_0.sql'
    input_file = tmp_path / 'test_input_override.sql'
    shutil.copy2(input_file_src, input_file)

    output_file = tmp_path / 'migrated_override.sql'
    args = ['migrate', str(input_file), '--output', str(output_file), '--type', 'sql']
    result = runner.invoke(app, args)

    assert result.exit_code == 0
    assert 'SQL dump migration completed' in result.stdout
    assert output_file.exists()


def test_cli_migrate_sql_file_silent(tmp_path: Path) -> None:
    """Test migrating a SQL file with --silent flag."""
    input_file_src = Path(__file__).parent.parent / 'data_files' / 'temoa_basics_0.sql'
    input_file = tmp_path / 'test_input_silent.sql'
    shutil.copy2(input_file_src, input_file)

    output_file = tmp_path / 'migrated_silent.sql'
    args = ['migrate', str(input_file), '--output', str(output_file), '--silent']  # Use --silent
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'Migration failed: {result.exception}\n{result.stderr}'
    # In silent mode, success messages should NOT be in stdout
    assert 'SQL dump migration completed' not in result.stdout
    assert output_file.exists()


def test_cli_migrate_db_file_silent(tmp_path: Path) -> None:
    """Test migrating a DB file with --silent flag."""
    input_file = tmp_path / 'test_v3_1_silent.sqlite'
    conn = sqlite3.connect(input_file)
    conn.execute('CREATE TABLE MetaData (name TEXT, value TEXT)')
    conn.execute("INSERT INTO MetaData VALUES ('DB_MAJOR', '3')")
    conn.commit()
    conn.close()

    output_file = tmp_path / 'migrated_silent.sqlite'
    args = ['migrate', str(input_file), '--output', str(output_file), '--silent']  # Use --silent
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'Migration failed: {result.exception}\n{result.stderr}'
    # In silent mode, success messages should NOT be in stdout
    assert 'Database migration completed' not in result.stdout
    assert output_file.exists()


def test_cli_migrate_sql_file_auto_output_non_writable_input_dir_fallback_cwd_silent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test migrating a SQL file with --silent, where input dir is not writable.
    Output should fall back to CWD, and the warning should NOT be printed.
    """
    non_writable_mock_parent = tmp_path / 'mock_non_writable_input_parent_silent'
    non_writable_mock_parent.mkdir()

    src_file = Path(__file__).parent.parent / 'data_files' / 'temoa_basics_0.sql'
    input_file = non_writable_mock_parent / src_file.name
    shutil.copy2(src_file, input_file)

    def mock_is_writable(path: Path) -> bool:
        if path == non_writable_mock_parent:
            return False
        if path == tmp_path:
            return True
        return _is_writable(path)

    monkeypatch.setattr('temoa.cli._is_writable', mock_is_writable)
    monkeypatch.setattr(
        Path,
        'cwd',
        classmethod(lambda cls: tmp_path),
    )

    args = ['migrate', str(input_file), '--silent']  # Use --silent here
    result = runner.invoke(app, args, catch_exceptions=False)

    assert result.exit_code == 0, (
        f'Migration failed: {result.exception}\n{result.stderr}\n{result.stdout}'
    )
    assert 'SQL dump migration completed' not in result.stdout  # Should be silent
    assert 'Warning: Input directory' not in result.stdout  # Warning should be silent

    expected_output_in_cwd = tmp_path / (input_file.stem + '_v4.sql')
    assert expected_output_in_cwd.exists()
    assert not (non_writable_mock_parent / (input_file.stem + '_v4.sql')).exists()


def test_cli_validate_fails_if_solver_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test that the validate command fails with SolverNotAvailableError if the configured solver is
    missing.
    """
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_config_with_solver(tmp_path, db_path, 'nonexistent_solver')

    # Mock shutil.which to always return None for any solver check
    monkeypatch.setattr(shutil, 'which', lambda _: None)

    args = ['validate', str(test_config_path), '--output', str(tmp_path)]
    result = runner.invoke(app, args, catch_exceptions=False)

    assert result.exit_code != 0, (
        f'Validate should have failed: {result.exception}\n{result.stderr}\n{result.stdout}'
    )
    assert isinstance(result.exception, SystemExit)
    assert result.exception.code == 1
    assert '❌ Validation failed:' in result.stdout
    assert 'nonexistent_solver' in result.stdout
    # Use the more robust phrase for checking installation instructions
    assert 'Please ensure the solver is installed and accessible.' in result.stdout
    assert (tmp_path / 'temoa-run.log').exists()


def test_cli_run_fails_if_solver_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test that the run command fails with SolverNotAvailableError if the configured solver is
    missing.
    """
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_config_with_solver(tmp_path, db_path, 'another_nonexistent_solver')

    # Mock shutil.which to always return None for any solver check
    monkeypatch.setattr(shutil, 'which', lambda _: None)

    args = ['run', str(test_config_path), '--output', str(tmp_path)]
    result = runner.invoke(app, args, catch_exceptions=False)

    assert result.exit_code != 0, (
        f'Run should have failed: {result.exception}\n{result.stderr}\n{result.stdout}'
    )
    assert isinstance(result.exception, SystemExit)
    assert result.exception.code == 1
    assert '❌ An error occurred:' in result.stdout
    assert 'another_nonexistent_solver' in result.stdout
    # Use the more robust phrase for checking installation instructions
    assert 'Please ensure the solver is installed and accessible.' in result.stdout
    assert (tmp_path / 'temoa-run.log').exists()
