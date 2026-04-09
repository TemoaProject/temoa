from _typeshed import Incomplete
from pyomo.contrib.mindtpy.algorithm_base_class import _MindtPyAlgorithm
from pyomo.contrib.mindtpy.cut_generation import add_oa_cuts as add_oa_cuts
from pyomo.contrib.mindtpy.cut_generation import (
    add_oa_cuts_for_grey_box as add_oa_cuts_for_grey_box,
)
from pyomo.contrib.mindtpy.util import calc_jacobians as calc_jacobians
from pyomo.core import ConstraintList as ConstraintList
from pyomo.opt import SolverFactory as SolverFactory

class MindtPy_OA_Solver(_MindtPyAlgorithm):
    CONFIG: Incomplete
    regularization_mip_type: str
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
    integer_list: Incomplete
    def deactivate_no_good_cuts_when_fixing_bound(self, no_good_cuts) -> None: ...
    def objective_reformulation(self) -> None: ...
