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

    placeholder = 'path = "tests/testing_outputs/utopia.sqlite"'
    replacement = f'path = "{db_path.as_posix()}"'

    config_content = template_content.replace(placeholder, replacement)

    test_config_path = tmp_path / 'test_config.toml'
    test_config_path.write_text(config_content)

    return test_config_path


def test_cli_version():
    """Test the `temoa --version` command."""
    result = runner.invoke(app, ['--version'])
    assert result.exit_code == 0
    assert 'Temoa Version' in result.stdout


def test_cli_run_command_success(tmp_path):
    """Test a successful run by creating a self-contained config."""
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_test_config(tmp_path, db_path)

    args = ['run', str(test_config_path), '--output', str(tmp_path), '--silent']
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'CLI crashed with error: {result.exception}'
    assert 'Temoa run completed successfully' in result.stdout
    assert (tmp_path / 'temoa-run.log').exists()


def test_cli_run_build_only(tmp_path):
    """Test the --build-only flag with a self-contained config."""
    db_path = Path(__file__).parent / 'testing_outputs' / 'utopia.sqlite'
    test_config_path = create_test_config(tmp_path, db_path)

    args = ['run', str(test_config_path), '--output', str(tmp_path), '--build-only', '--silent']
    result = runner.invoke(app, args)

    assert result.exit_code == 0, f'CLI crashed with error: {result.exception}'
    assert 'Model built successfully' in result.stdout


def test_cli_run_missing_config():
    """Test graceful failure for a missing config file."""
    args = ['run', 'non_existent_file.toml']
    result = runner.invoke(app, args)

    assert result.exit_code != 0

    # Normalize the stderr string to be immune to rich's word wrapping
    # by removing formatting characters and collapsing whitespace.
    cleaned_stderr = ' '.join(result.stderr.replace('│', '').split())

    # Now, check for the logical error message in the cleaned string.
    assert (
        "Invalid value for 'CONFIG_FILE': File 'non_existent_file.toml' does not exist."
        in cleaned_stderr
    )
