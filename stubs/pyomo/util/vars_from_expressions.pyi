from collections.abc import Generator

from _typeshed import Incomplete
from pyomo.core import Block as Block
from pyomo.core.expr.visitor import IdentifyVariableVisitor as IdentifyVariableVisitor

def get_vars_from_components(
    block,
    ctype,
    include_fixed: bool = True,
    active=None,
    sort: bool = False,
    descend_into=...,
    descent_order=None,
) -> Generator[Incomplete]: ...
