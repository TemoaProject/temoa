from _typeshed import Incomplete
from pyomo.common.download import FileDownloader as FileDownloader
from pyomo.common.envvar import PYOMO_CONFIG_DIR as PYOMO_CONFIG_DIR
from pyomo.common.fileutils import find_library as find_library
from pyomo.common.fileutils import this_file_dir as this_file_dir
from pyomo.common.tempfiles import TempfileManager as TempfileManager

logger: Incomplete

def build_ginac_library(parallel=None, argv=None, env=None) -> None: ...
def build_ginac_interface(parallel=None, args=None) -> None: ...

class GiNaCInterfaceBuilder:
    def __call__(self, parallel): ...
    def skip(self): ...
