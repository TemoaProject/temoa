from typing import Mapping, Sequence

from _typeshed import Incomplete
from pyomo.common import Executable as Executable
from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.config import ConfigDict as ConfigDict
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.errors import ApplicationError as ApplicationError
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.common.errors import InfeasibleConstraintException as InfeasibleConstraintException
from pyomo.common.tee import TeeStream as TeeStream
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.common.timing import HierarchicalTimer as HierarchicalTimer
from pyomo.contrib.solver.common.base import Availability as Availability
from pyomo.contrib.solver.common.base import SolverBase as SolverBase
from pyomo.contrib.solver.common.config import SolverConfig as SolverConfig
from pyomo.contrib.solver.common.results import Results as Results
from pyomo.contrib.solver.common.results import SolutionStatus as SolutionStatus
from pyomo.contrib.solver.common.results import TerminationCondition as TerminationCondition
from pyomo.contrib.solver.common.util import NoFeasibleSolutionError as NoFeasibleSolutionError
from pyomo.contrib.solver.common.util import NoOptimalSolutionError as NoOptimalSolutionError
from pyomo.contrib.solver.common.util import NoSolutionError as NoSolutionError
from pyomo.contrib.solver.solvers.sol_reader import SolSolutionLoader as SolSolutionLoader
from pyomo.contrib.solver.solvers.sol_reader import parse_sol_file as parse_sol_file
from pyomo.core.base.suffix import Suffix as Suffix
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr.numvalue import value as value
from pyomo.core.expr.visitor import replace_expressions as replace_expressions
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.repn.plugins.nl_writer import NLWriter as NLWriter
from pyomo.repn.plugins.nl_writer import NLWriterInfo as NLWriterInfo
from pyomo.solvers.amplfunc_merge import amplfunc_merge as amplfunc_merge

logger: Incomplete

class IpoptConfig(SolverConfig):
    executable: Executable
    writer_config: ConfigDict
    def __init__(
        self,
        description=None,
        doc=None,
        implicit: bool = False,
        implicit_domain=None,
        visibility: int = 0,
    ) -> None: ...

class IpoptSolutionLoader(SolSolutionLoader):
    def get_reduced_costs(
        self, vars_to_load: Sequence[VarData] | None = None
    ) -> Mapping[VarData, float]: ...

ipopt_command_line_options: Incomplete

class Ipopt(SolverBase):
    CONFIG: Incomplete
    def __init__(self, **kwds) -> None: ...
    def available(self, config=None): ...
    def version(self, config=None): ...
    def has_linear_solver(self, linear_solver): ...
    def solve(self, model, **kwds): ...
