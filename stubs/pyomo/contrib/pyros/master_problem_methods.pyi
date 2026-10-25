from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.pyros.solve_data import MasterResults as MasterResults
from pyomo.contrib.pyros.util import (
    DR_POLISHING_PARAM_PRODUCT_ZERO_TOL as DR_POLISHING_PARAM_PRODUCT_ZERO_TOL,
)
from pyomo.contrib.pyros.util import TIC_TOC_SOLVE_TIME_ATTR as TIC_TOC_SOLVE_TIME_ATTR
from pyomo.contrib.pyros.util import ObjectiveType as ObjectiveType
from pyomo.contrib.pyros.util import call_solver as call_solver
from pyomo.contrib.pyros.util import check_time_limit_reached as check_time_limit_reached
from pyomo.contrib.pyros.util import enforce_dr_degree as enforce_dr_degree
from pyomo.contrib.pyros.util import (
    generate_all_decision_rule_var_data_objects as generate_all_decision_rule_var_data_objects,
)
from pyomo.contrib.pyros.util import get_all_first_stage_eq_cons as get_all_first_stage_eq_cons
from pyomo.contrib.pyros.util import get_dr_expression as get_dr_expression
from pyomo.contrib.pyros.util import pyrosTerminationCondition as pyrosTerminationCondition
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core.base import Block as Block
from pyomo.core.base import ConcreteModel as ConcreteModel
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Objective as Objective
from pyomo.core.base import Var as Var
from pyomo.core.base.set_types import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core.base.set_types import NonNegativeReals as NonNegativeReals
from pyomo.core.expr import identify_variables as identify_variables
from pyomo.core.expr import value as value
from pyomo.core.util import prod as prod
from pyomo.repn.standard_repn import generate_standard_repn as generate_standard_repn

def construct_initial_master_problem(model_data): ...
def add_scenario_block_to_master_problem(
    master_model, scenario_idx, param_realization, from_block, clone_first_stage_components
) -> None: ...
def construct_master_feasibility_problem(master_data): ...
def solve_master_feasibility_problem(master_data): ...
def construct_dr_polishing_problem(master_data): ...
def minimize_dr_vars(master_data): ...
def get_master_dr_degree(master_data): ...
def higher_order_decision_rule_efficiency(master_data) -> None: ...
def log_master_solve_results(master_model, config, results, desc: str = 'Optimized'): ...
def process_termination_condition_master_problem(config, results): ...
def solver_call_master(master_data): ...
def solve_master(master_data): ...

class MasterProblemData:
    master_model: Incomplete
    original_model_name: Incomplete
    iteration: int
    timing: Incomplete
    config: Incomplete
    def __init__(self, model_data) -> None: ...
    def solve_master(self): ...
    def solve_dr_polishing(self): ...
