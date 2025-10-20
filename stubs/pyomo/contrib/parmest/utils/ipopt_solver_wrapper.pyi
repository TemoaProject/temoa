from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.opt import TerminationCondition as TerminationCondition

def ipopt_solve_with_stats(model, solver, max_iter: int = 500, max_cpu_time: int = 120): ...
