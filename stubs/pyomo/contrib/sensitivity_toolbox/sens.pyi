from _typeshed import Incomplete
from pyomo.common.dependencies import scipy as scipy
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.common.sorting import sorted_robust as sorted_robust
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.contrib.sensitivity_toolbox.k_aug import InTempDir as InTempDir
from pyomo.contrib.sensitivity_toolbox.k_aug import K_augInterface as K_augInterface
from pyomo.core.expr import ExpressionReplacementVisitor as ExpressionReplacementVisitor
from pyomo.core.expr.numvalue import is_potentially_variable as is_potentially_variable
from pyomo.environ import Block as Block
from pyomo.environ import ComponentMap as ComponentMap
from pyomo.environ import ComponentUID as ComponentUID
from pyomo.environ import Constraint as Constraint
from pyomo.environ import ConstraintList as ConstraintList
from pyomo.environ import Objective as Objective
from pyomo.environ import Param as Param
from pyomo.environ import Suffix as Suffix
from pyomo.environ import Var as Var
from pyomo.environ import value as value
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.opt import SolverStatus as SolverStatus

logger: Incomplete

def sipopt(
    instance,
    paramSubList,
    perturbList,
    cloneModel: bool = True,
    tee: bool = False,
    keepfiles: bool = False,
    streamSoln: bool = False,
): ...
def kaug(
    instance,
    paramSubList,
    perturbList,
    cloneModel: bool = True,
    tee: bool = False,
    keepfiles: bool = False,
    solver_options=None,
    streamSoln: bool = False,
): ...

class _NotAnIndex: ...

def sensitivity_calculation(
    method,
    instance,
    paramList,
    perturbList,
    cloneModel: bool = True,
    tee: bool = False,
    keepfiles: bool = False,
    solver_options=None,
): ...
def get_dsdp(model, theta_names, theta, tee: bool = False): ...
def get_dfds_dcds(model, theta_names, tee: bool = False, solver_options=None): ...
def line_num(file_name, target): ...

class SensitivityInterface:
    model_instance: Incomplete
    def __init__(self, instance, clone_model: bool = True) -> None: ...
    @classmethod
    def get_default_block_name(self): ...
    @staticmethod
    def get_default_var_name(name): ...
    @staticmethod
    def get_default_param_name(name): ...
    def setup_sensitivity(self, paramList) -> None: ...
    def perturb_parameters(self, perturbList) -> None: ...
