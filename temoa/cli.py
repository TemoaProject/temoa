import argparse
import logging
import shutil
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path
from typing import Annotated

import rich
import tomlkit
import typer
from rich.logging import RichHandler
from rich.text import Text

from temoa.__about__ import __version__
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode
from temoa.utilities import db_migration_v3_1_to_v4, sql_migration_v3_1_to_v4

# =============================================================================
# Logging & Helper Setup
# =============================================================================
logger = logging.getLogger(__name__)


def _create_output_folder() -> Path:
    """Create a default time-stamped folder for outputs."""
    output_path = Path('output_files', datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def _setup_logging(output_path: Path, debug: bool = False, silent: bool = False) -> None:
    """Set up logging with different levels for console and file."""
    # The root logger should be set to the most verbose level required by any handler.
    # The file handler will always be more verbose than the console in silent mode.
    root_level = logging.DEBUG if debug else logging.INFO

    # Determine console level based on flags. `debug` takes precedence.
    if debug:
        console_level = logging.DEBUG
    elif silent:
        console_level = logging.WARNING
    else:
        console_level = logging.INFO

    # Configure the rich handler for the console
    rich_handler = RichHandler(
        level=console_level,
        rich_tracebacks=True,
        show_path=False,
        show_time=True,
        log_time_format='[%X]',
    )

    # Configure the file handler (always verbose)
    log_file = output_path / 'temoa-run.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(root_level)
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            '%Y-%m-%d %H:%M:%S',
        )
    )

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(root_level)
    root_logger.handlers = [file_handler, rich_handler]

    # Silence other overly verbose libraries
    logging.getLogger('pyomo').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    # Log the initialization message (will go to file, and to console if not silent)
    logger.info('Logging initialized. Log file at: %s', log_file)


def _setup_sequencer(
    config_file: Path,
    output_path: Path | None,
    silent: bool,
    debug: bool,
    mode_override: TemoaMode | None = None,
) -> tuple[TemoaSequencer, Path]:
    """Handles the common setup logic for creating and configuring the sequencer."""
    final_output_path = output_path if output_path else _create_output_folder()
    final_output_path.mkdir(parents=True, exist_ok=True)

    # Pass the silent flag to the logging setup
    _setup_logging(final_output_path, debug=debug, silent=silent)

    config = TemoaConfig.build_config(
        config_file=config_file, output_path=final_output_path, silent=silent
    )
    sequencer = TemoaSequencer(config=config, mode_override=mode_override)
    return sequencer, final_output_path


# =============================================================================
# Callbacks and Typer App Setup
# =============================================================================
def _version_callback(value: bool) -> None:
    if value:
        version = __version__
        rich.print(f'Temoa Version: [bold green]{version}[/bold green]')
        raise typer.Exit()


def _cite_callback(value: bool) -> None:
    if value:
        citation_text = Text()
        citation_text.append(
            'If you use Temoa in your research, please cite the following publication:\n\n'
        )

        citation_text.append(
            """Hunter, K., Sreepathi, S., & DeCarolis, J. F. (2013). """
            """Modeling for insight using Tools for Energy Model Optimization and Analysis """
            """(Temoa). """
            """Energy Economics, 40, 339-349. """
            """https://doi.org/10.1016/j.eneco.2013.07.014""",
            style='italic',
        )
        citation_text.append('\n\n')
        citation_text.append(
            'You can also find citation information in the CITATION.cff file in the repository.',
            style='dim',
        )

        rich.print(citation_text)
        raise typer.Exit()


def get_default_schema() -> Path:
    """Get the default path to the v4 schema file, handling both installed and development cases."""
    try:
        schema_path = resources.files('temoa.db_schema') / 'temoa_schema_v4.sql'

        if not schema_path.is_file():
            raise FileNotFoundError(
                f'Schema file not found at expected resource path: {schema_path}'
            )
        return Path(str(schema_path))  # Convert Traversable to concrete Path
    except Exception as e:
        logger.exception('Failed to load schema from resources')
        # The fallback for development needs to reflect the current repository structure
        # assuming `cli.py` is in `temoa/` and `db_schema/` is a sibling of `cli.py` within
        # `temoa/`.
        fallback_path = Path(__file__).parent / 'db_schema' / 'temoa_schema_v4.sql'
        if fallback_path.is_file():
            logger.warning(
                'Using fallback schema path: %s. '
                'This might indicate an issue with package installation or resource setup.',
                fallback_path,
            )
            return fallback_path
        else:
            raise FileNotFoundError(
                f'Schema file not found using resource system or fallback at {fallback_path}'
            ) from e


app = typer.Typer(
    name='temoa',
    help='The Temoa Project: Tools for Energy Model Optimization and Analysis.',
    rich_markup_mode='markdown',
    no_args_is_help=True,
    context_settings={'help_option_names': ['-h', '--help']},
)


# =============================================================================
# CLI Commands
# =============================================================================
@app.command()
def validate(
    config_file: Annotated[
        Path,
        typer.Argument(
            help='Path to the configuration file to validate.',
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    output_path: Annotated[
        Path | None,
        typer.Option('--output', '-o', help='Directory to save validation log.'),
    ] = None,
    silent: Annotated[
        bool, typer.Option('--silent', '-q', help='Suppress informational output on success.')
    ] = False,
    debug: Annotated[
        bool, typer.Option('--debug', '-d', help='Enable debug-level logging.')
    ] = False,
) -> None:
    """
    Validates a configuration file and database by building the model instance without solving it.
    """
    if not silent:
        rich.print(f'Validating configuration: [cyan]{config_file}[/cyan]')
    try:
        ts, final_output_path = _setup_sequencer(
            config_file=config_file,
            output_path=output_path,
            silent=True,  # Sequencer is always non-interactive for validation
            debug=debug,
            mode_override=TemoaMode.BUILD_ONLY,
        )
        _ = ts.build_model()
        if not silent:
            rich.print('\n[bold green]✅ Validation successful.[/bold green]')
            rich.print('The model can be built from the provided configuration.')
            rich.print(f'Log file is available in: [cyan]{final_output_path}[/cyan]')
    except Exception as e:
        logger.exception('An error occurred during validation.')
        rich.print(f'\n[bold red]❌ Validation failed:[/bold red] {e}')
        raise typer.Exit(code=1) from e


@app.command()
def run(
    config_file: Annotated[
        Path,
        typer.Argument(
            help='Path to the model configuration file.',
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    output_path: Annotated[
        Path | None,
        typer.Option('--output', '-o', help='Directory to save outputs.'),
    ] = None,
    build_only: Annotated[
        bool,
        typer.Option('--build-only', '-b', help='Build the model without solving.'),
    ] = False,
    silent: Annotated[
        bool,
        typer.Option(
            '--silent', '-q', help='Silent run. No interactive prompts or INFO logs on console.'
        ),
    ] = False,
    debug: Annotated[
        bool, typer.Option('--debug', '-d', help='Enable debug-level logging.')
    ] = False,
) -> None:
    """
    Builds and solves a Temoa model based on the provided configuration.
    """
    try:
        mode_override = TemoaMode.BUILD_ONLY if build_only else None
        ts, final_output_path = _setup_sequencer(
            config_file=config_file,
            output_path=output_path,
            silent=silent,
            debug=debug,
            mode_override=mode_override,
        )
        if not silent:
            rich.print(ts.config)
            typer.confirm('\nPlease confirm the settings above to continue', abort=True)
        if build_only or ts.temoa_mode is TemoaMode.BUILD_ONLY:
            logger.info('Build-only mode selected. Calling build_model().')
            _ = ts.build_model()
            if not silent:
                rich.print('\n[bold green]✅ Model built successfully.[/bold green]')
                rich.print(f'Log file is available in: [cyan]{final_output_path}[/cyan]')
        else:
            logger.info('Full run mode selected. Calling start().')
            ts.start()
            if not silent:
                rich.print('\n[bold green]✅ Temoa run completed successfully.[/bold green]')
                rich.print(f'Outputs are available in: [cyan]{final_output_path}[/cyan]')
    except typer.Abort:
        rich.print('\n[yellow]Run aborted by user.[/yellow]')
        raise typer.Exit() from None
    except Exception as e:
        logger.exception('An unhandled error occurred during the Temoa run.')
        rich.print(f'\n[bold red]❌ An error occurred:[/bold red] {e}')
        raise typer.Exit(code=1) from e


@app.command('check-units')
def check_units(
    database: Annotated[
        Path,
        typer.Argument(
            help='Path to the Temoa database file to check.',
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            '--output',
            '-o',
            help='Directory to save the unit check report. '
            'Defaults to current directory/unit_check_reports.',
        ),
    ] = None,
    silent: Annotated[
        bool,
        typer.Option('--silent', '-q', help='Suppress informational output.'),
    ] = False,
) -> None:
    """
    Check units consistency in a Temoa database.

    Validates that units are properly defined and consistent across all tables
    in the database. Generates a detailed report of any issues found.

    The unit checker verifies:
    - Units format and registry compliance
    - Technology input/output unit alignment
    - Commodity unit consistency
    - Cost table unit alignment
    """
    from temoa.model_checking.unit_checking.screener import screen

    if not silent:
        rich.print(f'Checking units in database: [cyan]{database}[/cyan]')

    # Determine output directory
    if output_dir is None:
        output_dir = Path.cwd() / 'unit_check_reports'
    else:
        output_dir = output_dir.resolve()

    # Create output directory if it doesn't exist
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        rich.print(f'[red]Error: Could not create output directory: {e}[/red]')
        raise typer.Exit(1) from e

    # Run the unit checker
    try:
        all_clear = screen(database, report_dir=output_dir)

        if all_clear:
            if not silent:
                rich.print('\n[bold green]✅ All unit checks passed![/bold green]')
                rich.print('No unit inconsistencies found in the database.')
        else:
            # Find the most recent report
            reports = sorted(output_dir.glob('units_check_*.txt'), reverse=True)
            if reports:
                report_file = reports[0]
                if not silent:
                    rich.print('\n[bold yellow]⚠ Unit check found issues.[/bold yellow]')
                    rich.print(f'Detailed report saved to: [cyan]{report_file}[/cyan]')
                # Brief summary of the report
                if not silent:
                    rich.print('\n[bold]Report Summary:[/bold]')
                    shown = 0
                    with open(report_file, encoding='utf-8') as f:
                        for idx, line in enumerate(f):
                            if idx >= 40:
                                break
                            if shown > 0 and line.strip() == '':
                                break
                            if line.strip():
                                rich.print(f'  {line.rstrip()}')
                                shown += 1
            else:
                if not silent:
                    rich.print(
                        '\n[yellow]Unit check completed but no report was generated.[/yellow]'
                    )

    except FileNotFoundError as e:
        rich.print(f'[red]Error: Database file not found: {e}[/red]')
        raise typer.Exit(1) from e
    except Exception as e:
        logger.exception('Unit check failed')
        rich.print(f'\n[bold red]❌ Unit check failed:[/bold red] {e}')
        raise typer.Exit(1) from e

    if not all_clear:
        raise typer.Exit(1)


@app.command()
def migrate(
    input_path: Annotated[
        Path,
        typer.Argument(
            help='Path to input file to migrate (SQL dump or SQLite DB).',
            exists=True,
            resolve_path=True,
        ),
    ],
    output_path: Annotated[
        Path | None,
        typer.Option(
            '--output',
            '-o',
            help='Output path for the migrated file. If not provided, a default name '
            '(e.g., input_v4.sql or input_v4.sqlite) will be used in a writable location.',
        ),
    ] = None,
    schema_path: Annotated[
        Path | None,
        typer.Option('--schema', '-s', help='Path to v4 schema SQL file.'),
    ] = None,
    migration_type: Annotated[
        str | None,
        typer.Option(
            '--type',
            help='Migration type: "sql" for SQL dump to SQLite dump, "db" for SQLite DB in-place '
            'migration, if omitted, infers from input extension.',
        ),
    ] = None,
    silent: Annotated[
        bool, typer.Option('--silent', '-q', help='Suppress informational output on success.')
    ] = False,
    debug: Annotated[bool, typer.Option('--debug', '-d', help='Enable debug output.')] = False,
) -> None:
    """
    Migrate a single Temoa database file (SQL dump or SQLite DB) from v3.1 to v4 format.
    """
    if schema_path is None:
        schema_path = get_default_schema()
    if not schema_path.is_file():
        rich.print(f'[red]Error: Schema file {schema_path} does not exist or is not a file.[/red]')
        raise typer.Exit(1)

    # Validate that input_path is a file, not a directory
    if not input_path.is_file():
        rich.print(f'[red]Error: Input path must be a file, not a directory: {input_path}[/red]')
        raise typer.Exit(1)

    ext = input_path.suffix.lower()

    # Determine the effective output directory and file
    effective_output_dir: Path
    final_output_file: Path

    if output_path:
        # If explicit output_path is provided, its parent is the desired directory
        effective_output_dir = output_path.parent
        # Ensure the explicitly provided output_path parent exists
        try:
            effective_output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            rich.print(
                f'[red]Error: Could not create output directory "{effective_output_dir}": {e}[/red]'
            )
            raise typer.Exit(1) from e
        final_output_file = effective_output_dir / output_path.name
    else:
        # Try to use the input file's directory
        input_dir = input_path.parent
        if _is_writable(input_dir):
            effective_output_dir = input_dir
        else:
            # Fallback to current working directory if input_dir is not writable
            current_dir = Path.cwd()
            if _is_writable(current_dir):
                effective_output_dir = current_dir
                if not silent:
                    rich.print(
                        f'[yellow]Warning: Input directory "{input_dir}" is not writable. '
                        f'Saving output to current directory: "{current_dir}"[/yellow]'
                    )
            else:
                rich.print(
                    f'[red]Error: Neither input directory "{input_dir}" '
                    f'nor current working directory "{current_dir}" are writable. '
                    'Please specify a writable output path with --output.[/red]'
                )
                raise typer.Exit(1)

        # Ensure the chosen output directory exists
        try:
            effective_output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            rich.print(
                f'[red]Error: Could not create auto-generated output directory '
                f'"{effective_output_dir}": {e}[/red]'
            )
            raise typer.Exit(1) from e

        # For auto-output, derive filename from input_path, place in effective_output_dir
        # Determine output file extension based on migration type
        if migration_type == 'db' or (migration_type is None and ext in ['.db', '.sqlite']):
            # If migrating to DB, output should be .sqlite
            final_output_file = effective_output_dir / (input_path.stem + '_v4.sqlite')
        else:
            # Default to .sql if migrating SQL dump or type 'auto' for .sql input
            final_output_file = effective_output_dir / (input_path.stem + '_v4.sql')

    # --- Execute the migration based on type ---
    if migration_type == 'sql' or (migration_type is None and ext == '.sql'):
        # SQL dump to SQL dump migration
        args_namespace = argparse.Namespace(
            input=str(input_path),
            schema=str(schema_path),
            output=str(final_output_file),
            debug=debug,
        )
        try:
            sql_migration_v3_1_to_v4.migrate_dump_to_sqlite(args_namespace)
            if not silent:
                rich.print(f'[green]SQL dump migration completed: {final_output_file}[/green]')
        except Exception as e:
            logger.exception('SQL dump migration failed for %s', input_path)
            rich.print(
                f'[red]SQL dump migration failed for {input_path} -> {final_output_file}: {e}[/red]'
            )
            raise typer.Exit(1) from e
    elif migration_type == 'db' or (migration_type is None and ext in ['.db', '.sqlite']):
        # SQLite DB to SQLite DB migration
        args_namespace = argparse.Namespace(
            source=str(input_path),
            schema=str(schema_path),
            out=str(final_output_file),
        )
        try:
            db_migration_v3_1_to_v4.migrate_all(args_namespace)
            if not silent:
                rich.print(f'[green]Database migration completed: {final_output_file}[/green]')
        except Exception as e:
            logger.exception('Database migration failed for %s', input_path)
            rich.print(
                f'[red]Database migration failed for {input_path} -> {final_output_file}: {e}[/red]'
            )
            raise typer.Exit(1) from e
    else:
        rich.print(
            f'[red]Error: Cannot determine migration type for {input_path}. '
            'Use --type sql, --type db, or ensure file has a .sql, .db, or .sqlite extension.[/red]'
        )
        raise typer.Exit(1)


def _copy_tutorial_resources(target_config: Path, target_database: Path) -> None:
    """
    Copy tutorial resource files directly to target locations.

    The database is generated from the SQL source file to ensure it uses
    the latest schema with unit-compliant data (single source of truth).

    Args:
        target_config: Path where configuration file should be copied
        target_database: Path where database file should be created
    """
    import sqlite3

    try:
        # Try to load resources from the package using resources.files()
        base = resources.files('temoa') / 'tutorial_assets'
        config_resource = base / 'config_sample.toml'
        sql_resource = base / 'utopia.sql'

        # Copy configuration file
        with config_resource.open('rb') as source:
            with open(target_config, 'wb') as target:
                shutil.copyfileobj(source, target)

        # Delete existing database if it exists (required for overwrite to work)
        if target_database.exists():
            target_database.unlink()

        # Generate database from SQL source (single source of truth)
        sql_content = sql_resource.read_text(encoding='utf-8')
        with sqlite3.connect(target_database) as conn:
            conn.executescript(sql_content)

    except (ModuleNotFoundError, FileNotFoundError, AttributeError) as e:
        logger.exception('Failed to load tutorial resources from package')
        # Fallback to development paths (for development environments)
        fallback_config = Path(__file__).parent / 'tutorial_assets' / 'config_sample.toml'
        fallback_sql = Path(__file__).parent / 'tutorial_assets' / 'utopia.sql'

        if not fallback_config.exists():
            raise FileNotFoundError(
                f'Tutorial config not found. Tried package resources and fallback path:\n'
                f'Config: {fallback_config}'
            ) from e

        if not fallback_sql.exists():
            raise FileNotFoundError(
                f'Tutorial SQL source not found. Tried package resources and fallback path:\n'
                f'SQL: {fallback_sql}'
            ) from e

        # Copy config file using fallback path
        shutil.copy2(fallback_config, target_config)

        # Delete existing database if it exists (required for overwrite to work)
        if target_database.exists():
            target_database.unlink()

        # Generate database from SQL source
        with sqlite3.connect(target_database) as conn:
            conn.executescript(fallback_sql.read_text(encoding='utf-8'))


def _update_toml_database_paths(config_path: Path, new_database_name: str) -> None:
    """
    Update database paths in a TOML configuration file using tomlkit.

    Args:
        config_path: Path to the configuration file
        new_database_name: Base name for the new database (without extension)
    """
    try:
        # Load TOML document with tomlkit
        with open(config_path, 'rb') as f:
            doc = tomlkit.load(f)

        # Update database paths safely
        if 'input_database' in doc:
            doc['input_database'] = f'{new_database_name}.sqlite'

        if 'output_database' in doc:
            doc['output_database'] = f'{new_database_name}.sqlite'

        # Write back with tomlkit
        with open(config_path, 'w', encoding='utf-8') as f:
            tomlkit.dump(doc, f)

    except Exception as _e:
        logger.warning('Failed to update TOML configuration %s', config_path)
        raise


@app.command()
def tutorial(
    config_name: Annotated[
        str, typer.Argument(help='Name for the tutorial configuration file (without extension).')
    ] = 'tutorial_config',
    database_name: Annotated[
        str, typer.Argument(help='Name for the tutorial database file (without extension).')
    ] = 'tutorial_database',
    force: Annotated[
        bool, typer.Option('--force', '-f', help='Overwrite existing files without prompting.')
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option('--verbose', '-v', help='Show detailed information about the tutorial setup.'),
    ] = False,
) -> None:
    """
    Create tutorial configuration and database files in the current directory with guidance.

    This command creates:
    - A configuration file (.toml)
    - A sample database (.sqlite)

    Both files will be configured to work together for running your first Temoa model.
    """
    current_dir = Path.cwd()

    target_config = current_dir / f'{config_name}.toml'
    target_database = current_dir / f'{database_name}.sqlite'

    # Check for existing files and handle conflicts
    existing_files = []
    if target_config.exists():
        existing_files.append(str(target_config))
    if target_database.exists():
        existing_files.append(str(target_database))

    if existing_files and not force:
        rich.print('[yellow]Tutorial files already exist:[/yellow]')
        for file in existing_files:
            rich.print(f'  - {file}')

        try:
            typer.confirm('Do you want to overwrite these files?', abort=True)
        except typer.Abort:
            rich.print('[yellow]Tutorial setup cancelled.[/yellow]')
            raise typer.Exit() from None

    try:
        # Copy tutorial resources directly to target locations
        if verbose:
            rich.print('Copying tutorial resources...')
        _copy_tutorial_resources(target_config, target_database)

        # Update database paths using tomlkit (preserves formatting/comments)
        if verbose:
            rich.print('Updating database paths in configuration...')

        _update_toml_database_paths(target_config, database_name)

        if verbose:
            rich.print('\n[bold green]✅ Tutorial files created successfully![/bold green]')

        rich.print('\n[bold]Tutorial Setup Complete![/bold]')
        rich.print(f'Configuration file: [cyan]{target_config.name}[/cyan]')
        rich.print(f'Database file: [cyan]{target_database.name}[/cyan]')

        rich.print('\n[bold]Next Steps:[/bold]')
        rich.print(f'1. Review the configuration: [cyan]{target_config.name}[/cyan]')
        rich.print('2. Run your first model:')
        rich.print(f'   [green]uv run temoa run {target_config.name}[/green]')
        rich.print('   or')
        rich.print(f'   [green]python -m temoa run {target_config.name}[/green]')
        rich.print(
            f'\nTo learn more about the configuration options, see the comments in '
            f'[cyan]{target_config.name}[/cyan]'
        )

        if verbose:
            rich.print(
                f"\n[dim]The configuration file points to your local '{database_name}.sqlite' "
                'database.[/dim]'
            )
            rich.print("[dim]Results will be saved in the 'output_files' directory.[/dim]")

    except Exception as e:
        logger.exception('Failed to create tutorial files')
        rich.print(f'\n[bold red]❌ Failed to create tutorial files:[/bold red] {e}')
        raise typer.Exit(1) from e


def _is_writable(path: Path) -> bool:
    """Check if a path is writable."""
    try:
        test_file = path / f'.temoa_write_test_{datetime.now(UTC).timestamp()}'
        test_file.touch()
        test_file.unlink()  # Clean up
        return True
    except OSError:
        return False


# =============================================================================
# Global Options
# =============================================================================
@app.callback()
def main_options(
    version: bool | None = typer.Option(
        None,
        '--version',
        '-v',
        help='Show Temoa version and exit.',
        callback=_version_callback,
        is_eager=True,
    ),
    how_to_cite: bool | None = typer.Option(
        None,
        '--how-to-cite',
        help='Show citation information and exit.',
        callback=_cite_callback,
        is_eager=True,
    ),
) -> None:
    """Manage global options for the Temoa CLI."""


if __name__ == '__main__':
    app()
