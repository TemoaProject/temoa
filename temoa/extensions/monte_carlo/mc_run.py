"""

"""

from collections import defaultdict, namedtuple
from collections.abc import Generator
from itertools import product
from logging import getLogger
from pathlib import Path

from pyomo.dataportal import DataPortal

from temoa.core.config import TemoaConfig
from temoa.core.model import TemoaModel
from temoa.data_io.hybrid_loader import HybridLoader

logger = getLogger(__name__)

RowData = namedtuple('RowData', ['run', 'param_name', 'indices', 'adjustment', 'value', 'notes'])
"""cleaned and converted tuple from data in a row of the csv file"""
ChangeRecord = namedtuple('ChangeRecord', ['param_name', 'param_index', 'old_value', 'new_value'])
"""a record of a data element change, for an element acted on by a Tweak"""


class Tweak:
    """
    objects of this class represent individual tweaks to single (or wildcard)
    data elements for a Monte Carlo run
    """

    def __init__(self, param_name: str, indices: tuple, adjustment: str, value: float):
        if not isinstance(indices, tuple):
            raise TypeError('indices must be a tuple')
        if adjustment not in {'r', 'a', 's'}:
            raise ValueError('adjustment must be either r/a/s')
        if not isinstance(value, float | int):
            raise TypeError('value must be a float or int')

        self.param_name = param_name
        self.indices = indices
        self.adjustment = adjustment
        self.value = value

    def __repr__(self):
        return (
            f'<param: {self.param_name}, indices: {self.indices}, adjustment: {self.adjustment}, '
            f'value: {self.value}>'
        )


class TweakFactory:
    """
    factor (likely a singleton) to manufacture Tweaks from input data
    """

    def __init__(self, data_store: dict):
        """
        make a new factor and use data_store as a validation tool
        :param data_store: the data dictionary holding the base values for the model
        """
        if not isinstance(data_store, dict):
            raise TypeError('data_store must be a dict')
        self.val_data = data_store
        tweak_dict: dict[int, list[Tweak]] = defaultdict(list)

    def make_tweaks(self, row_number: int, row: str) -> tuple[int, list[Tweak]]:
        """
        make a tuple of tweaks from the row input.  Rows with multiple identifiers (separated by /)
        will produce 1 tweak per identifier per group
        :param row: run, param, index, adjustment, value
        :return: tuple of Tweaks generated from the row
        """
        rd = self.row_parser(row_number=row_number, row=row)
        # pry the index
        p_index = rd.indices.replace('(', '').replace(')', '')  # remove any optional parens
        tokens = p_index.split('|')
        tokens = [t.strip() for t in tokens]
        tweaks = []
        # locate all 'multi' indices...
        index_vals: dict[int, list] = defaultdict(list)
        for pos, token in enumerate(tokens):
            if '/' in token:  # it is a multi-token
                sub_tokens = token.split('/')
                sub_tokens = [t.strip() for t in sub_tokens]
                for sub_token in sub_tokens:
                    try:  # integer conversion
                        sub_token = int(sub_token)
                        index_vals[pos].append(sub_token)
                    except ValueError:
                        index_vals[pos].append(sub_token)
            else:  # singleton
                try:  # integer conversion
                    token = int(token)
                    index_vals[pos].append(token)
                except ValueError:
                    index_vals[pos].append(token)

        # iterate through the positions and make all sets of indices...
        index_groups = [index_vals[pos] for pos in sorted(index_vals.keys())]
        all_inedexes = product(*index_groups)
        res = [
            Tweak(param_name=rd.param_name, indices=index, adjustment=rd.adjustment, value=rd.value)
            for index in all_inedexes
        ]
        logger.debug('Made %d Tweaks for data labeled with run: %d', len(res), rd.run)
        return rd.run, res

    def row_parser(self, row_number: int, row: str) -> RowData:
        """
        Parse an individual row of the input .csv file
        :param row_number: the row number from the reader (used to ID errors)
        :param row: the raw row in string format
        :return: a RowData tuple element
        """
        tokens = row.strip().split(',')
        tokens = [t.strip() for t in tokens]
        # check length
        if len(tokens) != 6:
            raise ValueError(
                f'Error parsing line {row_number}.  Did you omit notes / trailing comma for no '
                'notes or have a comma in your note?'
            )
        # convert the run number
        try:
            tokens[0] = int(tokens[0])
        except ValueError:
            raise ValueError(f'run number at row {row_number} must be an integer')
        # convert the value
        try:
            tokens[-2] = float(tokens[-2])
        except ValueError:
            raise ValueError('value at row {idx} must be numeric')
        rd = RowData(*tokens)

        # make other checks...
        if rd.param_name not in self.val_data:
            # the param name should be a key value in the data dictionary
            raise ValueError(
                f'param_name at index: {row_number} is either invalid or not represented in the '
                'input dataset'
            )
        if rd.adjustment not in {'r', 'a', 's'}:
            raise ValueError(f'adjustment at index {row_number} must be either r/a/s')
        # check for no "empty" indices in the index
        if '||' in rd.indices:
            raise ValueError(
                f'indices at index {row_number} cannot contain empty marker: ||.  Did you mean to '
                'put in wildcard "*"?'
            )
        return rd


class MCRun:
    """
    A Container class to hold the data (and more?) to support a model build + run
    """

    def __init__(
        self,
        scenario_name: str,
        run_index: int,
        data_store: dict,
        included_tweaks: dict[Tweak, list[ChangeRecord]],
    ):
        self.scenario_name = scenario_name
        self.run_index = run_index
        self.data_store = data_store
        self.included_tweaks = included_tweaks

    @property
    def change_records(self) -> list[ChangeRecord]:
        res = []
        for k in self.included_tweaks:
            res.extend(self.included_tweaks[k])
        return res

    @property
    def model_dp(self) -> tuple[str, DataPortal]:
        """tuple of the indexed name for the scenario, and the DP"""
        name = f'{self.scenario_name}-{self.run_index}'
        dp = HybridLoader.data_portal_from_data(self.data_store)
        return name, dp

    @property
    def model(self) -> TemoaModel:
        dp = self.model_dp
        model = TemoaModel()
        instance = model.create_instance(data=dp)
        # update the name to indexed...
        instance.name = f'{self.scenario_name}-{self.run_index}'
        logger.info('Created model instance for run %d', self.run_index)
        return instance


class MCRunFactory:
    """
    objects of this class represent individual run settings for Monte Carlo.

    They will hold the "data tweaks" gathered from input file for application to the base data
    """

    def __init__(self, config: TemoaConfig, data_store: dict):
        self.config = config
        self.data_store = data_store
        self.tweak_factory = TweakFactory(data_store)
        self.settings_file = Path(self.config.monte_carlo_inputs['run_settings'])

    def prescreen_input_file(self):
        """
        read the input csv file and screen common errors
        :return: True if file passes, false otherwise with log entries
        """
        with open(self.settings_file) as f:
            header = f.readline().strip()
            assert header == 'run,param,index,mod,value,notes', (
                'header should be: run,param,index,mod,value,notes'
            )
            current_run = -1
            for idx, row in enumerate(f.readlines(), start=2):
                rd = self.tweak_factory.row_parser(idx, row)
                # check that run indexing is monotonically increasing
                if idx == 2:
                    current_run = rd.run
                elif current_run > rd.run:
                    raise ValueError(f'Run sequence violation at row {idx}')
                elif current_run < rd.run:
                    current_run = rd.run
        logger.info(f'Pre-screen of data file: {self.settings_file} successful.')
        return True

    def _next_row_generator(self) -> Generator[tuple[int, str], None, None]:
        """
        A generator to read lines from thr run settings file
        :return:
        """
        with open(self.settings_file) as f:
            # burn header
            f.readline()
            idx = 2
            for line in f:
                yield idx, line
                idx += 1

    def tweak_set_generator(self) -> tuple[int, list[Tweak]]:
        """
        generator for lists of tweaks per run
        :return:
        """
        rows = self._next_row_generator()
        empty = False
        run_tweaks = []
        row_number, next_row = next(rows)
        run_number, tweaks = self.tweak_factory.make_tweaks(row_number=row_number, row=next_row)
        current_run = run_number
        while not empty:
            while run_number == current_run and not empty:
                run_tweaks.extend(tweaks)
                try:
                    row_number, next_row = next(rows)
                    run_number, tweaks = self.tweak_factory.make_tweaks(
                        row_number=row_number, row=next_row
                    )
                except StopIteration:
                    empty = True
            yield current_run, run_tweaks
            # prep the next
            run_tweaks = []
            current_run = run_number

    @staticmethod
    def element_locator(data_store: dict, param: str, target_index: tuple) -> list[tuple]:
        """
        find the associated indices that match the index, which may
        contain wildcards
        :param data_store: the data dictionary to search
        :param target_index: the search criteria
        :return: list of matching indices
        """
        # locate non-wildcards
        non_wildcard_locs = []
        for idx, item in enumerate(target_index):
            if item != '*':
                non_wildcard_locs.append(idx)
        # grab all the indices for the given parameter
        param_data = data_store.get(param)
        if not param_data:
            return []
        # check for correct index length (would be odd, but...)
        first_index = tuple(param_data.keys())[0]
        if len(target_index) != len(first_index):
            raise ValueError(
                f'length of search index {target_index} for parameter {param} does not match data '
                f'ex: {first_index}'
            )
        raw_indices = param_data.keys()
        matches = [
            k
            for k in raw_indices
            if all(k[idx] == target_index[idx] for idx in non_wildcard_locs)
        ]
        return matches

    @staticmethod
    def _adjust_value(old_value: float, adjust_type: str, factor: float) -> float:
        match adjust_type:
            case 'r':  # relative (ratio) based change
                res = old_value * (1 + factor)
            case 's':  # pure substitution
                res = factor
            case 'a':  # absolute change
                res = old_value + factor
            case _:
                raise ValueError(f'Unsupported adjustment type {adjust_type}')
        return res

    def run_generator(self) -> Generator[MCRun, None, None]:
        """
        make a new MC Run, log problems with tweaks and write successful
        tweaks to the DB Output
        :return:
        """
        ts_gen = self.tweak_set_generator()
        for run, tweaks in ts_gen:
            logger.info('Making run %d from %d tweaks', run, len(tweaks))
            logger.debug('Run %d tweaks: %s', run, tweaks)

            # need to make a DEEP copy of the orig, which holds other dictionaries...
            data_store = {k: v.copy() for k, v in self.data_store.items()}
            failed_tweaks = []
            good_tweaks: dict[Tweak, list[ChangeRecord]] = defaultdict(list)
            for tweak in tweaks:
                # locate the element
                matching_indices = self.element_locator(data_store, tweak.param_name, tweak.indices)
                if not matching_indices:  # catalog as failure
                    failed_tweaks.append(tweak)
                else:
                    for index in matching_indices:
                        old_value = data_store.get(tweak.param_name)[index]
                        new_value = self._adjust_value(old_value, tweak.adjustment, tweak.value)
                        data_store[tweak.param_name][index] = new_value
                        good_tweaks[tweak].append(
                            ChangeRecord(tweak.param_name, index, old_value, new_value)
                        )

            # do the logging
            for tweak in good_tweaks:
                logger.debug('Successful tweak: %s', tweak)
                for adjustment in good_tweaks[tweak]:
                    logger.debug('  made delta: %s', adjustment)

            for tweak in failed_tweaks:
                logger.warning('Failed tweak: %s', tweak)
            # skip the creation of the run if no tweaks were successful (it would just be the
            # baseline run...)
            if not good_tweaks:
                logger.warning(f'Aborting run: {run}.  No good tweaks found')
                continue
            mc_run = MCRun(
                scenario_name=self.config.scenario,
                run_index=run,
                data_store=data_store,
                included_tweaks=good_tweaks,
            )
            yield mc_run
