from _typeshed import Incomplete
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.opt import UnknownSolver as UnknownSolver
from pyomo.scripting.pyomo_parser import CustomHelpFormatter as CustomHelpFormatter
from pyomo.scripting.pyomo_parser import add_subparser as add_subparser

def create_parser(parser=None): ...
def create_temporary_parser(solver: bool = False, generate: bool = False): ...
def solve_exec(args, unparsed): ...

solve_parser: Incomplete
