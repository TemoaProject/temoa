import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated

import rich
import typer
from rich.logging import RichHandler

from definitions import set_OUTPUT_PATH

# Updated imports to bring in the config object
from temoa._internal.temoa_sequencer import TemoaSequencer
from temoa.core.config import TemoaConfig
from temoa.core.modes import TemoaMode
from temoa.version_information import TEMOA_MAJOR, TEMOA_MINOR

# =============================================================================
# Logging Setup
# =============================================================================
logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================
def _create_output_folder() -> Path:
    """Create a default time-stamped folder for outputs."""
    output_path = Path('output_files', datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def _setup_logging(output_path: Path, debug: bool = False) -> None:
    """Set up logging to a file and a rich console."""
    level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    log_file = output_path / 'temoa-run.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    rich_handler = RichHandler(rich_tracebacks=True, show_path=False, log_time_format='[%X]')
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [file_handler, rich_handler]
    logging.getLogger('pyomo').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logger.info(f'Logging initialized. Log file at: {log_file}')


def _version_callback(value: bool) -> None:
    """Callback to print version information and exit."""
    if value:
        version = f'{TEMOA_MAJOR}.{TEMOA_MINOR}'
        rich.print(f'Temoa Version: [bold green]{version}[/bold green]')
        raise typer.Exit()


def _cite_callback(value: bool) -> None:
    """Callback to print citation information and exit."""
    if value:
        citation_text = """
        [bold]How to Cite Temoa:[/bold]

        Please consult the project documentation or associated publications
        for the most up-to-date citation information.
        """
        rich.print(citation_text)
        raise typer.Exit()


# =============================================================================
# Typer Application Setup
# =============================================================================
app = typer.Typer(
    name='temoa',
    help='The Temoa Project: Tools for Energy Model Optimization and Analysis.',
    rich_markup_mode='markdown',
    no_args_is_help=True,
    context_settings={'help_option_names': ['-h', '--help']},
)


# =============================================================================
# Main 'run' Subcommand
# =============================================================================
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
        typer.Option(
            '--output',
            '-o',
            help='Directory to save outputs. Defaults to a new time-stamped folder.',
            file_okay=False,
            dir_okay=True,
            writable=True,
            resolve_path=True,
        ),
    ] = None,
    build_only: Annotated[
        bool,
        typer.Option(
            '--build-only',
            '-b',
            help='Build an unsolved TemoaModel instance without solving.',
        ),
    ] = False,
    silent: Annotated[
        bool, typer.Option('--silent', '-s', help='Silent run. No interactive prompts.')
    ] = False,
    debug: Annotated[
        bool, typer.Option('--debug', '-d', help='Enable debug-level logging.')
    ] = False,
) -> None:
    """
    Builds and solves a Temoa model based on the provided configuration.
    """
    final_output_path = output_path if output_path else _create_output_folder()
    final_output_path.mkdir(parents=True, exist_ok=True)

    _setup_logging(final_output_path, debug)
    set_OUTPUT_PATH(final_output_path)

    try:
        # Step 1: Create the configuration object first.
        config = TemoaConfig.build_config(
            config_file=config_file, output_path=final_output_path, silent=silent
        )

        # Step 2: Handle user interaction in the CLI, not the sequencer.
        if not silent:
            rich.print(config)  # Print the rich representation of the config
            # Use Typer's confirmation prompt, which aborts on "n".
            typer.confirm('\nPlease confirm the settings above to continue', abort=True)

        # Step 3: Instantiate the sequencer and decide which method to call.
        mode_override = TemoaMode.BUILD_ONLY if build_only else None
        ts = TemoaSequencer(config=config, mode_override=mode_override)

        if build_only:
            logger.info('Build-only mode selected. Calling build_model().')
            # The returned model is not used here, but could be in other contexts.
            _ = ts.build_model()
            rich.print('\n[bold green]✅ Model built successfully.[/bold green]')
            rich.print(f'Log file is available in: [cyan]{final_output_path}[/cyan]')
        else:
            logger.info('Full run mode selected. Calling start().')
            ts.start()
            rich.print('\n[bold green]✅ Temoa run completed successfully.[/bold green]')
            rich.print(f'Outputs are available in: [cyan]{final_output_path}[/cyan]')

    except typer.Abort:
        # This catches the "n" from the confirmation prompt.
        rich.print('\n[yellow]Run aborted by user.[/yellow]')
        raise typer.Exit() from None

    except Exception as e:
        # This now correctly catches all errors raised from the sequencer.
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
