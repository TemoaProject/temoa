from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.core.base import Connector as Connector
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import ConstraintList as ConstraintList
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import Transformation as Transformation
from pyomo.core.base import TransformationFactory as TransformationFactory
from pyomo.core.base import Var as Var
from pyomo.core.base.connector import ConnectorData as ConnectorData
from pyomo.core.base.connector import ScalarConnector as ScalarConnector

logger: Incomplete

class ExpandConnectors(Transformation): ...
