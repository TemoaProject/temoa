from _typeshed import Incomplete
from pyomo.common import Factory as Factory
from pyomo.opt.base.error import ConverterError as ConverterError
from pyomo.opt.base.formats import guess_format as guess_format

ProblemConverterFactory: Incomplete

def convert_problem(args, target_problem_type, valid_problem_types, has_capability=..., **kwds): ...
