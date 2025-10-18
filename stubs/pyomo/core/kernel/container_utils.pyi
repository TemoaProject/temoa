from pyomo.core.kernel.dict_container import DictContainer as DictContainer
from pyomo.core.kernel.list_container import ListContainer as ListContainer
from pyomo.core.kernel.tuple_container import TupleContainer as TupleContainer

def define_homogeneous_container_type(
    namespace, name, container_class, ctype, doc=None, use_slots: bool = True
) -> None: ...
def define_simple_containers(namespace, prefix, ctype, use_slots: bool = True) -> None: ...
