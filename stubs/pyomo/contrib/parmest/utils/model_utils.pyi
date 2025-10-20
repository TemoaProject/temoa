from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.core.base.param import IndexedParam as IndexedParam
from pyomo.core.base.var import IndexedVar as IndexedVar
from pyomo.core.expr import identify_mutable_parameters as identify_mutable_parameters
from pyomo.core.expr import replace_expressions as replace_expressions
from pyomo.environ import ComponentUID as ComponentUID

logger: Incomplete

def convert_params_to_vars(model, param_names=None, fix_vars: bool = False): ...
