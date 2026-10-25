from collections.abc import Generator
from contextlib import contextmanager

from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.dependencies import numpy_available as numpy_available
from pyomo.common.modeling import unique_component_name as unique_component_name

logger: Incomplete

@contextmanager
def logcontext(level) -> Generator[None]: ...
def get_active_objective(model): ...

rng: Incomplete

def get_model_variables(
    model,
    components=None,
    include_continuous: bool = True,
    include_binary: bool = True,
    include_integer: bool = True,
    include_fixed: bool = False,
): ...
