import enum
import types
import unittest as _unittest
from io import StringIO as StringIO
from unittest import *
from unittest import mock as mock

from _typeshed import Incomplete
from pyomo.common.collections import Mapping as Mapping
from pyomo.common.collections import Sequence as Sequence
from pyomo.common.dependencies import attempt_import as attempt_import
from pyomo.common.dependencies import check_min_version as check_min_version
from pyomo.common.errors import InvalidValueError as InvalidValueError
from pyomo.common.fileutils import import_file as import_file
from pyomo.common.log import LoggingIntercept as LoggingIntercept
from pyomo.common.log import pyomo_formatter as pyomo_formatter
from pyomo.common.tee import capture_output as capture_output

pytest: Incomplete
pytest_available: Incomplete

def assertStructuredAlmostEqual(
    first,
    second,
    places=None,
    msg=None,
    delta=None,
    reltol=None,
    abstol=None,
    allow_second_superset: bool = False,
    item_callback=...,
    exception=...,
    formatter=...,
) -> None: ...

class _RunnerResult(enum.Enum):
    exception = 0
    call = 1
    unittest = 2

def timeout(seconds, require_fork: bool = False, timeout_raises=...): ...

class _AssertRaisesContext_NormalizeWhitespace(_unittest.case._AssertRaisesContext):
    expected_regex: Incomplete
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        tb: types.TracebackType | None,
    ): ...

class TestCase(_unittest.TestCase):
    maxDiff: Incomplete
    def assertStructuredAlmostEqual(
        self,
        first,
        second,
        places=None,
        msg=None,
        delta=None,
        reltol=None,
        abstol=None,
        allow_second_superset: bool = False,
        item_callback=...,
    ) -> None: ...
    def assertRaisesRegex(self, expected_exception, expected_regex, *args, **kwargs): ...
    def assertExpressionsEqual(self, a, b, include_named_exprs: bool = True, places=None): ...
    def assertExpressionsStructurallyEqual(
        self, a, b, include_named_exprs: bool = True, places=None
    ): ...

class BaselineTestDriver:
    @staticmethod
    def custom_name_func(test_func, test_num, test_params): ...
    def __init__(self, test) -> None: ...
    def initialize_dependencies(self) -> None: ...
    @classmethod
    def gather_tests(cls, test_dirs): ...
    def check_skip(self, name): ...
    def filter_fcn(self, line): ...
    def filter_file_contents(self, lines, abstol=None): ...
    def compare_baseline(
        self, test_output, baseline, abstol: float = 1e-06, reltol: float = 1e-08
    ): ...
    def python_test_driver(self, tname, test_file, base_file) -> None: ...
    def shell_test_driver(self, tname, test_file, base_file) -> None: ...
