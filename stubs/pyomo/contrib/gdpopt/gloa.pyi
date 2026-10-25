from _typeshed import Incomplete
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.gdp_bounds.info import disjunctive_bounds as disjunctive_bounds
from pyomo.contrib.gdpopt.algorithm_base_class import _GDPoptAlgorithm
from pyomo.contrib.gdpopt.create_oa_subproblems import (
    add_constraints_by_disjunct as add_constraints_by_disjunct,
)
from pyomo.contrib.gdpopt.create_oa_subproblems import (
    add_global_constraint_list as add_global_constraint_list,
)
from pyomo.contrib.gdpopt.cut_generation import add_no_good_cut as add_no_good_cut
from pyomo.contrib.gdpopt.oa_algorithm_utils import _OAAlgorithmMixIn
from pyomo.contrib.gdpopt.solve_discrete_problem import (
    solve_MILP_discrete_problem as solve_MILP_discrete_problem,
)
from pyomo.contrib.gdpopt.util import time_code as time_code
from pyomo.contrib.mcpp.pyomo_mcpp import MCPP_Error as MCPP_Error
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import Objective as Objective
from pyomo.core import value as value
from pyomo.core.expr.numvalue import is_potentially_variable as is_potentially_variable
from pyomo.core.expr.visitor import identify_variables as identify_variables
from pyomo.opt.base import SolverFactory as SolverFactory

class GDP_GLOA_Solver(_GDPoptAlgorithm, _OAAlgorithmMixIn):
    CONFIG: Incomplete
    algorithm: str
    def solve(self, model, **kwds): ...
