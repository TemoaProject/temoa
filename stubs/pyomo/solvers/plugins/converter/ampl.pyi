from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.opt.base import ConverterError as ConverterError
from pyomo.opt.base import ProblemFormat as ProblemFormat
from pyomo.opt.base.convert import ProblemConverterFactory as ProblemConverterFactory

class AmplMIPConverter:
    def can_convert(self, from_type, to_type): ...
    def apply(self, *args, **kwargs): ...
