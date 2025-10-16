"""
Type stubs for Pyomo external dependency.

This module provides type annotations for Pyomo classes and functions
that are heavily used in Temoa but don't have proper type information.
"""

from abc import ABC
from typing import Any, Optional, Protocol, Tuple, Union, runtime_checkable

# Forward declarations for Pyomo core types
class AbstractModel(ABC):
    """Base class for Pyomo models."""

    def __init__(self, name: Optional[str] = None, **kwargs: Any) -> None: ...
    def add_set(self, name: str, **kwargs: Any) -> 'PyomoSet': ...
    def add_param(self, name: str, **kwargs: Any) -> 'PyomoParam': ...
    def add_var(self, name: str, **kwargs: Any) -> 'PyomoVar': ...
    def add_constraint(self, name: str, **kwargs: Any) -> 'PyomoConstraint': ...
    def add_objective(self, name: str, **kwargs: Any) -> 'PyomoObjective': ...

class PyomoSet:
    """Pyomo Set class for defining index sets."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    @property
    def data(self) -> Any: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Any: ...
    def __contains__(self, item: Any) -> bool: ...

class PyomoParam:
    """Pyomo Param class for defining parameters."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    @property
    def value(self) -> Any: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...

class PyomoVar:
    """Pyomo Var class for defining decision variables."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    @property
    def value(self) -> Any: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...

class PyomoConstraint:
    """Pyomo Constraint class for defining constraints."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...

class PyomoObjective:
    """Pyomo Objective class for defining optimization objectives."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    @property
    def expr(self) -> Any: ...

class PyomoBuildAction:
    """Pyomo BuildAction class for model construction actions."""

    def __init__(self, rule: Any, **kwargs: Any) -> None: ...

# Common Pyomo function stubs
def value(obj: Any) -> Any: ...
def sum_product(*args: Any, **kwargs: Any) -> Any: ...
def quicksum(args: Any, **kwargs: Any) -> Any: ...

# Type aliases for common Pyomo patterns in Temoa
PyomoIndex = Union[str, int, float, Tuple[Any, ...]]
PyomoExpression = Any  # Complex expressions are hard to type statically

# Protocol for Pyomo model components
@runtime_checkable
class PyomoComponent(Protocol):
    """Protocol for Pyomo model components."""

    name: str
    parent: Optional[Any]

    def pprint(self) -> None: ...
    def display(self) -> None: ...

# Export all stubs
__all__ = [
    'AbstractModel',
    'PyomoSet',
    'PyomoParam',
    'PyomoVar',
    'PyomoConstraint',
    'PyomoObjective',
    'PyomoBuildAction',
    'PyomoIndex',
    'PyomoExpression',
    'PyomoComponent',
    'value',
    'sum_product',
    'quicksum',
]
