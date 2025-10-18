import pyomo.opt
from pyomo.common.collections import Bunch as Bunch
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.opt import SolverFactory as SolverFactory

class MPEC_Solver2(pyomo.opt.OptSolver):
    def __init__(self, **kwds) -> None: ...
