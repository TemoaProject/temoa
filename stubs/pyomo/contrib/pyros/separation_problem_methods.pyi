from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.contrib.pyros.solve_data import (
    DiscreteSeparationSolveCallResults as DiscreteSeparationSolveCallResults,
)
from pyomo.contrib.pyros.solve_data import SeparationLoopResults as SeparationLoopResults
from pyomo.contrib.pyros.solve_data import SeparationResults as SeparationResults
from pyomo.contrib.pyros.solve_data import SeparationSolveCallResults as SeparationSolveCallResults
from pyomo.contrib.pyros.uncertainty_sets import Geometry as Geometry
from pyomo.contrib.pyros.util import ABS_CON_CHECK_FEAS_TOL as ABS_CON_CHECK_FEAS_TOL
from pyomo.contrib.pyros.util import call_solver as call_solver
from pyomo.contrib.pyros.util import check_time_limit_reached as check_time_limit_reached
from pyomo.contrib.pyros.util import get_all_first_stage_eq_cons as get_all_first_stage_eq_cons
from pyomo.core.base import Block as Block
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Objective as Objective
from pyomo.core.base import Var as Var
from pyomo.core.base import maximize as maximize
from pyomo.core.base import value as value
from pyomo.core.expr import identify_mutable_parameters as identify_mutable_parameters
from pyomo.core.expr import identify_variables as identify_variables
from pyomo.core.expr import replace_expressions as replace_expressions

def add_uncertainty_set_constraints(separation_model, config) -> None: ...
def construct_separation_problem(model_data): ...
def get_sep_objective_values(separation_data, ss_ineq_cons): ...
def get_argmax_sum_violations(solver_call_results_map, ss_ineq_cons_to_evaluate): ...
def solve_separation_problem(separation_data, master_data): ...
def evaluate_violations_by_nominal_master(separation_data, master_data, ss_ineq_cons): ...
def group_ss_ineq_constraints_by_priority(separation_data): ...
def get_worst_discrete_separation_solution(
    ss_ineq_con, config, ss_ineq_cons_to_evaluate, discrete_solve_results
): ...
def get_con_name_repr(separation_model, con, with_obj_name: bool = True): ...
def perform_separation_loop(separation_data, master_data, solve_globally): ...
def evaluate_ss_ineq_con_violations(
    separation_data, ss_ineq_con_to_maximize, ss_ineq_cons_to_evaluate
): ...
def initialize_separation(ss_ineq_con_to_maximize, separation_data, master_data): ...

locally_acceptable: Incomplete
globally_acceptable: Incomplete

def solver_call_separation(
    separation_data, master_data, solve_globally, ss_ineq_con_to_maximize, ss_ineq_cons_to_evaluate
): ...
def discrete_solve(
    separation_data, master_data, solve_globally, ss_ineq_con_to_maximize, ss_ineq_cons_to_evaluate
): ...

class SeparationProblemData:
    separation_model: Incomplete
    timing: Incomplete
    separation_priority_order: Incomplete
    iteration: int
    config: Incomplete
    points_added_to_master: Incomplete
    auxiliary_values_for_master_points: Incomplete
    idxs_of_master_scenarios: Incomplete
    def __init__(self, model_data) -> None: ...
    def solve_separation(self, master_data): ...
