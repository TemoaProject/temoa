import types

from _typeshed import Incomplete
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.dependencies import numpy_available as numpy_available
from pyomo.common.deprecation import relocated_module_attribute as relocated_module_attribute
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.common.tee import capture_output as capture_output
from pyomo.common.timing import TicTocTimer as TicTocTimer
from pyomo.core.base import Block as Block
from pyomo.core.base import Objective as Objective
from pyomo.core.base import minimize as minimize
from pyomo.opt import SolverResults as SolverResults
from pyomo.opt import SolverStatus as SolverStatus
from pyomo.opt import TerminationCondition as TerminationCondition
from pyomo.opt.results.solution import Solution as Solution

pyomo_nlp: Incomplete
pyomo_grey_box: Incomplete
egb: Incomplete
cyipopt_interface: Incomplete
_: Incomplete
logger: Incomplete

class CyIpoptSolver:
    def __init__(self, problem_interface, options=None) -> None: ...
    def solve(self, x0=None, tee: bool = False): ...

class PyomoCyIpoptSolver:
    CONFIG: Incomplete
    config: Incomplete
    def __init__(self, **kwds) -> None: ...
    def available(self, exception_flag: bool = False): ...
    def license_is_valid(self): ...
    def version(self): ...
    def solve(self, model, **kwds): ...
    def __enter__(self): ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
