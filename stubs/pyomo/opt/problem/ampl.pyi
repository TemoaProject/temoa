from _typeshed import Incomplete
from pyomo.opt.base import ProblemFormat as ProblemFormat
from pyomo.opt.base import convert_problem as convert_problem
from pyomo.opt.base import guess_format as guess_format

class AmplModel:
    modfile: Incomplete
    datfile: Incomplete
    def __init__(self, modfile, datfile=None) -> None: ...
    def valid_problem_types(self): ...
    def write(self, filename, format=None, solver_capability=None): ...
