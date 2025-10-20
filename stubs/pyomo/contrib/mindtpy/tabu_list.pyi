from _typeshed import Incomplete
from pyomo.common.dependencies import UnavailableClass as UnavailableClass
from pyomo.common.dependencies import attempt_import as attempt_import

cplex: Incomplete
cplex_available: Incomplete

class IncumbentCallback_cplex:
    def __call__(self) -> None: ...
