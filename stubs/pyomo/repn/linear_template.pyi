from itertools import chain as chain

import pyomo.repn.linear as linear
from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.errors import MouseTrap as MouseTrap
from pyomo.common.numeric_types import native_types as native_types
from pyomo.core.expr import ExpressionType as ExpressionType
from pyomo.repn.linear import LinearRepn as LinearRepn

code_type: Incomplete

class LinearTemplateRepn(LinearRepn):
    linear_sum: Incomplete
    def __init__(self) -> None: ...
    def walker_exitNode(self): ...
    def duplicate(self): ...
    def append(self, other) -> None: ...
    def compile(
        self,
        env,
        smap,
        expr_cache,
        args,
        remove_fixed_vars: bool = False,
        check_duplicates: bool = False,
    ): ...

class LinearTemplateBeforeChildDispatcher(linear.LinearBeforeChildDispatcher): ...

def define_exit_node_handlers(_exit_node_handlers=None): ...

class LinearTemplateRepnVisitor(linear.LinearRepnVisitor):
    Result = LinearTemplateRepn
    before_child_dispatcher: Incomplete
    exit_node_dispatcher: Incomplete
    indexed_vars: Incomplete
    indexed_params: Incomplete
    expr_cache: Incomplete
    env: Incomplete
    symbolmap: Incomplete
    expanded_templates: Incomplete
    remove_fixed_vars: Incomplete
    def __init__(
        self, subexpression_cache, var_recorder, remove_fixed_vars: bool = False
    ) -> None: ...
    def enterNode(self, node): ...
    def expand_expression(self, obj, template_info): ...
