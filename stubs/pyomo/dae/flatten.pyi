from collections.abc import Generator

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.core.base import Block as Block
from pyomo.core.base import Reference as Reference
from pyomo.core.base.block import SubclassOf as SubclassOf
from pyomo.core.base.component import ActiveComponent as ActiveComponent
from pyomo.core.base.indexed_component import UnindexedComponent_set as UnindexedComponent_set
from pyomo.core.base.indexed_component import normalize_index as normalize_index
from pyomo.core.base.indexed_component_slice import IndexedComponent_slice as IndexedComponent_slice
from pyomo.core.base.set import SetProduct as SetProduct

def get_slice_for_set(s): ...

class _NotAnIndex: ...

def slice_component_along_sets(
    component, sets, context_slice=None, normalize=None
) -> Generator[Incomplete]: ...
def generate_sliced_components(
    b, index_stack, slice_, sets, ctype, index_map, active=None
) -> Generator[Incomplete]: ...
def flatten_components_along_sets(m, sets, ctype, indices=None, active=None): ...
def flatten_dae_components(model, time, ctype, indices=None, active=None): ...
