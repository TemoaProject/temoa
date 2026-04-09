from _typeshed import Incomplete
from pyomo.core import Binary as Binary
from pyomo.core import value as value
from pyomo.core.base import Block as Block
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import ConstraintList as ConstraintList
from pyomo.core.base import RangeSet as RangeSet
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base import Var as Var
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr import PowExpression as PowExpression
from pyomo.core.expr import ProductExpression as ProductExpression
from pyomo.core.expr.numvalue import as_numeric as as_numeric

logger: Incomplete

class RadixLinearization(Transformation): ...
