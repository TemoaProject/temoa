import types
from types import ModuleType

from _typeshed import Incomplete
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.common.deprecation import deprecation_warning as deprecation_warning
from pyomo.common.errors import DeferredImportError as DeferredImportError
from pyomo.common.flags import building_documentation as building_documentation
from pyomo.common.flags import in_testing_environment as in_testing_environment
from pyomo.common.flags import serializing as serializing

SUPPRESS_DEPENDENCY_WARNINGS: bool

class ModuleUnavailable:
    def __init__(self, name, message, version_error, import_error, package) -> None: ...
    def __getattr__(self, attr) -> None: ...
    def mro(self): ...
    def log_import_warning(self, logger: str = 'pyomo', msg=None) -> None: ...
    def generate_import_warning(self, logger: str = 'pyomo.common') -> None: ...

class DeferredImportModule:
    def __init__(self, indicator, deferred_submodules, submodule_name) -> None: ...
    def __getattr__(self, attr): ...
    def mro(self): ...

def UnavailableClass(unavailable_module): ...

class _DeferredImportIndicatorBase:
    def __and__(self, other): ...
    def __or__(self, other): ...
    def __rand__(self, other): ...
    def __ror__(self, other): ...

class DeferredImportIndicator(_DeferredImportIndicatorBase):
    def __init__(
        self,
        name,
        error_message,
        catch_exceptions,
        minimum_version,
        original_globals,
        callback,
        importer,
        deferred_submodules,
    ) -> None: ...
    def __bool__(self) -> bool: ...
    def resolve(self) -> None: ...
    def replace_self_in_globals(self, _globals) -> None: ...

class _DeferredAnd(_DeferredImportIndicatorBase):
    def __init__(self, a, b) -> None: ...
    def __bool__(self) -> bool: ...

class _DeferredOr(_DeferredImportIndicatorBase):
    def __init__(self, a, b) -> None: ...
    def __bool__(self) -> bool: ...

def check_min_version(module, min_version): ...

class DeferredImportCallbackLoader:
    def __init__(self, loader, deferred_indicators: list[DeferredImportIndicator]) -> None: ...
    def module_repr(self, module: ModuleType) -> str: ...
    def create_module(self, spec) -> ModuleType: ...
    def exec_module(self, module: ModuleType) -> None: ...
    def load_module(self, fullname) -> ModuleType: ...

class DeferredImportCallbackFinder:
    def find_spec(self, fullname, path, target=None): ...
    def invalidate_caches(self) -> None: ...

def attempt_import(
    name,
    error_message=None,
    only_catch_importerror=None,
    minimum_version=None,
    alt_names=None,
    callback=None,
    importer=None,
    defer_check=None,
    defer_import=None,
    deferred_submodules=None,
    catch_exceptions=None,
): ...
def declare_deferred_modules_as_importable(globals_dict): ...

class declare_modules_as_importable:
    globals_dict: Incomplete
    init_dict: Incomplete
    init_modules: Incomplete
    def __init__(self, globals_dict) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...

yaml_load_args: Incomplete
ctypes: Incomplete
_: Incomplete
random: Incomplete
dill: Incomplete
dill_available: Incomplete
mpi4py: Incomplete
mpi4py_available: Incomplete
networkx: Incomplete
networkx_available: Incomplete
numpy: Incomplete
numpy_available: Incomplete
pandas: Incomplete
pandas_available: Incomplete
pathlib: Incomplete
pathlib_available: Incomplete
pint: Incomplete
pint_available: Incomplete
plotly: Incomplete
plotly_available: Incomplete
pympler: Incomplete
pympler_available: Incomplete
pyutilib: Incomplete
pyutilib_available: Incomplete
scipy: Incomplete
scipy_available: Incomplete
yaml: Incomplete
yaml_available: Incomplete
matplotlib: Incomplete
matplotlib_available: Incomplete
