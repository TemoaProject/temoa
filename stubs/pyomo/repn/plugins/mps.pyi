from _typeshed import Incomplete
from pyomo.common.gc_manager import PauseGC as PauseGC
from pyomo.core.base import ComponentMap as ComponentMap
from pyomo.core.base import Constraint as Constraint
from pyomo.core.base import NumericLabeler as NumericLabeler
from pyomo.core.base import Objective as Objective
from pyomo.core.base import SortComponents as SortComponents
from pyomo.core.base import SOSConstraint as SOSConstraint
from pyomo.core.base import SymbolMap as SymbolMap
from pyomo.core.base import TextLabeler as TextLabeler
from pyomo.core.base import Var as Var
from pyomo.core.base import is_fixed as is_fixed
from pyomo.core.base import value as value
from pyomo.opt import ProblemFormat as ProblemFormat
from pyomo.opt.base import AbstractProblemWriter as AbstractProblemWriter
from pyomo.opt.base import WriterFactory as WriterFactory
from pyomo.repn import generate_standard_repn as generate_standard_repn

logger: Incomplete

class ProblemWriter_mps(AbstractProblemWriter):
    def __init__(self, int_marker: bool = False) -> None: ...
    def __call__(self, model, output_filename, solver_capability, io_options): ...
