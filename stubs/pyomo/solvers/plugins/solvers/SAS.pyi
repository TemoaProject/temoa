import abc
from abc import ABC

from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.log import LogStream as LogStream
from pyomo.common.tee import TeeStream as TeeStream
from pyomo.common.tee import capture_output as capture_output
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core.base import Var as Var
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.kernel.block import IBlock as IBlock
from pyomo.opt.base import OptSolver as OptSolver
from pyomo.opt.base import ProblemFormat as ProblemFormat
from pyomo.opt.base import ResultsFormat as ResultsFormat
from pyomo.opt.base.solvers import SolverFactory as SolverFactory
from pyomo.opt.results import ProblemSense as ProblemSense
from pyomo.opt.results import SolutionStatus as SolutionStatus
from pyomo.opt.results import SolverResults as SolverResults
from pyomo.opt.results import SolverStatus as SolverStatus
from pyomo.opt.results import TerminationCondition as TerminationCondition

uuid: Incomplete
uuid_available: Incomplete
logger: Incomplete
STATUS_TO_SOLVERSTATUS: Incomplete
SOLSTATUS_TO_TERMINATIONCOND: Incomplete
SOLSTATUS_TO_MESSAGE: Incomplete

class SAS(OptSolver):
    def __new__(cls, *args, **kwds): ...

class SASAbc(ABC, OptSolver, metaclass=abc.ABCMeta):
    def __init__(self, **kwds) -> None: ...
    def available(self, exception_flag: bool = False): ...
    def warm_start_capable(self): ...

class SAS94(SASAbc):
    def __init__(self, **kwds) -> None: ...
    def __del__(self) -> None: ...
    def sas_version(self): ...
    def start_sas_session(self): ...

class SASCAS(SASAbc):
    def __init__(self, **kwds) -> None: ...
    def __del__(self) -> None: ...
    def start_sas_session(self): ...
