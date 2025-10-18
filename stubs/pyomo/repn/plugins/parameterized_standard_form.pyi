from _typeshed import Incomplete
from pyomo.common.config import ConfigValue as ConfigValue
from pyomo.common.config import document_kwargs_from_configdict as document_kwargs_from_configdict
from pyomo.common.gc_manager import PauseGC as PauseGC
from pyomo.common.numeric_types import native_numeric_types as native_numeric_types
from pyomo.core import Var as Var
from pyomo.opt import WriterFactory as WriterFactory
from pyomo.repn.parameterized_linear import (
    ParameterizedLinearRepnVisitor as ParameterizedLinearRepnVisitor,
)
from pyomo.repn.plugins.standard_form import (
    LinearStandardFormCompiler as LinearStandardFormCompiler,
)
from pyomo.repn.plugins.standard_form import LinearStandardFormInfo as LinearStandardFormInfo
from pyomo.repn.plugins.standard_form import _LinearStandardFormCompiler_impl
from pyomo.util.config_domains import ComponentDataSet as ComponentDataSet

class ParameterizedLinearStandardFormCompiler(LinearStandardFormCompiler):
    CONFIG: Incomplete
    def write(self, model, ostream=None, **options): ...

class _SparseMatrixBase:
    data: Incomplete
    indices: Incomplete
    indptr: Incomplete
    shape: Incomplete
    def __init__(self, matrix_data, shape) -> None: ...
    def __eq__(self, other): ...

class _CSRMatrix(_SparseMatrixBase):
    def __init__(self, matrix_data, shape) -> None: ...
    def tocsc(self): ...
    def todense(self): ...

class _CSCMatrix(_SparseMatrixBase):
    def __init__(self, matrix_data, shape) -> None: ...
    def todense(self): ...
    data: Incomplete
    row_index: Incomplete
    def sum_duplicates(self) -> None: ...
    def eliminate_zeros(self) -> None: ...

class _ParameterizedLinearStandardFormCompiler_impl(_LinearStandardFormCompiler_impl): ...
