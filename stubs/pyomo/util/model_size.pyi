from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import Var as Var
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction

default_logger: Incomplete

class ModelSizeReport(Bunch): ...

def build_model_size_report(model): ...
def log_model_size_report(model, logger=...) -> None: ...
