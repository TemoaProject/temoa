from _typeshed import Incomplete
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core.kernel.block import IBlock as IBlock
from pyomo.opt.base import ProblemFormat as ProblemFormat
from pyomo.opt.base.convert import ProblemConverterFactory as ProblemConverterFactory
from pyomo.solvers.plugins.converter.pico import PicoMIPConverter as PicoMIPConverter

class PyomoMIPConverter:
    pico_converter: Incomplete
    def can_convert(self, from_type, to_type): ...
    def apply(self, *args, **kwds): ...
