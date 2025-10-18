from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.contrib.gdpopt.algorithm_base_class import _GDPoptAlgorithm
from pyomo.contrib.gdpopt.create_oa_subproblems import (
    add_discrete_variable_list as add_discrete_variable_list,
)
from pyomo.contrib.gdpopt.create_oa_subproblems import add_disjunction_list as add_disjunction_list
from pyomo.contrib.gdpopt.create_oa_subproblems import get_subproblem as get_subproblem
from pyomo.contrib.gdpopt.nlp_initialization import (
    restore_vars_to_original_values_enumerate as restore_vars_to_original_values_enumerate,
)
from pyomo.contrib.gdpopt.solve_subproblem import solve_subproblem as solve_subproblem
from pyomo.contrib.gdpopt.util import (
    fix_discrete_solution_in_subproblem as fix_discrete_solution_in_subproblem,
)
from pyomo.contrib.gdpopt.util import get_main_elapsed_time as get_main_elapsed_time
from pyomo.contrib.gdpopt.util import time_code as time_code
from pyomo.core import value as value
from pyomo.opt.base import SolverFactory as SolverFactory

class GDP_Enumeration_Solver(_GDPoptAlgorithm):
    CONFIG: Incomplete
    algorithm: str
    def solve(self, model, **kwds): ...
