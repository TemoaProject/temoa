from typing import NamedTuple

from _typeshed import Incomplete
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.dependencies import attempt_import as attempt_import
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
from pyomo.contrib.gdpopt.util import get_main_elapsed_time as get_main_elapsed_time
from pyomo.contrib.satsolver.satsolver import satisfiable as satisfiable
from pyomo.core import Objective as Objective
from pyomo.core import Suffix as Suffix
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import minimize as minimize
from pyomo.core import value as value
from pyomo.core.expr.logical_expr import ExactlyExpression as ExactlyExpression
from pyomo.opt import SolverFactory as SolverFactory

tabulate: Incomplete
tabulate_available: Incomplete

class ExternalVarInfo(NamedTuple):
    exactly_number: Incomplete
    Boolean_vars: Incomplete
    UB: Incomplete
    LB: Incomplete

class GDP_LDSDA_Solver(_GDPoptAlgorithm):
    CONFIG: Incomplete
    algorithm: str
    def solve(self, model, **kwds): ...
    def any_termination_criterion_met(self, config): ...
    def fix_disjunctions_with_external_var(self, external_var_values_list) -> None: ...
    best_direction: Incomplete
    current_point: Incomplete
    def neighbor_search(self, config): ...
    def line_search(self, config) -> None: ...
