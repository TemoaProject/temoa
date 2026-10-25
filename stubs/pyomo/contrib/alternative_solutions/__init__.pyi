from pyomo.contrib.alternative_solutions.aos_utils import logcontext as logcontext
from pyomo.contrib.alternative_solutions.balas import (
    enumerate_binary_solutions as enumerate_binary_solutions,
)
from pyomo.contrib.alternative_solutions.lp_enum import (
    enumerate_linear_solutions as enumerate_linear_solutions,
)
from pyomo.contrib.alternative_solutions.obbt import obbt_analysis as obbt_analysis
from pyomo.contrib.alternative_solutions.obbt import (
    obbt_analysis_bounds_and_solutions as obbt_analysis_bounds_and_solutions,
)
from pyomo.contrib.alternative_solutions.solnpool import (
    gurobi_generate_solutions as gurobi_generate_solutions,
)
from pyomo.contrib.alternative_solutions.solution import Solution as Solution
