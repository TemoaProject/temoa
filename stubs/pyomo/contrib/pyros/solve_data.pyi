from _typeshed import Incomplete

class ROSolveResults:
    config: Incomplete
    iterations: Incomplete
    time: Incomplete
    final_objective_value: Incomplete
    pyros_termination_condition: Incomplete
    def __init__(
        self,
        config=None,
        iterations=None,
        time=None,
        final_objective_value=None,
        pyros_termination_condition=None,
    ) -> None: ...

class MasterResults:
    master_model: Incomplete
    feasibility_problem_results: Incomplete
    master_results_list: Incomplete
    pyros_termination_condition: Incomplete
    def __init__(
        self,
        master_model=None,
        feasibility_problem_results=None,
        master_results_list=None,
        pyros_termination_condition=None,
    ) -> None: ...

class SeparationSolveCallResults:
    results_list: Incomplete
    solved_globally: Incomplete
    scaled_violations: Incomplete
    violating_param_realization: Incomplete
    auxiliary_param_values: Incomplete
    variable_values: Incomplete
    found_violation: Incomplete
    time_out: Incomplete
    subsolver_error: Incomplete
    discrete_set_scenario_index: Incomplete
    def __init__(
        self,
        solved_globally,
        results_list=None,
        scaled_violations=None,
        violating_param_realization=None,
        auxiliary_param_values=None,
        variable_values=None,
        found_violation=None,
        time_out=None,
        subsolver_error=None,
        discrete_set_scenario_index=None,
    ) -> None: ...
    def termination_acceptable(self, acceptable_terminations): ...

class DiscreteSeparationSolveCallResults:
    solved_globally: Incomplete
    solver_call_results: Incomplete
    second_stage_ineq_con: Incomplete
    def __init__(
        self, solved_globally, solver_call_results=None, second_stage_ineq_con=None
    ) -> None: ...
    @property
    def time_out(self): ...
    @property
    def subsolver_error(self): ...

class SeparationLoopResults:
    solver_call_results: Incomplete
    solved_globally: Incomplete
    worst_case_ss_ineq_con: Incomplete
    all_discrete_scenarios_exhausted: Incomplete
    def __init__(
        self,
        solved_globally,
        solver_call_results,
        worst_case_ss_ineq_con,
        all_discrete_scenarios_exhausted: bool = False,
    ) -> None: ...
    @property
    def found_violation(self): ...
    @property
    def violating_param_realization(self): ...
    @property
    def auxiliary_param_values(self): ...
    @property
    def scaled_violations(self): ...
    @property
    def violating_separation_variable_values(self): ...
    @property
    def violated_second_stage_ineq_cons(self): ...
    @property
    def subsolver_error(self): ...
    @property
    def time_out(self): ...

class SeparationResults:
    local_separation_loop_results: Incomplete
    global_separation_loop_results: Incomplete
    def __init__(self, local_separation_loop_results, global_separation_loop_results) -> None: ...
    @property
    def time_out(self): ...
    @property
    def subsolver_error(self): ...
    @property
    def solved_locally(self): ...
    @property
    def solved_globally(self): ...
    def get_violating_attr(self, attr_name): ...
    @property
    def all_discrete_scenarios_exhausted(self): ...
    @property
    def worst_case_ss_ineq_con(self): ...
    @property
    def main_loop_results(self): ...
    @property
    def found_violation(self): ...
    @property
    def violating_param_realization(self): ...
    @property
    def auxiliary_param_values(self): ...
    @property
    def scaled_violations(self): ...
    @property
    def violating_separation_variable_values(self): ...
    @property
    def violated_second_stage_ineq_cons(self): ...
    @property
    def robustness_certified(self): ...
