from typing import NamedTuple

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.gdpopt.algorithm_base_class import _GDPoptAlgorithm
from pyomo.contrib.gdpopt.create_oa_subproblems import add_constraint_list as add_constraint_list
from pyomo.contrib.gdpopt.cut_generation import add_no_good_cut as add_no_good_cut
from pyomo.contrib.gdpopt.oa_algorithm_utils import _OAAlgorithmMixIn
from pyomo.contrib.gdpopt.solve_discrete_problem import (
    solve_MILP_discrete_problem as solve_MILP_discrete_problem,
)
from pyomo.contrib.gdpopt.util import time_code as time_code
from pyomo.core import Block as Block
from pyomo.core import Constraint as Constraint
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import NonNegativeReals as NonNegativeReals
from pyomo.core import Objective as Objective
from pyomo.core import Var as Var
from pyomo.core import VarList as VarList
from pyomo.core import minimize as minimize
from pyomo.core import value as value
from pyomo.core.expr import differentiate as differentiate
from pyomo.core.expr.visitor import identify_variables as identify_variables
from pyomo.gdp import Disjunct as Disjunct
from pyomo.opt.base import SolverFactory as SolverFactory
from pyomo.repn import generate_standard_repn as generate_standard_repn

MAX_SYMBOLIC_DERIV_SIZE: int

class JacInfo(NamedTuple):
    mode: Incomplete
    vars: Incomplete
    jac: Incomplete

class GDP_LOA_Solver(_GDPoptAlgorithm, _OAAlgorithmMixIn):
    CONFIG: Incomplete
    algorithm: str
    def solve(self, model, **kwds): ...
