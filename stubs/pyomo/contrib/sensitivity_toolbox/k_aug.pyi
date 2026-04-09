import types

from _typeshed import Incomplete
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.environ import SolverFactory as SolverFactory

debug_dir: str
gjh_dir: str
known_files: Incomplete

class InTempDir:
    def __init__(self, suffix=None, prefix=None, dir=None) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        ex_type: type[BaseException] | None,
        ex_val: BaseException | None,
        ex_bt: types.TracebackType | None,
    ) -> None: ...

class K_augInterface:
    data: Incomplete
    def __init__(self, k_aug=None, dot_sens=None) -> None: ...
    def k_aug(self, model, **kwargs): ...
    def dot_sens(self, model, **kwargs): ...
    def set_k_aug_options(self, **options) -> None: ...
    def set_dot_sens_options(self, **options) -> None: ...
