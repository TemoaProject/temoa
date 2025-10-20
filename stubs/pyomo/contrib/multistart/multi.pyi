import types

from _typeshed import Incomplete
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import In as In
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.multistart.high_conf_stop import should_stop as should_stop
from pyomo.contrib.multistart.reinit import reinitialize_variables as reinitialize_variables
from pyomo.contrib.multistart.reinit import strategies as strategies
from pyomo.core import Objective as Objective
from pyomo.core import Var as Var
from pyomo.core import minimize as minimize
from pyomo.core import value as value
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.opt import SolverStatus as SolverStatus

logger: Incomplete

class MultiStart:
    CONFIG: Incomplete
    def available(self, exception_flag: bool = True): ...
    def license_is_valid(self): ...
    def solve(self, model, **kwds): ...
    def __enter__(self): ...
    def __exit__(
        self,
        t: type[BaseException] | None,
        v: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
