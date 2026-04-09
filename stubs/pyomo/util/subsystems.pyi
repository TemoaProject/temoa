import types
from collections.abc import Generator

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.core.base.block import Block as Block
from pyomo.core.base.constraint import Constraint as Constraint
from pyomo.core.base.expression import Expression as Expression
from pyomo.core.base.external import ExternalFunction as ExternalFunction
from pyomo.core.base.objective import Objective as Objective
from pyomo.core.base.reference import Reference as Reference
from pyomo.core.expr.numeric_expr import ExternalFunctionExpression as ExternalFunctionExpression
from pyomo.core.expr.numvalue import NumericValue as NumericValue
from pyomo.core.expr.numvalue import native_types as native_types
from pyomo.core.expr.visitor import StreamBasedExpressionVisitor as StreamBasedExpressionVisitor
from pyomo.core.expr.visitor import identify_variables as identify_variables
from pyomo.util.vars_from_expressions import get_vars_from_components as get_vars_from_components

class _ExternalFunctionVisitor(StreamBasedExpressionVisitor):
    named_expressions: Incomplete
    def __init__(self, descend_into_named_expressions: bool = True) -> None: ...
    def initializeWalker(self, expr): ...
    def beforeChild(self, parent, child, index): ...
    def exitNode(self, node, data) -> None: ...
    def finalizeResult(self, result): ...

def identify_external_functions(expr) -> Generator[Incomplete, Incomplete]: ...
def add_local_external_functions(block): ...
def create_subsystem_block(constraints, variables=None, include_fixed: bool = False): ...
def generate_subsystem_blocks(subsystems, include_fixed: bool = False) -> Generator[Incomplete]: ...

class TemporarySubsystemManager:
    def __init__(
        self,
        to_fix=None,
        to_deactivate=None,
        to_reset=None,
        to_unfix=None,
        remove_bounds_on_fix: bool = False,
    ) -> None: ...
    def __enter__(self): ...
    def __exit__(
        self,
        ex_type: type[BaseException] | None,
        ex_val: BaseException | None,
        ex_bt: types.TracebackType | None,
    ) -> None: ...

class ParamSweeper(TemporarySubsystemManager):
    input_values: Incomplete
    output_values: Incomplete
    n_scenario: Incomplete
    initial_state_values: Incomplete
    def __init__(
        self,
        n_scenario,
        input_values,
        output_values=None,
        to_fix=None,
        to_deactivate=None,
        to_reset=None,
    ) -> None: ...
    def __iter__(self): ...
    def __next__(self): ...
