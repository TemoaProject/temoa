import types

from _typeshed import Incomplete
from pyomo.common.config import Bool as Bool
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import In as In
from pyomo.common.config import PositiveFloat as PositiveFloat
from pyomo.common.config import PositiveInt as PositiveInt
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.contrib.trustregion.filter import Filter as Filter
from pyomo.contrib.trustregion.filter import FilterElement as FilterElement
from pyomo.contrib.trustregion.interface import TRFInterface as TRFInterface
from pyomo.contrib.trustregion.util import IterationLogger as IterationLogger
from pyomo.core.base.range import NumericRange as NumericRange
from pyomo.opt import SolverFactory as SolverFactory

logger: Incomplete
__version__: Incomplete

def trust_region_method(model, decision_variables, ext_fcn_surrogate_map_rule, config): ...

class TrustRegionSolver:
    CONFIG: Incomplete
    config: Incomplete
    def __init__(self, **kwds) -> None: ...
    def available(self, exception_flag: bool = True): ...
    def version(self): ...
    def license_is_valid(self): ...
    def __enter__(self): ...
    def __exit__(
        self,
        et: type[BaseException] | None,
        ev: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None: ...
    def solve(
        self, model, degrees_of_freedom_variables, ext_fcn_surrogate_map_rule=None, **kwds
    ): ...
