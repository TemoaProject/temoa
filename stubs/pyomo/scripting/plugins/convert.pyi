from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.opt import guess_format as guess_format
from pyomo.scripting.pyomo_parser import CustomHelpFormatter as CustomHelpFormatter
from pyomo.scripting.pyomo_parser import add_subparser as add_subparser
from pyomo.scripting.solve_config import Default_Config as Default_Config

def create_parser(parser=None): ...
def run_convert(options=..., parser=None): ...
def convert_exec(args, unparsed): ...

convert_parser: Incomplete

def create_temporary_parser(output: bool = False, generate: bool = False): ...
