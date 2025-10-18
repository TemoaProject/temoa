from _typeshed import Incomplete
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import TraversalStrategy as TraversalStrategy
from pyomo.core.base import Block as Block
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base.indexed_component import ActiveIndexedComponent as ActiveIndexedComponent
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.gdp import GDP_Error as GDP_Error

logger: Incomplete

class HACK_GDP_Disjunct_Reclassifier(Transformation): ...
