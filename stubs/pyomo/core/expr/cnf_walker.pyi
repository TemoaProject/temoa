from _typeshed import Incomplete
from pyomo.common import DeveloperError as DeveloperError
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.core.expr.logical_expr import special_boolean_atom_types as special_boolean_atom_types
from pyomo.core.expr.numvalue import native_types as native_types
from pyomo.core.expr.numvalue import value as value
from pyomo.core.expr.sympy_tools import Pyomo2SympyVisitor as Pyomo2SympyVisitor
from pyomo.core.expr.sympy_tools import PyomoSympyBimap as PyomoSympyBimap
from pyomo.core.expr.sympy_tools import sympy as sympy
from pyomo.core.expr.sympy_tools import sympy2pyomo_expression as sympy2pyomo_expression

class CNF_Pyomo2SympyVisitor(Pyomo2SympyVisitor):
    boolean_variable_list: Incomplete
    special_atom_map: Incomplete
    def __init__(self, object_map, bool_varlist) -> None: ...
    def beforeChild(self, node, child, child_idx): ...

def to_cnf(expr, bool_varlist=None, bool_var_to_special_atoms=None): ...
