from typing import NamedTuple

from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.contrib.pyros.util import IterationLogRecord as IterationLogRecord
from pyomo.contrib.pyros.util import ObjectiveType as ObjectiveType
from pyomo.contrib.pyros.util import check_time_limit_reached as check_time_limit_reached
from pyomo.contrib.pyros.util import get_dr_var_to_monomial_map as get_dr_var_to_monomial_map
from pyomo.contrib.pyros.util import get_main_elapsed_time as get_main_elapsed_time
from pyomo.contrib.pyros.util import pyrosTerminationCondition as pyrosTerminationCondition
from pyomo.core.base import value as value

class GRCSResults:
    master_results: Incomplete
    separation_results: Incomplete
    pyros_termination_condition: Incomplete
    iterations: Incomplete
    def __init__(
        self, master_results, separation_results, pyros_termination_condition, iterations
    ) -> None: ...

class VariableValueData(NamedTuple):
    first_stage_variables: Incomplete
    second_stage_variables: Incomplete
    decision_rule_monomials: Incomplete

def get_variable_value_data(working_blk, dr_var_to_monomial_map): ...
def evaluate_variable_shifts(current_var_data, previous_var_data, initial_var_data): ...
def ROSolver_iterative_solve(model_data): ...
