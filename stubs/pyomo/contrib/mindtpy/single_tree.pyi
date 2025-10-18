from _typeshed import Incomplete
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.contrib.gdpopt.util import get_main_elapsed_time as get_main_elapsed_time
from pyomo.contrib.gdpopt.util import time_code as time_code
from pyomo.contrib.mcpp.pyomo_mcpp import MCPP_Error as MCPP_Error
from pyomo.contrib.mindtpy.cut_generation import add_no_good_cuts as add_no_good_cuts
from pyomo.contrib.mindtpy.cut_generation import add_oa_cuts as add_oa_cuts
from pyomo.contrib.mindtpy.util import copy_var_list_values as copy_var_list_values
from pyomo.contrib.mindtpy.util import get_integer_solution as get_integer_solution
from pyomo.contrib.mindtpy.util import set_var_valid_value as set_var_valid_value
from pyomo.core import minimize as minimize
from pyomo.core import value as value
from pyomo.core.expr import identify_variables as identify_variables
from pyomo.repn import generate_standard_repn as generate_standard_repn
from pyomo.solvers.plugins.solvers.gurobi_direct import gurobipy as gurobipy

cplex: Incomplete
cplex_available: Incomplete

class LazyOACallback_cplex:
    def copy_lazy_var_list_values(
        self, opt, from_list, to_list, config, skip_stale: bool = False, skip_fixed: bool = True
    ) -> None: ...
    def add_lazy_oa_cuts(
        self,
        target_model,
        dual_values,
        mindtpy_solver,
        config,
        opt,
        linearize_active: bool = True,
        linearize_violated: bool = True,
    ) -> None: ...
    def add_lazy_affine_cuts(self, mindtpy_solver, config, opt) -> None: ...
    def add_lazy_no_good_cuts(
        self, var_values, mindtpy_solver, config, opt, feasible: bool = False
    ) -> None: ...
    def handle_lazy_main_feasible_solution(self, main_mip, mindtpy_solver, config, opt) -> None: ...
    def handle_lazy_subproblem_optimal(self, fixed_nlp, mindtpy_solver, config, opt) -> None: ...
    def handle_lazy_subproblem_infeasible(self, fixed_nlp, mindtpy_solver, config, opt) -> None: ...
    def handle_lazy_subproblem_other_termination(
        self, fixed_nlp, termination_condition, mindtpy_solver, config
    ) -> None: ...
    def __call__(self) -> None: ...

def LazyOACallback_gurobi(cb_m, cb_opt, cb_where, mindtpy_solver, config) -> None: ...
def handle_lazy_main_feasible_solution_gurobi(cb_m, cb_opt, mindtpy_solver, config) -> None: ...
