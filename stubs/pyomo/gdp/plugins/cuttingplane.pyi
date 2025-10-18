from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.config import ConfigBlock as ConfigBlock
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import In as In
from pyomo.common.config import NonNegativeFloat as NonNegativeFloat
from pyomo.common.config import PositiveInt as PositiveInt
from pyomo.common.modeling import unique_component_name as unique_component_name
from pyomo.contrib.fme.fourier_motzkin_elimination import (
    Fourier_Motzkin_Elimination_Transformation as Fourier_Motzkin_Elimination_Transformation,
)
from pyomo.core import Any as Any
from pyomo.core import Block as Block
from pyomo.core import ComponentMap as ComponentMap
from pyomo.core import Constraint as Constraint
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import NonNegativeReals as NonNegativeReals
from pyomo.core import Objective as Objective
from pyomo.core import Param as Param
from pyomo.core import Reals as Reals
from pyomo.core import SortComponents as SortComponents
from pyomo.core import Suffix as Suffix
from pyomo.core import Transformation as Transformation
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import Var as Var
from pyomo.core import value as value
from pyomo.core.expr import differentiate as differentiate
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.gdp import GDP_Error as GDP_Error
from pyomo.gdp.util import NORMAL as NORMAL
from pyomo.gdp.util import (
    clone_without_expression_components as clone_without_expression_components,
)
from pyomo.gdp.util import verify_successful_solve as verify_successful_solve
from pyomo.opt import SolverFactory as SolverFactory
from pyomo.repn import generate_standard_repn as generate_standard_repn

logger: Incomplete

def do_not_tighten(m): ...
def create_cuts_fme(
    transBlock_rHull,
    var_info,
    hull_to_bigm_map,
    rBigM_linear_constraints,
    rHull_vars,
    disaggregated_vars,
    norm,
    cut_threshold,
    zero_tolerance,
    integer_arithmetic,
    constraint_tolerance,
): ...
def create_cuts_normal_vector(
    transBlock_rHull,
    var_info,
    hull_to_bigm_map,
    rBigM_linear_constraints,
    rHull_vars,
    disaggregated_vars,
    norm,
    cut_threshold,
    zero_tolerance,
    integer_arithmetic,
    constraint_tolerance,
): ...
def back_off_constraint_with_calculated_cut_violation(
    cut, transBlock_rHull, bigm_to_hull_map, opt, stream_solver, TOL
) -> None: ...
def back_off_constraint_by_fixed_tolerance(
    cut, transBlock_rHull, bigm_to_hull_map, opt, stream_solver, TOL
) -> None: ...

class CuttingPlane_Transformation(Transformation):
    CONFIG: Incomplete
    def __init__(self) -> None: ...
