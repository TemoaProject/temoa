import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated

import rich
import typer
from rich.logging import RichHandler

from definitions import set_OUTPUT_PATH
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode
from temoa.version_information import TEMOA_MAJOR, TEMOA_MINOR

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
    logger.info(f'Logging initialized. Log file at: {log_file}')


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

    set_OUTPUT_PATH(final_output_path)
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
        version = f'{TEMOA_MAJOR}.{TEMOA_MINOR}'
        rich.print(f'Temoa Version: [bold green]{version}[/bold green]')
        raise typer.Exit()


def _cite_callback(value: bool) -> None:
    if value:
        citation_text = """
        [bold]How to Cite Temoa:[/bold]

        Please consult the project documentation or associated publications
        for the most up-to-date citation information.
        """
        rich.print(citation_text)
        raise typer.Exit()


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
        bool, typer.Option('--silent', '-s', help='Suppress informational output on success.')
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
            '--silent', '-s', help='Silent run. No interactive prompts or INFO logs on console.'
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
        if build_only:
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
    pass


if __name__ == '__main__':
    app()
