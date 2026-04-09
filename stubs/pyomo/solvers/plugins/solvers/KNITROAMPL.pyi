from _typeshed import Incomplete
from pyomo.common import Executable as Executable
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.dependencies import pathlib as pathlib
from pyomo.opt.base.formats import ProblemFormat as ProblemFormat
from pyomo.opt.base.formats import ResultsFormat as ResultsFormat
from pyomo.opt.base.solvers import OptSolver as OptSolver
from pyomo.opt.base.solvers import SolverFactory as SolverFactory
from pyomo.solvers.plugins.solvers.ASL import ASL as ASL

logger: Incomplete

class KNITROAMPL(ASL):
    def __init__(self, **kwds) -> None: ...
