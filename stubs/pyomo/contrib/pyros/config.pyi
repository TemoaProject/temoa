from _typeshed import Incomplete
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import In as In
from pyomo.common.config import InEnum as InEnum
from pyomo.common.config import IsInstance as IsInstance
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.config import Path as Path
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.errors import PyomoException as PyomoException
from pyomo.contrib.pyros.uncertainty_sets import UncertaintySet as UncertaintySet
from pyomo.contrib.pyros.util import ObjectiveType as ObjectiveType
from pyomo.contrib.pyros.util import setup_pyros_logger as setup_pyros_logger
from pyomo.contrib.pyros.util import standardize_component_data as standardize_component_data
from pyomo.core.base import Var as Var
from pyomo.core.base import VarData as VarData
from pyomo.core.base.param import Param as Param
from pyomo.core.base.param import ParamData as ParamData
from pyomo.opt import SolverFactory as SolverFactory

default_pyros_solver_logger: Incomplete

def logger_domain(obj): ...
def positive_int_or_minus_one(obj): ...
def uncertain_param_validator(uncertain_obj) -> None: ...
def uncertain_param_data_validator(uncertain_obj) -> None: ...

class InputDataStandardizer:
    ctype: Incomplete
    cdatatype: Incomplete
    ctype_validator: Incomplete
    cdatatype_validator: Incomplete
    allow_repeats: Incomplete
    def __init__(
        self,
        ctype,
        cdatatype,
        ctype_validator=None,
        cdatatype_validator=None,
        allow_repeats: bool = False,
    ) -> None: ...
    def __call__(self, obj, from_iterable=None, allow_repeats=None): ...
    def domain_name(self): ...

class SolverNotResolvable(PyomoException): ...

class SolverResolvable:
    require_available: Incomplete
    solver_desc: Incomplete
    def __init__(self, require_available: bool = True, solver_desc: str = 'solver') -> None: ...
    @staticmethod
    def is_solver_type(obj): ...
    def __call__(self, obj, require_available=None, solver_desc=None): ...
    def domain_name(self): ...

class SolverIterable:
    require_available: Incomplete
    filter_by_availability: Incomplete
    solver_desc: Incomplete
    def __init__(
        self,
        require_available: bool = True,
        filter_by_availability: bool = True,
        solver_desc: str = 'solver',
    ) -> None: ...
    def __call__(
        self, obj, require_available=None, filter_by_availability=None, solver_desc=None
    ): ...
    def domain_name(self): ...

def pyros_config(): ...
