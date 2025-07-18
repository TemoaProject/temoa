"""
Entry point for running the model.
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from deprecated import deprecated

import definitions
from definitions import PROJECT_ROOT
from temoa.temoa_model.temoa_model import TemoaModel
from temoa.temoa_model.temoa_sequencer import TemoaMode, TemoaSequencer
from temoa.version_information import TEMOA_MAJOR, TEMOA_MINOR

# Written by:  J. F. Hyink
# jeff@westernspark.us
# https://westernspark.us
# Created on:  7/18/23

logger = logging.getLogger(__name__)


@deprecated('currently deprecated functionality')
def runModelUI(config_filename):
    """This function launches the model run from the Temoa GUI"""
    raise NotImplementedError
    # solver = TemoaSolver(model, config_filename)
    # for k in solver.createAndSolve():
    #     yield k
    #     # yield " " * 1024


def runModel(arg_list: list[str] | None = None) -> TemoaModel | None:
    """
    Start the program
    :param arg_list: optional arg_list
    :return: A TemoaModel instance (if asked for), more likely None
    """
    options = parse_args(arg_list=arg_list)
    mode = TemoaMode.BUILD_ONLY if options.build_only else None
    ts = TemoaSequencer(
        config_file=options.config_file,
        output_path=options.output_path,
        mode_override=mode,
        silent=options.silent,
    )
    result = ts.start()
    return result


def parse_args(arg_list: list[str] | None) -> argparse.Namespace:
    """
    Parse the command line args (CLA) if None is passed in (normal operation) or the arg_list,
    if provided :param arg_list: default None --> process sys.argv :return:  options Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        help='Path to file containing configuration information.',
        action='store',
        dest='config_file',
        default=None,
    )
    parser.add_argument(
        '-b',
        '--build_only',
        help='Build and return an unsolved TemoaModel instance.',
        action='store_true',
        dest='build_only',
    )
    parser.add_argument(
        '-s', '--silent', help='Silent run.  No prompts.', action='store_true', dest='silent'
    )
    parser.add_argument(
        '-d',
        '--debug',
        help='Set logging level to DEBUG to see debugging output in log file.',
        action='store_true',
        dest='debug',
    )
    parser.add_argument(
        '-o',
        '--output_path',
        help='Set the path for log and program outputs to an existing directory.  '
        'Default is time-stamped folder in output_files.',
        action='store',
        dest='output_path',
    )
    parser.add_argument(
        '--how_to_cite',
        help='Show citation information for publishing purposes.',
        action='store_true',
        dest='how_to_cite',
    )
    parser.add_argument(
        '-v', '--version', help='Show current Temoa version', action='store_true', dest='version'
    )

    options = parser.parse_args(args=arg_list)  # dev note:  The default (if None) is sys.argv

    # handle the non-execution options and quit
    if options.how_to_cite or options.version:
        if options.version:
            version = f'{TEMOA_MAJOR}.{TEMOA_MINOR}'
            print(f'Temoa Version: {version}')
        if options.how_to_cite:
            raise NotImplementedError('Need this information...')
        sys.exit()

    # validate the output folder if provided, or make the default
    output_path: Path
    if options.output_path:
        if not Path(options.output_path).is_dir():
            raise FileNotFoundError(
                f'The selected output path directory {options.output_path} could not be located.'
            )
        else:
            output_path = Path(options.output_path)
    else:
        output_path = create_output_folder()
    # capture it in options
    options.output_path = output_path
    definitions.set_OUTPUT_PATH(options.output_path)

    # initialize the logging now that option & path are known...
    setup_logging(output_path=output_path, debug_level=options.debug)

    # check for config file existence
    if not options.config_file:
        logger.error(
            'No config file found in CLA.  Temoa needs a config file to operate, see documentation.'
        )
        raise AttributeError('no config file provided.')
    else:
        # convert it to a Path, if it isn't one already
        options.config_file = Path(options.config_file)
    if not options.config_file.is_file():
        logger.error('Config file provided: %s is not valid', options.config_file)
        raise FileNotFoundError('Config file not found.  See log for info.')

    logger.debug('Received Command Line Args: %s', sys.argv[1:])

    if options.build_only:
        logger.info('Build-only selected.')
    return options


def create_output_folder() -> Path:
    """
    create a time-stamped folder as the default catch-all for outputs
    :return: Path to default folder
    """
    output_path = Path(PROJECT_ROOT, 'output_files', datetime.now().strftime('%Y-%m-%d %H%Mh'))
    if not output_path.is_dir():
        output_path.mkdir()
    return output_path


def setup_logging(output_path: Path, debug_level=False):
    # set up logger
    if debug_level:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.getLogger('pyomo').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    filename = 'log.log'
    logging.basicConfig(
        filename=os.path.join(output_path, filename),
        filemode='w',
        format='%(asctime)s | %(module)s | %(levelname)s | %(message)s',
        datefmt='%d-%b-%y %H:%M:%S',
        level=level,
    )
    logger.info('*** STARTING TEMOA ***')


if __name__ == '__main__':
    options = runModel()
