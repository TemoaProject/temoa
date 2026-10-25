from _typeshed import Incomplete
from pyomo.common.fileutils import find_library as find_library
from pyomo.common.gc_manager import PauseGC as PauseGC
from pyomo.core.base import ComponentMap as ComponentMap
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import ExternalFunction as ExternalFunction
from pyomo.core.base import NamedExpressionData as NamedExpressionData
from pyomo.core.base import NameLabeler as NameLabeler
from pyomo.core.base import Objective as Objective
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import SOSConstraint as SOSConstraint
from pyomo.core.base import Suffix as Suffix
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import Var as Var
from pyomo.core.base import param as param
from pyomo.core.base import var as var
from pyomo.core.expr.numvalue import NumericConstant as NumericConstant
from pyomo.core.expr.numvalue import is_fixed as is_fixed
from pyomo.core.expr.numvalue import native_numeric_types as native_numeric_types
from pyomo.core.expr.numvalue import value as value
from pyomo.core.kernel.block import IBlock as IBlock
from pyomo.core.kernel.expression import IIdentityExpression as IIdentityExpression
from pyomo.core.kernel.variable import IVariable as IVariable
from pyomo.opt import AbstractProblemWriter as AbstractProblemWriter
from pyomo.opt import ProblemFormat as ProblemFormat
from pyomo.opt import WriterFactory as WriterFactory
from pyomo.repn.standard_repn import generate_standard_repn as generate_standard_repn

logger: Incomplete

def set_pyomo_amplfunc_env(external_libs) -> None: ...

class StopWatch:
    start: Incomplete
    def __init__(self) -> None: ...
    def report(self, msg) -> None: ...
    def reset(self) -> None: ...

class _Counter:
    def __init__(self, start) -> None: ...
    def __call__(self, obj): ...

class ModelSOS:
    class AmplSuffix:
        name: Incomplete
        ids: Incomplete
        vals: Incomplete
        def __init__(self, name) -> None: ...
        def add(self, idx, val) -> None: ...
        def genfilelines(self): ...
        def is_empty(self): ...

    ampl_var_id: Incomplete
    sosno: Incomplete
    ref: Incomplete
    block_cntr: int
    varID_map: Incomplete
    def __init__(self, ampl_var_id, varID_map) -> None: ...
    def count_constraint(self, soscondata) -> None: ...

class RepnWrapper:
    repn: Incomplete
    linear_vars: Incomplete
    nonlinear_vars: Incomplete
    def __init__(self, repn, linear, nonlinear) -> None: ...

class ProblemWriter_nl(AbstractProblemWriter):
    def __init__(self) -> None: ...
    def __call__(self, model, filename, solver_capability, io_options): ...
