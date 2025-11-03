from pathlib import Path

from typer.testing import CliRunner

from temoa.cli import app

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


def test_cli_version():
    """Test the `temoa --version` command."""
    result = runner.invoke(app, ['--version'])
    assert result.exit_code == 0
    assert 'Temoa Version' in result.stdout


def test_cli_run_command_success_silent(tmp_path):
    """Test a successful silent run of the `temoa run` command."""
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_test_config(tmp_path, db_path)
    args = ['run', str(test_config_path), '--output', str(tmp_path), '--silent']
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'CLI crashed with error: {result.exception}'
    assert 'Temoa run completed successfully' not in result.stdout
    assert (tmp_path / 'temoa-run.log').exists()


def test_cli_run_build_only_silent(tmp_path):
    """Test the `temoa run --build-only --silent` flags."""
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_test_config(tmp_path, db_path)
    args = ['run', str(test_config_path), '--output', str(tmp_path), '--build-only', '--silent']
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'CLI crashed with error: {result.exception}'
    assert 'Model built successfully' not in result.stdout
    assert (tmp_path / 'temoa-run.log').exists()


# =============================================================================
# Tests for the `validate` command
# =============================================================================


def test_cli_validate_success_verbose(tmp_path):
    """Test a successful verbose run of the `temoa validate` command."""
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_test_config(tmp_path, db_path)
    args = ['validate', str(test_config_path), '--output', str(tmp_path)]
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'CLI crashed with error: {result.exception}'
    assert 'Validation successful' in result.stdout
    assert (tmp_path / 'temoa-run.log').exists()


def test_cli_validate_success_silent(tmp_path):
    """Test a successful silent run of the `temoa validate` command."""
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_test_config(tmp_path, db_path)
    args = ['validate', str(test_config_path), '--output', str(tmp_path), '--silent']
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'CLI crashed with error: {result.exception}'
    assert 'Validation successful' not in result.stdout
    assert (tmp_path / 'temoa-run.log').exists()


def test_cli_validate_failure_on_invalid_db(tmp_path):
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


def test_cli_run_missing_config():
    """Test graceful failure for a missing config file."""
    args = ['run', 'non_existent_file.toml']
    result = runner.invoke(app, args)

    assert result.exit_code != 0
    # Check that the error mentions the missing file (more robust than exact string match)
    assert 'non_existent_file.toml' in result.stderr
    assert 'does not' in result.stderr and 'exist' in result.stderr
