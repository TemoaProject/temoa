from _typeshed import Incomplete
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.contrib.gdpopt.algorithm_base_class import _GDPoptAlgorithm
from pyomo.contrib.gdpopt.cut_generation import add_no_good_cut as add_no_good_cut
from pyomo.contrib.gdpopt.oa_algorithm_utils import _OAAlgorithmMixIn
from pyomo.contrib.gdpopt.solve_discrete_problem import (
    solve_MILP_discrete_problem as solve_MILP_discrete_problem,
)
from pyomo.contrib.gdpopt.util import time_code as time_code
from pyomo.core import Objective as Objective
from pyomo.opt.base import SolverFactory as SolverFactory

class GDP_RIC_Solver(_GDPoptAlgorithm, _OAAlgorithmMixIn):
    CONFIG: Incomplete
    algorithm: str
    def solve(self, model, **kwds): ...
