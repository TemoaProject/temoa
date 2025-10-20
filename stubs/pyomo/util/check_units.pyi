from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.core.base import Block as Block
from pyomo.core.base import BooleanVar as BooleanVar
from pyomo.core.base import BuildAction as BuildAction
from pyomo.core.base import BuildCheck as BuildCheck
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import Expression as Expression
from pyomo.core.base import ExternalFunction as ExternalFunction
from pyomo.core.base import Objective as Objective
from pyomo.core.base import Param as Param
from pyomo.core.base import RangeSet as RangeSet
from pyomo.core.base import Set as Set
from pyomo.core.base import SetOf as SetOf
from pyomo.core.base import Suffix as Suffix
from pyomo.core.base import Var as Var
from pyomo.core.base import value as value
from pyomo.core.base.units_container import UnitsError as UnitsError
from pyomo.core.base.units_container import units as units
from pyomo.core.expr.numvalue import native_types as native_types
from pyomo.core.expr.template_expr import IndexTemplate as IndexTemplate
from pyomo.dae import ContinuousSet as ContinuousSet
from pyomo.dae import DerivativeVar as DerivativeVar
from pyomo.gdp import Disjunct as Disjunct
from pyomo.gdp import Disjunction as Disjunction
from pyomo.mpec import Complementarity as Complementarity
from pyomo.network import Arc as Arc
from pyomo.network import Port as Port
from pyomo.util.components import iter_component as iter_component

logger: Incomplete

def check_units_equivalent(*args): ...
def assert_units_equivalent(*args) -> None: ...
def assert_units_consistent(obj) -> None: ...
def identify_inconsistent_units(block): ...
