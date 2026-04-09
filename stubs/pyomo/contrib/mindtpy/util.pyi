from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.contrib.fbbt.fbbt import compute_bounds_on_expr as compute_bounds_on_expr
from pyomo.contrib.gdpopt.util import get_main_elapsed_time as get_main_elapsed_time
from pyomo.contrib.gdpopt.util import time_code as time_code
from pyomo.contrib.mcpp.pyomo_mcpp import McCormick as McCormick
from pyomo.contrib.mcpp.pyomo_mcpp import mcpp_available as mcpp_available
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import ConstraintList as ConstraintList
from pyomo.core import Objective as Objective
from pyomo.core import RangeSet as RangeSet
from pyomo.core import Reals as Reals
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import Var as Var
from pyomo.core import VarList as VarList
from pyomo.core import minimize as minimize
from pyomo.core import value as value
from pyomo.repn import generate_standard_repn as generate_standard_repn
from pyomo.solvers.plugins.solvers.gurobi_direct import gurobipy as gurobipy
from pyomo.solvers.plugins.solvers.gurobi_persistent import GurobiPersistent as GurobiPersistent
from pyomo.util.model_size import build_model_size_report as build_model_size_report

pyomo_nlp: Incomplete
numpy: Incomplete

def calc_jacobians(constraint_list, differentiate_mode): ...
def initialize_feas_subproblem(m, feasibility_norm) -> None: ...
def add_var_bound(model, config) -> None: ...
def generate_norm2sq_objective_function(model, setpoint_model, discrete_only: bool = False): ...
def generate_norm1_objective_function(model, setpoint_model, discrete_only: bool = False): ...
def generate_norm_inf_objective_function(model, setpoint_model, discrete_only: bool = False): ...
def generate_lag_objective_function(
    model, setpoint_model, config, timing, discrete_only: bool = False
): ...
def generate_norm1_norm_constraint(model, setpoint_model, config, discrete_only: bool = True): ...
def update_solver_timelimit(opt, solver_name, timing, config) -> None: ...
def set_solver_mipgap(opt, solver_name, config) -> None: ...
def set_solver_constraint_violation_tolerance(
    opt, solver_name, config, warm_start: bool = True
) -> None: ...
def get_integer_solution(model, string_zero: bool = False): ...
def copy_var_list_values_from_solution_pool(
    from_list,
    to_list,
    config,
    solver_model,
    var_map,
    solution_name,
    ignore_integrality: bool = False,
) -> None: ...

class GurobiPersistent4MindtPy(GurobiPersistent): ...

def epigraph_reformulation(exp, slack_var_list, constraint_list, use_mcpp, sense) -> None: ...
def setup_results_object(results, model, config) -> None: ...
def fp_converged(working_model, mip_model, proj_zero_tolerance, discrete_only: bool = True): ...
def add_orthogonality_cuts(working_model, mip_model, config) -> None: ...
def generate_norm_constraint(fp_nlp_model, mip_model, config) -> None: ...
def copy_var_list_values(
    from_list,
    to_list,
    config,
    skip_stale: bool = False,
    skip_fixed: bool = True,
    ignore_integrality: bool = False,
) -> None: ...
def set_var_valid_value(
    var, var_val, integer_tolerance, zero_tolerance, ignore_integrality
) -> None: ...
