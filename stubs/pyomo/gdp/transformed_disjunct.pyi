from _typeshed import Incomplete
from pyomo.common.autoslots import AutoSlots as AutoSlots
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.block import IndexedBlock as IndexedBlock
from pyomo.core.base.global_set import UnindexedComponent_index as UnindexedComponent_index
from pyomo.core.base.global_set import UnindexedComponent_set as UnindexedComponent_set

class _TransformedDisjunctData(BlockData):
    __autoslot_mappers__: Incomplete
    @property
    def src_disjunct(self): ...
    def __init__(self, component) -> None: ...

class _TransformedDisjunct(IndexedBlock): ...
