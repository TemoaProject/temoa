import pyomo.core.expr as EXPR
from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.dependencies import numpy_available as numpy_available
from pyomo.common.dependencies import scipy as scipy
from pyomo.common.dependencies import scipy_available as scipy_available
from pyomo.core.base import Block as Block
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Param as Param
from pyomo.core.base import Suffix as Suffix
from pyomo.core.base import value as value
from pyomo.core.expr.numvalue import native_numeric_types as native_numeric_types
from pyomo.core.expr.template_expr import IndexTemplate as IndexTemplate
from pyomo.dae import ContinuousSet as ContinuousSet
from pyomo.dae import DerivativeVar as DerivativeVar
from pyomo.dae.diffvar import DAE_Error as DAE_Error

logger: Incomplete
casadi_intrinsic: Incomplete
casadi: Incomplete
casadi_available: Incomplete

class Pyomo2Scipy_Visitor(EXPR.ExpressionReplacementVisitor):
    templatemap: Incomplete
    def __init__(self, templatemap) -> None: ...
    def beforeChild(self, node, child, child_idx): ...

def convert_pyomo2scipy(expr, templatemap): ...

class Substitute_Pyomo2Casadi_Visitor(EXPR.ExpressionReplacementVisitor):
    templatemap: Incomplete
    def __init__(self, templatemap) -> None: ...
    def exitNode(self, node, data): ...
    def beforeChild(self, node, child, child_idx): ...

class Convert_Pyomo2Casadi_Visitor(EXPR.ExpressionValueVisitor):
    def visit(self, node, values): ...
    def visiting_potential_leaf(self, node): ...

def substitute_pyomo2casadi(expr, templatemap): ...
def convert_pyomo2casadi(expr): ...

class Simulator:
    def __init__(self, m, package: str = 'scipy') -> None: ...
    def get_variable_order(self, vartype=None): ...
    def simulate(
        self,
        numpoints=None,
        tstep=None,
        integrator=None,
        varying_inputs=None,
        initcon=None,
        integrator_options=None,
    ): ...
    def initialize_model(self) -> None: ...
