from _typeshed import Incomplete
from pyomo.contrib.gdpopt.util import get_main_elapsed_time as get_main_elapsed_time
from pyomo.contrib.mindtpy.algorithm_base_class import _MindtPyAlgorithm
from pyomo.contrib.mindtpy.cut_generation import add_affine_cuts as add_affine_cuts
from pyomo.core import ConstraintList as ConstraintList
from pyomo.opt import SolverFactory as SolverFactory

class MindtPy_GOA_Solver(_MindtPyAlgorithm):
    CONFIG: Incomplete
    def check_config(self) -> None: ...
    def initialize_mip_problem(self) -> None: ...
    def update_primal_bound(self, bound_value) -> None: ...
    def add_cuts(
        self,
        dual_values=None,
        linearize_active: bool = True,
        linearize_violated: bool = True,
        cb_opt=None,
        nlp=None,
    ) -> None: ...
    integer_list: Incomplete
    def deactivate_no_good_cuts_when_fixing_bound(self, no_good_cuts) -> None: ...
