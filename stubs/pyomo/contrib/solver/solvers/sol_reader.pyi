import io
from typing import Any, Mapping, NoReturn, Sequence

from pyomo.common.collections import ComponentMap as ComponentMap
from pyomo.common.errors import DeveloperError as DeveloperError
from pyomo.common.errors import PyomoException as PyomoException
from pyomo.contrib.solver.common.results import Results as Results
from pyomo.contrib.solver.common.results import SolutionStatus as SolutionStatus
from pyomo.contrib.solver.common.results import TerminationCondition as TerminationCondition
from pyomo.contrib.solver.common.solution_loader import SolutionLoaderBase as SolutionLoaderBase
from pyomo.core.base.constraint import ConstraintData as ConstraintData
from pyomo.core.base.var import VarData as VarData
from pyomo.core.expr import value as value
from pyomo.core.expr.visitor import replace_expressions as replace_expressions
from pyomo.core.staleflag import StaleFlagManager as StaleFlagManager
from pyomo.repn.plugins.nl_writer import NLWriterInfo as NLWriterInfo

class SolFileData:
    primals: list[float]
    duals: list[float]
    var_suffixes: dict[str, dict[int, Any]]
    con_suffixes: dict[str, dict[Any]]
    obj_suffixes: dict[str, dict[int, Any]]
    problem_suffixes: dict[str, list[Any]]
    other: None
    def __init__(self) -> None: ...

class SolSolutionLoader(SolutionLoaderBase):
    def __init__(self, sol_data: SolFileData, nl_info: NLWriterInfo) -> None: ...
    def load_vars(self, vars_to_load: Sequence[VarData] | None = None) -> NoReturn: ...
    def get_primals(
        self, vars_to_load: Sequence[VarData] | None = None
    ) -> Mapping[VarData, float]: ...
    def get_duals(
        self, cons_to_load: Sequence[ConstraintData] | None = None
    ) -> dict[ConstraintData, float]: ...

def parse_sol_file(
    sol_file: io.TextIOBase, nl_info: NLWriterInfo, result: Results
) -> tuple[Results, SolFileData]: ...
