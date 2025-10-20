from _typeshed import Incomplete
from pyomo.common.collections import ComponentSet as ComponentSet
from pyomo.common.dependencies import mpi4py as mpi4py
from pyomo.common.dependencies import mpi4py_available as mpi4py_available
from pyomo.common.dependencies import numpy_available as numpy_available
from pyomo.core.base.block import BlockData as BlockData
from pyomo.core.base.block import declare_custom_block as declare_custom_block
from pyomo.core.expr.visitor import identify_variables as identify_variables
from pyomo.solvers.plugins.solvers.persistent_solver import PersistentSolver as PersistentSolver

MPI: Incomplete
logger: Incomplete
__doc__: str
solver_dual_sign_convention: Incomplete

class BendersCutGeneratorData(BlockData):
    num_subproblems_by_rank: int
    subproblems: Incomplete
    complicating_vars_maps: Incomplete
    root_vars: Incomplete
    root_vars_indices: Incomplete
    root_etas: Incomplete
    cuts: Incomplete
    subproblem_solvers: Incomplete
    tol: Incomplete
    all_root_etas: Incomplete
    def __init__(self, component) -> None: ...
    def global_num_subproblems(self): ...
    def local_num_subproblems(self): ...
    comm: Incomplete
    def set_input(self, root_vars, tol: float = 1e-06, comm=None) -> None: ...
    def add_subproblem(
        self,
        subproblem_fn,
        subproblem_fn_kwargs,
        root_eta,
        subproblem_solver: str = 'gurobi_persistent',
        relax_subproblem_cons: bool = False,
    ) -> None: ...
    def generate_cut(self): ...
