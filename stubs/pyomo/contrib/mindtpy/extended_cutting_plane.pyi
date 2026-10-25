from _typeshed import Incomplete
from pyomo.contrib.gdpopt.util import get_main_elapsed_time as get_main_elapsed_time
from pyomo.contrib.gdpopt.util import time_code as time_code
from pyomo.contrib.mindtpy.algorithm_base_class import _MindtPyAlgorithm
from pyomo.contrib.mindtpy.cut_generation import add_ecp_cuts as add_ecp_cuts
from pyomo.contrib.mindtpy.util import calc_jacobians as calc_jacobians
from pyomo.core import ConstraintList as ConstraintList
from pyomo.opt import SolverFactory as SolverFactory

class MindtPy_ECP_Solver(_MindtPyAlgorithm):
    CONFIG: Incomplete
    last_iter_cuts: bool
    def MindtPy_iteration_loop(self) -> None: ...
    def check_config(self) -> None: ...
    jacobians: Incomplete
    def initialize_mip_problem(self) -> None: ...
    def init_rNLP(self) -> None: ...
    def algorithm_should_terminate(self): ...
    primal_bound: Incomplete
    best_solution_found: Incomplete
    def all_nonlinear_constraint_satisfied(self): ...
