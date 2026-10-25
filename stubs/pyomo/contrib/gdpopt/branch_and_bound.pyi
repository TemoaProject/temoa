from typing import NamedTuple

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.errors import InfeasibleConstraintException as InfeasibleConstraintException
from pyomo.contrib.fbbt.fbbt import fbbt as fbbt
from pyomo.contrib.gdpopt.algorithm_base_class import _GDPoptAlgorithm
from pyomo.contrib.gdpopt.create_oa_subproblems import (
    add_algebraic_variable_list as add_algebraic_variable_list,
)
from pyomo.contrib.gdpopt.create_oa_subproblems import (
    add_boolean_variable_lists as add_boolean_variable_lists,
)
from pyomo.contrib.gdpopt.create_oa_subproblems import add_disjunct_list as add_disjunct_list
from pyomo.contrib.gdpopt.create_oa_subproblems import add_disjunction_list as add_disjunction_list
from pyomo.contrib.gdpopt.create_oa_subproblems import (
    add_transformed_boolean_variable_list as add_transformed_boolean_variable_list,
)
from pyomo.contrib.gdpopt.create_oa_subproblems import add_util_block as add_util_block
from pyomo.contrib.gdpopt.nlp_initialization import (
    restore_vars_to_original_values as restore_vars_to_original_values,
)
from pyomo.contrib.gdpopt.util import SuppressInfeasibleWarning as SuppressInfeasibleWarning
from pyomo.contrib.gdpopt.util import copy_var_list_values as copy_var_list_values
from pyomo.contrib.gdpopt.util import get_main_elapsed_time as get_main_elapsed_time
from pyomo.contrib.satsolver.satsolver import satisfiable as satisfiable
from pyomo.core import Constraint as Constraint
from pyomo.core import Suffix as Suffix
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import minimize as minimize
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.opt import SolverStatus as SolverStatus

class BBNodeData(NamedTuple):
    obj_lb: Incomplete
    obj_ub: Incomplete
    is_screened: Incomplete
    is_evaluated: Incomplete
    num_unbranched_disjunctions: Incomplete
    node_count: Incomplete
    unbranched_disjunction_indices: Incomplete

class GDP_LBB_Solver(_GDPoptAlgorithm):
    CONFIG: Incomplete
    algorithm: str
    def solve(self, model, **kwds): ...
