import pyomo.core.expr as EXPR
from _typeshed import Incomplete
from pyomo.core import Binary as Binary
from pyomo.core import Constraint as Constraint
from pyomo.core import Integers as Integers
from pyomo.core import IntegerSet as IntegerSet
from pyomo.core import NegativeIntegers as NegativeIntegers
from pyomo.core import NegativeReals as NegativeReals
from pyomo.core import NonNegativeIntegers as NonNegativeIntegers
from pyomo.core import NonNegativeReals as NonNegativeReals
from pyomo.core import NonPositiveIntegers as NonPositiveIntegers
from pyomo.core import NonPositiveReals as NonPositiveReals
from pyomo.core import Objective as Objective
from pyomo.core import PercentFraction as PercentFraction
from pyomo.core import PositiveIntegers as PositiveIntegers
from pyomo.core import PositiveReals as PositiveReals
from pyomo.core import Reals as Reals
from pyomo.core import RealSet as RealSet
from pyomo.core import Set as Set
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import Var as Var
from pyomo.core import nonpyomo_leaf_types as nonpyomo_leaf_types
from pyomo.core import value as value
from pyomo.core.base.misc import create_name as create_name
from pyomo.core.plugins.transform.hierarchy import (
    IsomorphicTransformation as IsomorphicTransformation,
)
from pyomo.core.plugins.transform.util import collectAbstractComponents as collectAbstractComponents
from pyomo.core.plugins.transform.util import partial as partial

logger: Incomplete

class VarmapVisitor(EXPR.ExpressionReplacementVisitor):
    varmap: Incomplete
    def __init__(self, varmap) -> None: ...
    def visiting_potential_leaf(self, node): ...

class NonNegativeTransformation(IsomorphicTransformation):
    realSets: Incomplete
    discreteSets: Incomplete
    def __init__(self, **kwds) -> None: ...
    @staticmethod
    def boundsConstraintRule(lb, ub, attr, vars, model): ...
    @staticmethod
    def noConstraint(*args) -> None: ...
    @staticmethod
    def sumRule(attr, vars, model): ...
    @staticmethod
    def exprMapRule(ruleMap, model, ndx=None): ...
    @staticmethod
    def delayedExprMapRule(ruleMap, model, ndx=None): ...
