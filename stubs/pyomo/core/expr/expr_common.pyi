from contextlib import nullcontext

from pyomo.common import enums as enums
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.common.modeling import NOTSET as NOTSET

TO_STRING_VERBOSE: bool

class Mode(enums.IntEnum):
    coopr_trees = 1
    coopr3_trees = 3
    pyomo4_trees = 4
    pyomo5_trees = 5
    pyomo6_trees = 6
    CURRENT = pyomo6_trees

class OperatorAssociativity(enums.IntEnum):
    RIGHT_TO_LEFT = -1
    NON_ASSOCIATIVE = 0
    LEFT_TO_RIGHT = 1

class ExpressionType(enums.Enum):
    NUMERIC = 0
    RELATIONAL = 1
    LOGICAL = 2

class NUMERIC_ARG_TYPE(enums.IntEnum):
    MUTABLE = -2
    ASNUMERIC = -1
    INVALID = 0
    NATIVE = 1
    NPV = 2
    PARAM = 3
    VAR = 4
    MONOMIAL = 5
    LINEAR = 6
    SUM = 7
    OTHER = 8

class RELATIONAL_ARG_TYPE(enums.IntEnum, metaclass=enums.ExtendedEnumType):
    __base_enum__ = NUMERIC_ARG_TYPE
    INEQUALITY = 100
    INVALID_RELATIONAL = 101

class clone_counter(nullcontext):
    def __init__(self) -> None: ...
    @property
    def count(self): ...
