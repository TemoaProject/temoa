from _typeshed import Incomplete
from pyomo.contrib.mindtpy.algorithm_base_class import _MindtPyAlgorithm
from pyomo.contrib.mindtpy.cut_generation import add_oa_cuts as add_oa_cuts
from pyomo.contrib.mindtpy.util import calc_jacobians as calc_jacobians
from pyomo.core import ConstraintList as ConstraintList
from pyomo.opt import SolverFactory as SolverFactory

class MindtPy_FP_Solver(_MindtPyAlgorithm):
    CONFIG: Incomplete
    def check_config(self) -> None: ...
    jacobians: Incomplete
    def initialize_mip_problem(self) -> None: ...
    def add_cuts(
        self,
        dual_values,
        linearize_active: bool = True,
        linearize_violated: bool = True,
        cb_opt=None,
        nlp=None,
    ) -> None: ...
    def MindtPy_iteration_loop(self) -> None: ...
