from _typeshed import Incomplete
from pyomo.common import deprecated as deprecated
from pyomo.core.base import Reals as Reals
from pyomo.core.base import Suffix as Suffix
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base import Var as Var

logger: Incomplete

class RelaxIntegerVars(Transformation):
    def __init__(self) -> None: ...

class RelaxDiscreteVars(RelaxIntegerVars):
    def __init__(self, **kwds) -> None: ...

class FixIntegerVars(Transformation):
    def __init__(self) -> None: ...

class FixDiscreteVars(FixIntegerVars):
    def __init__(self, **kwds) -> None: ...
