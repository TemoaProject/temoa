from pyomo.common.enums import ExtendedEnumType as ExtendedEnumType
from pyomo.common.enums import IntEnum as IntEnum
from pyomo.common.enums import ObjectiveSense as ObjectiveSense
from pyomo.opt.results.container import MapContainer as MapContainer

class ProblemSense(IntEnum, metaclass=ExtendedEnumType):
    __base_enum__ = ObjectiveSense
    unknown = 0

class ProblemInformation(MapContainer):
    def __init__(self) -> None: ...
