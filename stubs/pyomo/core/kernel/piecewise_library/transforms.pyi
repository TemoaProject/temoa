from _typeshed import Incomplete
from pyomo.core.kernel.block import block as block
from pyomo.core.kernel.constraint import constraint_list as constraint_list
from pyomo.core.kernel.constraint import constraint_tuple as constraint_tuple
from pyomo.core.kernel.constraint import linear_constraint as linear_constraint
from pyomo.core.kernel.expression import expression as expression
from pyomo.core.kernel.expression import expression_tuple as expression_tuple
from pyomo.core.kernel.piecewise_library.util import (
    PiecewiseValidationError as PiecewiseValidationError,
)
from pyomo.core.kernel.piecewise_library.util import characterize_function as characterize_function
from pyomo.core.kernel.piecewise_library.util import generate_gray_code as generate_gray_code
from pyomo.core.kernel.piecewise_library.util import is_nondecreasing as is_nondecreasing
from pyomo.core.kernel.piecewise_library.util import (
    is_positive_power_of_two as is_positive_power_of_two,
)
from pyomo.core.kernel.piecewise_library.util import log2floor as log2floor
from pyomo.core.kernel.set_types import IntegerSet as IntegerSet
from pyomo.core.kernel.sos import sos2 as sos2
from pyomo.core.kernel.variable import IVariable as IVariable
from pyomo.core.kernel.variable import variable as variable
from pyomo.core.kernel.variable import variable_dict as variable_dict
from pyomo.core.kernel.variable import variable_list as variable_list
from pyomo.core.kernel.variable import variable_tuple as variable_tuple

logger: Incomplete
registered_transforms: Incomplete

class _shadow_list:
    def __init__(self, x) -> None: ...
    def __len__(self) -> int: ...
    def __getitem__(self, i): ...

def piecewise(
    breakpoints,
    values,
    input=None,
    output=None,
    bound: str = 'eq',
    repn: str = 'sos2',
    validate: bool = True,
    simplify: bool = True,
    equal_slopes_tolerance: float = 1e-06,
    require_bounded_input_variable: bool = True,
    require_variable_domain_coverage: bool = True,
): ...

class PiecewiseLinearFunction:
    def __init__(self, breakpoints, values, validate: bool = True, **kwds) -> None: ...
    def validate(self, equal_slopes_tolerance: float = 1e-06): ...
    @property
    def breakpoints(self): ...
    @property
    def values(self): ...
    def __call__(self, x): ...

class TransformedPiecewiseLinearFunction(block):
    def __init__(
        self, f, input=None, output=None, bound: str = 'eq', validate: bool = True, **kwds
    ) -> None: ...
    @property
    def input(self): ...
    @property
    def output(self): ...
    @property
    def bound(self): ...
    def validate(
        self,
        equal_slopes_tolerance: float = 1e-06,
        require_bounded_input_variable: bool = True,
        require_variable_domain_coverage: bool = True,
    ): ...
    @property
    def breakpoints(self): ...
    @property
    def values(self): ...
    def __call__(self, x): ...

class piecewise_convex(TransformedPiecewiseLinearFunction):
    c: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def validate(self, **kwds): ...

class piecewise_sos2(TransformedPiecewiseLinearFunction):
    c: Incomplete
    s: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def validate(self, **kwds): ...

class piecewise_dcc(TransformedPiecewiseLinearFunction):
    v: Incomplete
    c: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def validate(self, **kwds): ...

class piecewise_cc(TransformedPiecewiseLinearFunction):
    v: Incomplete
    c: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def validate(self, **kwds): ...

class piecewise_mc(TransformedPiecewiseLinearFunction):
    v: Incomplete
    c: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def validate(self, **kwds): ...

class piecewise_inc(TransformedPiecewiseLinearFunction):
    v: Incomplete
    c: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def validate(self, **kwds): ...

class piecewise_dlog(TransformedPiecewiseLinearFunction):
    v: Incomplete
    c: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def validate(self, **kwds): ...

class piecewise_log(TransformedPiecewiseLinearFunction):
    v: Incomplete
    c: Incomplete
    def __init__(self, *args, **kwds) -> None: ...
    def validate(self, **kwds): ...
