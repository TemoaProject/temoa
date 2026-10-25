from collections.abc import Generator

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.core.expr.numvalue import NumericValue as NumericValue
from pyomo.core.kernel.base import ICategorizedObject as ICategorizedObject

def preorder_traversal(
    node, ctype=..., active: bool = True, descend: bool = True
) -> Generator[Incomplete, None, Incomplete]: ...
def generate_names(node, convert=..., prefix: str = '', **kwds): ...
def pprint(obj, indent: int = 0, stream=...) -> None: ...
