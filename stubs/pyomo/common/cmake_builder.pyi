from pyomo.common.fileutils import find_executable as find_executable
from pyomo.common.fileutils import this_file_dir as this_file_dir

def handleReadonly(function, path, excinfo) -> None: ...
def build_cmake_project(
    targets, package_name=None, description=None, user_args=[], parallel=None
) -> None: ...
