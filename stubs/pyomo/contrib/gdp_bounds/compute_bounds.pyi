from _typeshed import Incomplete
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.errors import InfeasibleConstraintException as InfeasibleConstraintException
from pyomo.contrib.fbbt.fbbt import BoundsManager as BoundsManager
from pyomo.contrib.fbbt.fbbt import fbbt as fbbt
from pyomo.core import Constraint as Constraint
from pyomo.core import Objective as Objective
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import minimize as minimize
from pyomo.core import value as value
from pyomo.core.base.block import Block as Block
from pyomo.core.base.block import TraversalStrategy as TraversalStrategy
from pyomo.core.expr import identify_variables as identify_variables
from pyomo.core.plugins.transform.hierarchy import Transformation as Transformation
from pyomo.gdp.disjunct import Disjunct as Disjunct
from pyomo.opt import SolverFactory as SolverFactory

linear_degrees: Incomplete
inf: Incomplete

def disjunctive_obbt(model, solver) -> None: ...
def obbt_disjunct(orig_model, idx, solver): ...
def solve_bounding_problem(model, solver): ...
def disjunctive_fbbt(model) -> None: ...
def fbbt_disjunct(disj, parent_bounds) -> None: ...

class ComputeDisjunctiveVarBounds(Transformation): ...
