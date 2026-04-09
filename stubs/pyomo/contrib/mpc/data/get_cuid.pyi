from pyomo.core.base.componentuid import ComponentUID as ComponentUID
from pyomo.core.base.indexed_component_slice import IndexedComponent_slice as IndexedComponent_slice
from pyomo.dae.flatten import get_slice_for_set as get_slice_for_set
from pyomo.util.slices import slice_component_along_sets as slice_component_along_sets

def get_indexed_cuid(var, sets=None, dereference=None, context=None): ...
