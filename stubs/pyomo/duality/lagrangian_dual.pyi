from pyomo.common.deprecation import deprecated as deprecated
from pyomo.core import AbstractModel as AbstractModel
from pyomo.core import Constraint as Constraint
from pyomo.core import Objective as Objective
from pyomo.core import Set as Set
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import Var as Var
from pyomo.core import maximize as maximize
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.core.plugins.transform.standard_form import StandardForm as StandardForm
from pyomo.core.plugins.transform.util import partial as partial
from pyomo.core.plugins.transform.util import process_canonical_repn as process_canonical_repn
from pyomo.repn import generate_standard_repn as generate_standard_repn

class DualTransformation(IsomorphicTransformation):
    def __init__(self, **kwds) -> None: ...

class _sparse(dict):
    def __init__(self, default, *args, **kwds) -> None: ...
    def __getitem__(self, ndx): ...
