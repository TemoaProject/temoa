from _typeshed import Incomplete
from pyomo.opt import SolutionStatus as SolutionStatus
from pyomo.opt import SolverResults as SolverResults
from pyomo.opt import SolverStatus as SolverStatus
from pyomo.opt import TerminationCondition as TerminationCondition
from pyomo.opt.base import results as results
from pyomo.opt.base.formats import ResultsFormat as ResultsFormat

class ResultsReader_sol(results.AbstractResultsReader):
    name: Incomplete
    def __init__(self, name=None) -> None: ...
    def __call__(self, filename, res=None, soln=None, suffixes=[]): ...
