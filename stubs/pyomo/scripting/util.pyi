import types

from _typeshed import Incomplete
from pyomo.common.collections import Bunch as Bunch
from pyomo.common.dependencies import pympler as pympler
from pyomo.common.dependencies import pympler_available as pympler_available
from pyomo.common.dependencies import yaml as yaml
from pyomo.common.dependencies import yaml_available as yaml_available
from pyomo.common.dependencies import yaml_load_args as yaml_load_args
from pyomo.common.deprecation import deprecated as deprecated
from pyomo.common.fileutils import import_file as import_file
from pyomo.common.log import is_debug_set as is_debug_set
from pyomo.common.tee import capture_output as capture_output
from pyomo.common.tempfiles import TempfileManager as TempfileManager
from pyomo.core import Model as Model
from pyomo.core import Suffix as Suffix
from pyomo.core import TransformationFactory as TransformationFactory
from pyomo.core import display as display
from pyomo.dataportal import DataPortal as DataPortal
from pyomo.opt import ProblemFormat as ProblemFormat
from pyomo.opt.base import SolverFactory as SolverFactory
from pyomo.opt.parallel import SolverManagerFactory as SolverManagerFactory
from pyomo.scripting.interface import ExtensionPoint as ExtensionPoint
from pyomo.scripting.interface import IPyomoScriptCreateDataPortal as IPyomoScriptCreateDataPortal
from pyomo.scripting.interface import IPyomoScriptCreateModel as IPyomoScriptCreateModel
from pyomo.scripting.interface import IPyomoScriptModifyInstance as IPyomoScriptModifyInstance
from pyomo.scripting.interface import IPyomoScriptPostprocess as IPyomoScriptPostprocess
from pyomo.scripting.interface import IPyomoScriptPreprocess as IPyomoScriptPreprocess
from pyomo.scripting.interface import IPyomoScriptPrintInstance as IPyomoScriptPrintInstance
from pyomo.scripting.interface import IPyomoScriptPrintModel as IPyomoScriptPrintModel
from pyomo.scripting.interface import IPyomoScriptPrintResults as IPyomoScriptPrintResults
from pyomo.scripting.interface import IPyomoScriptSaveInstance as IPyomoScriptSaveInstance
from pyomo.scripting.interface import IPyomoScriptSaveResults as IPyomoScriptSaveResults
from pyomo.scripting.interface import Plugin as Plugin
from pyomo.scripting.interface import implements as implements
from pyomo.scripting.interface import registered_callback as registered_callback

memory_data: Incomplete
IPython_available: Incomplete
filter_excepthook: bool
modelapi: Incomplete
logger: Incomplete
start_time: float

def setup_environment(data) -> None: ...
def apply_preprocessing(data, parser=None): ...
def create_model(data): ...
def apply_optimizer(data, instance=None): ...
def process_results(data, instance=None, results=None, opt=None) -> None: ...
def apply_postprocessing(data, instance=None, results=None) -> None: ...
def finalize(data, model=None, instance=None, results=None) -> None: ...
def configure_loggers(options=None, shutdown: bool = False) -> None: ...

class PyomoCommandLogContext:
    options: Incomplete
    fileLogger: Incomplete
    original: Incomplete
    def __init__(self, options) -> None: ...
    capture: Incomplete
    def __enter__(self): ...
    def __exit__(
        self,
        et: type[BaseException] | None,
        ev: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None: ...

def run_command(
    command=None, parser=None, args=None, name: str = 'unknown', data=None, options=None
): ...
def cleanup() -> None: ...
def get_config_values(filename): ...
